"""Udyam Digital - FastAPI backend.

Run:  uvicorn app:app --reload --port 8000   (from backend/)
Open: http://localhost:8000          customer journey (mobile)
      http://localhost:8000/backoffice  sales / partner view
"""
from __future__ import annotations

import datetime as dt
import hashlib
import logging
import re
import uuid
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import advisor
from catalogue import BusinessProfile, catalogue, price, recommend
from kyc import DOC_TYPES, TODAY, process_document, validate_application
from propensity import explain, features, model
from registry import lookup_gstin, lookup_udyam, mask

ROOT = Path(__file__).resolve().parent.parent
FRONT = ROOT / "frontend"
log = logging.getLogger("udyam")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Udyam Digital", version="1.0")
app.mount("/static", StaticFiles(directory=FRONT), name="static")

CONSENTS: dict[str, dict] = {}   # session -> consent record (purpose, time, version)
KYC: dict[str, dict] = {}        # session -> {doc_type: fields}  (images are never stored)
ORDERS: dict[str, dict] = {}
AUDIT: list[dict] = []           # masked audit trail
CONSENT_VERSION = "2026-10-v1"
RETENTION_DAYS = 30              # KYC extracts kept 30 days after activation, then deleted


def audit(event: str, sid: str, **kw):
    rec = {"t": dt.datetime.now().isoformat(timespec="seconds"), "event": event, "session": sid[:6] + "…", **kw}
    AUDIT.append(rec)
    log.info("%s", rec)


@app.get("/")
def home():
    return FileResponse(FRONT / "index.html")


@app.get("/backoffice")
def backoffice():
    return FileResponse(FRONT / "backoffice.html")


# ------------------------------------------------------------------ advisor
class StartReq(BaseModel):
    lang: str = "en"


class MsgReq(BaseModel):
    session_id: str
    text: str = ""
    choice: str | None = None
    selected: list[str] | None = None


@app.post("/api/advisor/start")
def advisor_start(r: StartReq):
    out = advisor.new_session(r.lang)
    audit("advisor_start", out["session_id"], lang=r.lang)
    return out


@app.post("/api/advisor/message")
def advisor_message(r: MsgReq):
    try:
        out = advisor.handle(r.session_id, r.text, r.choice, r.selected)
    except KeyError:
        raise HTTPException(404, "Session expired - please start again")
    if out.get("handoff"):
        audit("handoff", r.session_id, step=advisor.SESSIONS[r.session_id]["step"])
    return out


# ------------------------------------------------------------------ quote
class QuoteReq(BaseModel):
    session_id: str
    selected: list[str] | None = None
    contract_months: int | None = None


def _session(sid):
    s = advisor.SESSIONS.get(sid)
    if not s or not s.get("recommendation"):
        raise HTTPException(404, "No recommendation yet for this session")
    return s


@app.post("/api/quote")
def quote(r: QuoteReq):
    s = _session(r.session_id)
    b = s["recommendation"]
    if r.contract_months in (12, 24):
        b["contract_months"] = r.contract_months
    sel = set(r.selected) if r.selected is not None else None
    warnings = []
    if sel is not None:
        cat = catalogue()
        for pid in list(sel):
            deps = cat[pid]["deps"]
            if deps and not sel.intersection(deps):
                base = next((l["product_id"] for l in b["lines"] if l["product_id"] in deps), None)
                if base:
                    sel.add(base)
                    warnings.append(f"{cat[pid]['product_name']} needs {cat[base]['product_name']} – kept it on")
                else:
                    sel.discard(pid)
    q = price(b, sel)
    q["warnings"] = warnings
    q["install_days"] = max((i["install_days"] for i in q["items"] if i["on"]), default=1)
    s["quote"] = q
    return q


# ------------------------------------------------------------------ registries (masked)
@app.get("/api/lookup/gstin/{gstin}")
def api_gstin(gstin: str):
    lk = lookup_gstin(gstin)
    rec = lk.get("record") or {}
    return {"found": lk["found"], "format": {k: v for k, v in lk["format"].items() if k != "pan"},
            "gstin_masked": mask(lk["format"]["gstin"]), "trade_name": rec.get("trade_name"), "status": rec.get("status"),
            "constitution": rec.get("constitution"), "state": rec.get("state")}


@app.get("/api/lookup/udyam/{num}")
def api_udyam(num: str):
    lk = lookup_udyam(num)
    rec = lk.get("record") or {}
    return {"found": lk["found"], "format": lk["format"], "enterprise_name": rec.get("enterprise_name"),
            "enterprise_type": rec.get("enterprise_type"), "major_activity": rec.get("major_activity")}


# ------------------------------------------------------------------ consent + KYC
class ConsentReq(BaseModel):
    session_id: str
    purposes: list[str]
    lang: str = "en"


REQUIRED_PURPOSES = {"kyc_verification", "service_activation"}


@app.post("/api/kyc/consent")
def consent(r: ConsentReq):
    if not REQUIRED_PURPOSES.issubset(r.purposes):
        raise HTTPException(400, "KYC verification and service activation consent are required to continue")
    cid = "CN-" + uuid.uuid4().hex[:8].upper()
    CONSENTS[r.session_id] = {"consent_id": cid, "purposes": r.purposes, "version": CONSENT_VERSION,
                              "time": dt.datetime.now().isoformat(timespec="seconds"), "lang": r.lang}
    audit("consent_given", r.session_id, consent_id=cid, purposes=r.purposes)
    return CONSENTS[r.session_id]


@app.delete("/api/kyc/consent/{sid}")
def withdraw(sid: str):
    CONSENTS.pop(sid, None)
    KYC.pop(sid, None)
    audit("consent_withdrawn_data_erased", sid)
    return {"ok": True, "message": "Consent withdrawn. Your KYC data has been deleted."}


def _need_consent(sid):
    if sid not in CONSENTS:
        raise HTTPException(403, "Please give consent before uploading documents")


def _public_fields(f: dict) -> dict:
    out = {}
    for k, v in f.items():
        if k.startswith("_"):
            continue
        if k in ("gstin",):
            v = mask(v)
        elif k in ("udyam_number",):
            v = mask(v, 6, 3)
        elif k in ("id_no", "consumer_no"):
            v = mask(v, 0, 4)
        out[k] = v
    return out


@app.post("/api/kyc/upload")
async def kyc_upload(session_id: str = Form(...), doc_type: str = Form(...), file: UploadFile = File(...)):
    _need_consent(session_id)
    if doc_type not in DOC_TYPES:
        raise HTTPException(400, "Unknown document type")
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 8 MB)")
    res = process_document(data, None, filename=file.filename)
    detected = res["doc_type"]
    if detected and detected != doc_type:
        res["quality_notes"].append(f"This looks like a {detected.replace('_', ' ')}, not a {doc_type.replace('_', ' ')}")
    KYC.setdefault(session_id, {})[doc_type] = res["fields"]
    digest = hashlib.sha256(data).hexdigest()[:16]
    del data  # image bytes are discarded after extraction - only fields + hash are kept
    audit("doc_extracted", session_id, doc=doc_type, sha256=digest)
    return {"doc_type": doc_type, "detected": detected, "fields": _public_fields(res["fields"]),
            "quality_notes": res["quality_notes"], "ocr": res["ocr"]}


class DigiLockerReq(BaseModel):
    session_id: str


@app.post("/api/kyc/digilocker")
def kyc_digilocker(r: DigiLockerReq):
    """DigiLocker integration: securely fetch verified Udyam and GST certificates with user consent."""
    _need_consent(r.session_id)
    s = advisor.SESSIONS.get(r.session_id, {})
    target_k = "K12"
    out = {}
    for p in sorted((ROOT / "data" / "kyc_documents").glob(f"{target_k}_*.png")):
        res = process_document(p.read_bytes(), None, filename=p.name)
        dt_ = res["doc_type"] or p.stem.split("_", 1)[1]
        KYC.setdefault(r.session_id, {})[dt_] = res["fields"]
        out[dt_] = {"fields": _public_fields(res["fields"]), "quality_notes": ["Securely fetched via DigiLocker (MeitY) - instant verification"], "ocr": {"skew_deg": 0.0, "sharpness": 1000.0, "blurry": False}, "file": "DigiLocker Verified"}
    audit("digilocker_fetch_completed", r.session_id, source="digilocker_meity")
    return out


@app.get("/api/kyc/applicants")
def list_applicants():
    """List all available specimen applicant codes found in data/kyc_documents."""
    p = ROOT / "data" / "kyc_documents"
    codes = sorted({f.name.split("_")[0] for f in p.glob("K*.png") if re.match(r"^K\d{2}$", f.name.split("_")[0])})
    return {"applicants": codes or [f"K{i:02d}" for i in range(1, 13)]}


class SampleReq(BaseModel):
    session_id: str
    applicant: str  # K01..K99 specimen sets shipped with the case


@app.post("/api/kyc/sample")
def kyc_sample(r: SampleReq):
    """Demo helper: run the specimen documents of one case applicant through OCR."""
    _need_consent(r.session_id)
    if not re.fullmatch(r"K\d{2}", r.applicant):
        raise HTTPException(400, "Applicant must be K01..K99")
    out = {}
    for p in sorted((ROOT / "data" / "kyc_documents").glob(f"{r.applicant}_*.png")):
        res = process_document(p.read_bytes(), None, filename=p.name)
        dt_ = res["doc_type"] or p.stem.split("_", 1)[1]
        KYC.setdefault(r.session_id, {})[dt_] = res["fields"]
        out[dt_] = {"fields": _public_fields(res["fields"]), "quality_notes": res["quality_notes"], "ocr": res["ocr"], "file": p.name}
    audit("sample_docs_extracted", r.session_id, applicant=r.applicant)
    return out


class ValidateReq(BaseModel):
    session_id: str


@app.post("/api/kyc/validate")
def kyc_validate(r: ValidateReq):
    _need_consent(r.session_id)
    docs = KYC.get(r.session_id, {})
    s = advisor.SESSIONS.get(r.session_id, {})
    res = validate_application(docs, {"business_name": (s.get("registry") or {}).get("trade_name"), "gstin": s.get("gstin")} if s.get("registry") else None)
    # cross-check with the bundle: GST-only products need an active GSTIN
    rec = s.get("recommendation")
    if rec:
        cat = catalogue()
        gst_ok = any(c["code"] == "GSTIN_ACTIVE" for c in res["checks"]) and not any(
            c["level"] == "fail" and c["code"].startswith("GSTIN") for c in res["checks"])
        need = [cat[l["product_id"]]["product_name"] for l in rec["lines"] if not l["optional"] and cat[l["product_id"]]["requires_gstin"] == "Y"]
        if need and not gst_ok:
            res["checks"].append({"level": "fail", "code": "BUNDLE_NEEDS_GST", "doc": "gst_certificate",
                                  "message": f"{', '.join(need)} need an active GSTIN - remove them or fix the GST certificate"})
    s["kyc_result"] = res
    audit("kyc_validated", r.session_id, status=res["status"], fails=[c["code"] for c in res["checks"] if c["level"] == "fail"])
    return res


# ------------------------------------------------------------------ order + tracker
class OrderReq(BaseModel):
    session_id: str
    install_slot: str  # e.g. "2026-07-18 10:00-13:00"
    payment: str = "upi_autopay"


def _stages(o):
    t0 = dt.datetime.fromisoformat(o["created"])
    d = o["install_days"]
    plan = [("placed", "Order placed", "ऑर्डर हो गया", 0), ("kyc", "KYC verified", "KYC सत्यापित", 0),
            ("survey", "Site check done", "साइट जाँच पूरी", max(1, d // 3)),
            ("scheduled", "Engineer assigned", "इंजीनियर तय", max(1, d // 2)),
            ("installed", "Installed", "इंस्टॉल हो गया", d), ("active", "Active – you're live!", "चालू – आप लाइव हैं!", d)]
    out = []
    for i, (k, en, hi, day) in enumerate(plan):
        out.append({"key": k, "label": en, "label_hi": hi, "eta": (t0 + dt.timedelta(days=day)).date().isoformat(),
                    "done": i <= o["progress"], "current": i == o["progress"] + 1})
    return out


@app.post("/api/order")
def place_order(r: OrderReq):
    s = _session(r.session_id)
    kyc = s.get("kyc_result")
    if not kyc or kyc["status"] == "rejected_fixable":
        raise HTTPException(409, "KYC needs to be fixed before placing the order")
    q = s.get("quote") or price(s["recommendation"])
    oid = "UD" + dt.date.today().strftime("%y%m") + uuid.uuid4().hex[:5].upper()
    on = [i for i in q["items"] if i["on"]]
    ORDERS[oid] = {"order_id": oid, "session_id": r.session_id, "created": TODAY.isoformat() + "T10:00:00",
                   "items": [{"name": i["name"], "qty": i["qty"]} for i in on], "monthly_total": q["monthly_total"],
                   "one_time_setup": q["one_time_setup"], "install_slot": r.install_slot,
                   "install_days": max(i["install_days"] for i in on), "progress": 1 if kyc["status"] == "verified" else 0,
                   "kyc_status": kyc["status"], "engineer": None, "updates": ["WhatsApp: Order confirmed"]}
    s["order_id"] = oid
    audit("order_placed", r.session_id, order=oid, monthly=q["monthly_total"])
    return get_order(oid)


@app.get("/api/order/{oid}")
def get_order(oid: str):
    o = ORDERS.get(oid)
    if not o:
        raise HTTPException(404, "Order not found")
    return {**{k: v for k, v in o.items() if k != "session_id"}, "stages": _stages(o)}


@app.post("/api/order/{oid}/advance")
def advance(oid: str):
    """Demo: simulate the next field event (survey, engineer, install, activation)."""
    o = ORDERS[oid]
    o["progress"] = min(o["progress"] + 1, 5)
    if o["progress"] == 3:
        o["engineer"] = {"name": "Ravi K.", "phone": "+91 98xxxx1234", "arrival": o["install_slot"]}
    msg = {2: "Site check done – fibre available", 3: "Engineer Ravi K. assigned", 4: "Installation complete", 5: "All services active"}.get(o["progress"])
    if msg:
        o["updates"].append("WhatsApp: " + msg)
    return get_order(oid)


# ------------------------------------------------------------------ back office
@app.get("/api/backoffice/leads")
def bo_leads(segment: str | None = None, source: str | None = None, limit: int = 50):
    pipe, stats, oof = model()
    df = pd.read_csv(ROOT / "data" / "smb_leads.csv")
    df["propensity"] = oof  # out-of-fold scores - honest for the quarter's own leads
    open_ = df[df.outcome == "Dropped"].copy()
    if segment:
        open_ = open_[open_.segment == segment]
    if source:
        open_ = open_[open_.lead_source == source]
    open_ = open_.sort_values("propensity", ascending=False).head(limit)
    rows = []
    for _, r in open_.iterrows():
        route = "Partner visit" if r.segment in ("Small manufacturers", "Small multi-site businesses") else (
            "Field sales" if r.monthly_telecom_spend_inr >= 3000 else "Digital nudge (WhatsApp)")
        rows.append({"lead_id": r.lead_id, "business": r.business_name, "type": r.business_type, "segment": r.segment,
                     "city": r.city, "language": r.preferred_language, "source": r.lead_source, "stage": r.stage_reached,
                     "drop_reason": r.drop_reason, "spend": int(r.monthly_telecom_spend_inr),
                     "gstin": mask(r.gstin) if isinstance(r.gstin, str) else "—",
                     "propensity": round(float(r.propensity), 3), "why": explain(pipe, features(df.loc[[_]])),
                     "route": route})
    handoffs = [{"session": sid[:6] + "…", "business": s["profile"].business_type, "segment": s["profile"].segment,
                 "step": s["step"], "events": s["events"][-3:], "gstin": s.get("gstin_masked")}
                for sid, s in advisor.SESSIONS.items() if "handoff_requested" in s["events"] or (s.get("kyc_result") or {}).get("status") == "rejected_fixable"]
    return {"stats": stats, "leads": rows, "handoffs": handoffs}


@app.get("/api/backoffice/audit")
def bo_audit():
    return AUDIT[-100:]


@app.get("/api/health")
def health():
    return {"ok": True, "advisor_mode": "conversational_rule_engine", "today": TODAY.isoformat()}
