from common import read_indicator, PROCESSED, ensure_dirs
import pandas as pd

ensure_dirs()
for kind in ['ai','analytics','cloud']:
    df = read_indicator(kind)
    path = PROCESSED / f'{kind}_filtered.csv'
    df.to_csv(path, index=False)
    print(kind, len(df), 'rows ->', path)
