from pathlib import Path
import pandas as pd, numpy as np, hashlib, re, json
source=Path(__file__).resolve().parents[1]
out=source/'outputs'/'tables'/'week4_eda'; out.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(source/'data/processed/eu_ai_country_industry_2023_2025.csv').set_index(['country','industry'])
filevars=[('ai','isoc_eb_ain2_tabular.tsv.gz','E_AI_TANY'),('analytics','isoc_eb_dan2_tabular.tsv.gz','E_DA'),('cloud','isoc_cicce_usen2_tabular.tsv.gz','E_CC')]
spots=[('AT','C10-C12'),('EE','C19'),('HR','C21'),('HR','C29_C30'),('CZ','J58-J60'),('CZ','F'),('FR','C10-C12'),('SE','C10-C12'),('MT','G45'),('RO','F'),('DE','J62_J63')]
rows=[]
for kind,filename,indicator in filevars:
    path=source/'data/raw'/filename
    raw=pd.read_csv(path,sep='\t',compression='gzip',dtype=str)
    key=raw.columns[0]
    split=raw[key].str.split(',',expand=True)
    dims=key.replace('\\TIME_PERIOD','').split(',')
    split.columns=dims
    raw=pd.concat([split,raw.drop(columns=key)],axis=1)
    raw.columns=[c.strip() for c in raw.columns]
    raw=raw[(raw.freq=='A')&(raw.unit=='PC_ENT')&(raw.size_emp=='GE10')&(raw.indic_is==indicator)].copy()
    for country,industry in spots:
        hit=raw[(raw.geo==country)&(raw.nace_r2==industry)]
        if hit.empty:
            assert (country,industry) not in df.index or (pd.isna(df.loc[(country,industry),kind+'_2023']) and pd.isna(df.loc[(country,industry),kind+'_2025']))
            continue
        assert len(hit)==1
        for year in [2023,2025]:
            token=str(hit.iloc[0][str(year)]).strip()
            m=re.match(r'^([-+]?\d+(?:\.\d+)?)\s*(.*)$',token)
            extracted=float(m.group(1)) if m else np.nan
            flag=m.group(2).strip() if m else token[1:].strip() if token.startswith(':') else ''
            if (country,industry) not in df.index: continue
            actual=df.loc[(country,industry),f'{kind}_{year}']
            actualflag=df.loc[(country,industry),f'{kind}_{year}_flag']
            assert (pd.isna(actual) and pd.isna(extracted)) or (np.isclose(actual,extracted,atol=1e-10)), (kind,country,industry,year,token,actual)
            assert flag==(actualflag if pd.notna(actualflag) else ''), (kind,country,industry,year,flag,actualflag)
            rows.append({'source':kind,'country':country,'industry':industry,'year':year,'raw_token':token,'parsed_value':actual,'parsed_flag':actualflag if pd.notna(actualflag) else '', 'match':'PASS'})
pd.DataFrame(rows).to_csv(out/'raw_to_processed_spot_checks.csv',index=False)
print('Validated',len(rows),'source-year raw tokens against processed numeric values and flags')
print('Archive hash:',hashlib.sha256((source/'data/processed/eu_ai_country_industry_2023_2025.csv').read_bytes()).hexdigest())
