import pandas as pd, statsmodels.formula.api as smf
from common import PROCESSED, TABLES, ensure_dirs
ensure_dirs(); df=pd.read_csv(PROCESSED/'eu_ai_country_industry_2023_2025.csv'); d=df[df.rq2_eligible.astype(bool)].copy()
m=smf.ols('ai_2025 ~ ai_2023 + analytics_2023',data=d).fit(cov_type='HC3')
out=pd.DataFrame({'term':m.params.index,'coef':m.params.values,'se_hc3':m.bse.values,'t':m.tvalues.values,'p':m.pvalues.values,'ci_low':m.conf_int()[0].values,'ci_high':m.conf_int()[1].values})
out.to_csv(TABLES/'rq2_analytics_model_hc3.csv',index=False); print(m.summary())
