# Data quality and comparability notes

- Raw Eurostat TSV observation values and their attached status flags are parsed separately.
- `:` is treated as unavailable, never as zero.
- The primary comparability screen excludes numeric observations carrying `b` (break in time series) or `d` (definition differs) in variables needed for the specific RQ.
- Numeric observations carrying `u` (low reliability) are preserved in the primary dataset and remain visibly flagged; sensitivity analysis should assess whether conclusions depend on them.
- Each RQ uses its own complete-case eligibility rule instead of forcing all analyses to the smallest common sample.
- The study uses aggregate country-industry adoption rates. Results must not be interpreted as evidence that the same individual firms using analytics/cloud in 2023 are the firms adopting AI in 2025.
- Eurostat can revise disseminated datasets. The submitted repository should preserve the archived raw files actually used and record the retrieval/submission date.
