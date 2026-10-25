from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm,statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
root=Path(__file__).resolve().parents[1];out=root/'outputs'/'tables'/'week4_models';out.mkdir(exist_ok=True,parents=True);data=root/'data'/'processed'/'eu_ai_country_industry_2023_2025.csv';df=pd.read_csv(data)
rows=[]
for key,mask,formula,testcols in [('rq1','rq1_eligible','delta_ai ~ 1',['Intercept']),('rq2','rq2_eligible','ai_2025 ~ ai_2023 + analytics_2023',['analytics_2023']),('rq3','rq3_eligible','ai_2025 ~ ai_2023 + cloud_2023',['cloud_2023']),('rq4','rq4_eligible','ai_2025 ~ ai_2023 + analytics_2023 + cloud_2023 + C(country) + C(industry)',['analytics_2023','cloud_2023'])]:
    d=df[df[mask]].copy();fit=smf.ols(formula,d).fit();countries=pd.factorize(d.country)[0];industries=pd.factorize(d.industry)[0]
    c2,cc,ci=cov_cluster_2groups(fit,countries,industries)
    cols=list(fit.params.index)
    for c in testcols:
        j=cols.index(c)
        rec={'rq':key,'n':len(d),'country_clusters':d.country.nunique(),'industry_clusters':d.industry.nunique(),'term':c,'coef':fit.params[c]}
        for name,cov in [('country',cc),('industry',ci),('two_way',c2)]:
            se=np.sqrt(cov[j,j]) if cov[j,j]>=0 else np.nan
            rec[f'{name}_cluster_se']=se
            rec[f'{name}_cluster_t']=fit.params[c]/se
            # reference only, conservative two-sided t with df min(clusters)-1, not validated small-sample multiway calibration
            clusters=rec['country_clusters'] if name=='country' else rec['industry_clusters'] if name=='industry' else min(rec['country_clusters'],rec['industry_clusters'])
            rec[f'{name}_cluster_p_approx_df_clustersminus1']=2*stats.t.sf(abs(fit.params[c]/se),clusters-1)
        rows.append(rec)
pd.DataFrame(rows).to_csv(out/'clustered_sensitivity_by_rq.csv',index=False)
print(pd.DataFrame(rows).round(6).to_string(index=False))
