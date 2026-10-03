import numpy as np, pandas as pd
from scipy import stats
from common import PROCESSED, TABLES, ensure_dirs
ensure_dirs(); df=pd.read_csv(PROCESSED/'eu_ai_country_industry_2023_2025.csv'); d=df[df.rq1_eligible.astype(bool)].delta_ai.dropna()
n=len(d); mean=d.mean(); sd=d.std(ddof=1); se=sd/np.sqrt(n); t=mean/se; p=2*stats.t.sf(abs(t),n-1); crit=stats.t.ppf(.975,n-1)
res=pd.DataFrame([{'n':n,'mean_change_pp':mean,'sd_change':sd,'t':t,'df':n-1,'p_two_sided':p,'ci95_low':mean-crit*se,'ci95_high':mean+crit*se,'dz':mean/sd,'median_change_pp':d.median(),'pct_increase':100*(d>0).mean(),'pct_unchanged':100*(d==0).mean(),'pct_decrease':100*(d<0).mean()}])
res.to_csv(TABLES/'rq1_paired_change.csv',index=False); print(res.to_string(index=False))
