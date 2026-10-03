from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
TABLES = ROOT / 'outputs' / 'tables'
FIGURES = ROOT / 'outputs' / 'figures'

EU27 = ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','EL','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE']
INDUSTRIES = ['C10-C12','C13-C15','C16-C18','C19','C20','C21','C22_C23','C24_C25','C26','C27','C28','C29_C30','C31-C33','D35','E','F','G45','G46','G47','H','I','J58-J60','J61','J62_J63','L','M69-M71','M72','M73-M75','N77-N82_X_N79','N79','S951']

FILES = {
    'ai': ('isoc_eb_ain2_tabular.tsv.gz', 'E_AI_TANY'),
    'analytics': ('isoc_eb_dan2_tabular.tsv.gz', 'E_DA'),
    'cloud': ('isoc_cicce_usen2_tabular.tsv.gz', 'E_CC'),
}

BAD_COMPARABILITY_FLAGS = {'b','d'}

def parse_cell(x):
    if pd.isna(x):
        return (np.nan, '')
    s = str(x).strip()
    if not s or s.startswith(':'):
        flag = s[1:].strip() if len(s) > 1 else ''
        return (np.nan, flag)
    m = re.match(r'^([-+]?\d+(?:\.\d+)?)\s*(.*)$', s)
    if not m:
        return (np.nan, s)
    return (float(m.group(1)), m.group(2).strip())

def read_indicator(kind, years=(2023, 2025)):
    filename, indicator = FILES[kind]
    p = RAW / filename
    df = pd.read_csv(p, sep='\t', compression='gzip', dtype=str)
    key = df.columns[0]
    dims = key.replace('\\TIME_PERIOD','').split(',')
    keys = df[key].str.split(',', expand=True)
    keys.columns = dims
    df = pd.concat([keys, df.drop(columns=[key])], axis=1)
    df.columns = [str(c).strip() for c in df.columns]
    df = df[(df['freq']=='A') & (df['size_emp']=='GE10') & (df['unit']=='PC_ENT') &
            (df['indic_is']==indicator) & (df['geo'].isin(EU27)) & (df['nace_r2'].isin(INDUSTRIES))].copy()
    out = df[['geo','nace_r2']].copy()
    for y in years:
        vals = df[str(y)].apply(parse_cell)
        out[f'{kind}_{y}'] = vals.map(lambda z: z[0])
        out[f'{kind}_{y}_flag'] = vals.map(lambda z: z[1])
    return out

def has_bad_flag(flag):
    tokens = set(str(flag).replace('@',' ').split())
    return bool(tokens & BAD_COMPARABILITY_FLAGS)

def quality_ok(value, flag):
    return pd.notna(value) and not has_bad_flag(flag)

def ensure_dirs():
    for p in (PROCESSED,TABLES,FIGURES): p.mkdir(parents=True, exist_ok=True)
