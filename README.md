# Digital Readiness and Enterprise AI Adoption in the European Union

Reproducibility package for the QM640 Data Analytics Capstone synopsis/project by **Dayanand Krishna**.

## Research purpose
This quantitative observational study examines enterprise AI adoption across matched EU Member State × industry contexts in 2023 and 2025 and tests whether baseline data-analytics and cloud-computing adoption are associated with 2025 AI adoption after accounting for baseline AI adoption. The project does **not** claim firm-level causality.

## Data sources
The repository archives three Eurostat enterprise ICT datasets used in the analysis:

| Construct | Eurostat dataset | Indicator | Primary years |
|---|---|---|---|
| AI adoption | `isoc_eb_ain2` | `E_AI_TANY` | 2023, 2025 |
| Data analytics | `isoc_eb_dan2` | `E_DA` | 2023, 2025 |
| Paid cloud computing | `isoc_cicce_usen2` | `E_CC` | 2023, 2025 |

Core filters: annual frequency (`A`), enterprises with 10+ persons employed (`GE10`), percentage of enterprises (`PC_ENT`), EU27 individual countries, and the harmonized non-overlapping NACE Rev. 2 categories documented in the code.

Eurostat API documentation: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/api

Eurostat datasets can be revised. The files under `data/raw/` are the archived copies used for this project. The optional download script retrieves current disseminated versions and should not silently replace the archived analysis inputs.

## Repository structure
```text
eu-ai-digital-readiness/
├── README.md
├── LICENSE
├── requirements.txt
├── data/
│   ├── raw/                  # archived Eurostat TSV.GZ inputs
│   ├── processed/            # generated analytical files
│   └── data_dictionary.csv
├── src/
│   ├── common.py
│   ├── 01_download_data.py
│   ├── 02_clean_eurostat.py
│   ├── 03_build_analytical_dataset.py
│   ├── 04_descriptive_analysis.py
│   ├── 05_rq1_change_analysis.py
│   ├── 06_rq2_analytics_model.py
│   ├── 07_rq3_cloud_model.py
│   ├── 08_rq4_combined_model.py
│   ├── 09_robustness_checks.py  # executes Week 4 diagnostics and sensitivity
│   ├── 10_week4_eda_audit.py
│   ├── 11_source_spot_checks.py
│   ├── 12_literature_matrix.py
│   ├── week4_model_diagnostics.py
│   ├── week4_cluster_sensitivity.py
│   └── run_week5_pipeline.py
├── outputs/
│   ├── tables/             # original RQ CSVs and verified Week 4 audit/model outputs
│   └── figures/            # verified Week 4 EDA/model figures
└── docs/
    ├── methodology.md
    └── data_quality_notes.md
```

## Reproduce the analytical dataset
Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/03_build_analytical_dataset.py
```

The build script validates percentage bounds, checks duplicate country-industry keys, preserves Eurostat flags, and deliberately fails if the archived-data eligibility counts differ from the verified values:

- RQ1: 551
- RQ2: 506
- RQ3: 481
- RQ4: 448

Then run the analyses:

```bash
python src/04_descriptive_analysis.py
python src/05_rq1_change_analysis.py
python src/06_rq2_analytics_model.py
python src/07_rq3_cloud_model.py
python src/08_rq4_combined_model.py
python src/09_robustness_checks.py
```

## Data-quality rules
The Eurostat TSV status flag is preserved separately from the numeric value. Missing `:` cells are never converted to zero. For the primary comparability screen, observations carrying `b` or `d` on variables required by an RQ are excluded. Numeric `u` observations remain flagged and are intended for sensitivity analysis. The frozen extract contains no numeric u-flagged observations, so no numeric-u sensitivity contrast was conducted. See `docs/data_quality_notes.md`.

## Important interpretation limits
The unit of analysis is a **country-industry context**, not an enterprise. Associations in this repository do not establish that individual firms with analytics/cloud in 2023 subsequently adopted AI, and they do not establish causality. The AI technology basket also evolves over time, which is treated as a comparability limitation.

## License and attribution
Code in this repository is released under the MIT License. Eurostat data remain subject to Eurostat/European Commission reuse terms and should be cited to the original source. This repository preserves source identifiers and raw files for academic reproducibility.


## Week 5 graded interim package — reproducibility update

The original Week 3 files are retained. This update integrates **locally generated Week 4 audit,
EDA, and inferential validation** into the same repository structure. The original data files,
processed CSV and seven original RQ output CSVs were confirmed unchanged. The original
`src/09_robustness_checks.py` placeholder has been replaced by an executable wrapper.

**Run from a clean checkout (without downloading new Eurostat data):**

```bash
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/run_week5_pipeline.py
```

The runner verifies all archived source SHA-256 values, rebuilds the baseline dataset,
runs original RQ1–RQ4 scripts, generates missingness/flag audits and seven EDA charts,
checks 66 source tokens, performs Week 4 regression diagnostics, runs **exploratory**
country/industry-cluster sensitivities, generates the fourteen-source literature
relevance matrix, and verifies the rebuilt processed CSV checksum. It uses
repository-relative paths throughout. A complete run was verified on
**2026-10-25** using Python 3.13.5, pandas 2.2.3, NumPy 2.3.5,
SciPy 1.17.0, statsmodels 0.14.6 and matplotlib 3.10.8. These are verified
environment versions, not strict minimum requirements.

### Where to find the new evidence

| Output | Directory |
|---|---|
| Data-quality tables and country/RQ coverage | `outputs/tables/week4_eda/` |
| Seven descriptive charts | `outputs/figures/week4_eda/` |
| Regression outputs, diagnostics, tests, RMSE/MAE and power | `outputs/tables/week4_models/` |
| Model residual/fitted and RQ4 fit plots | `outputs/figures/week4_models/` |
| Literature comparison | `outputs/tables/week4_literature/` |
| Frozen-source SHA-256 manifest | `docs/frozen_snapshot_manifest.json` |
| Verification results and interpretation caveats | `docs/week5_reproducibility_validation.md` |

### Statistical interpretation and limitations

- RQ1 matched n=551, RQ2 n=506, RQ3 n=481 and RQ4 n=448. These counts
  **do not represent numbers of individual firms**.
- Model fit/RMSE/MAE are **in-sample**; no out-of-sample forecast validation is claimed.
- RQ4 reduced/full models share the same n=448. The classical joint test is
  significant at .05, but HC3 robust joint inference is not. We report both;
  we do **not** present a definitive significant joint effect.
- Multiway-cluster p-values are diagnostic approximations rather than
  finite-cluster-calibrated confirmatory tests.
- The original archived Eurostat retrieval dates are not contained in the supplied
  files. We do not invent them; 2026-10-25 is the **local verification date**.
- This update does not establish causal effects, independent survey validity,
  firm-level conclusions, or out-of-sample prediction accuracy.

Do **not** run `01_download_data.py` to reproduce a frozen analysis: doing so
would retrieve the latest published Eurostat revision, which could differ from
this archived data. The original 2023/2025 research design is unchanged.
