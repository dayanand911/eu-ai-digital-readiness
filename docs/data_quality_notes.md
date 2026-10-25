# Data quality and comparability notes

- Raw Eurostat TSV observation values and their attached status flags are parsed separately.
- `:` is treated as unavailable, never as zero.
- The primary comparability screen excludes numeric observations carrying `b` (break in time series) or `d` (definition differs) in variables needed for the specific RQ.
- Numeric observations carrying `u` (low reliability) are preserved in the primary dataset and remain visibly flagged; sensitivity analysis should assess whether conclusions depend on them.
- Each RQ uses its own complete-case eligibility rule instead of forcing all analyses to the smallest common sample.
- The study uses aggregate country-industry adoption rates. Results must not be interpreted as evidence that the same individual firms using analytics/cloud in 2023 are the firms adopting AI in 2025.
- Eurostat can revise disseminated datasets. The submitted repository should preserve the archived raw files actually used and record the retrieval/submission date.


## Reproduced Week 4 completeness audit (833 observed contexts)

| Indicator | Numeric | Unavailable | Numeric `b`/`d` excluded | Eligible numeric |
|---|---:|---:|---:|---:|
| 2023 AI | 665 | 168 | 59 | 606 |
| 2025 AI | 652 | 181 | 1 | 651 |
| 2023 analytics | 649 | 184 | 30 | 619 |
| 2025 analytics | 651 | 182 | 31 | 620 |
| 2023 paid cloud | 568 | 265 | 53 | 515 |
| 2025 paid cloud | 607 | 226 | 1 | 606 |

Numeric comparability exclusions are a *subset* of the numeric column; do not
add them to unavailable counts. There are four missing combinations among the
27×31=837 theoretical source-frame keys. The merged archived file has 833 keys,
zero duplicate country–industry pairs, and zero numeric rates outside 0–100.
The strict RQ samples represent 25/24/25/24 countries respectively, not a
complete 27-country sample in every RQ. France and Sweden are absent in all
primary complete-case samples; Czechia is also absent in RQ2/RQ4.

No numeric `u`-flagged cells occur in the archived six-indicator extract.
Flag rules are applied only to the variables required by each RQ.
The raw-to-processed script checks 66 country–industry/year/source numeric
values/flags against their archived Eurostat source tokens.
