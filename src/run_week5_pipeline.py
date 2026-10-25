"""Rebuild the frozen Eurostat analysis and all documented interim outputs.

Does not call the Eurostat API or overwrite archived raw files.
Execute from any working directory using: python src/run_week5_pipeline.py
"""
from pathlib import Path
import subprocess,sys,hashlib,json
root=Path(__file__).resolve().parents[1]
raw=root/'data'/'raw'
processed=root/'data'/'processed'/'eu_ai_country_industry_2023_2025.csv'
expected=json.loads((root/'docs'/'frozen_snapshot_manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for fn,h in expected['archived_raw_sha256'].items():
    p=raw/fn
    if not p.is_file() or sha(p)!=h: raise RuntimeError('Source mismatch: '+str(p))
cmds=['02_clean_eurostat.py','03_build_analytical_dataset.py','04_descriptive_analysis.py',
      '05_rq1_change_analysis.py','06_rq2_analytics_model.py','07_rq3_cloud_model.py',
      '08_rq4_combined_model.py','10_week4_eda_audit.py','11_source_spot_checks.py',
      '09_robustness_checks.py','12_literature_matrix.py']
for script in cmds:
    print('=== '+script+' ===',flush=True)
    subprocess.run([sys.executable,str(root/'src'/script)],cwd=root,check=True)
if sha(processed)!=expected['processed_sha256']:
    raise AssertionError('Rebuilt processed CSV differs from frozen baseline')
want=[
  'outputs/tables/week4_eda/raw_to_processed_spot_checks.csv',
  'outputs/tables/week4_eda/variable_coverage_and_flags.csv',
  'outputs/tables/week4_eda/rq_sample_eligibility_audit.csv',
  'outputs/figures/week4_eda/figure_01_matched_ai_distributions.png',
  'outputs/figures/week4_eda/figure_07_rq_country_eligibility_heatmap.png',
  'outputs/tables/week4_models/rq1_inference_robustness.csv',
  'outputs/tables/week4_models/rq2_rq3_verified_models.csv',
  'outputs/tables/week4_models/rq4_nested_inference.csv',
  'outputs/tables/week4_models/clustered_sensitivity_by_rq.csv',
  'outputs/tables/week4_literature/verified_literature_relevance_matrix.csv'
]
absent=[name for name in want if not (root/name).exists()]
if absent: raise AssertionError('Missing outputs: '+str(absent))
print('PASS: all baseline and Week 4 outputs generated from frozen data.')
print('PASS: raw and processed SHA-256 checksums match the frozen manifest.')
