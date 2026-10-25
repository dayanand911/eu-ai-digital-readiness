# Week 5 consolidated repository — local verification report

**Verification date:** 2026-10-25. **Source:** user-uploaded ZIP of the public
`eu-ai-digital-readiness` repository; combined with separately verified Week 4
Step 2 and Step 3 working packages. **Live GitHub:** not yet updated by this work.

## Clean-copy reproduction

The independent runner `python src/run_week5_pipeline.py` was executed against a
separate cloned folder and completed successfully. The archived raw file hashes,
re-generated processed CSV SHA-256, source spot-checks, all baseline RQ scripts,
Week 4 EDA scripts, and Week 4 extended model checks passed.

- Frozen merged dataset: **833 rows × 19 columns**, no duplicate keys.
- Quality-screened n: **RQ1 551, RQ2 506, RQ3 481, RQ4 448**.
- Original 7 CSV results reproduced **byte-for-byte** against the user-uploaded
  GitHub ZIP.
- New audit/model CSVs numerically matched the supplied Week 4 working outputs.
- EDA generates **7 PNG charts** and completes **66 raw-token checks**.
- Statistical diagnostics generate residual plots, same-sample RQ4 comparison,
  Breusch–Pagan checks, HC3 and exploratory two-way clustering evidence.
- The fourteen-source literature relevance matrix was generated from the
  previously compiled references. This run validates file generation, **not**
  external publisher metadata or bibliography accuracy anew.

## Primary interim results reproduced

| Question | Verified result | Interpretation boundary |
|---|---|---|
| RQ1 | +12.4875 percentage points; n=551 | Equal-weight matched contexts, not EU total |
| RQ2 | beta=0.0869, HC3 p=0.0560; n=506 | Positive but not significant at .05 |
| RQ3 | beta=0.2307, HC3 p=3.5e-10; n=481 | Positive baseline-adjusted association, not causation |
| RQ4 | reduced R²=0.8891, full R²=0.8926, delta=0.00344 | Small in-sample fit gain |
| RQ4 joint | classical p=0.0021, HC3 p=0.1406 | Joint robustness disagreement disclosed |

## Outstanding methodological and operational cautions

1. The 2023 and 2025 Eurostat AI measurement basket may not be invariant.
2. Complete-case model coverage excludes some member states; results do not
   represent an equally weighted full EU27 sample or any individual enterprise.
3. The RQ4 planned 80% small-effect benchmark n=486 exceeds available n=448.
4. RQ4 contains heteroskedasticity, material fixed-effects VIFs and 11 fitted
   values outside 0–100. A bounded-response sensitivity is **not yet run**.
5. Exploratory clustered inference is **not** a calibrated finite-cluster test.
6. All RMSE/MAE values are in-sample; no cross-validation is reported.
7. This archive is a **local candidate for GitHub upload**. Publication and an
   independent post-upload clean checkout are **not yet confirmed**.

## Original files retained

All three archived compressed Eurostat raw datasets, the processed CSV and
these seven original output CSVs remain unchanged:

- `rq1_descriptive_summary.csv`
- `rq1_paired_change.csv`
- `rq2_analytics_model_hc3.csv`
- `rq3_cloud_model_hc3.csv`
- `rq4_full_model_hc3.csv`
- `rq4_nested_model_summary.csv`
- `sample_counts.csv`
