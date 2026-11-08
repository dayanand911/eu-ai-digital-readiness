# Week 6 supplementary verification and held-out evaluation

Date: 8 November 2026. Input: user-provided GitHub repository ZIP, not a fresh clone of a named remote commit. No live Eurostat download was performed.

## Archived pipeline verification

Executed `python src/run_week5_pipeline.py` from a clean extracted copy using Python 3.13.5. All three `data/raw` files matched the SHA-256 entries in `docs/frozen_snapshot_manifest.json`, and the rebuilt processed CSV matched the expected SHA-256. Rebuilt processed file: 833 rows and 19 columns. Complete-case sample sizes: RQ1 551, RQ2 506, RQ3 481, RQ4 448.

Selected reproduced findings: RQ1 mean paired adoption change +12.487459 pp; RQ2 analytics coefficient 0.086878657 (HC3 p=.055998079); RQ3 cloud coefficient 0.230689402 (HC3 p=3.498929e-10); RQ4 reduced/full R-squared .889144067/.892587647; RQ4 classical joint p=.002092808 versus HC3 joint p=.140601168. RQ4 diagnostics and exploratory clustering were also regenerated. These statistics relate to equal-weight country-industry contexts, not individual enterprises and not causal treatment effects.

## New five-fold RQ4 evaluation

Executed `python src/13_rq4_independent_validation.py` on 448 eligible contexts. Primary validation is `KFold(n_splits=5, shuffle=True, random_state=42)` and holds out each entire country-industry *row*. Both specifications receive identical folds. One-hot categorical encoding (`drop='first'`, `handle_unknown='ignore'`) and linear regression are fit only on the training rows. Numeric features are passed through unscaled. The reduced model includes baseline AI and country/industry effects; the full adds baseline analytics and paid cloud. Results are means and sample standard deviations of the five fold-specific errors.

| Specification | Fold mean RMSE (pp) | SD | Fold mean MAE (pp) | SD |
|---|---:|---:|---:|---:|
| Reduced | 6.818514 | 1.158919 | 4.862946 | 0.491382 |
| Full | 6.868712 | 1.009823 | 4.890410 | 0.422578 |

Additional **non-comparable stress test**: five-fold leave-groups-of-countries-out using GroupKFold. Mean RMSE reduced 14.884515 pp; full 15.896740 pp. Country fixed effects for previously unseen countries are not estimable from training data; one-hot unseen-country handling is a pragmatic coding convention, not scientific identification of a new country's fixed effect. Thus the country-holdout results are a warning about transportability, not a direct alternative ranking.

Files in `outputs/tables/week6_validation/` include fold assignments, fold-level metrics, all held-out predictions, and protocol metadata. The documented KFold random seed reproduces the same folds on the archived processed dataset. `scikit-learn>=1.4,<2` was added to `requirements.txt` for this new optional script.

## Important limitations

1. Five shuffled folds retain countries and industries across training and validation; correlated errors may make performance optimistic for a new country.
2. Independent Eurostat source-survey error and enterprise denominators are not available in this processed file.
3. The previously mentioned 6.695/6.777 RMSE values were not reproduced because their fold definitions and implementation were not preserved. The results above replace them for reproducible reporting.
4. Archived source retrieval timestamps and the original workstation CPU/GPU configuration are unknown. The verification ran on a CPU-only Linux environment reporting an AMD EPYC 9V74 processor; that is not a claim about the original workstation.
5. Uploading this package to GitHub and the college's similarity review are separate actions not performed here.
