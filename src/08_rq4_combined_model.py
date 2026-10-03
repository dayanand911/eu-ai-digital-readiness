import pandas as pd, statsmodels.formula.api as smf
from common import PROCESSED, TABLES, ensure_dirs
ensure_dirs(); df=pd.read_csv(PROCESSED/'eu_ai_country_industry_2023_2025.csv'); d=df[df.rq4_eligible.astype(bool)].copy()
reduced=smf.ols('ai_2025 ~ ai_2023 + C(country) + C(industry)',data=d).fit()
full=smf.ols('ai_2025 ~ ai_2023 + analytics_2023 + cloud_2023 + C(country) + C(industry)',data=d).fit(cov_type='HC3')
r2_reduced=reduced.rsquared; r2_full=full.rsquared; delta=r2_full-r2_reduced; f2=delta/(1-r2_full)
pd.DataFrame([{'n':len(d),'r2_reduced':r2_reduced,'r2_full':r2_full,'delta_r2':delta,'f2_incremental':f2}]).to_csv(TABLES/'rq4_nested_model_summary.csv',index=False)
terms=['ai_2023','analytics_2023','cloud_2023']; out=pd.DataFrame({'term':terms,'coef':[full.params[t] for t in terms],'se_hc3':[full.bse[t] for t in terms],'p':[full.pvalues[t] for t in terms]}); out.to_csv(TABLES/'rq4_full_model_hc3.csv',index=False)
print('N',len(d),'R2 reduced',r2_reduced,'R2 full',r2_full,'Delta R2',delta,'f2',f2); print(out)
