import pandas as pd, numpy as np, sys
pd.set_option('display.width',250); pd.set_option('display.max_columns',50)
D=sys.argv[1]
L=pd.read_csv(D+'/smb_leads.csv')
L['act']=(L.outcome=='Activated').astype(int)
stages=['Lead','Contacted','Needs assessed','Quote accepted','KYC complete','Activated']
L['stage_idx']=L.stage_reached.map({s:i for i,s in enumerate(stages)})
print(L.stage_reached.value_counts())
def grp(col):
    g=L.groupby(col).agg(n=('lead_id','size'),act=('act','mean'),cac=('acquisition_cost_inr','sum'))
    g['act_n']=L.groupby(col).act.sum(); g['cac_per_act']=g.cac/g.act_n.replace(0,np.nan); g['act']=(g.act*100).round(1)
    return g.sort_values('n',ascending=False)
for c in ['segment','lead_source','city_tier','preferred_language','has_gstin','has_udyam','current_internet','current_provider','contact_role','annual_turnover_band']:
    print('\n##',c); print(grp(c))
print('\n## drop reasons'); dr=L[L.outcome=='Dropped'].groupby(['stage_reached','drop_reason']).size().sort_values(ascending=False); print(dr.to_string())
print('\n## drop reasons total'); print(L.drop_reason.value_counts())
A=L[L.act==1].copy()
print('\nactivated',len(A), 'avg days',A.days_lead_to_activation.mean(), 'avg calls', A.customer_follow_up_calls.mean(), 'median bundle',A.monthly_bundle_value_inr.median())
print('total CAC',L.acquisition_cost_inr.sum(),'per act',L.acquisition_cost_inr.sum()/len(A))
A['churn']=(A.churned_within_6_months=='Y').astype(int)
print('churn overall',A.churn.mean(),'NPS mean',A.nps_score.mean())
for c in ['segment','lead_source','preferred_language','customer_follow_up_calls','contract_months','city_tier']:
    print('\n## activated by',c); print(A.groupby(c).agg(n=('lead_id','size'),churn=('churn','mean'),nps=('nps_score','mean'),days=('days_lead_to_activation','mean'),val=('monthly_bundle_value_inr','median'),calls=('customer_follow_up_calls','mean')).round(2))
A['days_b']=pd.cut(A.days_lead_to_activation,[0,10,14,18,22,30,60])
print(A.groupby('days_b',observed=True).agg(n=('lead_id','size'),churn=('churn','mean'),nps=('nps_score','mean')).round(2))
A['nprod']=A.bundle_products.str.count(';')+1
print(A.groupby('nprod').agg(n=('lead_id','size'),churn=('churn','mean'),nps=('nps_score','mean'),val=('monthly_bundle_value_inr','median')).round(2))
# segment x funnel
print('\n## segment funnel')
print(pd.crosstab(L.segment,L.stage_idx).iloc[:,::-1].cumsum(axis=1).iloc[:,::-1])
print(pd.crosstab(L.segment,L.lead_source,values=L.act,aggfunc='mean').round(3))
# language x source
print(pd.crosstab(L.preferred_language,L.segment))
# English vs non-English
L['eng']=np.where(L.preferred_language.isin(['English']),'English','Regional/Hindi')
print(grp('eng'))
print(pd.crosstab([L.eng],L.lead_source,values=L.act,aggfunc='mean').round(3))
# needs assessed to quote by segment
na=L[L.stage_idx>=2]; print('NA->QA by seg', na.groupby('segment').apply(lambda d:(d.stage_idx>=3).mean()).round(3))
print('NA->QA by lang', na.groupby('preferred_language').apply(lambda d:(d.stage_idx>=3).mean()).round(3))
print('NA->QA by source', na.groupby('lead_source').apply(lambda d:(d.stage_idx>=3).mean()).round(3))
# products of interest vs bought
from collections import Counter
print(Counter(';'.join(L.products_of_interest.dropna()).split(';')).most_common(25))
bp=Counter([p.split('x')[0] for b in A.bundle_products for p in b.split(';')]); print(bp.most_common(25))
print(A.groupby('segment').monthly_bundle_value_inr.describe())
print(L.monthly_telecom_spend_inr.groupby(L.segment).median())
print(L.groupby('segment').employee_count.median(), L.groupby('segment').num_sites.median())
print('days stage to stage', A[['created_date','contacted_date','needs_assessed_date','quote_accepted_date','kyc_complete_date','activated_date']].apply(pd.to_datetime).diff(axis=1).mean())
