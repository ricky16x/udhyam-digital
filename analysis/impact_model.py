"""Funnel impact model: which drop-offs the digital journey removes, and the
resulting activations, time to activate and acquisition cost.
Recovery rates are explicit, conservative assumptions - edit and rerun."""
import json, sys
import pandas as pd, numpy as np
D = sys.argv[1] if len(sys.argv) > 1 else "data"
L = pd.read_csv(f"{D}/smb_leads.csv"); C = pd.read_csv(f"{D}/product_catalogue.csv").set_index("product_id")
stages = ["Lead", "Contacted", "Needs assessed", "Quote accepted", "KYC complete", "Activated"]
idx = {s: i for i, s in enumerate(stages)}
L["si"] = L.stage_reached.map(idx)
reached = [(L.si >= i).sum() for i in range(6)]
conv = [reached[i + 1] / reached[i] for i in range(5)]  # stage i -> i+1
def p_activate_from(i):  # lead that has just reached stage i
    return float(np.prod(conv[i:])) if i < 5 else 1.0
RECOVERY = {  # share of these drop-offs the digital journey keeps in the funnel
 "Owner had no time for a visit": (0.50, "Advisor on phone, 24x7 - no visit needed"),
 "Visit not scheduled by sales": (0.60, "Advisor on phone, 24x7 - no visit needed"),
 "Quote too complex to understand": (0.50, "One plain-language monthly price"),
 "Quote took too long to arrive": (0.70, "Instant quote"),
 "Missing GST or Udyam document": (0.30, "DigiLocker / registry fetch, GST-free bundle"),
 "Found paperwork too long": (0.60, "Smart KYC in ~5 minutes"),
 "Document details did not match": (0.50, "Mismatch flagged at upload, fix on the spot"),
 "Authorised signatory not available": (0.60, "Remote Aadhaar e-sign by signatory"),
 "Installation delayed beyond 21 days": (0.40, "Slot booking + 5G AirFiber bridge"),
 "Site not feasible for fibre": (0.60, "5G AirFiber fallback"),
 "First payment failed": (0.60, "UPI Autopay with retry"),
 "Customer cancelled before install": (0.20, "Live tracker, no status chasing"),
 "Unreachable after 3 attempts": (0.15, "WhatsApp-first async follow-up"),
 "Price too high": (0.15, "Right-sized bundles, affordability cap"),
 "Competitor offered cheaper plan": (0.10, "Transparent bundle savings"),
 "Decided to wait": (0.10, "Saved quote + reminder"),
}
rows, extra = [], 0.0
for (reason, st), g in L[L.outcome == "Dropped"].groupby(["drop_reason", "stage_reached"]):
    r, lever = RECOVERY.get(reason, (0.0, "Not addressed"))
    nxt = idx[st] + 1
    gain = len(g) * r * p_activate_from(nxt)
    extra += gain
    rows.append({"reason": reason, "stage": st, "leads": len(g), "recovery": r, "lever": lever, "added_activations": round(gain, 1)})
T = pd.DataFrame(rows).sort_values("added_activations", ascending=False)
base = int((L.outcome == "Activated").sum())
# time to activate under digital journey: same-day discovery/quote/KYC + install days of the bundle bought
A = L[L.outcome == "Activated"].copy()
A["inst"] = A.bundle_products.apply(lambda b: max(C.loc[p.split("x")[0], "typical_install_days"] for p in b.split(";")))
seg_inst = A.groupby("segment").inst.median().to_dict()
gaps = A[["created_date", "contacted_date", "needs_assessed_date", "quote_accepted_date", "kyc_complete_date", "activated_date"]].apply(pd.to_datetime).diff(axis=1).mean().dt.total_seconds().div(86400).round(1).to_dict()
src = L.groupby("lead_source").agg(leads=("lead_id", "size"), cost=("acquisition_cost_inr", "sum"), act=("outcome", lambda s: (s == "Activated").sum()))
src["cost_per_lead"] = (src.cost / src.leads).round(0); src["cac"] = (src.cost / src.act).round(0); src["act_rate"] = (src.act / src.leads).round(3)
out = {"baseline_activations": base, "added_activations": round(extra), "new_activations": round(base + extra),
       "baseline_rate": round(base / len(L), 4), "new_rate": round((base + extra) / len(L), 4),
       "uplift_pct": round(extra / base * 100), "stage_conversion": [round(c, 3) for c in conv],
       "median_install_days_by_segment": seg_inst, "median_install_days_all": float(A.inst.median()),
       "mean_stage_gaps_days": gaps, "by_source": src.reset_index().to_dict("records"),
       "levers": T.groupby("lever").added_activations.sum().sort_values(ascending=False).round(1).to_dict()}
print(T.to_string(index=False)); print(json.dumps(out, indent=1, default=str))
json.dump(out, open("analysis/impact_results.json", "w"), indent=1, default=str)
