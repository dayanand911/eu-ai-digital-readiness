"""Download the three complete Eurostat TSV datasets used in the capstone.

This is optional when archived raw files already exist in data/raw. Eurostat can revise
published datasets; record the retrieval date/version used for a submitted analysis.
"""
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
BASE = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/{code}/1.0?format=TSV&compress=true'
DATASETS = ['ISOC_EB_AIN2','ISOC_EB_DAN2','ISOC_CICCE_USEN2']

for code in DATASETS:
    target = RAW / f'{code.lower()}_tabular.tsv.gz'
    print(f'Downloading {code} -> {target}')
    urlretrieve(BASE.format(code=code), target)
print('Done. Verify filenames/content against the archived source files before replacing a submitted analysis dataset.')
