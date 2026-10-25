"""Reproduce QM640 Week 4 interim regression and robustness analysis from frozen archived CSV.
Does not overwrite Week 3 repo outputs. Executable: python step3_models.py.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.optimize import brentq
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
import statsmodels.formula.api as smf
from scipy.stats import f as fdist, ncf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; TABLES=OUT/'tables'/'week4_models'; FIGS=OUT/'figures'/'week4_models'
for p in [TABLES,FIGS]:p.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'data'/'processed'/'eu_ai_country_industry_2023_2025.csv'
df=pd.read_csv(DATA)
for v in ['rq1_eligible','rq2_eligible','rq3_eligible','rq4_eligible']:
    assert df[v].dropna().isin([True,False]).all()
d1=df[df.rq1_eligible].copy();d2=df[df.rq2_eligible].copy();d3=df[df.rq3_eligible].copy();d4=df[df.rq4_eligible].copy()
assert (len(d1),len(d2),len(d3),len(d4))==(551,506,481,448)
results={}
def record(key,d):results[key]=d

# RQ1 paired tests, Wilcoxon, bounded/unweighted warnings
d=d1.delta_ai.to_numpy(); n=len(d)
t,pt=st.ttest_1samp(d,0);ci=st.t.interval(.95,n-1,loc=d.mean(),scale=st.sem(d));wil=st.wilcoxon(d,zero_method='wilcox',alternative='two-sided',method='auto')
q1,q3=np.percentile(d,[25,75]);iqr=q3-q1;lo=q1-1.5*iqr;hi=q3+1.5*iqr
inliers=d[(d>=lo)&(d<=hi)]; outliers=d[(d<lo)|(d>hi)]
rec={'n':n,'mean_2023':d1.ai_2023.mean(),'mean_2025':d1.ai_2025.mean(),'mean_change_pp':d.mean(),'sd_change_pp':d.std(ddof=1),'ci95_low':ci[0],'ci95_high':ci[1],'t':t,'df':n-1,'p_t':pt,'dz':d.mean()/d.std(ddof=1),'wilcoxon_W':wil.statistic,'wilcoxon_p':wil.pvalue,'n_zero_differences':int((d==0).sum()),'outlier_iqr_n':len(outliers),'inlier_mean_diagnostic_only':inliers.mean(),'outlier_removed_n_diagnostic_only':len(inliers),'median_change_pp':np.median(d),'pct_positive':100*np.mean(d>0)}
record('rq1',rec);pd.DataFrame([rec]).to_csv(TABLES/'rq1_inference_robustness.csv',index=False)

# independent RQ2, RQ3 baseline-adjusted HC3 coefficients plus classical fit
designs={'rq2':(d2,'ai_2025 ~ ai_2023 + analytics_2023','analytics_2023'), 'rq3':(d3,'ai_2025 ~ ai_2023 + cloud_2023','cloud_2023')}
rows=[]; diagnostic_rows=[]
for tag,(d,formula,term) in designs.items():
    m=smf.ols(formula,data=d).fit()
    hc=m.get_robustcov_results(cov_type='HC3')
    ix=list(m.params.index).index(term)
    bp=het_breuschpagan(m.resid,m.model.exog)
    infl=OLSInfluence(m)
    # HC3 stat uses normal asymptotics by statsmodels default when fitting cov_type HC3 directly, match archived approach
    hcasym=smf.ols(formula,data=d).fit(cov_type='HC3')
    rec={'rq':tag,'n':int(m.nobs),'term':term,'coef':m.params[term],'se_HC3':hcasym.bse[term],'p_HC3':hcasym.pvalues[term],'ci_HC3_low':hcasym.conf_int().loc[term,0],'ci_HC3_high':hcasym.conf_int().loc[term,1],'r2':m.rsquared,'adj_r2':m.rsquared_adj,'rmse_insample':np.sqrt(np.mean(m.resid**2)),'mae_insample':np.mean(abs(m.resid)),'n_pred_outside_0_100':int(((m.fittedvalues<0)|(m.fittedvalues>100)).sum()),'bp_p':bp[1],'cook_gt_4_n':int((infl.cooks_distance[0]>4/m.nobs).sum()),'n_nonzero_cook':int(np.isfinite(infl.cooks_distance[0]).sum())}
    rows.append(rec);record(tag,rec)
    diag={'rq':tag,'n':len(d),'model_rank':int(m.model.rank),'num_params':len(m.params),'residual_skew':float(st.skew(m.resid)),'residual_kurtosis_excess':float(st.kurtosis(m.resid)),'BP_LM_p':bp[1],'BP_F_p':bp[3], 'max_abs_studentized_resid':float(np.nanmax(abs(infl.resid_studentized_external))),'max_cooks_d':float(infl.cooks_distance[0].max())}
    diagnostic_rows.append(diag)
    plt.figure(figsize=(6.6,4.5));plt.scatter(m.fittedvalues,m.resid,s=13,alpha=.5);plt.axhline(0,linestyle='--',color='black');plt.title(f'{tag.upper()} residuals versus fitted (n={len(d)})');plt.xlabel('Fitted AI adoption 2025 (percentage points)');plt.ylabel('Residual (percentage points)');plt.tight_layout();plt.savefig(FIGS/f'{tag}_residual_vs_fitted.png',dpi=175);plt.close()
pd.DataFrame(rows).to_csv(TABLES/'rq2_rq3_verified_models.csv',index=False)

# RQ4 same-sample reduced/full regression models
red_f='ai_2025 ~ ai_2023 + C(country) + C(industry)'
full_f='ai_2025 ~ ai_2023 + analytics_2023 + cloud_2023 + C(country) + C(industry)'
red=smf.ols(red_f,data=d4).fit();full=smf.ols(full_f,data=d4).fit();fullhc=smf.ols(full_f,data=d4).fit(cov_type='HC3')
assert (len(red.model.endog),len(full.model.endog))==(448,448)
R=np.zeros((2,len(full.params))); colnames=list(full.params.index)
for i,term in enumerate(['analytics_2023','cloud_2023']): R[i,colnames.index(term)]=1
ft=full.f_test(R);w_hc=fullhc.wald_test(R,scalar=True)
# 2-way cluster by country and industry; use binary-coded country / industry groups
country=pd.factorize(d4['country'])[0].astype(int); industry=pd.factorize(d4['industry'])[0].astype(int)
cov2,cov_c,cov_i=cov_cluster_2groups(full,country,industry,use_correction=True)
sel=['ai_2023','analytics_2023','cloud_2023']; coeff=[]
for term in sel:
    j=colnames.index(term)
    v=float(cov2[j,j]);se=float(np.sqrt(v)) if v>=0 else np.nan
    # exploratory diagnostic only: normal approximation (does not correct finite # clusters)
    z=full.params[term]/se if np.isfinite(se) else np.nan
    coeff.append({'term':term,'coefficient':full.params[term],'HC3_se':fullhc.bse[term],'HC3_p':fullhc.pvalues[term], 'HC3_CI_low':fullhc.conf_int().loc[term,0],'HC3_CI_high':fullhc.conf_int().loc[term,1],'two_way_cluster_se':se,'two_way_cluster_z_approx':z,'two_way_cluster_p_norm_approx_NOT_CONFIRMATORY':2*st.norm.sf(abs(z)) if np.isfinite(z) else np.nan})
pd.DataFrame(coeff).to_csv(TABLES/'rq4_coefficients_hc3_cluster_sensitivity.csv',index=False)
# joint 2-way Wald test diagnostic: potential indefinite variance matrix; check eigenvalues
Rb=R@full.params.values
Rc=R@cov2@R.T
Eig=np.linalg.eigvalsh(Rc)
if min(Eig)>0:
    joint2=float(Rb.T@np.linalg.inv(Rc)@Rb);joint2p=st.chi2.sf(joint2,2)
else:joint2=joint2p=np.nan
f2=(full.rsquared-red.rsquared)/(1-full.rsquared)
rec4={'n':int(full.nobs),'country_n':d4.country.nunique(),'industry_n':d4.industry.nunique(),'full_rank_total':int(full.model.rank),'full_slopes':int(full.model.rank-1),'reduced_rank_total':int(red.model.rank),'r2_reduced':red.rsquared,'r2_full':full.rsquared,'adj_r2_reduced':red.rsquared_adj,'adj_r2_full':full.rsquared_adj,'delta_r2':full.rsquared-red.rsquared,'incremental_f2':f2,'classical_joint_F':float(ft.fvalue),'classical_joint_p':float(ft.pvalue),'classical_df_num':2,'classical_df_den':float(full.df_resid),'HC3_joint_chi2':float(w_hc.statistic),'HC3_joint_p':float(w_hc.pvalue),'two_way_cluster_joint_chi2_exploratory':joint2,'two_way_cluster_joint_p_exploratory':joint2p,'two_way_cluster_Rcov_min_eigenvalue':float(Eig.min()),'rmse_insample_reduced':np.sqrt(np.mean(red.resid**2)),'rmse_insample_full':np.sqrt(np.mean(full.resid**2)),'mae_insample_reduced':np.mean(abs(red.resid)),'mae_insample_full':np.mean(abs(full.resid)),'n_full_predictions_outside_0_100':int(((full.fittedvalues<0)|(full.fittedvalues>100)).sum()),'bp_p_full':het_breuschpagan(full.resid,full.model.exog)[1]}
record('rq4',rec4);pd.DataFrame([rec4]).to_csv(TABLES/'rq4_nested_inference.csv',index=False)
# VIF for substantive predictors by country/industry adjusted matrix (calculated all features)
vifs=[]
for term in sel:
    j=colnames.index(term)
    vifs.append({'term':term,'vif_full_model':variance_inflation_factor(full.model.exog,j)})
pd.DataFrame(vifs).to_csv(TABLES/'rq4_vif.csv',index=False)
inf4=OLSInfluence(full); diagnostic_rows.append({'rq':'rq4','n':len(d4),'model_rank':int(full.model.rank),'num_params':len(full.params),'residual_skew':float(st.skew(full.resid)),'residual_kurtosis_excess':float(st.kurtosis(full.resid)),'BP_LM_p':rec4['bp_p_full'],'BP_F_p':het_breuschpagan(full.resid,full.model.exog)[3], 'max_abs_studentized_resid':float(np.nanmax(abs(inf4.resid_studentized_external))),'max_cooks_d':float(inf4.cooks_distance[0].max()),'cook_gt_4_n':int((inf4.cooks_distance[0]>4/len(d4)).sum())})
pd.DataFrame(diagnostic_rows).to_csv(TABLES/'model_diagnostics.csv',index=False)
plt.figure(figsize=(6.6,4.5));plt.scatter(full.fittedvalues,full.resid,s=14,alpha=.48);plt.axhline(0,linestyle='--',color='black');plt.title('RQ4 full-model residuals vs fitted (n=448)');plt.xlabel('Fitted AI adoption 2025 (%)');plt.ylabel('Residual (percentage points)');plt.tight_layout();plt.savefig(FIGS/'rq4_residual_vs_fitted.png',dpi=175);plt.close()

# Row-wise model comparison figure (same n=448)
fig,ax=plt.subplots(figsize=(7.5,4.3));ax.bar(['Baseline + fixed effects','Add analytics + cloud'],[red.rsquared,full.rsquared],width=.6);ax.set_ylim(0,1);ax.set_ylabel('In-sample R²');ax.set_title('RQ4 same-sample nested model comparison (n=448)');
for ix,val in enumerate([red.rsquared,full.rsquared]):ax.text(ix,val+.015,f'{val:.4f}',ha='center',size=11)
fig.tight_layout();fig.savefig(FIGS/'rq4_same_sample_r2.png',dpi=175);plt.close(fig)

# power via noncentral F, presuming independent OLS errors and planned f2, no clustering (not empirical assurance)
def regression_power(N, u, total_slopes, f2=.02, alpha=.05):
    v=N-total_slopes-1
    if v<=0:return np.nan
    fcrit=fdist.isf(alpha,u,v)
    return ncf.sf(fcrit,u,v,f2*N)
def required_n(u,p,f2=.02,alpha=.05,target=.8):
    start=p+2
    for N in range(start,4000):
        if regression_power(N,u,p,f2,alpha)>=target:return N
power_rows=[]
for name,tested,p,N in [('rq2',1,2,506),('rq3',1,2,481),('rq4_original_plan',2,59,448),('rq4_actual_design',2,56,448)]:
    minN=required_n(tested,p)
    power_rows.append({'case':name,'tested_predictors':tested,'full_model_slopes':p,'observed_N':N,'effect_size_f2':.02,'alpha':.05,'target_power':.8,'required_N_by_ncf':minN,'achieved_power_approx':regression_power(N,tested,p)})
pd.DataFrame(power_rows).to_csv(TABLES/'power_reconciliation.csv',index=False)
record('power',power_rows)
# warning: for RQ2/3 empirical predictors partial f2 nomenclature; N solver is integer ncf approximation, can differ from GPower setup
with open(OUT/'step3_stats.json','w') as f:json.dump(results,f,indent=2,default=lambda x: x.item() if hasattr(x,'item') else str(x))
print(json.dumps(results,indent=2,default=lambda x: x.item() if hasattr(x,'item') else str(x)))
