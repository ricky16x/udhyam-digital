"""Run Smart KYC over all specimen applicants and print a report."""
import sys, json, glob, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from kyc import process_document, validate_application
D = os.path.join(os.path.dirname(__file__), "..", "data", "kyc_documents")
out = {}
for k in sorted({os.path.basename(p)[:3] for p in glob.glob(D + "/K*.png")}):
    docs = {}
    for p in sorted(glob.glob(f"{D}/{k}_*.png")):
        t = time.time()
        r = process_document(open(p, "rb").read(), filename=os.path.basename(p))
        docs[r["doc_type"] or os.path.basename(p)] = r["fields"]
        if "-v" in sys.argv: print(k, os.path.basename(p), r["doc_type"], r["ocr"], json.dumps(r["fields"]), f"{time.time()-t:.1f}s")
    res = validate_application(docs)
    out[k] = res
    print(f"\n{k}: {res['status'].upper()}")
    for c in res["checks"]:
        if c["level"] != "pass" or "-v" in sys.argv: print(f"   [{c['level']}] {c['code']}: {c['message']}")
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "analysis", "kyc_batch_results.json"), "w"), indent=1)
