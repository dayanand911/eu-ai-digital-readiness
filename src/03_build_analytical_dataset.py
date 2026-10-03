from functools import reduce
import pandas as pd
from common import read_indicator, quality_ok, PROCESSED, TABLES, ensure_dirs

ensure_dirs()
parts = [read_indicator(k) for k in ['ai','analytics','cloud']]
df = reduce(lambda l,r: pd.merge(l,r,on=['geo','nace_r2'],how='outer',validate='one_to_one'), parts)
df = df.rename(columns={
    'geo':'country','nace_r2':'industry',
    'ai_2023':'ai_2023','ai_2025':'ai_2025',
    'analytics_2023':'analytics_2023','analytics_2025':'analytics_2025',
    'cloud_2023':'cloud_2023','cloud_2025':'cloud_2025',
})

def ok(var): return [quality_ok(v,f) for v,f in zip(df[var],df[var+'_flag'])]
for var in ['ai_2023','ai_2025','analytics_2023','cloud_2023']:
    df[var+'_ok'] = ok(var)
df['delta_ai'] = df['ai_2025'] - df['ai_2023']
df['rq1_eligible'] = df['ai_2023_ok'] & df['ai_2025_ok']
df['rq2_eligible'] = df['rq1_eligible'] & df['analytics_2023_ok']
df['rq3_eligible'] = df['rq1_eligible'] & df['cloud_2023_ok']
df['rq4_eligible'] = df['rq2_eligible'] & df['cloud_2023_ok']

for c in ['ai_2023','ai_2025','analytics_2023','analytics_2025','cloud_2023','cloud_2025']:
    bad = df[c].dropna().loc[lambda s: (s<0)|(s>100)]
    assert bad.empty, f'Out-of-range values in {c}'
assert not df.duplicated(['country','industry']).any()
counts = {rq:int(df[f'{rq}_eligible'].sum()) for rq in ['rq1','rq2','rq3','rq4']}
expected = {'rq1':551,'rq2':506,'rq3':481,'rq4':448}
if counts != expected:
    raise RuntimeError(f'Eligibility counts changed. Expected {expected}, got {counts}. Check Eurostat revisions/raw archive and quality rules.')

cols = ['country','industry','ai_2023','ai_2023_flag','ai_2025','ai_2025_flag',
        'analytics_2023','analytics_2023_flag','analytics_2025','analytics_2025_flag',
        'cloud_2023','cloud_2023_flag','cloud_2025','cloud_2025_flag','delta_ai',
        'rq1_eligible','rq2_eligible','rq3_eligible','rq4_eligible']
df[cols].sort_values(['country','industry']).to_csv(PROCESSED/'eu_ai_country_industry_2023_2025.csv',index=False)
pd.DataFrame([{'research_question':k.upper(),'available_n':v} for k,v in counts.items()]).to_csv(TABLES/'sample_counts.csv',index=False)
print('Eligibility counts:', counts)
