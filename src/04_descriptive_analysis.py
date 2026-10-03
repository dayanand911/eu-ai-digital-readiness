import pandas as pd
from common import PROCESSED, TABLES, ensure_dirs
ensure_dirs()
df=pd.read_csv(PROCESSED/'eu_ai_country_industry_2023_2025.csv')
r=df[df.rq1_eligible.astype(bool)].copy()
summary=r[['ai_2023','ai_2025','delta_ai']].describe(percentiles=[.25,.5,.75]).T
summary.to_csv(TABLES/'rq1_descriptive_summary.csv')
print(summary)
