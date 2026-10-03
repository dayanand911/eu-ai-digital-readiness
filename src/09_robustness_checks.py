"""Planned robustness checks.

Primary synopsis commitments:
1. Preserve Eurostat flags and compare the primary b/d-screened analysis with broader defensible numeric samples.
2. Use HC3 heteroskedasticity-robust covariance for regression inference.
3. Examine country/industry dependence with multiway cluster-robust inference where supported by the analysis environment.
4. Inspect residuals, leverage/Cook's distance, VIF and fitted-value bounds.
5. For RQ1, supplement the paired t-test with Wilcoxon signed-rank inference if the paired-difference distribution is seriously problematic.

This file intentionally does not hard-code a significance-seeking fallback. Any additional specification must be documented before interpreting results.
"""
print(__doc__)
