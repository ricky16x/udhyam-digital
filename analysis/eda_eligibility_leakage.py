import pandas as pd, numpy as np, sys
D=sys.argv[1]; L=pd.read_csv(D+'/smb_leads.csv'); C=pd.read_csv(D+'/product_catalogue.csv').set_index('product_id')
G=pd.read_csv(D+'/mock_gstin_registry.csv').set_index('gstin')
A=L[L.outcome=='Activated'].copy(); A['churn']=(A.churned_within_6_months=='Y').astype(int)
def viol(r):
    b={p.split('x')[0]:int(p.split('x')[1]) for p in r.bundle_products.split(';')}
    v=[]
    gst_ok = r.has_gstin=='Y' and G.loc[r.gstin,'status']=='Active'
    for p in b:
        c=C.loc[p]
        if str(r.city_tier) not in str(c.available_city_tiers).split(';'): v.append(p+':tier')
        if r.employee_count<c.min_employees: v.append(p+':emp')
        if r.num_sites<c.min_sites: v.append(p+':sites')
        if c.requires_gstin=='Y' and not gst_ok: v.append(p+':gst')
        if isinstance(c.requires_one_of,str) and not set(c.requires_one_of.split('|'))&set(b): v.append(p+':dep')
    return v
A['viol']=A.apply(viol,axis=1); A['nv']=A.viol.str.len()
print((A.nv>0).sum(), A.nv.sum()); 
from collections import Counter; print(Counter([x.split(':')[1] for v in A.viol for x in v]))
print(A.groupby(A.nv>0).agg(n=('lead_id','size'),churn=('churn','mean'),nps=('nps_score','mean')))
print(A[A.nv>0][['lead_id','segment','has_gstin','bundle_products','viol']].head(20).to_string())
# price check: implied monthly value vs catalog range
def rng(r):
    lo=hi=0
    for p in r.bundle_products.split(';'):
        pid,q=p.split('x'); lo+=C.loc[pid,'price_min_inr_per_month']*int(q); hi+=C.loc[pid,'price_max_inr_per_month']*int(q)
    return pd.Series({'lo':lo,'hi':hi})
A=A.join(A.apply(rng,axis=1)); A['pos']=(A.monthly_bundle_value_inr-A.lo)/(A.hi-A.lo)
print(A.pos.describe()); print(((A.monthly_bundle_value_inr<A.lo)|(A.monthly_bundle_value_inr>A.hi)).sum())
A['pb']=pd.cut(A.pos,[-9,0.25,0.5,0.75,9]); print(A.groupby('pb',observed=True).agg(n=('lead_id','size'),churn=('churn','mean'),nps=('nps_score','mean')))
# setup fee
# common bundles per segment
for s,g in A.groupby('segment'):
    cnt=Counter([p.split('x')[0] for b in g.bundle_products for p in b.split(';')]); print(s,len(g),[(k,round(v/len(g),2)) for k,v in cnt.most_common(8)])
    print('  qty med', {k: g.bundle_products.str.extract(k+r'x(\d+)')[0].dropna().astype(int).median() for k,_ in cnt.most_common(6)})
    print('  contract',g.contract_months.value_counts().to_dict(),'setup med',g.one_time_setup_inr.median())
# micro: bundles with P01 vs P04
