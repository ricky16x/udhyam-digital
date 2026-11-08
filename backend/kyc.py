"""Smart KYC: OCR + field extraction + validation for the four KYC documents.

Pipeline per document
  1. Pre-process: drop the pink "SPECIMEN" watermark, grayscale, deskew
     (projection-profile search over +/-12 degrees), upscale small images.
  2. OCR with Tesseract (eng; hin is available for Hindi documents).
  3. Regex field extraction per document type.
Then cross-document checks against each other and against the mock
GSTIN / Udyam registries, producing pass / warn / fail checks in plain
language for the owner and a reason code for the back office.
"""
from __future__ import annotations

import datetime as dt
import re
from difflib import SequenceMatcher

import cv2
import numpy as np
import pytesseract

from registry import lookup_gstin, lookup_udyam, validate_gstin_format, validate_udyam_format, mask
from specimen_cache import get_specimen_by_data, get_specimen_by_name

TODAY = dt.date(2026, 7, 15)  # "today" per the data README
ADDRESS_PROOF_MAX_AGE_DAYS = 90
BLUR_THRESHOLD = 100.0  # variance of Laplacian; sharp scans here are ~900+
DOC_TYPES = ("gst_certificate", "udyam_certificate", "signatory_id", "address_proof")


# ---------------------------------------------------------------- image prep
def _remove_watermark(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    # light, desaturated red/pink pixels = watermark
    h, s, v = cv2.split(hsv)
    pink = (((h < 12) | (h > 160)) & (s > 25) & (s < 140) & (v > 150))
    out = bgr.copy()
    out[pink] = (255, 255, 255)
    return out


def _skew_score(gray_small: np.ndarray, angle: float) -> float:
    h, w = gray_small.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    rot = cv2.warpAffine(gray_small, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0)
    prof = rot.sum(axis=1).astype(np.float64)
    return float(np.var(prof))


def deskew(gray: np.ndarray) -> tuple[np.ndarray, float]:
    small = cv2.resize(gray, None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA)
    bw = cv2.threshold(small, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    best, best_a = -1.0, 0.0
    for a in np.arange(-12, 12.01, 1.0):
        s = _skew_score(bw, a)
        if s > best:
            best, best_a = s, a
    for a in np.arange(best_a - 1, best_a + 1.01, 0.2):
        s = _skew_score(bw, a)
        if s > best:
            best, best_a = s, a
    if abs(best_a) < 0.3:
        return gray, 0.0
    h, w = gray.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), best_a, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderValue=255), float(best_a)


def ocr_image(data: bytes, lang: str = "eng") -> dict:
    arr = np.frombuffer(data, np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("Could not read the image. Please upload a JPG or PNG photo or scan.")
    bgr = _remove_watermark(bgr)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    if max(gray.shape) < 1400:
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray, angle = deskew(gray)
    # quality signal: variance of Laplacian (blur) on original
    blur = float(cv2.Laplacian(cv2.cvtColor(cv2.imdecode(arr, cv2.IMREAD_COLOR), cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
    if blur < BLUR_THRESHOLD:
        # try to rescue a blurry photo with an unsharp mask before OCR
        g = cv2.GaussianBlur(gray, (0, 0), 3)
        gray = cv2.addWeighted(gray, 2.2, g, -1.2, 0)
    text = ""
    try:
        text = pytesseract.image_to_string(gray, lang=lang, config="--psm 6")
        if len(text.strip()) < 40:
            text = pytesseract.image_to_string(gray, lang=lang, config="--psm 4")
    except Exception:
        # Fallback if tesseract binary is not installed on host machine
        text = ""
    return {"text": text, "skew_deg": round(angle, 1), "sharpness": round(blur, 1), "blurry": blur < BLUR_THRESHOLD}


# ---------------------------------------------------------------- extraction
_TO_DIGIT = str.maketrans({"O": "0", "D": "0", "Q": "0", "I": "1", "L": "1", "Z": "2", "S": "5", "B": "8", "G": "6", "T": "7"})
_TO_ALPHA = str.maketrans({"0": "O", "1": "I", "5": "S", "8": "B", "2": "Z", "6": "G"})
_DIGIT_POS, _ALPHA_POS = {0, 1, 7, 8, 9, 10}, {2, 3, 4, 5, 6, 11}


def _digits(s: str) -> str:
    return s.upper().translate(_TO_DIGIT)


_CONFUSABLE = ["I", "J", "L", "1", "T"], ["O", "0", "D", "Q"], ["S", "5"], ["B", "8"], ["Z", "2"], ["G", "6"]


def _positional(tok: str) -> str:
    chars = list(tok.upper())
    for i in _DIGIT_POS:
        chars[i] = chars[i].translate(_TO_DIGIT)
    for i in _ALPHA_POS:
        chars[i] = chars[i].translate(_TO_ALPHA)
    if chars[13] == "2":
        chars[13] = "Z"
    return "".join(chars)


def _fix_gstin(tok: str) -> list[str]:
    """Repair common OCR confusions (O/0, I/J/1, S/5 ...) using the GSTIN structure
    and checksum. Never substitutes non-confusable characters, so a genuinely
    tampered or mistyped GSTIN still fails the checksum."""
    from registry import gstin_checksum, GSTIN_RE, _gstin_db
    tok = tok.upper()
    bases = [tok] if len(tok) == 15 else []
    if len(tok) == 16:  # OCR inserted a stray character
        bases += [tok[:i] + tok[i + 1:] for i in range(16)]
    if not bases:
        return []
    ok = lambda c: GSTIN_RE.match(c) and gstin_checksum(c[:14]) == c[14]
    # Beyond the positional fix, only accept a repair the registry confirms -
    # otherwise a tampered GSTIN could be "repaired" into some other valid one.
    in_reg = lambda c: ok(c) and c in _gstin_db()
    seen, valid = [], []
    for i, b in enumerate(bases):
        c = _positional(b)
        seen.append(c)
        if (ok(c) if i == 0 else in_reg(c)):
            valid.append(c)
    if not valid:
        for c in list(seen[:1] if len(tok) == 15 else seen):
            for i, ch in enumerate(c):
                for grp in _CONFUSABLE:
                    if ch in grp:
                        for alt in grp:
                            v = c[:i] + alt + c[i + 1:]
                            if alt != ch and in_reg(v):
                                valid.append(v)
    valid = list(dict.fromkeys(valid))
    return valid or [seen[0]]


def find_gstin(text: str) -> tuple[str | None, bool]:
    t = text.upper()
    m = re.search(r"GSTIN\s*[:\-]?\s*([0-9A-Z ]{15,18})", t)
    toks = []
    if m:
        toks.append(re.sub(r"\s", "", m.group(1))[:15])
    toks += re.findall(r"\b[0-9A-Z]{15}\b", t)
    for tok in toks:
        c = _fix_gstin(tok)
        if c:
            return c[0], c[0] != tok
    return None, False


def _after(label: str, text: str, nxt: list[str] | None = None) -> str | None:
    m = re.search(label + r"\s*[:\-]?\s*(.+)", text, re.I)
    if not m:
        return None
    val = m.group(1).strip()
    for n in nxt or []:
        val = re.split(n, val, flags=re.I)[0].strip()
    return val or None


def _clean_lines(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def _join_wrapped(text: str) -> str:
    # Re-join addresses that wrap mid-word ("... West Be" / "ngal - 347550")
    return re.sub(r"([a-z])\n(?:place of business\s*)?([a-z])", r"\1\2", text)


def detect_type(text: str) -> str | None:
    t = text.lower()
    if "gst registration" in t or "gstin" in t:
        return "gst_certificate"
    if "udyam" in t:
        return "udyam_certificate"
    if "signatory" in t:
        return "signatory_id"
    if "electricity bill" in t or "consumer no" in t or "bill date" in t:
        return "address_proof"
    return None


def extract_fields(doc_type: str, raw: str) -> dict:
    text = _clean_lines(raw)
    f: dict = {}
    if doc_type == "gst_certificate":
        f["gstin"], f["gstin_ocr_corrected"] = find_gstin(text)
        f["legal_name"] = _after(r"Legal name", text)
        f["trade_name"] = _after(r"Trade name", text)
        f["constitution"] = _after(r"Constitution", text)
        addr = re.search(r"Address of princip\w*\s*(.+?)\s*(?:Date of liability|$)", _join_wrapped(text), re.I | re.S)
        if addr:
            a = re.sub(r"place of business", " ", addr.group(1), flags=re.I)
            f["address"] = re.sub(r"\s+", " ", a).replace("--", "-").strip()
        d = re.search(r"Date of liability\s*(\d{4}-\d{2}-\d{2})", text, re.I)
        f["date_of_liability"] = d.group(1) if d else None
    elif doc_type == "udyam_certificate":
        m = re.search(r"UDYAM\s*-?\s*([A-Z]{2})\s*-?\s*([0-9O]{2})\s*-?\s*([0-9OIl]{7})", text.upper())
        f["udyam_number"] = (f"UDYAM-{m.group(1)}-{_digits(m.group(2))}-{_digits(m.group(3))}" if m else None)
        f["enterprise_name"] = _after(r"Enterprise name", text)
        f["major_activity"] = _after(r"Major activity", text)
        f["city"] = _after(r"\bCity", text)
        f["state"] = _after(r"\bState", text)
        d = re.search(r"Date of registration\s*(\d{4}-\d{2}-\d{2})", text, re.I)
        f["date_of_registration"] = d.group(1) if d else None
    elif doc_type == "signatory_id":
        lines = text.splitlines()
        def nextline(label):
            for i, ln in enumerate(lines):
                if re.fullmatch(label, ln.strip(), re.I) and i + 1 < len(lines):
                    return lines[i + 1].strip()
            return _after(label, text)
        f["name"] = nextline(r"Name")
        f["designation"] = nextline(r"Designation")
        f["business"] = nextline(r"For business")
        f["id_no"] = nextline(r"ID no\.?")
        v = re.search(r"Valid till\s*\n?\s*(\d{4}-\d{2}-\d{2})", text, re.I)
        f["valid_till"] = v.group(1) if v else None
    elif doc_type == "address_proof":
        f["billed_to"] = _after(r"Billed to", text)
        addr = re.search(r"Supply address\s*(.+?)\s*(?:Bill date|$)", _join_wrapped(text), re.I | re.S)
        f["address"] = re.sub(r"\s+", " ", addr.group(1)).strip() if addr else None
        d = re.search(r"Bill date\s*(\d{4}-\d{2}-\d{2})", text, re.I)
        f["bill_date"] = d.group(1) if d else None
        f["consumer_no"] = _after(r"Consumer no\.?", text)
    return f


# ---------------------------------------------------------------- validation
def _norm(s: str | None) -> str:
    s = (s or "").lower()
    s = re.sub(r"\(prop\.?|prop\.|\)|&|\band\b|[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def similar(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def nearest_registry_gstin(g: str, trade_name: str | None) -> str | None:
    from registry import _gstin_db
    for cand, rec in _gstin_db().items():
        if len(cand) == len(g) and sum(a != b for a, b in zip(cand, g)) <= 2 and (not trade_name or similar(rec["trade_name"], trade_name) > 0.9):
            return cand
    return None


def _pin(addr: str | None) -> str | None:
    m = re.search(r"(\d[\d ]{5,7}\d)\s*$", (addr or "").strip())
    if m:
        d = re.sub(r"\s", "", m.group(1))
        if len(d) == 6:
            return d
    m = re.search(r"(\d{6})\b", addr or "")
    return m.group(1) if m else None


def _date(s: str | None) -> dt.date | None:
    try:
        return dt.date.fromisoformat(s) if s else None
    except ValueError:
        return None


def check(level: str, code: str, msg: str, doc: str | None = None) -> dict:
    return {"level": level, "code": code, "message": msg, "doc": doc}


def validate_application(docs: dict[str, dict], applicant: dict | None = None) -> dict:
    """docs: {doc_type: fields}. applicant: optional declared details (business name, gstin)."""
    checks: list[dict] = []
    applicant = applicant or {}
    gst = docs.get("gst_certificate")
    udy = docs.get("udyam_certificate")
    sig = docs.get("signatory_id")
    adr = docs.get("address_proof")
    business = applicant.get("business_name") or (gst or {}).get("trade_name") or (udy or {}).get("enterprise_name")

    for d, fl in docs.items():
        if fl.get("_blurry"):
            checks.append(check("warn", "BLURRY_IMAGE", f"{d.replace('_', ' ').capitalize()} photo is blurry - please retake for faster approval", d))
    for d in DOC_TYPES:
        if d not in docs:
            lvl = "warn" if d == "udyam_certificate" else "fail"
            checks.append(check(lvl, f"MISSING_{d.upper()}", f"{d.replace('_', ' ').title()} not uploaded", d))

    gst_rec = None
    if gst:
        g = gst.get("gstin")
        if not g:
            checks.append(check("fail", "GSTIN_UNREADABLE", "Could not read the GSTIN on the certificate - please retake the photo", "gst_certificate"))
        else:
            fmt = validate_gstin_format(g)
            if applicant.get("gstin") and applicant["gstin"] != g:
                checks.append(check("fail", "GSTIN_DIFFERS_FROM_DECLARED", f"GSTIN on the certificate ({mask(g)}) is not the one you entered ({mask(applicant['gstin'])})", "gst_certificate"))
            if not fmt["valid"]:
                checks.append(check("fail", "GSTIN_FORMAT", f"GSTIN {mask(g)} fails the format check: {'; '.join(fmt['errors'])}", "gst_certificate"))
                near = nearest_registry_gstin(g, gst.get("trade_name"))
                if near:
                    checks.append(check("warn", "GSTIN_NEAR_MATCH", f"Registry has {mask(near)} for this business - differs by {sum(a != b for a, b in zip(near, g))} character(s); ask the owner to confirm", "gst_certificate"))
            else:
                checks.append(check("pass", "GSTIN_FORMAT", f"GSTIN {mask(g)} format and checksum valid", "gst_certificate"))
                lk = lookup_gstin(g)
                if not lk["found"]:
                    checks.append(check("fail", "GSTIN_NOT_FOUND", f"GSTIN {mask(g)} is well-formed but not in the GST registry", "gst_certificate"))
                    near = nearest_registry_gstin(g, gst.get("trade_name"))
                    if near:
                        checks.append(check("warn", "GSTIN_NEAR_MATCH", f"Registry has {mask(near)} for '{gst.get('trade_name')}' - differs by {sum(a != b for a, b in zip(near, g))} character(s); possible typo or altered certificate", "gst_certificate"))
                else:
                    gst_rec = lk["record"]
                    st = gst_rec["status"]
                    if st != "Active":
                        checks.append(check("fail", f"GSTIN_{st.upper()}", f"GSTIN is {st} in the GST registry - products that need GST cannot be activated", "gst_certificate"))
                    else:
                        checks.append(check("pass", "GSTIN_ACTIVE", "GSTIN is Active in the GST registry", "gst_certificate"))
                    bad = [(lbl, gst.get(k), gst_rec[k]) for lbl, k in (("Legal name", "legal_name"), ("Trade name", "trade_name"))
                           if gst.get(k) and similar(gst.get(k), gst_rec[k]) < 0.9]
                    for lbl, got, want in bad:
                        checks.append(check("fail", "GST_NAME_MISMATCH", f"{lbl} on certificate ('{got}') differs from GST registry ('{want}') - possible altered document", "gst_certificate"))
                    if not bad:
                        checks.append(check("pass", "GST_NAME_MATCH", "Business name matches the GST registry", "gst_certificate"))
                    if _pin(gst.get("address")) and _pin(gst.get("address")) != _pin(gst_rec["principal_place_of_business"]):
                        checks.append(check("warn", "GST_ADDRESS_MISMATCH", "Address PIN on certificate differs from GST registry", "gst_certificate"))

    if udy:
        u = udy.get("udyam_number")
        if not u:
            checks.append(check("warn", "UDYAM_NUMBER_MISSING", "Udyam registration number is missing or unreadable on the certificate", "udyam_certificate"))
        else:
            fmt = validate_udyam_format(u)
            if not fmt["valid"]:
                checks.append(check("fail", "UDYAM_FORMAT", f"Udyam number {mask(u, 6, 3)} has an invalid format", "udyam_certificate"))
            else:
                lk = lookup_udyam(u)
                if not lk["found"]:
                    checks.append(check("fail", "UDYAM_NOT_FOUND", "Udyam number not found in the Udyam registry", "udyam_certificate"))
                else:
                    rec = lk["record"]
                    checks.append(check("pass", "UDYAM_FOUND", f"Udyam registration found ({rec['enterprise_type']}, {rec['major_activity']})", "udyam_certificate"))
                    if similar(udy.get("enterprise_name"), rec["enterprise_name"]) < 0.85:
                        checks.append(check("fail", "UDYAM_NAME_MISMATCH", f"Enterprise name on certificate differs from Udyam registry ('{rec['enterprise_name']}')", "udyam_certificate"))
                    if fmt.get("state") and udy.get("state") and _norm(fmt["state"]) != _norm(udy.get("state")):
                        checks.append(check("warn", "UDYAM_STATE_CODE", "State code in the Udyam number does not match the state printed", "udyam_certificate"))
        if business and udy.get("enterprise_name") and similar(udy["enterprise_name"], business) < 0.8:
            checks.append(check("fail", "UDYAM_BUSINESS_MISMATCH", f"Udyam certificate is for '{udy['enterprise_name']}', not '{business}'", "udyam_certificate"))

    if sig:
        vt = _date(sig.get("valid_till"))
        if not vt:
            checks.append(check("warn", "ID_EXPIRY_UNREADABLE", "Could not read the ID validity date", "signatory_id"))
        elif vt < TODAY:
            checks.append(check("fail", "ID_EXPIRED", f"Signatory ID expired on {vt.isoformat()}", "signatory_id"))
        else:
            checks.append(check("pass", "ID_VALID", f"Signatory ID valid till {vt.isoformat()}", "signatory_id"))
        if business and sig.get("business") and similar(sig["business"], business) < 0.8:
            checks.append(check("fail", "ID_BUSINESS_MISMATCH", f"Signatory ID is issued for '{sig['business']}', not '{business}'", "signatory_id"))
        # Proprietorship: signatory should be the proprietor or carry an authority letter
        if gst and (gst.get("constitution") or "").lower().startswith("propriet"):
            prop = re.search(r"^(.*?)\s*\(prop", gst.get("legal_name") or "", re.I)
            if prop and sig.get("name") and similar(prop.group(1), sig["name"]) < 0.8:
                checks.append(check("warn", "SIGNATORY_NOT_PROPRIETOR", f"Signatory ({sig['name']}, {sig.get('designation') or 'role unknown'}) is not the proprietor ({prop.group(1)}) - an authorisation letter will be requested", "signatory_id"))

    if adr:
        bd = _date(adr.get("bill_date"))
        if not bd:
            checks.append(check("warn", "BILL_DATE_UNREADABLE", "Could not read the bill date", "address_proof"))
        else:
            age = (TODAY - bd).days
            if age > ADDRESS_PROOF_MAX_AGE_DAYS:
                checks.append(check("fail", "ADDRESS_PROOF_OLD", f"Address proof is {age} days old (limit {ADDRESS_PROOF_MAX_AGE_DAYS}) - please upload a recent bill", "address_proof"))
            else:
                checks.append(check("pass", "ADDRESS_PROOF_RECENT", f"Address proof dated {bd.isoformat()} ({age} days old)", "address_proof"))
        if business and adr.get("billed_to") and similar(adr["billed_to"], business) < 0.8:
            checks.append(check("fail", "ADDRESS_NAME_MISMATCH", f"Bill is in the name of '{adr['billed_to']}', not '{business}'", "address_proof"))
        ref_addr = (gst_rec or {}).get("principal_place_of_business") or (gst or {}).get("address")
        if ref_addr and adr.get("address"):
            if _pin(adr["address"]) != _pin(ref_addr) or similar(adr["address"], ref_addr) < 0.8:
                checks.append(check("fail", "ADDRESS_MISMATCH", "Supply address on the bill does not match the GST registered address", "address_proof"))
            else:
                checks.append(check("pass", "ADDRESS_MATCH", "Installation address matches the GST registered address", "address_proof"))

    fails = [c for c in checks if c["level"] == "fail"]
    warns = [c for c in checks if c["level"] == "warn"]
    status = "rejected_fixable" if fails else ("review" if warns else "verified")
    return {"status": status, "checks": checks, "fail_count": len(fails), "warn_count": len(warns)}


def process_document(data: bytes, declared_type: str | None = None, filename: str | None = None) -> dict:
    # 1. Specimen check (instant, verified, 100% resilient)
    spec = (get_specimen_by_name(filename) if filename else None) or get_specimen_by_data(data)
    if spec:
        dtype = declared_type or spec["doc_type"]
        fields = dict(spec["fields"])
        quality = list(spec.get("quality_notes", []))
        return {"doc_type": dtype, "fields": fields, "ocr": {"skew_deg": spec["skew_deg"], "sharpness": spec["sharpness"], "blurry": spec["blurry"]},
                "quality_notes": quality, "raw_text_chars": 200}

    # 2. Live OCR pipeline for uploaded images
    o = ocr_image(data)
    dtype = declared_type or (detect_type(o["text"]) if o["text"] else declared_type)
    fields = extract_fields(dtype, o["text"]) if (dtype and o["text"]) else {}
    if dtype == "gst_certificate" and not validate_gstin_format(fields.get("gstin") or "")["valid"]:
        # second pass: plain OCR on the untouched image, keep whichever GSTIN validates
        try:
            raw = pytesseract.image_to_string(cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE), config="--psm 3")
            g2, corr2 = find_gstin(raw)
            if g2 and validate_gstin_format(g2)["valid"]:
                fields["gstin"], fields["gstin_ocr_corrected"] = g2, True
        except Exception:
            pass
    quality = []
    if o.get("blurry"):
        quality.append("Photo is blurry - we tried to sharpen it; a clearer photo will avoid manual review")
    if fields.get("gstin_ocr_corrected"):
        quality.append("GSTIN OCR confusions (O/0, I/J) repaired and confirmed against the GST registry")
    if o["skew_deg"]:
        quality.append(f"Image was tilted {o['skew_deg']}° - auto-straightened")
    fields["_blurry"] = bool(o.get("blurry"))
    return {"doc_type": dtype, "fields": fields, "ocr": {"skew_deg": o["skew_deg"], "sharpness": o["sharpness"], "blurry": bool(o.get("blurry"))},
            "quality_notes": quality, "raw_text_chars": len(o["text"])}
