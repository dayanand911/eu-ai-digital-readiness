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
│   └── 09_robustness_checks.py
├── outputs/
│   ├── tables/
│   └── figures/
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
The Eurostat TSV status flag is preserved separately from the numeric value. Missing `:` cells are never converted to zero. For the primary comparability screen, observations carrying `b` or `d` on variables required by an RQ are excluded. Numeric `u` observations remain flagged and are intended for sensitivity analysis. See `docs/data_quality_notes.md`.

## Important interpretation limits
The unit of analysis is a **country-industry context**, not an enterprise. Associations in this repository do not establish that individual firms with analytics/cloud in 2023 subsequently adopted AI, and they do not establish causality. The AI technology basket also evolves over time, which is treated as a comparability limitation.

## License and attribution
Code in this repository is released under the MIT License. Eurostat data remain subject to Eurostat/European Commission reuse terms and should be cited to the original source. This repository preserves source identifiers and raw files for academic reproducibility.
