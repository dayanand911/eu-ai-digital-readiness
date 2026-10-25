# Methodology

## Design
Quantitative observational two-wave analysis of matched EU Member State × NACE Rev. 2 industry contexts in 2023 and 2025. The study is contextual, not firm-level, and does not make causal claims.

## Research questions
1. What was the magnitude and distribution of change in enterprise AI adoption between 2023 and 2025 across matched EU country-industry contexts?
2. To what extent is data-analytics adoption in 2023 associated with enterprise AI adoption in 2025, after accounting for AI adoption in 2023?
3. To what extent is cloud-computing adoption in 2023 associated with enterprise AI adoption in 2025, after accounting for AI adoption in 2023?
4. To what extent do 2023 analytics and cloud adoption provide additional explanatory power for 2025 AI adoption beyond 2023 AI adoption and country and industry differences?

## Primary analyses
- RQ1: paired change analysis; paired t-test, 95% CI and paired standardized effect size (dz). Wilcoxon signed-rank is a robustness check if warranted.
- RQ2: OLS, `AI2025 ~ AI2023 + Analytics2023`, with HC3 robust inference.
- RQ3: OLS, `AI2025 ~ AI2023 + Cloud2023`, with HC3 robust inference.
- RQ4: nested OLS. Reduced: `AI2025 ~ AI2023 + country FE + industry FE`. Full adds Analytics2023 and Cloud2023. Primary quantities: delta R-squared, incremental f-squared, and joint contribution of the two capability variables. HC3 is reported; two-way country/industry clustered inference is computed as an exploratory sensitivity; finite-cluster calibration is not claimed.

## A priori power planning
Alpha = .05 and target power = .80. RQ1 uses dz=.20 and requires approximately 199 matched contexts. RQ2 and RQ3 use f-squared=.02 for one tested predictor and require approximately 395. RQ4 uses fixed-model R-squared increase, two tested predictors and 59 total predictors, requiring approximately 486 under the conventional calculation. Available quality-screened N values are 551, 506, 481 and 448 respectively; the RQ4 limitation is disclosed.


## Methods executed by Week 5 interim integration

- The baseline Eurostat source, industry selection, variables, and primary RQs
  remain exactly as defined above.
- EDA includes source completeness, numeric/flag status, country/RQ eligibility,
  paired AI change, country and industry context averages and unadjusted
  analytics/cloud correlations. Extreme observations were audited and retained
  in primary results; exclusions are only descriptive sensitivities.
- RQ1's paired t-test is supplemented by a Wilcoxon signed-rank test.
- RQ2/RQ3 include HC3 inference, R-squared, adjusted R-squared,
  in-sample RMSE/MAE, fitted/residual diagnostics, influence and
  heteroskedasticity screening.
- RQ4 compares reduced and full OLS fits on the **same 448 contexts**, with
  baseline AI and country/industry fixed effects retained. Added analytics/cloud
  explain ΔR² ≈ .00344. HC3 robust joint Wald p ≈ .1406, while the classical
  homoskedastic F-test gives p ≈ .0021; heteroskedasticity makes it important
  not to select the favorable classical result uncritically.
- The observed RQ4 fit contains 56 slopes, not the original 59 planning slopes,
  but the conventional small-effect required-N calculation remains 486.
- Eleven fitted RQ4 values fall outside 0–100, suggesting a bounded-outcome
  sensitivity could be worthwhile. No claim that such a model has been estimated
  is made here.
- All figures and coefficient/error metrics are derived from frozen archived
  percentages. Correlation is not a causal estimate. Unweighted context averages
  must not be presented as the official enterprise-weighted Eurostat EU rate.

See `docs/week5_reproducibility_validation.md` and the structured CSV tables for
actual outputs and limitations. Only statistical procedures present in runnable
source scripts are described as executed.
