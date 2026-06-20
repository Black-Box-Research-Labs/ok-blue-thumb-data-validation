# QUICKSTART: Reproducing the Blue Thumb Chloride Manuscript

This repository ships a one-command reproducibility harness for the manuscript
in `paper/main_v2.tex`. There are two tiers:

1. **Fast verification** (about 5 seconds to 1 minute, no raw data needed):
   recompute every headline claim from small committed derived files and fail
   loudly on any mismatch.
2. **Full reproduction from scratch** (longer, needs the source data): rebuild
   the derived files and rerun the full analysis pipeline.

Most readers and reviewers only need Tier 1.

---

## Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The harness needs `statsmodels>=0.14` and `openpyxl>=3.1` in addition to the
core scientific stack; both are in `requirements.txt`.

---

## Tier 1: Fast verification (recommended)

```bash
python verify.py
```

This recomputes all six headline claim groups directly from committed data and
prints a PASS/FAIL table (claim, expected, computed, tolerance, status). It
exits non-zero if any check fails, so it doubles as a CI gate (see
`.github/workflows/ci.yml`).

It reads only files committed to the repository:

| Claim group | Committed input |
|:---|:---|
| Precision (97.3%, 1.53, 2.51, 3.58) | `data/outputs/phase2_lme/replicate_diffs.csv` |
| Accuracy (read high, N=867) | `data/outputs/phase2_lme/historical_qa_results_corrected.csv` |
| Regional GLMM (beta -0.433, p 0.047) | `data/outputs/phase2_lme/lme_analysis_df.csv` |
| Stratified subsampling (~98.6% non-sig) | `data/outputs/phase2_lme/lme_analysis_df.csv` |
| Identifiability (VIF 1.29, 0 overlap) | `data/outputs/phase2_lme/lme_analysis_df.csv` |
| Coverage (93%, 327 sites) | `data/outputs/phase2_lme/coverage_distances.csv` |

No raw ArcGIS export or large processed coordinate CSV is required for Tier 1;
the derived files (`replicate_diffs.csv`, `coverage_distances.csv`) carry the
per-pair and per-site values that `verify.py` re-aggregates.

**Subsampling note.** For speed, `verify.py` runs a seeded 200-draw set of
geographically balanced subsamples (claim 4) and asserts the non-significant
fraction exceeds 0.95. The full 1,000-seed run gives 98.6 percent; reproduce it
with the standalone script in Tier 2.

Expected output footer:

```
ALL CHECKS PASSED (27/27). Every headline claim reproduces from committed data.
```

---

## Tier 2: Full reproduction from scratch

This path rebuilds everything from the source data. It requires the data files
that are gitignored (they are property of the Oklahoma Conservation Commission
and the EPA Water Quality Portal; see Data Availability in the manuscript):

- `data/raw/arcgis_volunteer_chloride.csv` (Blue Thumb titration replicates)
- `data/2.5 QA Data.xlsx` (OCC Rotating Basin QA workbook)
- `data/processed/volunteer_chloride.csv`, `data/processed/professional_chloride.csv`

Steps:

```bash
# 1. Run the ETL pipeline (use cached EPA download; full run re-downloads it)
python -m src.pipeline --skip-extract

# 2. Run the Phase 2 LME / variance-decomposition / accuracy analysis
python scripts/phase2_lme_analysis.py

# 3. Run the full 1,000-seed stratified subsampling (the primary result)
python scripts/stratified_subsampling.py 1000 42

# 4. Regenerate the committed derived files that verify.py consumes
python scripts/generate_verification_data.py

# 5. Re-run the fast verifier to confirm the regenerated files still pass
python verify.py
```

`scripts/generate_verification_data.py` rebuilds `replicate_diffs.csv` and
`coverage_distances.csv` from the raw and processed sources using the exact
logic in `scripts/phase2_lme_analysis.py` (volunteer `|test3 - test5| * 5` mg/L,
professional QA pairs) and `src/analysis.py` (nearest-professional distance,
degree-to-km factor 111.0).

---

## What maps to what

`CLAIMS.md` is the full claim ledger: each headline number, the line in
`paper/main_v2.tex` where it appears, the script and data that regenerate it,
and the `verify.py` check name. Start there if you want to trace a single
number end to end.
