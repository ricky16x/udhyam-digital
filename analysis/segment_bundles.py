"""What activated customers bought per segment; churn by micro bundle value (basis for the affordability cap)."""
import sys, pandas as pd
from collections import Counter
L = pd.read_csv((sys.argv[1] if len(sys.argv) > 1 else "data") + "/smb_leads.csv")
A = L[L.outcome == "Activated"].copy(); A["churn"] = A.churned_within_6_months.eq("Y")
for seg, g in A.groupby("segment"):
    c = Counter(p.split("x")[0] for b in g.bundle_products for p in b.split(";"))
    print(seg, len(g), [(k, round(v / len(g), 2)) for k, v in c.most_common(8)], "median Rs", g.monthly_bundle_value_inr.median())
m = A[A.segment.str.startswith("Micro")]
print(m.groupby(pd.qcut(m.monthly_bundle_value_inr, 4), observed=True).churn.agg(["size", "mean"]))
