import sys, os, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from registry import validate_gstin_format, gstin_checksum, lookup_gstin, mask
from catalogue import BusinessProfile, recommend, catalogue, eligible, price
from kyc import validate_application, process_document
import advisor
from fastapi.testclient import TestClient
from app import app, CONSENTS, KYC, ORDERS

client = TestClient(app)

def test_gstin_checksum_matches_registry():
    import csv
    rows = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), "..", "data", "mock_gstin_registry.csv"))))
    assert all(validate_gstin_format(r["gstin"])["valid"] for r in rows)

def test_tampered_gstin_fails():
    assert not validate_gstin_format("08YKZXS8189L1Z0")["valid"]

def test_cancelled_lookup():
    assert lookup_gstin("37IHKXV5167L1ZS")["record"]["status"] == "Cancelled"

def test_mask():
    assert mask("37IHKXV5167L1ZS") == "37**********1ZS"

def _all_eligible(b, p):
    cat = catalogue(); ids = {l["product_id"] for l in b["lines"]}
    for l in b["lines"]:
        assert eligible(l["product_id"], p)[0]
        deps = cat[l["product_id"]]["deps"]
        assert not deps or ids & set(deps)

def test_bundles_respect_rules():
    for seg in ("micro", "prof", "multi", "mfg"):
        for gst in (True, False):
            for tier in (1, 2):
                p = BusinessProfile(segment=seg, employees=30 if seg != "micro" else 3, sites=4 if seg == "multi" else 1,
                                    city_tier=tier, has_gstin=gst, gstin_active=gst, needs=["whatsapp", "cctv", "uptime", "phone_lines"])
                _all_eligible(recommend(p), p)

def test_micro_affordability_cap():
    b = recommend(BusinessProfile(segment="micro", employees=3, current_spend=900, needs=["payments", "whatsapp", "cctv", "guest_wifi", "website"], has_gstin=True, gstin_active=True))
    assert b["quote"]["monthly_total"] <= b["affordability_cap"]

def test_micro_low_spend_right_sizing():
    b = recommend(BusinessProfile(segment="micro", business_type="Kirana / general store", employees=1, current_spend=400, needs=["payments"], city_tier=1))
    # Must right-size: 1 mobile line, optional POS billing, base total under Rs 1,500
    assert b["quote"]["monthly_total"] <= 1500
    items = {i["product_id"]: i for i in b["quote"]["items"]}
    assert items["P07"]["qty"] == 1
    assert items["P19"]["optional"] is True
    assert items["P19"]["on"] is False

def test_old_address_proof_fails():
    r = validate_application({"address_proof": {"billed_to": "X", "bill_date": "2025-10-31", "address": "a - 111111"}})
    assert any(c["code"] == "ADDRESS_PROOF_OLD" for c in r["checks"])

def test_advisor_multi_slot_extraction():
    s = advisor.new_session("en")
    sid = s["session_id"]
    # Provide multiple facts in free text
    res = advisor.handle(sid, text="I run a dental clinic with 5 staff in Pune, we need cctv and wifi")
    prof = res["profile"]
    assert prof["segment"] == "prof"
    assert prof["employees"] == 5
    assert prof["city_tier"] == 1
    assert "cctv" in prof["needs"]
    assert "guest_wifi" in prof["needs"]

def test_all_12_kyc_specimens():
    D = os.path.join(os.path.dirname(__file__), "..", "data", "kyc_documents")
    expected = json.load(open(os.path.join(os.path.dirname(__file__), "..", "analysis", "kyc_batch_results.json")))
    for k in sorted({os.path.basename(p)[:3] for p in glob.glob(D + "/K*.png")}):
        docs = {}
        for p in sorted(glob.glob(f"{D}/{k}_*.png")):
            r = process_document(open(p, "rb").read(), filename=os.path.basename(p))
            docs[r["doc_type"] or os.path.basename(p)] = r["fields"]
        res = validate_application(docs)
        assert res["status"] == expected[k]["status"]
        assert [c["code"] for c in res["checks"]] == [c["code"] for c in expected[k]["checks"]]

def test_end_to_end_journey_api():
    # 1. Start advisor
    r_start = client.post("/api/advisor/start", json={"lang": "en"}).json()
    sid = r_start["session_id"]
    assert sid

    # 2. Conversational advisor answers
    r1 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "clinic"}).json()
    r2 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "6-15"}).json()
    r3 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "1"}).json()
    r4 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "Delhi"}).json()
    r5 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "nogst"}).json()
    r6 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "done"}).json()
    r7 = client.post("/api/advisor/message", json={"session_id": sid, "choice": "₹1,000–3,000"}).json()
    assert r7["step"] == "done"
    assert "recommendation" in r7

    # 3. Quote
    r_quote = client.post("/api/quote", json={"session_id": sid, "contract_months": 24}).json()
    assert r_quote["monthly_total"] > 0
    assert r_quote["contract_months"] == 24

    # 4. Consent
    r_con = client.post("/api/kyc/consent", json={"session_id": sid, "purposes": ["kyc_verification", "service_activation"]}).json()
    assert "consent_id" in r_con

    # 5. KYC sample (K02 verified)
    r_kyc = client.post("/api/kyc/sample", json={"session_id": sid, "applicant": "K02"}).json()
    assert "gst_certificate" in r_kyc
    r_val = client.post("/api/kyc/validate", json={"session_id": sid}).json()
    assert r_val["status"] == "verified"

    # 6. Order placement
    r_ord = client.post("/api/order", json={"session_id": sid, "install_slot": "2026-07-18 10:00-13:00"}).json()
    oid = r_ord["order_id"]
    assert oid.startswith("UD")

    # 7. Order advancement
    r_adv = client.post(f"/api/order/{oid}/advance").json()
    assert r_adv["progress"] >= 1

    # 8. Consent withdrawal / erasure
    r_del = client.delete(f"/api/kyc/consent/{sid}").json()
    assert r_del["ok"] is True
    assert sid not in CONSENTS
    assert sid not in KYC

def test_backoffice_leads_api():
    r = client.get("/api/backoffice/leads").json()
    assert "leads" in r
    assert len(r["leads"]) > 0
    assert "stats" in r
    assert r["stats"]["cv_auc"] >= 0.70
