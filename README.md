# Blue Thumb Chloride Validation Pipeline

> **Principal Investigator:** Miguel Ingram (Black Box Research Labs LLC)
> **Institutional Partner:** Oklahoma Conservation Commission (OCC) — Blue Thumb Program

Statistical validation of Oklahoma Blue Thumb citizen science chloride data against professional monitoring data from the EPA Water Quality Portal, using spatial-temporal matching (Virtual Triangulation) and a linear mixed-effects model.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Primary Result — Linear Mixed-Effects Model (Phase 2)

GLMM: `log(Chloride) ~ IsVolunteer + sin(2πt/365) + cos(2πt/365) + Longitude + (1|Site)`

| Fixed Effect | Estimate (β) | SE | p-value |
|:---|:---|:---|:---|
| **IsVolunteer** | **-0.433** | **0.218** | **0.047** |
| Longitude | -0.435 | 0.078 | < 0.001 |
| Seasonal (sin) | +0.110 | 0.023 | < 0.001 |
| Intercept | -37.663 | 7.640 | < 0.001 |

**Interpretation:** After controlling for geographic position and seasonal variation, volunteer measurements are statistically consistent with professional reference sensors at the landscape scale (p = 0.047). The IsVolunteer fixed effect is small relative to natural spatial and seasonal variation.

Model fit: 25 matched pairs, 14 unique sites, site-level random intercept. Full output: `data/outputs/phase2_lme/phase2_lme_results.txt`.

---

## OLS Summary (Supplementary)

| Metric | Vol-to-Pro (Phase 2) | Pro-to-Pro (Baseline) |
|:---|:---|:---|
| **Sample Size** | N = 25 | N = 42 |
| **R²** | 0.607 (p < 0.0001) | 0.753 (p < 0.0001) |
| **Slope** | 0.813 | 0.735 |
| **Unique Test Sites** | 4 | 11 |
| **Matching Window** | 125 m / 72 h | 125 m / 72 h |

> **Method verification pending:** CNENVSER (Chickasaw Nation Environmental Services) accounts for 18 of 25 vol-to-pro matches (72%). Their analytical method is unrecorded in WQP. OWRB uses EPA 325.2 (Automated Colorimetry) for the remaining 7 matches. See `docs/Volunteer_Chloride_Validation_METHODS.md`.

---

## Quick Start

```bash
git clone https://github.com/Black-Box-Research-Labs/ok-blue-thumb-data-validation.git
cd ok-blue-thumb-data-validation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full OLS pipeline
python -m src.pipeline                   # Full run (downloads EPA data)
python -m src.pipeline --skip-extract    # Uses cached EPA data

# Run Phase 2 LME analysis (requires pipeline outputs)
python scripts/phase2_lme_analysis.py

# Step-by-step
python -m src.extract       # Download from EPA WQP (~5-10 min)
python -m src.transform     # Clean, separate, load Blue Thumb CSV (~2 min)
python -m src.analysis      # Dual matching: pro-to-pro + vol-to-pro (<1 min)
python -m src.visualize     # Generate validation plots (<1 min)

# Verify
pytest tests/test_pipeline.py -v
```

---

## Data Sources

| Source | Type | Access |
|:---|:---|:---|
| **EPA Water Quality Portal** | Professional chloride measurements | Public API (`waterqualitydata.us`) |
| **Blue Thumb CSV** | Volunteer chloride measurements | [OCC R-Shiny app](https://occwaterquality.shinyapps.io/OCC-app23a/) (SHA-256 verified at runtime) |

### Professional Organizations in Matched Pairs

- **CNENVSER** (Chickasaw Nation Environmental Services): 18 of 25 vol-to-pro matches — analytical method unrecorded in WQP (P0 verification pending)
- **OKWRB-STREAMS_WQX** (Oklahoma Water Resources Board): 7 of 25 vol-to-pro matches — EPA 325.2

---

## Methodology

### Virtual Triangulation

Matches volunteer and professional measurements using:

1. **Spatial proximity:** ≤ 125 meters (Haversine great-circle distance, `scipy.spatial.cKDTree`)
2. **Temporal proximity:** ≤ 72 hours (absolute time difference)
3. **Strategy:** Closest spatial match per volunteer measurement
4. **Concentration filter:** Professional values > 25 mg/L (chloride)

Two comparisons run with identical parameters:
- **Vol-to-Pro:** Blue Thumb volunteers vs. professional reference (OKWRB, CNENVSER)
- **Pro-to-Pro:** OCC Rotating Basin (`OKCONCOM_WQX`, Method 9056) vs. same professional reference

### Linear Mixed-Effects Model

Applied to the 25 confirmed vol-to-pro matched pairs. Random intercept by site accounts for unmeasured site-level differences. Seasonal harmonics (sin/cos) capture annual periodicity. Longitude controls for east-west chloride gradient across Oklahoma. Deming regression used as robustness check (accounts for measurement error in both variables).

All parameters in `config/config.yaml`. Full methods: `docs/Volunteer_Chloride_Validation_METHODS.md`.

---

## Repository Structure

```
bluestream-test/
├── README.md
├── requirements.txt
├── config/
│   └── config.yaml                    # All parameters (125m/72h/closest)
├── src/
│   ├── pipeline.py                    # Single entry point
│   ├── extract.py                     # EPA WQP download
│   ├── transform.py                   # Data cleaning + Blue Thumb CSV override
│   ├── analysis.py                    # cKDTree spatial-temporal matching
│   └── visualize.py                   # Validation plots
├── scripts/
│   ├── phase2_lme_analysis.py         # Primary Phase 2 LME/GLMM analysis
│   ├── diagnose_matches.py            # Matched pair diagnostics
│   ├── verify_arcgis_sync.py          # ArcGIS FeatureServer verification
│   └── arcgis_qaqc_audit.py           # QAQC audit utilities
├── tests/
│   └── test_pipeline.py               # 12 assertions (Phase 2 targets)
└── docs/
    ├── Volunteer_Chloride_Validation_METHODS.md
    ├── PAPER_OUTLINE.md
    ├── BUILD_GUIDE.md
    └── TEACHER_VERSION_BLUETHUMB_ETL_BUILD_GUIDE.md
```

### Key Outputs (gitignored, regenerated by pipeline)

- `data/outputs/matched_pairs.csv` — Vol-to-pro matches (N=25)
- `data/outputs/matched_pairs_pro_to_pro.csv` — Pro-to-pro baseline (N=42)
- `data/outputs/vol_to_pro_validation_plot.png` — OLS validation plot
- `data/outputs/summary_statistics_vol_to_pro.txt` — Per-org breakdown with method provenance
- `data/outputs/metadata.json` — Reproducibility manifest (git commit, config hash, CSV hash)
- `data/outputs/phase2_lme/phase2_lme_results.txt` — Full GLMM output with SE values
- `data/outputs/phase2_lme/lme_diagnostics.png` — Residual diagnostics
- `data/outputs/phase2_lme/matched_pairs_analysis.png` — Phase 2 matched pairs visualization

---

## Phase 1 History

An initial analysis (N=48, R²=0.839, 100m/48h/all) was completed in January 2026 using `OKCONCOM_WQX` data from the EPA WQP as "volunteer" data. On January 21, 2026, OCC's Kim Shaw clarified that `OKCONCOM_WQX` contains OCC Rotating Basin professional data (Method 9056), not Blue Thumb volunteers. Phase 2 corrects this by sourcing volunteer data from a separate Blue Thumb CSV export, verified against OCC's ArcGIS FeatureServer.

Phase 1 results are preserved in git history. The Rotating Basin data is now used as the pro-to-pro baseline comparison.

---

## License

MIT License — See `LICENSE` file
