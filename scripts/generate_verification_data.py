#!/usr/bin/env python3
"""
generate_verification_data.py - Regenerate the small committed derived files
that verify.py consumes, from the raw / processed sources.

Produces (in data/outputs/phase2_lme/, which is NOT gitignored):
  - replicate_diffs.csv     per-pair absolute differences for the precision claim
  - coverage_distances.csv  per-volunteer-site nearest professional distance (km)

These derived files let `python verify.py` recompute the precision (97.3%, 1.53,
2.51, 3.58) and coverage (93%, 327 sites) claims WITHOUT the raw ArcGIS export or
the large processed coordinate CSVs (both of which are gitignored).

Logic mirrors the existing analysis code exactly:
  - Volunteer precision: |chloridetest3 - chloridetest5| * 5 mg/L
    (scripts/phase2_lme_analysis.py variance_decomposition / load_arcgis_replicates)
  - Professional precision: |routine - duplicate| and |routine - replicate| from
    data/2.5 QA Data.xlsx (same function)
  - Coverage: Haversine great-circle distance to the nearest professional site
    (src/analysis.py run_spatial_coverage)

Inputs (gitignored locally; present in the authors' working tree):
  - data/raw/arcgis_volunteer_chloride.csv
  - data/2.5 QA Data.xlsx
  - data/processed/volunteer_chloride.csv
  - data/processed/professional_chloride.csv

Usage:  python scripts/generate_verification_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import spatial

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "outputs" / "phase2_lme"
OUT.mkdir(parents=True, exist_ok=True)


def build_replicate_diffs():
    """Per-pair absolute differences for all three precision groups."""
    rows = []

    # --- Volunteer titration replicates: drop-count diff * 5 mg/L ---
    a = pd.read_csv(DATA / "raw" / "arcgis_volunteer_chloride.csv")
    for c in ["chloridetest3", "chloridetest5", "Chloride_Low1_Final"]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a = a.dropna(subset=["chloridetest3", "chloridetest5", "Chloride_Low1_Final"])
    a["drop_diff"] = (a["chloridetest3"] - a["chloridetest5"]).abs()
    a["mg_diff"] = a["drop_diff"] * 5.0
    for dd, md in zip(a["drop_diff"].astype(int), a["mg_diff"].astype(float)):
        rows.append(("volunteer_within_test", int(dd), float(md)))

    # --- Professional QA pairs from the Rotating Basin QA workbook ---
    q = pd.read_excel(DATA / "2.5 QA Data.xlsx", sheet_name="2_5 QA Data")
    q["Chloride"] = pd.to_numeric(q["Chloride"], errors="coerce")
    q["DateActivityStart"] = pd.to_datetime(q["DateActivityStart"])
    q = q[q["Chloride"].notna()].copy()
    routine = q[q["Type"] == "Routine Sample"].set_index(
        ["WBID", "DateActivityStart"])["Chloride"]
    duplicate = q[q["Type"] == "Field Duplicate"].set_index(
        ["WBID", "DateActivityStart"])["Chloride"]
    replicate = q[q["Type"] == "Field Replicate"].set_index(
        ["WBID", "DateActivityStart"])["Chloride"]

    rd = pd.DataFrame({"routine": routine, "duplicate": duplicate}).dropna()
    for v in (rd["routine"] - rd["duplicate"]).abs():
        rows.append(("professional_within_test", "", float(v)))

    rr = pd.DataFrame({"routine": routine, "replicate": replicate}).dropna()
    for v in (rr["routine"] - rr["replicate"]).abs():
        rows.append(("professional_within_site", "", float(v)))

    rep = pd.DataFrame(rows, columns=["group", "drop_diff", "abs_diff_mgL"])
    rep.to_csv(OUT / "replicate_diffs.csv", index=False)
    summ = rep.groupby("group").agg(n=("abs_diff_mgL", "size"),
                                    mean_abs_diff=("abs_diff_mgL", "mean"))
    print("Wrote replicate_diffs.csv:", len(rep), "rows")
    print(summ.round(4).to_string())
    return rep


def build_coverage_distances():
    """Nearest professional distance (km) for each volunteer site."""
    vol = pd.read_csv(DATA / "processed" / "volunteer_chloride.csv", low_memory=False)
    pro = pd.read_csv(DATA / "processed" / "professional_chloride.csv", low_memory=False)
    vol_sites = vol.groupby("MonitoringLocationIdentifier").agg(
        lat=("LatitudeMeasure", "first"), lon=("LongitudeMeasure", "first"))
    pro_sites = pro.groupby("MonitoringLocationIdentifier").agg(
        lat=("LatitudeMeasure", "first"), lon=("LongitudeMeasure", "first"))

    # Haversine great-circle distance to the nearest professional site (km).
    # Correct at Oklahoma latitude, where a degree of longitude is ~91 km, not 111.
    R = 6371.0
    vlat = np.radians(vol_sites["lat"].values)[:, None]
    vlon = np.radians(vol_sites["lon"].values)[:, None]
    plat = np.radians(pro_sites["lat"].values)[None, :]
    plon = np.radians(pro_sites["lon"].values)[None, :]
    a = (np.sin((plat - vlat) / 2) ** 2
         + np.cos(vlat) * np.cos(plat) * np.sin((plon - vlon) / 2) ** 2)
    dist_km = (2 * R * np.arcsin(np.sqrt(a))).min(axis=1)

    cov = pd.DataFrame({
        "volunteer_site": vol_sites.index,
        "nearest_professional_km": np.round(dist_km, 6),
    })
    cov.to_csv(OUT / "coverage_distances.csv", index=False)
    n_far = int((cov["nearest_professional_km"] > 1).sum())
    print("Wrote coverage_distances.csv:", len(cov), "rows")
    print(f"  sites > 1 km: {n_far} ({100 * n_far / len(cov):.1f}%)")
    return cov


def main():
    build_replicate_diffs()
    print()
    build_coverage_distances()


if __name__ == "__main__":
    main()
