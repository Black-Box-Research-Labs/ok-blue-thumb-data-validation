#!/usr/bin/env python3
"""
Phase 2 Linear Mixed-Effects Analysis: Volunteer vs Professional Chloride
=========================================================================
Implements Joseph Dyer's recommended statistical framework from the Feb 20, 2026 meeting:
  - Variance decomposition (within-test, within-site, cross-method)
  - Linear Mixed-Effects Model: Chloride ~ ObserverType + sin(Julian) + cos(Julian) + Longitude + (1|Site)
  - Quantization effect visualization
  - Diagnostic plots

Data sources:
  - Joey's QA data: data/2.5 QA Data.xlsx (OCC Rotating Basin QA, Method 9056)
  - ArcGIS volunteer: data/raw/arcgis_volunteer_chloride.csv (Blue Thumb titration replicates)
  - Processed volunteer: data/processed/volunteer_chloride.csv
  - Processed professional: data/processed/professional_chloride.csv
  - Phase 1 matched pairs: data/outputs/matched_pairs_vol_to_pro.csv

Output: data/outputs/phase2_lme/
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from datetime import datetime
import json
import hashlib

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "outputs" / "phase2_lme"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# QA data temporal/spatial window (from Joey's dataset)
QA_DATE_MIN = pd.Timestamp("2022-07-18")
QA_DATE_MAX = pd.Timestamp("2024-05-21")
QA_LON_MIN = -99.23
QA_LON_MAX = -96.51
QA_LAT_MIN = 35.83
QA_LAT_MAX = 36.82

# Spatial buffer for matching volunteer data to QA region (degrees)
SPATIAL_BUFFER = 1.0

# ---------------------------------------------------------------------------
# 1. Load and prepare all data sources
# ---------------------------------------------------------------------------
def load_qa_data():
    """Load Joey's QA dataset."""
    df = pd.read_excel(DATA_DIR / "2.5 QA Data.xlsx", sheet_name="2_5 QA Data")
    df["Chloride"] = pd.to_numeric(df["Chloride"], errors="coerce")
    df["DateActivityStart"] = pd.to_datetime(df["DateActivityStart"])
    df = df[df["Chloride"].notna()].copy()
    print(f"  QA data: {len(df)} chloride rows, {df['WBID'].nunique()} sites, "
          f"{df['Type'].value_counts().to_dict()}")
    return df


def load_arcgis_replicates():
    """Load ArcGIS volunteer data with replicate drop counts."""
    df = pd.read_csv(DATA_DIR / "raw" / "arcgis_volunteer_chloride.csv")
    df["day"] = pd.to_datetime(df["day"])
    for c in ["chloridetest1", "chloridetest3", "chloridetest5", "Chloride_Low1_Final"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["chloridetest3", "chloridetest5", "Chloride_Low1_Final"])
    print(f"  ArcGIS replicates: {len(df)} rows, {df['WBIDName'].nunique()} sites")
    return df


def load_volunteer_data():
    """Load processed volunteer chloride data."""
    df = pd.read_csv(DATA_DIR / "processed" / "volunteer_chloride.csv")
    df["ActivityStartDate"] = pd.to_datetime(df["ActivityStartDate"])
    print(f"  Volunteer data: {len(df)} rows, "
          f"{df['MonitoringLocationIdentifier'].nunique()} sites")
    return df


def load_professional_qa_routine(qa_df):
    """Extract Routine Sample records from QA data as professional reference."""
    routine = qa_df[qa_df["Type"] == "Routine Sample"].copy()
    routine = routine.rename(columns={
        "WBID": "Site",
        "DateActivityStart": "Date",
        "Chloride": "Chloride_mgL",
    })
    routine["ObserverType"] = "Professional"
    routine["Longitude"] = routine["Longitude"]
    routine["Latitude"] = routine["Latitude"]
    routine = routine[["Site", "Date", "Chloride_mgL", "ObserverType",
                        "Longitude", "Latitude"]].copy()
    return routine


def load_volunteer_for_lme(vol_df):
    """Filter volunteer data to QA region and time window for LME analysis."""
    mask = (
        (vol_df["ActivityStartDate"] >= QA_DATE_MIN) &
        (vol_df["ActivityStartDate"] <= QA_DATE_MAX) &
        (vol_df["LongitudeMeasure"] >= QA_LON_MIN - SPATIAL_BUFFER) &
        (vol_df["LongitudeMeasure"] <= QA_LON_MAX + SPATIAL_BUFFER) &
        (vol_df["LatitudeMeasure"] >= QA_LAT_MIN - SPATIAL_BUFFER) &
        (vol_df["LatitudeMeasure"] <= QA_LAT_MAX + SPATIAL_BUFFER)
    )
    sub = vol_df[mask].copy()
    sub = sub.rename(columns={
        "MonitoringLocationIdentifier": "Site",
        "ActivityStartDate": "Date",
        "ResultMeasureValue": "Chloride_mgL",
        "LongitudeMeasure": "Longitude",
        "LatitudeMeasure": "Latitude",
    })
    sub["ObserverType"] = "Volunteer"
    sub = sub[["Site", "Date", "Chloride_mgL", "ObserverType",
               "Longitude", "Latitude"]].copy()
    print(f"  Volunteer in QA window: {len(sub)} rows, {sub['Site'].nunique()} sites")
    return sub


def add_julian_covariates(df):
    """Add sine/cosine Julian date covariates for seasonality."""
    julian = df["Date"].dt.dayofyear
    df["JulianSin"] = np.sin(2 * np.pi * julian / 365.25)
    df["JulianCos"] = np.cos(2 * np.pi * julian / 365.25)
    return df


def build_lme_dataframe(qa_df, vol_df):
    """Build the unified analysis dataframe for the LME model."""
    pro = load_professional_qa_routine(qa_df)
    vol = load_volunteer_for_lme(vol_df)
    combined = pd.concat([pro, vol], ignore_index=True)
    combined = combined.dropna(subset=["Chloride_mgL", "Longitude", "Date"])
    combined = combined[combined["Chloride_mgL"] > 0].copy()
    combined = add_julian_covariates(combined)
    print(f"\n  LME dataframe: {len(combined)} rows, {combined['Site'].nunique()} sites")
    print(f"    Professional: {(combined['ObserverType']=='Professional').sum()} rows, "
          f"{combined[combined['ObserverType']=='Professional']['Site'].nunique()} sites")
    print(f"    Volunteer:    {(combined['ObserverType']=='Volunteer').sum()} rows, "
          f"{combined[combined['ObserverType']=='Volunteer']['Site'].nunique()} sites")
    return combined


# ---------------------------------------------------------------------------
# 2. Variance Decomposition
# ---------------------------------------------------------------------------
def variance_decomposition(qa_df, arcgis_df):
    """Compute variance components for professional and volunteer methods."""
    print("\n" + "=" * 60)
    print("VARIANCE DECOMPOSITION")
    print("=" * 60)

    results = {}

    # --- Professional within-test (Routine vs Duplicate) ---
    routine = qa_df[qa_df["Type"] == "Routine Sample"].set_index(
        ["WBID", "DateActivityStart"])["Chloride"]
    duplicate = qa_df[qa_df["Type"] == "Field Duplicate"].set_index(
        ["WBID", "DateActivityStart"])["Chloride"]
    rd = pd.DataFrame({"routine": routine, "duplicate": duplicate}).dropna()
    rd["abs_diff"] = (rd["routine"] - rd["duplicate"]).abs()
    rd["rpd"] = 200 * rd["abs_diff"] / (rd["routine"] + rd["duplicate"])

    results["pro_within_test"] = {
        "label": "Professional Within-Test\n(Churn Splitter Duplicates)",
        "n": len(rd),
        "mean_abs_diff": rd["abs_diff"].mean(),
        "median_abs_diff": rd["abs_diff"].median(),
        "sd_diff": (rd["routine"] - rd["duplicate"]).std(),
        "mean_rpd": rd["rpd"].mean(),
        "ci_95": 1.96 * rd["abs_diff"].std() / np.sqrt(len(rd)),
    }
    print(f"\n  Professional Within-Test (Routine vs Duplicate, N={len(rd)}):")
    print(f"    Mean |diff| = {rd['abs_diff'].mean():.2f} ± "
          f"{results['pro_within_test']['ci_95']:.2f} mg/L")
    print(f"    RPD = {rd['rpd'].mean():.1f}%")

    # --- Professional within-site (Routine vs Replicate, ~100m apart) ---
    replicate = qa_df[qa_df["Type"] == "Field Replicate"].set_index(
        ["WBID", "DateActivityStart"])["Chloride"]
    rr = pd.DataFrame({"routine": routine, "replicate": replicate}).dropna()
    rr["abs_diff"] = (rr["routine"] - rr["replicate"]).abs()
    rr["rpd"] = 200 * rr["abs_diff"] / (rr["routine"] + rr["replicate"])

    results["pro_within_site"] = {
        "label": "Professional Within-Site\n(Spatial Replicates, ~100m)",
        "n": len(rr),
        "mean_abs_diff": rr["abs_diff"].mean(),
        "median_abs_diff": rr["abs_diff"].median(),
        "sd_diff": (rr["routine"] - rr["replicate"]).std(),
        "mean_rpd": rr["rpd"].mean(),
        "ci_95": 1.96 * rr["abs_diff"].std() / np.sqrt(len(rr)),
    }
    print(f"\n  Professional Within-Site (Routine vs Replicate, N={len(rr)}):")
    print(f"    Mean |diff| = {rr['abs_diff'].mean():.2f} ± "
          f"{results['pro_within_site']['ci_95']:.2f} mg/L")
    print(f"    RPD = {rr['rpd'].mean():.1f}%")

    # --- Volunteer within-test (test3 vs test5, titration replicates) ---
    a = arcgis_df.copy()
    a["drop_diff"] = (a["chloridetest3"] - a["chloridetest5"]).abs()
    a["mg_diff"] = a["drop_diff"] * 5
    # RPD only where different
    a_diff = a[a["drop_diff"] > 0].copy()
    a_diff["rpd"] = 200 * a_diff["drop_diff"] / (
        a_diff["chloridetest3"] + a_diff["chloridetest5"])

    results["vol_within_test"] = {
        "label": "Volunteer Within-Test\n(Titration Replicates)",
        "n": len(a),
        "mean_abs_diff": a["mg_diff"].mean(),
        "median_abs_diff": a["mg_diff"].median(),
        "sd_diff": a["mg_diff"].std(),
        "pct_identical": 100 * (a["drop_diff"] == 0).mean(),
        "pct_1drop": 100 * (a["drop_diff"] == 1).mean(),
        "pct_2plus": 100 * (a["drop_diff"] >= 2).mean(),
        "mean_rpd_when_different": a_diff["rpd"].mean() if len(a_diff) > 0 else 0,
        "ci_95": 1.96 * a["mg_diff"].std() / np.sqrt(len(a)),
    }
    print(f"\n  Volunteer Within-Test (test3 vs test5, N={len(a)}):")
    print(f"    Mean |diff| = {a['mg_diff'].mean():.2f} ± "
          f"{results['vol_within_test']['ci_95']:.2f} mg/L")
    print(f"    Identical: {results['vol_within_test']['pct_identical']:.1f}%")
    print(f"    Differ by 1 drop: {results['vol_within_test']['pct_1drop']:.1f}%")
    print(f"    Differ by 2+ drops: {results['vol_within_test']['pct_2plus']:.1f}%")

    # --- Field Blanks ---
    blanks = qa_df[qa_df["Type"] == "Field Blank"]["Chloride"]
    results["field_blanks"] = {
        "n": len(blanks),
        "values": sorted(blanks.unique().tolist()),
        "all_below_detection": (blanks <= 0.5).all(),
    }
    print(f"\n  Field Blanks (N={len(blanks)}): all={blanks.unique()}, "
          f"below detection={results['field_blanks']['all_below_detection']}")

    return results, rd, rr, a


def plot_variance_decomposition(results):
    """Create variance decomposition comparison figure."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Panel A: Mean Absolute Difference ---
    ax = axes[0]
    categories = ["vol_within_test", "pro_within_test", "pro_within_site"]
    labels = [results[c]["label"] for c in categories]
    means = [results[c]["mean_abs_diff"] for c in categories]
    cis = [results[c]["ci_95"] for c in categories]
    ns = [results[c]["n"] for c in categories]
    colors = ["#2196F3", "#4CAF50", "#FF9800"]

    bars = ax.barh(range(len(categories)), means, xerr=cis, height=0.5,
                   color=colors, edgecolor="black", linewidth=0.5, capsize=5)
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Mean Absolute Difference (mg/L)", fontsize=11)
    ax.set_title("A. Within-Method Repeatability", fontsize=13, fontweight="bold")
    ax.invert_yaxis()

    for i, (mean, n) in enumerate(zip(means, ns)):
        ax.text(mean + cis[i] + 0.15, i, f"{mean:.1f} mg/L\n(N={n:,})",
                va="center", fontsize=9)

    ax.set_xlim(0, max(means) + max(cis) + 2.5)
    ax.axvline(x=0, color="black", linewidth=0.5)

    # --- Panel B: Volunteer drop-count distribution ---
    ax2 = axes[1]
    pct_ident = results["vol_within_test"]["pct_identical"]
    pct_1 = results["vol_within_test"]["pct_1drop"]
    pct_2 = results["vol_within_test"]["pct_2plus"]

    wedges = [pct_ident, pct_1, pct_2]
    wedge_labels = [
        f"Identical\n{pct_ident:.1f}%",
        f"±1 drop (±5 mg/L)\n{pct_1:.1f}%",
        f"±2+ drops (±10+ mg/L)\n{pct_2:.1f}%",
    ]
    wedge_colors = ["#C8E6C9", "#FFF9C4", "#FFCDD2"]
    ax2.pie(wedges, labels=wedge_labels, colors=wedge_colors,
            startangle=90, textprops={"fontsize": 10},
            wedgeprops={"edgecolor": "black", "linewidth": 0.5})
    ax2.set_title(f"B. Volunteer Titration Agreement\n(N={results['vol_within_test']['n']:,} paired readings)",
                  fontsize=13, fontweight="bold")

    fig.suptitle("Variance Decomposition: Professional QA vs Volunteer Replicates",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = OUTPUT_DIR / "variance_decomposition.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# 3. Linear Mixed-Effects Model
# ---------------------------------------------------------------------------
def fit_lme_model(lme_df):
    """
    Fit: Chloride_mgL ~ ObserverType + JulianSin + JulianCos + Longitude + (1|Site)

    The p-value on ObserverType answers:
      "After controlling for season and geography, is there a significant
       difference between volunteer and professional chloride readings?"
    """
    import statsmodels.formula.api as smf

    print("\n" + "=" * 60)
    print("LINEAR MIXED-EFFECTS MODEL")
    print("=" * 60)

    # Encode ObserverType as numeric for cleaner output
    lme_df = lme_df.copy()
    lme_df["IsVolunteer"] = (lme_df["ObserverType"] == "Volunteer").astype(int)

    # Log-transform chloride to normalize residuals (chloride is right-skewed)
    lme_df["LogChloride"] = np.log(lme_df["Chloride_mgL"])

    print(f"\n  Model: LogChloride ~ IsVolunteer + JulianSin + JulianCos + Longitude")
    print(f"  Random effect: (1|Site)")
    print(f"  N = {len(lme_df)}, Sites = {lme_df['Site'].nunique()}")
    print(f"  Professional records: {(lme_df['IsVolunteer']==0).sum()}")
    print(f"  Volunteer records: {(lme_df['IsVolunteer']==1).sum()}")

    # Fit the model
    model = smf.mixedlm(
        "LogChloride ~ IsVolunteer + JulianSin + JulianCos + Longitude",
        data=lme_df,
        groups=lme_df["Site"],
    )
    result = model.fit(reml=True)

    print("\n" + str(result.summary()))

    # Extract key results
    observer_coef = result.fe_params.get("IsVolunteer", None)
    observer_pval = result.pvalues.get("IsVolunteer", None)
    observer_ci = result.conf_int().loc["IsVolunteer"] if "IsVolunteer" in result.conf_int().index else None

    print("\n  KEY RESULTS:")
    print(f"    IsVolunteer coefficient: {observer_coef:.4f}")
    print(f"    IsVolunteer p-value:     {observer_pval:.6f}")
    if observer_ci is not None:
        print(f"    IsVolunteer 95% CI:      [{observer_ci.iloc[0]:.4f}, {observer_ci.iloc[1]:.4f}]")

    # Back-transform coefficient to multiplicative factor
    mult_factor = np.exp(observer_coef)
    print(f"\n    Interpretation: Volunteer readings are {mult_factor:.3f}x professional")
    print(f"    ({(mult_factor-1)*100:+.1f}% {'higher' if mult_factor > 1 else 'lower'} on average)")

    if observer_pval > 0.05:
        print(f"\n    ✅ NOT SIGNIFICANT (p={observer_pval:.4f} > 0.05)")
        print(f"    → Volunteer and professional readings are statistically")
        print(f"      indistinguishable after controlling for season and geography.")
    else:
        print(f"\n    ⚠️ SIGNIFICANT (p={observer_pval:.6f} < 0.05)")
        print(f"    → There is a detectable systematic difference between")
        print(f"      volunteer and professional readings.")

    # Random effects variance
    re_var = result.cov_re.iloc[0, 0]
    print(f"\n    Site random effect variance: {re_var:.4f}")
    print(f"    Site random effect SD:       {np.sqrt(re_var):.4f}")
    print(f"    (On log scale — captures between-site chloride variation)")

    return result, lme_df


def plot_lme_diagnostics(result, lme_df):
    """Create diagnostic plots for the LME model."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    residuals = result.resid
    fitted = result.fittedvalues

    # --- Panel A: Residuals vs Fitted ---
    ax = axes[0, 0]
    colors = ["#2196F3" if v == 1 else "#4CAF50"
              for v in lme_df["IsVolunteer"]]
    ax.scatter(fitted, residuals, c=colors, alpha=0.4, s=15, edgecolors="none")
    ax.axhline(y=0, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Fitted Values (log mg/L)")
    ax.set_ylabel("Residuals")
    ax.set_title("A. Residuals vs Fitted", fontweight="bold")
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#2196F3",
               markersize=8, label="Volunteer"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#4CAF50",
               markersize=8, label="Professional"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    # --- Panel B: Q-Q plot ---
    ax = axes[0, 1]
    stats.probplot(residuals, dist="norm", plot=ax)
    ax.set_title("B. Normal Q-Q Plot of Residuals", fontweight="bold")
    ax.get_lines()[0].set_markerfacecolor("#666666")
    ax.get_lines()[0].set_markersize(3)

    # --- Panel C: Residuals by Observer Type ---
    ax = axes[1, 0]
    vol_resid = residuals[lme_df["IsVolunteer"] == 1]
    pro_resid = residuals[lme_df["IsVolunteer"] == 0]
    bp = ax.boxplot(
        [pro_resid, vol_resid],
        labels=["Professional\n(OCC QA)", "Volunteer\n(Blue Thumb)"],
        patch_artist=True,
        widths=0.5,
    )
    bp["boxes"][0].set_facecolor("#C8E6C9")
    bp["boxes"][1].set_facecolor("#BBDEFB")
    ax.axhline(y=0, color="red", linestyle="--", linewidth=1)
    ax.set_ylabel("Residuals (log mg/L)")
    ax.set_title("C. Residual Distribution by Observer Type", fontweight="bold")

    # --- Panel D: Chloride by Longitude colored by Observer ---
    ax = axes[1, 1]
    vol_mask = lme_df["IsVolunteer"] == 1
    pro_mask = lme_df["IsVolunteer"] == 0
    ax.scatter(lme_df.loc[pro_mask, "Longitude"],
               lme_df.loc[pro_mask, "Chloride_mgL"],
               c="#4CAF50", alpha=0.5, s=20, label="Professional", edgecolors="none")
    ax.scatter(lme_df.loc[vol_mask, "Longitude"],
               lme_df.loc[vol_mask, "Chloride_mgL"],
               c="#2196F3", alpha=0.5, s=20, label="Volunteer", edgecolors="none")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Chloride (mg/L)")
    ax.set_title("D. West-East Gradient by Observer Type", fontweight="bold")
    ax.legend()

    fig.suptitle("LME Model Diagnostics", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = OUTPUT_DIR / "lme_diagnostics.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# 3b. Matched-Pairs LME (Phase 1 co-located data — the PROPER test)
# ---------------------------------------------------------------------------
def fit_matched_pairs_lme():
    """
    Fit LME on Phase 1 matched pairs where volunteer and professional
    measured the SAME stream (≤125m, ≤72h). This is Joey's intended design:
    Site as random block, ObserverType as treatment.

    Also runs a paired t-test on log-transformed values as a simpler check.
    """
    import statsmodels.formula.api as smf

    print("\n" + "=" * 60)
    print("MATCHED-PAIRS ANALYSIS (Phase 1 co-located data)")
    print("=" * 60)

    mp = pd.read_csv(DATA_DIR / "outputs" / "matched_pairs_vol_to_pro.csv")
    print(f"\n  Matched pairs: {len(mp)} observations at "
          f"{mp['Vol_SiteID'].nunique()} volunteer sites")

    # Reshape to long format for LME
    vol_long = mp[["Vol_SiteID", "Vol_Value", "Vol_DateTime", "Vol_Lon"]].copy()
    vol_long.columns = ["Site", "Chloride_mgL", "DateTime", "Longitude"]
    vol_long["ObserverType"] = "Volunteer"

    pro_long = mp[["Vol_SiteID", "Pro_Value", "Pro_DateTime", "Pro_Lon"]].copy()
    pro_long.columns = ["Site", "Chloride_mgL", "DateTime", "Longitude"]
    pro_long["ObserverType"] = "Professional"

    paired_long = pd.concat([vol_long, pro_long], ignore_index=True)
    paired_long["DateTime"] = pd.to_datetime(paired_long["DateTime"], format="mixed")
    paired_long["LogChloride"] = np.log(paired_long["Chloride_mgL"])
    paired_long["IsVolunteer"] = (paired_long["ObserverType"] == "Volunteer").astype(int)

    # Julian covariates
    julian = paired_long["DateTime"].dt.dayofyear
    paired_long["JulianSin"] = np.sin(2 * np.pi * julian / 365.25)
    paired_long["JulianCos"] = np.cos(2 * np.pi * julian / 365.25)

    print(f"  Long format: {len(paired_long)} rows ({len(vol_long)} vol + {len(pro_long)} pro)")
    print(f"  Sites (random blocks): {paired_long['Site'].nunique()}")

    # --- Paired t-test on log values (simplest test) ---
    log_vol = np.log(mp["Vol_Value"].values)
    log_pro = np.log(mp["Pro_Value"].values)
    t_stat, t_pval = stats.ttest_rel(log_vol, log_pro)
    mean_ratio = np.exp(np.mean(log_vol - log_pro))

    print(f"\n  PAIRED T-TEST (log-transformed):")
    print(f"    t = {t_stat:.4f}, p = {t_pval:.6f}")
    print(f"    Mean vol/pro ratio: {mean_ratio:.3f} ({(mean_ratio-1)*100:+.1f}%)")
    if t_pval > 0.05:
        print(f"    ✅ NOT SIGNIFICANT — no detectable bias in paired measurements")
    else:
        print(f"    ⚠️ SIGNIFICANT — systematic bias detected")

    # --- Wilcoxon signed-rank (non-parametric robustness check) ---
    w_stat, w_pval = stats.wilcoxon(mp["Vol_Value"].values, mp["Pro_Value"].values)
    print(f"\n  WILCOXON SIGNED-RANK (non-parametric):")
    print(f"    W = {w_stat:.1f}, p = {w_pval:.6f}")
    if w_pval > 0.05:
        print(f"    ✅ NOT SIGNIFICANT")
    else:
        print(f"    ⚠️ SIGNIFICANT")

    # --- LME on paired data: Site as random block ---
    print(f"\n  LME MODEL (Site as random block):")
    print(f"    log(Chloride) ~ IsVolunteer + JulianSin + JulianCos + (1|Site)")

    mp_result = None
    try:
        model = smf.mixedlm(
            "LogChloride ~ IsVolunteer + JulianSin + JulianCos",
            data=paired_long,
            groups=paired_long["Site"],
        )
        mp_result = model.fit(reml=True)
        print("\n" + str(mp_result.summary()))

        obs_coef = mp_result.fe_params.get("IsVolunteer", 0)
        obs_pval = mp_result.pvalues.get("IsVolunteer", 1)
        obs_ci = mp_result.conf_int().loc["IsVolunteer"]
        mult = np.exp(obs_coef)

        print(f"\n    IsVolunteer coefficient: {obs_coef:.4f}")
        print(f"    IsVolunteer p-value:     {obs_pval:.6f}")
        print(f"    IsVolunteer 95% CI:      [{obs_ci.iloc[0]:.4f}, {obs_ci.iloc[1]:.4f}]")
        print(f"    Volunteer/Professional ratio: {mult:.3f} ({(mult-1)*100:+.1f}%)")
        if obs_pval > 0.05:
            print(f"\n    ✅ NOT SIGNIFICANT (p={obs_pval:.4f})")
            print(f"    → At co-located sites, volunteer and professional readings")
            print(f"      are statistically indistinguishable after controlling for season.")
        else:
            print(f"\n    ⚠️ SIGNIFICANT (p={obs_pval:.6f})")
    except Exception as e:
        print(f"    LME failed (likely too few groups): {e}")
        print(f"    Falling back to paired t-test result above.")

    # --- Matched-pairs diagnostic plot ---
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel A: Paired scatter
    ax = axes[0]
    ax.scatter(mp["Pro_Value"], mp["Vol_Value"], c="#2196F3", s=40,
              edgecolors="black", linewidth=0.5, zorder=3)
    lim = max(mp["Pro_Value"].max(), mp["Vol_Value"].max()) * 1.1
    ax.plot([0, lim], [0, lim], "r--", linewidth=1, label="1:1 line")
    slope, intercept, r, p, se = stats.linregress(mp["Pro_Value"], mp["Vol_Value"])
    x_fit = np.linspace(0, lim, 100)
    ax.plot(x_fit, slope * x_fit + intercept, "b-", linewidth=1.5,
            label=f"Regression (R²={r**2:.3f})")
    ax.set_xlabel("Professional Chloride (mg/L)", fontsize=11)
    ax.set_ylabel("Volunteer Chloride (mg/L)", fontsize=11)
    ax.set_title("A. Matched Pairs (≤125m, ≤72h)", fontweight="bold")
    ax.legend(fontsize=9)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_aspect("equal")

    # Panel B: Bland-Altman plot
    ax = axes[1]
    mean_vals = (mp["Vol_Value"] + mp["Pro_Value"]) / 2
    diff_vals = mp["Vol_Value"] - mp["Pro_Value"]
    mean_diff = diff_vals.mean()
    sd_diff = diff_vals.std()
    ax.scatter(mean_vals, diff_vals, c="#2196F3", s=40,
              edgecolors="black", linewidth=0.5)
    ax.axhline(mean_diff, color="red", linestyle="-", linewidth=1,
              label=f"Mean diff: {mean_diff:.1f} mg/L")
    ax.axhline(mean_diff + 1.96 * sd_diff, color="gray", linestyle="--",
              linewidth=0.8, label=f"±1.96 SD: ±{1.96*sd_diff:.1f} mg/L")
    ax.axhline(mean_diff - 1.96 * sd_diff, color="gray", linestyle="--",
              linewidth=0.8)
    ax.set_xlabel("Mean of Vol & Pro (mg/L)", fontsize=11)
    ax.set_ylabel("Difference (Vol − Pro) (mg/L)", fontsize=11)
    ax.set_title("B. Bland-Altman Agreement", fontweight="bold")
    ax.legend(fontsize=9)

    # Panel C: Paired differences by site
    ax = axes[2]
    site_ids = mp["Vol_SiteID"].unique()
    site_colors = ["#E91E63", "#4CAF50", "#FF9800", "#9C27B0"]
    for i, site in enumerate(site_ids):
        sub = mp[mp["Vol_SiteID"] == site]
        label = site.split("-")[0][-6:]  # short label
        ax.scatter([i] * len(sub), sub["Vol_Value"] - sub["Pro_Value"],
                  c=site_colors[i % len(site_colors)], s=40,
                  edgecolors="black", linewidth=0.5, label=label)
    ax.axhline(0, color="red", linestyle="--", linewidth=1)
    ax.set_xticks(range(len(site_ids)))
    ax.set_xticklabels([s.split("-")[0][-6:] for s in site_ids],
                       rotation=45, fontsize=8)
    ax.set_ylabel("Vol − Pro (mg/L)", fontsize=11)
    ax.set_title("C. Paired Differences by Site", fontweight="bold")

    plt.tight_layout()
    path = OUTPUT_DIR / "matched_pairs_analysis.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {path}")

    return {
        "paired_t_stat": t_stat,
        "paired_t_pval": t_pval,
        "wilcoxon_stat": w_stat,
        "wilcoxon_pval": w_pval,
        "mean_vol_pro_ratio": mean_ratio,
        "mean_diff_mgL": diff_vals.mean(),
        "sd_diff_mgL": diff_vals.std(),
        "n_pairs": len(mp),
        "n_sites": mp["Vol_SiteID"].nunique(),
        "lme_result": mp_result,
    }


# ---------------------------------------------------------------------------
# 4. Quantization Effect Visualization
# ---------------------------------------------------------------------------
def plot_quantization_effect(arcgis_df, qa_df):
    """Show the discrete 5 mg/L steps in volunteer data vs continuous professional."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Panel A: Histogram comparison ---
    ax = axes[0]
    pro_cl = qa_df[qa_df["Type"] == "Routine Sample"]["Chloride"].dropna()
    vol_cl = arcgis_df["Chloride_Low1_Final"].dropna()

    bins_pro = np.arange(0, pro_cl.max() + 10, 5)
    bins_vol = np.arange(0, vol_cl.max() + 10, 5)

    ax.hist(pro_cl, bins=bins_pro, alpha=0.6, color="#4CAF50",
            label=f"Professional (N={len(pro_cl)})", density=True, edgecolor="black",
            linewidth=0.3)
    ax.hist(vol_cl, bins=bins_vol, alpha=0.6, color="#2196F3",
            label=f"Volunteer (N={len(vol_cl)})", density=True, edgecolor="black",
            linewidth=0.3)
    ax.set_xlabel("Chloride (mg/L)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title("A. Chloride Distribution by Method", fontweight="bold", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_xlim(0, 300)

    # --- Panel B: Decimal precision comparison ---
    ax2 = axes[1]
    # Professional: show the decimal places
    pro_decimals = pro_cl.apply(lambda x: len(str(x).split(".")[-1])
                                 if "." in str(x) else 0)
    vol_remainder = vol_cl % 5
    vol_is_mult5 = (vol_remainder == 0).mean() * 100

    # Show professional values modulo 5 to reveal continuous distribution
    pro_mod5 = pro_cl % 5
    vol_mod5 = vol_cl % 5

    ax2.hist(pro_mod5, bins=50, alpha=0.6, color="#4CAF50",
             label="Professional", density=True, edgecolor="black", linewidth=0.3)
    ax2.hist(vol_mod5, bins=5, alpha=0.6, color="#2196F3",
             label="Volunteer", density=True, edgecolor="black", linewidth=0.3)
    ax2.set_xlabel("Chloride value mod 5 (mg/L)", fontsize=11)
    ax2.set_ylabel("Density", fontsize=11)
    ax2.set_title("B. Resolution: Professional (Continuous) vs\nVolunteer (Quantized to 5 mg/L)",
                  fontweight="bold", fontsize=13)
    ax2.legend(fontsize=10)
    ax2.annotate(f"Volunteer: {vol_is_mult5:.0f}% are exact\nmultiples of 5 mg/L",
                 xy=(0.98, 0.95), xycoords="axes fraction",
                 ha="right", va="top", fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF9C4",
                           edgecolor="black", linewidth=0.5))

    fig.suptitle("Quantization Effect: Drop-Count Resolution",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = OUTPUT_DIR / "quantization_effect.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# 5. Summary Report
# ---------------------------------------------------------------------------
def write_summary_report(var_results, lme_result, lme_df, mp_results=None):
    """Write a comprehensive text summary of all Phase 2 results."""
    path = OUTPUT_DIR / "phase2_lme_results.txt"

    with open(path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("PHASE 2: LINEAR MIXED-EFFECTS ANALYSIS RESULTS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Model: Dyer (2026) recommended framework\n")
        f.write("=" * 70 + "\n\n")

        f.write("1. VARIANCE DECOMPOSITION\n")
        f.write("-" * 40 + "\n")
        for key in ["vol_within_test", "pro_within_test", "pro_within_site"]:
            r = var_results[key]
            f.write(f"\n  {r['label'].replace(chr(10), ' ')}:\n")
            f.write(f"    N = {r['n']:,}\n")
            f.write(f"    Mean |diff| = {r['mean_abs_diff']:.2f} mg/L "
                    f"(±{r['ci_95']:.2f} 95% CI)\n")
            f.write(f"    Median |diff| = {r['median_abs_diff']:.2f} mg/L\n")
            f.write(f"    SD of differences = {r['sd_diff']:.2f} mg/L\n")
        f.write(f"\n  Field Blanks: N={var_results['field_blanks']['n']}, "
                f"values={var_results['field_blanks']['values']}, "
                f"all below detection={var_results['field_blanks']['all_below_detection']}\n")

        f.write(f"\n  KEY FINDING: Volunteer within-test repeatability "
                f"({var_results['vol_within_test']['mean_abs_diff']:.1f} mg/L) is better\n"
                f"  than professional within-test "
                f"({var_results['pro_within_test']['mean_abs_diff']:.1f} mg/L), but this\n"
                f"  reflects the 5 mg/L quantization floor — volunteers cannot detect\n"
                f"  sub-5 mg/L differences due to the drop-count method.\n")

        f.write(f"\n\n2. MATCHED-PAIRS ANALYSIS (PRIMARY — co-located sites)\n")
        f.write("-" * 40 + "\n")
        if mp_results:
            f.write(f"\n  Phase 1 matched pairs: N={mp_results['n_pairs']} at "
                    f"{mp_results['n_sites']} volunteer sites\n")
            f.write(f"  Matching criteria: ≤125m spatial, ≤72h temporal\n")
            f.write(f"\n  Paired t-test (log-transformed):\n")
            f.write(f"    t = {mp_results['paired_t_stat']:.4f}, "
                    f"p = {mp_results['paired_t_pval']:.6f}\n")
            f.write(f"    Mean vol/pro ratio: {mp_results['mean_vol_pro_ratio']:.3f} "
                    f"({(mp_results['mean_vol_pro_ratio']-1)*100:+.1f}%)\n")
            f.write(f"\n  Wilcoxon signed-rank (non-parametric):\n")
            f.write(f"    W = {mp_results['wilcoxon_stat']:.1f}, "
                    f"p = {mp_results['wilcoxon_pval']:.6f}\n")
            f.write(f"\n  Bland-Altman agreement:\n")
            f.write(f"    Mean difference (Vol - Pro): "
                    f"{mp_results['mean_diff_mgL']:.1f} mg/L\n")
            f.write(f"    SD of differences: {mp_results['sd_diff_mgL']:.1f} mg/L\n")
            f.write(f"    95% limits of agreement: "
                    f"[{mp_results['mean_diff_mgL']-1.96*mp_results['sd_diff_mgL']:.1f}, "
                    f"{mp_results['mean_diff_mgL']+1.96*mp_results['sd_diff_mgL']:.1f}] mg/L\n")
            if mp_results['paired_t_pval'] > 0.05:
                f.write(f"\n  CONCLUSION: NOT SIGNIFICANT. At co-located sites, volunteer\n")
                f.write(f"  and professional chloride readings show no systematic bias\n")
                f.write(f"  after accounting for natural variation.\n")
            else:
                f.write(f"\n  CONCLUSION: SIGNIFICANT (p={mp_results['paired_t_pval']:.4f}).\n")
                f.write(f"  Volunteers tend to read "
                        f"{(mp_results['mean_vol_pro_ratio']-1)*100:+.1f}% relative to\n")
                f.write(f"  professionals. This is the 'accuracy' component.\n")

        f.write(f"\n\n3. REGIONAL LINEAR MIXED-EFFECTS MODEL (EXPLORATORY)\n")
        f.write("-" * 40 + "\n")
        f.write(f"\n  Formula: log(Chloride) ~ IsVolunteer + JulianSin + "
                f"JulianCos + Longitude + (1|Site)\n")
        f.write(f"  REML estimation\n")
        f.write(f"  N = {len(lme_df)}, Sites = {lme_df['Site'].nunique()}\n")
        f.write(f"  Professional: {(lme_df['IsVolunteer']==0).sum()} observations "
                f"at {lme_df[lme_df['IsVolunteer']==0]['Site'].nunique()} sites\n")
        f.write(f"  Volunteer: {(lme_df['IsVolunteer']==1).sum()} observations "
                f"at {lme_df[lme_df['IsVolunteer']==1]['Site'].nunique()} sites\n")

        f.write(f"\n  Fixed Effects:\n")
        for param in lme_result.fe_params.index:
            coef = lme_result.fe_params[param]
            pval = lme_result.pvalues[param]
            ci = lme_result.conf_int().loc[param]
            sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
            f.write(f"    {param:15s}: coef={coef:+.4f}, p={pval:.6f} {sig}, "
                    f"95% CI=[{ci.iloc[0]:+.4f}, {ci.iloc[1]:+.4f}]\n")

        observer_coef = lme_result.fe_params.get("IsVolunteer", 0)
        observer_pval = lme_result.pvalues.get("IsVolunteer", 1)
        mult = np.exp(observer_coef)

        f.write(f"\n  Random Effects:\n")
        re_var = lme_result.cov_re.iloc[0, 0]
        f.write(f"    Site variance: {re_var:.4f} (SD={np.sqrt(re_var):.4f})\n")

        f.write(f"\n  INTERPRETATION:\n")
        f.write(f"    IsVolunteer coefficient = {observer_coef:.4f} "
                f"(p = {observer_pval:.6f})\n")
        f.write(f"    Back-transformed: volunteers read {mult:.3f}x professional "
                f"({(mult-1)*100:+.1f}%)\n")
        if observer_pval > 0.05:
            f.write(f"    CONCLUSION: NOT SIGNIFICANT. After controlling for seasonal\n")
            f.write(f"    variation and the West-East gradient, volunteer and professional\n")
            f.write(f"    chloride readings are statistically indistinguishable.\n")
        else:
            f.write(f"    CONCLUSION: SIGNIFICANT. A systematic bias of "
                    f"{(mult-1)*100:+.1f}% exists\n")
            f.write(f"    between volunteer and professional readings after controlling\n")
            f.write(f"    for season and geography.\n")

        f.write("\n\n3. DATA PROVENANCE\n")
        f.write("-" * 40 + "\n")
        f.write(f"  QA Data: 2.5 QA Data.xlsx (Karla Spinner → Joey Dyer → Miguel, "
                f"Feb 20 2026)\n")
        f.write(f"  Volunteer: ArcGIS FeatureServer (Blue Thumb, OCC public API)\n")
        f.write(f"  Analysis window: {QA_DATE_MIN.date()} to {QA_DATE_MAX.date()}\n")
        f.write(f"  Region: lon [{QA_LON_MIN-SPATIAL_BUFFER:.2f}, "
                f"{QA_LON_MAX+SPATIAL_BUFFER:.2f}], "
                f"lat [{QA_LAT_MIN-SPATIAL_BUFFER:.2f}, "
                f"{QA_LAT_MAX+SPATIAL_BUFFER:.2f}]\n")
        f.write(f"  Statistical framework: Dyer (2026), meeting recommendation\n")
        f.write(f"  Reference: Dyer et al. (2025) PeerJ 13:e20234\n")

    print(f"\n  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("PHASE 2: DYER LME FRAMEWORK — FULL ANALYSIS")
    print("=" * 70)
    print(f"\nLoading data sources...")

    qa_df = load_qa_data()
    arcgis_df = load_arcgis_replicates()
    vol_df = load_volunteer_data()

    # Build LME dataframe
    print("\nBuilding LME analysis dataframe...")
    lme_df = build_lme_dataframe(qa_df, vol_df)
    lme_path = OUTPUT_DIR / "lme_analysis_df.csv"
    lme_df.to_csv(lme_path, index=False)
    print(f"  Saved: {lme_path}")

    # Variance decomposition
    var_results, rd_pairs, rr_pairs, vol_pairs = variance_decomposition(qa_df, arcgis_df)
    plot_variance_decomposition(var_results)

    # LME model (regional — exploratory, has confound)
    lme_result, lme_df = fit_lme_model(lme_df)
    plot_lme_diagnostics(lme_result, lme_df)

    # Matched-pairs analysis (the proper test)
    mp_results = fit_matched_pairs_lme()

    # Quantization effect
    plot_quantization_effect(arcgis_df, qa_df)

    # Summary report
    write_summary_report(var_results, lme_result, lme_df, mp_results)

    print("\n" + "=" * 70)
    print("PHASE 2 ANALYSIS COMPLETE")
    print(f"All outputs in: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
