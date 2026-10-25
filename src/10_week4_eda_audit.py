"""QM640 Week 4 Step 2: frozen archive EDA and quality audit.
Input: archived processed Eurostat dataset assembled from the project's frozen raw files.
Output: reproducible audit CSV summaries and EDA figures; no source files changed.
"""
from pathlib import Path
from itertools import product
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

ROOT = Path(__file__).resolve().parents[1]
FIG=ROOT/'outputs'/'figures'/'week4_eda'; TBL=ROOT/'outputs'/'tables'/'week4_eda'
FIG.mkdir(exist_ok=True,parents=True); TBL.mkdir(exist_ok=True,parents=True)
SRC=ROOT
sys.path.insert(0,str(SRC/'src'))
from common import EU27, INDUSTRIES, has_bad_flag, read_indicator
INPUT=SRC/'data/processed/eu_ai_country_industry_2023_2025.csv'
df=pd.read_csv(INPUT, dtype={'country':str,'industry':str})
VARS=['ai_2023','ai_2025','analytics_2023','analytics_2025','cloud_2023','cloud_2025']
PRIMARY=['ai_2023','ai_2025','analytics_2023','cloud_2023']
assert df.shape==(833,19)
assert not df.duplicated(['country','industry']).any()
assert set(df.country)==set(EU27) and set(df.industry)==set(INDUSTRIES)
assert all(df[x].dropna().between(0,100).all() for x in VARS)
missing_keys=sorted(set(product(EU27,INDUSTRIES))-set(zip(df.country,df.industry)))
assert len(missing_keys)==4
pd.DataFrame(missing_keys,columns=['country','industry']).to_csv(TBL/'four_absent_grid_cells.csv',index=False)

# Source audit: verify the corresponding raw Eurostat row keys are unique prior to join.
raw_counts=[]
for kind in ['ai','analytics','cloud']:
    p=read_indicator(kind)
    assert not p.duplicated(['geo','nace_r2']).any()
    raw_counts.append(dict(source=kind,rows_matching_filters=len(p),countries=p.geo.nunique(),industries=p.nace_r2.nunique(),duplicate_keys=p.duplicated(['geo','nace_r2']).sum()))
pd.DataFrame(raw_counts).to_csv(TBL/'raw_source_key_checks.csv',index=False)

# Status flags, available numeric counts, eligibility and ineligible breakdown
summary=[];flag_rows=[]
for v in VARS:
    fl=df[v+'_flag'].fillna('')
    numeric=df[v].notna()
    flagged_comparability=fl.map(has_bad_flag)
    valid=numeric & ~flagged_comparability
    summary.append({
        'variable':v,'grid_rows':837,'archive_rows':len(df),
        'numeric_cells':int(numeric.sum()),'missing_non_numeric_cells':int((~numeric).sum()),
        'numeric_excluded_b_or_d':int((numeric & flagged_comparability).sum()),
        'usable_numeric':int(valid.sum()),
        'usable_pct_of_833':round(100*valid.sum()/len(df),2),
        'usable_pct_of_837':round(100*valid.sum()/837,2),
        'numeric_u_flag':int((numeric & fl.astype(str).str.contains(r'(?<!\w)u(?!\w)',regex=True)).sum())
    })
    for flag,count in fl.replace('', '(unflagged)').value_counts().items():
        flag_rows.append({'variable':v,'flag':flag,'count':int(count),'non_numeric':int((~numeric & (fl.replace('','(unflagged)')==flag)).sum())})
pd.DataFrame(summary).to_csv(TBL/'variable_coverage_and_flags.csv',index=False)
pd.DataFrame(flag_rows).to_csv(TBL/'status_flag_inventory.csv',index=False)

# Independently reconstruct exact eligibility booleans using numeric values + exclusion flags.
checks={v:df[v].notna() & ~df[v+'_flag'].fillna('').map(has_bad_flag) for v in PRIMARY}
requested={
 'rq1':checks['ai_2023'] & checks['ai_2025'],
 'rq2':checks['ai_2023'] & checks['ai_2025'] & checks['analytics_2023'],
 'rq3':checks['ai_2023'] & checks['ai_2025'] & checks['cloud_2023'],
 'rq4':checks['ai_2023'] & checks['ai_2025'] & checks['analytics_2023'] & checks['cloud_2023'],
}
rq_counts=[]
for rq,mask in requested.items():
    assert np.array_equal(mask.to_numpy(),df[f'{rq}_eligible'].to_numpy()),f'Eligibility mismatch for {rq}'
    d=df.loc[mask]
    rq_counts.append({'rq':rq.upper(),'usable_n':len(d),'pct_of_837':round(100*len(d)/837,2),'countries':d.country.nunique(),'industries':d.industry.nunique(),'countries_absent':','.join(sorted(set(EU27)-set(d.country))),'min_country_contexts':int(d.groupby('country').size().min()),'max_country_contexts':int(d.groupby('country').size().max())})
pd.DataFrame(rq_counts).to_csv(TBL/'rq_sample_eligibility_audit.csv',index=False)
assert [x['usable_n'] for x in rq_counts]==[551,506,481,448]

# Diagnostics and EDA: paired only; never compare unmatched populations as paired changes.
paired=df.loc[requested['rq1']].copy()
paired['delta_independently']=paired['ai_2025']-paired['ai_2023']
assert np.allclose(paired['delta_independently'],paired['delta_ai'])

stats_rows=[]
for v in ['ai_2023','ai_2025','delta_ai']:
    s=paired[v]
    q1,q3=s.quantile([.25,.75]);iqr=q3-q1; lo=q1-1.5*iqr; hi=q3+1.5*iqr
    stats_rows.append({'variable':v,'n':len(s),'mean':s.mean(),'median':s.median(),'std':s.std(ddof=1),'min':s.min(),'q1':q1,'q3':q3,'max':s.max(),'iqr':iqr,'outlier_lower_fence':lo,'outlier_upper_fence':hi,'iqr_low_outliers':int((s<lo).sum()),'iqr_high_outliers':int((s>hi).sum()),'zero_values':int((s==0).sum())})
pd.DataFrame(stats_rows).to_csv(TBL/'rq1_paired_descriptive_and_iqr.csv',index=False)
change=paired.delta_ai
changes={
'n':len(change),'mean_change_pp':change.mean(),'median_change_pp':change.median(),'sd_pp':change.std(ddof=1),
'increase_count':int((change>0).sum()),'unchanged_count':int((change==0).sum()),'decrease_count':int((change<0).sum()),
'increase_pct':100*(change>0).mean(),'unchanged_pct':100*(change==0).mean(),'decrease_pct':100*(change<0).mean(),
'min_change_pp':change.min(),'max_change_pp':change.max(),'trimmed_mean_10pct_pp':__import__('scipy').stats.trim_mean(change,proportiontocut=.10),
 'mean_change_rq4_common_pp':df.loc[requested['rq4'],'delta_ai'].mean(),
 'zero_2023_count':int((paired.ai_2023==0).sum()),'zero_2025_count':int((paired.ai_2025==0).sum())}
pd.DataFrame([changes]).to_csv(TBL/'rq1_change_breakdown.csv',index=False)
paired.loc[paired.delta_ai<0,['country','industry','ai_2023','ai_2025','delta_ai']].sort_values('delta_ai').to_csv(TBL/'rq1_negative_change_contexts.csv',index=False)
paired.loc[paired.delta_ai>0,['country','industry','ai_2023','ai_2025','delta_ai']].sort_values('delta_ai',ascending=False).head(15).to_csv(TBL/'rq1_top_15_positive_change_contexts.csv',index=False)

country=paired.groupby('country').agg(n=('delta_ai','size'),mean_change_pp=('delta_ai','mean'),median_change_pp=('delta_ai','median'),mean_ai_2023=('ai_2023','mean'),mean_ai_2025=('ai_2025','mean')).sort_values('mean_change_pp')
country.to_csv(TBL/'rq1_country_unweighted_context_means.csv')
industry=paired.groupby('industry').agg(n=('delta_ai','size'),mean_change_pp=('delta_ai','mean'),median_change_pp=('delta_ai','median')).sort_values('mean_change_pp')
industry.to_csv(TBL/'rq1_industry_unweighted_context_means.csv')

# Country variable completeness: ratios from theoretical 31 industries; does not imply actual survey coverage.
ct=[]
for c in EU27:
    sub=df.loc[df.country==c]
    row={'country':c,'archive_rows':len(sub),'rq1_n':int(sub.rq1_eligible.sum()),'rq2_n':int(sub.rq2_eligible.sum()),'rq3_n':int(sub.rq3_eligible.sum()),'rq4_n':int(sub.rq4_eligible.sum())}
    for v in PRIMARY:
        row[v+'_usable']=int((sub[v].notna() & ~sub[v+'_flag'].fillna('').map(has_bad_flag)).sum())
    ct.append(row)
pd.DataFrame(ct).to_csv(TBL/'country_coverage_by_rq.csv',index=False)

# Correlations are exploratory raw associations only, not adjusted inference.
corrs=[]
for v,rq in [('analytics_2023','rq2'),('cloud_2023','rq3')]:
    ss=df.loc[requested[rq],[v,'ai_2025','ai_2023']].dropna()
    corrs.append({'predictor':v,'rq':rq.upper(),'n':len(ss),'raw_pearson_with_ai2025':ss[v].corr(ss.ai_2025),'raw_spearman_with_ai2025':ss[v].corr(ss.ai_2025,method='spearman'),'pearson_with_baseline_ai2023':ss[v].corr(ss.ai_2023)})
pd.DataFrame(corrs).to_csv(TBL/'exploratory_unadjusted_correlations.csv',index=False)

# Consistent presentation; avoid confusing EU aggregate with equal-weight context mean.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.dpi':135,'savefig.dpi':180,'axes.spines.top':False,'axes.spines.right':False})
def save(path):
    plt.tight_layout();plt.savefig(FIG/path,bbox_inches='tight');plt.close()

# Fig 1: matched context distributions.
fig,ax=plt.subplots(figsize=(10,5))
bins=np.arange(0,90,5)
ax.hist(paired.ai_2023,bins=bins,alpha=.62,label='2023 (same 551 contexts)')
ax.hist(paired.ai_2025,bins=bins,alpha=.55,label='2025 (same 551 contexts)')
ax.set(title='AI adoption distributions: matched 2023 and 2025',xlabel='Enterprises reporting AI adoption (%)',ylabel='Number of country–industry contexts')
ax.legend(frameon=False)
save('figure_01_matched_ai_distributions.png')

# Fig 2: paired difference histogram.
fig,ax=plt.subplots(figsize=(10,5))
ax.hist(change,bins=np.arange(-30,75,4),alpha=.8)
ax.axvline(0,linestyle='--',color='black',linewidth=1.2,label='No change')
ax.axvline(change.mean(),linestyle=':',color='gray',linewidth=2,label=f'Mean: +{change.mean():.2f} pp')
ax.set(title='Distribution of paired AI adoption changes (n = 551)',xlabel='2025 − 2023 AI adoption (percentage points)',ylabel='Number of matched contexts')
ax.legend(frameon=False)
save('figure_02_paired_ai_changes.png')

# Fig 3: countries, readable label and n, avert blind ranking.
fig,ax=plt.subplots(figsize=(10,8))
y=np.arange(len(country));ax.barh(y,country.mean_change_pp.values)
ax.set_yticks(y,[f'{c} (n={int(row.n)})' for c,row in country.iterrows()])
ax.axvline(0,color='gray',linewidth=.8)
ax.set(title='Mean change by country (unweighted industry-context means)',xlabel='Mean paired change, 2023–2025 (percentage points)')
ax.text(.98,.01,'Caution: country sample sizes vary; FR and SE have no eligible matched contexts.',ha='right',va='bottom',transform=ax.transAxes,fontsize=8)
save('figure_03_country_context_mean_change.png')

# Fig 4: industry contexts country means.
fig,ax=plt.subplots(figsize=(10,10))
y=np.arange(len(industry));ax.barh(y,industry.mean_change_pp.values)
ax.set_yticks(y,[f'{i} (n={int(row.n)})' for i,row in industry.iterrows()])
ax.axvline(0,color='gray',linewidth=.8)
ax.set(title='Mean change by NACE industry category (unweighted country means)',xlabel='Mean paired change, 2023–2025 (percentage points)')
ax.text(.98,.01,'Exploratory: unequal coverage and some small category samples.',ha='right',va='bottom',transform=ax.transAxes,fontsize=8)
save('figure_04_industry_context_mean_change.png')

for num,v,rq,title in [(5,'analytics_2023','rq2','2023 data-analytics adoption'),(6,'cloud_2023','rq3','2023 paid-cloud adoption')]:
    ss=df.loc[requested[rq],[v,'ai_2025','ai_2023']].copy()
    fig,ax=plt.subplots(figsize=(9,6))
    ax.scatter(ss[v],ss['ai_2025'],alpha=.35,s=15)
    xx=np.linspace(ss[v].min(),ss[v].max(),100)
    if ss[v].nunique()>1:
        slope,intercept=np.polyfit(ss[v],ss.ai_2025,1)
        ax.plot(xx,intercept+slope*xx,linestyle='--',linewidth=1.5,label='Unadjusted linear fit')
    ax.set(title=f'{title} vs 2025 AI adoption (n = {len(ss)})',xlabel=f'{title} (%)',ylabel='2025 AI adoption (%)')
    ax.legend(frameon=False)
    ax.text(.02,.97,'Descriptive only: does not adjust for 2023 AI adoption or other factors.',transform=ax.transAxes,ha='left',va='top',fontsize=8)
    save(f'figure_0{num}_{v}_vs_2025_ai.png')

# Fig 7: national eligibility coverage per question as absolute n (0–31).
coverage=pd.read_csv(TBL/'country_coverage_by_rq.csv').set_index('country')
fig,ax=plt.subplots(figsize=(11,9))
m=coverage[['rq1_n','rq2_n','rq3_n','rq4_n']].loc[EU27].values
im=ax.imshow(m,vmin=0,vmax=31,aspect='auto',cmap='viridis')
ax.set_yticks(np.arange(27),EU27)
ax.set_xticks(np.arange(4),['RQ1','RQ2','RQ3','RQ4'])
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        ax.text(j,i,str(m[i,j]),ha='center',va='center',fontsize=8,color=('white' if m[i,j]<14 else 'black'))
fig.colorbar(im,ax=ax,label='Eligible country–industry contexts (of 31 possible)')
ax.set(title='Uneven sample coverage after RQ-specific screening')
save('figure_07_rq_country_eligibility_heatmap.png')

print('Source filtered row counts:',raw_counts)
print('Four absent keys:',missing_keys)
print('RQ sample counts:',rq_counts)
print('Coverage:',summary)
print('Delta summary:',changes)
print('Correlations:',corrs)
print('Figures:',len(list(FIG.glob('*.png'))))
