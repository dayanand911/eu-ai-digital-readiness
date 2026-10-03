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
- RQ4: nested OLS. Reduced: `AI2025 ~ AI2023 + country FE + industry FE`. Full adds Analytics2023 and Cloud2023. Primary quantities: delta R-squared, incremental f-squared, and joint contribution of the two capability variables. HC3 is reported; two-way country/industry clustered inference is a planned sensitivity analysis.

## A priori power planning
Alpha = .05 and target power = .80. RQ1 uses dz=.20 and requires approximately 199 matched contexts. RQ2 and RQ3 use f-squared=.02 for one tested predictor and require approximately 395. RQ4 uses fixed-model R-squared increase, two tested predictors and 59 total predictors, requiring approximately 486 under the conventional calculation. Available quality-screened N values are 551, 506, 481 and 448 respectively; the RQ4 limitation is disclosed.
