"""Supplementary reproducible five-fold validation for QM640 RQ4.

Inputs: frozen processed CSV, 448 RQ4 eligible country-industry contexts.
Both reduced/full specifications share folds. Encoding and model fitting occur
within training folds. This is *not* causal validation or a country-independent
population generalization estimate.

Run: python src/13_rq4_independent_validation.py
Requires scikit-learn>=1.4.
"""
from pathlib import Path
import platform
import sys
import json
import warnings
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'/'tables'/'week6_validation'
OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(ROOT/'data'/'processed'/'eu_ai_country_industry_2023_2025.csv')
d=df.loc[df['rq4_eligible'].astype(bool)].reset_index(drop=True)
assert len(d)==448 and not d[['country','industry']].duplicated().any()
assert d[['ai_2025','ai_2023','analytics_2023','cloud_2023']].notna().all().all()
cat=['country','industry']
models={'reduced':['ai_2023'], 'full':['ai_2023','analytics_2023','cloud_2023']}
rows=[];preds=[];fold_members=[]
protocols=[
 ('five_fold_contexts',KFold(n_splits=5,shuffle=True,random_state=42),None),
 # Stress test. Country fixed effects for unseen countries are not estimable.
 ('five_fold_country_holdout_sensitivity', GroupKFold(n_splits=5),d['country']),
]
for protocol, cv, groups in protocols:
 for fold,(train,test) in enumerate(cv.split(d,groups=groups),start=1):
  y_train=d.loc[train,'ai_2025'];y_test=d.loc[test,'ai_2025']
  for index in test:
   fold_members.append({'protocol':protocol,'fold':fold,'row_id':int(index),'country':d.loc[index,'country'],'industry':d.loc[index,'industry']})
  for name,numerics in models.items():
   # Unseen country or industry levels are represented by zeros in the
   # category feature block; the country holdout is a harsh sensitivity test.
   pipe=Pipeline([
    ('features',ColumnTransformer([
     ('categories',OneHotEncoder(drop='first',handle_unknown='ignore'),cat),
     ('numeric','passthrough',numerics)
    ])),('model',LinearRegression())
   ])
   with warnings.catch_warnings():
    warnings.filterwarnings('ignore',message='Found unknown categories')
    pipe.fit(d.loc[train,cat+numerics],y_train)
    prediction=pipe.predict(d.loc[test,cat+numerics])
   rows.append({'protocol':protocol,'fold':fold,'model':name,'n_train':len(train),'n_test':len(test),'RMSE_pp':float(np.sqrt(mean_squared_error(y_test,prediction))),'MAE_pp':float(mean_absolute_error(y_test,prediction))})
   for loc,index in enumerate(test):
    preds.append({'protocol':protocol,'fold':fold,'model':name,'row_id':int(index),'country':d.loc[index,'country'],'industry':d.loc[index,'industry'],'actual_ai_2025':float(y_test.iloc[loc]),'predicted_ai_2025':float(prediction[loc])})
metrics=pd.DataFrame(rows);pred=pd.DataFrame(preds);folds=pd.DataFrame(fold_members)
metrics.to_csv(OUT/'rq4_fold_metrics.csv',index=False)
pred.to_csv(OUT/'rq4_fold_predictions.csv',index=False)
folds.to_csv(OUT/'rq4_fold_assignments.csv',index=False)
summary=(metrics.groupby(['protocol','model']).agg(n_folds=('fold','size'),mean_RMSE_pp=('RMSE_pp','mean'),sd_RMSE_pp=('RMSE_pp','std'),mean_MAE_pp=('MAE_pp','mean'),sd_MAE_pp=('MAE_pp','std')).reset_index())
summary.to_csv(OUT/'rq4_validation_summary.csv',index=False)
metadata={'purpose':'exploratory prediction validation; not causal inference','primary_protocol':'five_fold_contexts','primary_seed':42,'n':448,'k':5,'categorical_encoding':'one hot drop first handle unknown ignore, fit on training only','scaling':'none for OLS','method':'scikit-learn LinearRegression','sklearn_version':sklearn.__version__,'python_version':sys.version.split()[0],'platform':platform.platform(),'limitations':['random folds share countries and industries across folds','country-holdout extrapolation is not valid fixed effect transportability','sampling weights and survey-design error not available']}
(OUT/'rq4_validation_protocol.json').write_text(json.dumps(metadata,indent=2))
print(summary.to_string(index=False))
print('PASS: independently generated fold assignments and reproducible held-out predictions')
