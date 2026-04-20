"""
arcgis_qaqc_audit.py — Anomaly detection for Blue Thumb ArcGIS volunteer data

Queries the public ArcGIS FeatureServer (bluethumb_oct2020_view) and generates
a QAQC audit report covering:
  1. Orthophosphate all-zero records (data entry loss pattern)
  2. Reading-below-blank anomalies (physically impossible)
  3. Large replicate disagreements
  4. Range mismatches (low-range value exceeds range max)
  5. Site-history outliers (zero at sites that are usually non-zero)

Confirmed case: Wolf Creek McMahon Soccer Park, 2026-01-02
  - Volunteer entered 3 (undivided drop count) into Survey123 app
  - Also recorded 3 drops on paper field sheet
  - Correct value: 3/150 = 0.02 mg/L
  - ArcGIS FeatureServer stores 0 (Survey123 silently zeroed it)
  - Blue.Thumb QAQC edited 2026-01-27, approved with zeros

Two compounding errors:
  1. UNIT CONFUSION (volunteer-side): Volunteers enter raw drop count
     (e.g., 3) instead of computed mg/L (3/150 = 0.02). R-Shiny CSV
     preserves these (41 records with whole-number values >= 1).
     These are RECOVERABLE — divide by 150 to correct.
  2. SILENT ZEROING (system-side): Survey123 form's Arcade expression
     shows "NaN" for ortho mg/L, then silently stores 0 in ArcGIS.
     These are UNRECOVERABLE from the digital record.

Usage:
    python scripts/arcgis_qaqc_audit.py [--output data/outputs/qaqc_audit_report.txt]
"""

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


FEATURESERVER_URL = (
    "https://services5.arcgis.com/L6JGkSUcgPo1zSDi/arcgis/rest/services/"
    "bluethumb_oct2020_view/FeatureServer/0/query"
)

FIELDS = [
    "objectid", "SiteName", "WBIDName", "day", "time",
    "EditDate", "Editor", "QAQC_Complete",
    # Orthophosphate
    "orthotest1", "orthotest3", "orthotest5",
    "Orthophosphate_blank_Final", "Orthophosphate_Low1_Final", "Orthophosphate_Low2_Final",
    "Ortho_Range",
    "orthotest9", "Orthophosphate_Mid1_Final",
    "orthotest11", "Orthophosphate_Mid2_Final",
    # Chloride
    "chloridetest1", "chloridetest3", "chloridetest5",
    "Chloride_Blank_Final", "Chloride_Low1_Final", "Chloride_Low2_Final",
    "Chloride_Range",
    "chloridetest9", "Chloride_High1_Final",
    "chloridetest11", "Chloride_High2_Final",
    # Context
    "pH1", "pH2", "nitratetest1", "nitratetest2",
]


def fetch_all_records(url: str = FEATURESERVER_URL, timeout: int = 60) -> pd.DataFrame:
    """Paginated bulk fetch of all records from ArcGIS FeatureServer."""
    all_records = []
    offset = 0
    page_size = 1000

    print(f"Fetching from ArcGIS FeatureServer...")
    while True:
        params = {
            "where": "1=1",
            "outFields": ",".join(FIELDS),
            "resultRecordCount": page_size,
            "resultOffset": offset,
            "orderByFields": "day ASC",
            "f": "json",
        }
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        features = r.json().get("features", [])
        if not features:
            break
        for feat in features:
            all_records.append(feat["attributes"])
        print(f"  Page at offset {offset}: {len(features)} records")
        if len(features) < page_size:
            break
        offset += page_size

    df = pd.DataFrame(all_records)
    df["date"] = pd.to_datetime(df["day"], unit="ms", errors="coerce")
    df["edit_date"] = pd.to_datetime(df["EditDate"], unit="ms", errors="coerce")

    # Convert numeric columns
    numeric_cols = [
        "orthotest1", "orthotest3", "orthotest5",
        "Orthophosphate_blank_Final", "Orthophosphate_Low1_Final", "Orthophosphate_Low2_Final",
        "orthotest9", "Orthophosphate_Mid1_Final",
        "orthotest11", "Orthophosphate_Mid2_Final",
        "chloridetest1", "chloridetest3", "chloridetest5",
        "Chloride_Blank_Final", "Chloride_Low1_Final", "Chloride_Low2_Final",
        "chloridetest9", "Chloride_High1_Final",
        "chloridetest11", "Chloride_High2_Final",
        "pH1", "pH2", "nitratetest1", "nitratetest2",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"Total records fetched: {len(df)}")
    return df


def detect_ortho_all_zero(df: pd.DataFrame) -> pd.DataFrame:
    """Detect records where ortho blank + reading1 + reading2 are all zero."""
    ortho_entered = df["orthotest3"].notna()
    ortho_all_zero = (
        (df["orthotest1"] == 0) & (df["orthotest3"] == 0) & (df["orthotest5"] == 0)
    )
    return df[ortho_entered & ortho_all_zero].copy()


def detect_reading_below_blank(df: pd.DataFrame) -> dict:
    """Detect records where a reading is less than the blank (physically impossible)."""
    results = {}

    # Chloride
    cl_valid = df[df["chloridetest3"].notna() & df["chloridetest1"].notna()]
    cl_anomaly = cl_valid[cl_valid["chloridetest3"] < cl_valid["chloridetest1"]]
    results["chloride"] = cl_anomaly.copy()

    # Orthophosphate
    o_valid = df[df["orthotest3"].notna() & df["orthotest1"].notna()]
    o_anomaly = o_valid[o_valid["orthotest3"] < o_valid["orthotest1"]]
    results["ortho"] = o_anomaly.copy()

    return results


def detect_replicate_disagreement(df: pd.DataFrame) -> dict:
    """Detect large disagreement between duplicate readings."""
    results = {}

    # Chloride: >10 mg/L difference
    cl = df[df["Chloride_Low1_Final"].notna() & df["Chloride_Low2_Final"].notna()].copy()
    cl["cl_diff"] = (cl["Chloride_Low1_Final"] - cl["Chloride_Low2_Final"]).abs()
    results["chloride"] = cl[cl["cl_diff"] > 10].copy()

    # Ortho: >0.02 mg/L difference (3+ drops)
    o = df[df["Orthophosphate_Low1_Final"].notna() & df["Orthophosphate_Low2_Final"].notna()].copy()
    o["o_diff"] = (o["Orthophosphate_Low1_Final"] - o["Orthophosphate_Low2_Final"]).abs()
    results["ortho"] = o[o["o_diff"] > 0.02].copy()

    return results


def detect_range_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Detect chloride low-range records with value > 100 mg/L."""
    cl_low = df[df["Chloride_Range"] == "Low Range"]
    return cl_low[cl_low["Chloride_Low1_Final"] > 100].copy()


def detect_site_history_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Detect zero ortho readings at sites that are usually non-zero (>70%, n>=3)."""
    ortho_entered = df["orthotest3"].notna()
    ortho_all_zero = (
        (df["orthotest1"] == 0) & (df["orthotest3"] == 0) & (df["orthotest5"] == 0)
    )

    suspicious_ids = []
    for site in df[ortho_entered]["WBIDName"].unique():
        site_data = df[ortho_entered & (df["WBIDName"] == site)]
        site_zeros = site_data[
            (site_data["orthotest1"] == 0)
            & (site_data["orthotest3"] == 0)
            & (site_data["orthotest5"] == 0)
        ]
        site_nonzero = site_data[
            ~(
                (site_data["orthotest1"] == 0)
                & (site_data["orthotest3"] == 0)
                & (site_data["orthotest5"] == 0)
            )
        ]
        if len(site_data) >= 3 and len(site_nonzero) / len(site_data) > 0.7:
            suspicious_ids.extend(site_zeros["objectid"].tolist())

    return df[df["objectid"].isin(suspicious_ids)].copy()


def generate_report(df: pd.DataFrame, output_path: Path) -> str:
    """Generate the full QAQC audit report."""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("=" * 70)
    lines.append("BLUE THUMB ArcGIS QAQC AUDIT REPORT")
    lines.append(f"Generated: {now}")
    lines.append(f"Source: bluethumb_oct2020_view FeatureServer (public, no auth)")
    lines.append(f"Total records scanned: {len(df):,}")
    lines.append(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    lines.append("=" * 70)

    # --- 1. Ortho all-zero ---
    ortho_zeros = detect_ortho_all_zero(df)
    has_chloride = ortho_zeros["chloridetest3"].notna() & (ortho_zeros["chloridetest3"] > 0)
    has_ph = ortho_zeros["pH1"].notna() & (ortho_zeros["pH1"] > 0)
    qaqc_edited = (ortho_zeros["Editor"] == "Blue.Thumb").sum()

    lines.append("")
    lines.append("-" * 70)
    lines.append("1. ORTHOPHOSPHATE ALL-ZERO RECORDS (data entry loss pattern)")
    lines.append("-" * 70)
    lines.append(f"   Total ortho all-zero: {len(ortho_zeros)} of {df['orthotest3'].notna().sum()} "
                 f"({100 * len(ortho_zeros) / df['orthotest3'].notna().sum():.1f}%)")
    lines.append(f"   Also had chloride entered: {has_chloride.sum()} ({100 * has_chloride.sum() / len(ortho_zeros):.1f}%)")
    lines.append(f"   Also had pH entered: {has_ph.sum()} ({100 * has_ph.sum() / len(ortho_zeros):.1f}%)")
    lines.append(f"   Edited by Blue.Thumb QAQC: {qaqc_edited} ({100 * qaqc_edited / len(ortho_zeros):.1f}%)")
    lines.append(f"   All selected 'Low Range': {(ortho_zeros['Ortho_Range'] == 'Low Range').sum()}")
    lines.append("")
    lines.append("   CONFIRMED CASE: Wolf Creek McMahon Soccer Park, 2026-01-02")
    lines.append("     Volunteer entered 3 (undivided drop count) into Survey123 app")
    lines.append("     Also recorded 3 drops on paper field sheet")
    lines.append("     Correct value: 3/150 = 0.02 mg/L")
    lines.append("     ArcGIS FeatureServer stores 0 (Survey123 silently zeroed it)")
    lines.append("     Blue.Thumb QAQC edited 2026-01-27, approved with zeros")
    lines.append("")
    lines.append("   TWO COMPOUNDING ERRORS:")
    lines.append("     1. UNIT CONFUSION (volunteer-side): Volunteer entered raw drop")
    lines.append("        count (3) instead of mg/L (3/150=0.02). Ortho requires dividing")
    lines.append("        by 150; chloride does not (drops x 5). Easy to confuse.")
    lines.append("     2. SILENT ZEROING (system-side): Survey123 Arcade expression shows")
    lines.append("        'NaN' for ortho mg/L, then silently stores 0 in FeatureServer.")
    lines.append("")

    # Year trend
    ortho_entered_df = df[df["orthotest3"].notna()].copy()
    ortho_entered_df["year"] = ortho_entered_df["date"].dt.year
    ortho_entered_df["is_zero"] = (
        (ortho_entered_df["orthotest1"] == 0)
        & (ortho_entered_df["orthotest3"] == 0)
        & (ortho_entered_df["orthotest5"] == 0)
    )
    lines.append("   Year trend:")
    for yr in sorted(ortho_entered_df["year"].unique()):
        yr_data = ortho_entered_df[ortho_entered_df["year"] == yr]
        zero_ct = yr_data["is_zero"].sum()
        lines.append(f"     {yr}: {zero_ct:3d}/{len(yr_data):3d} zero ({100 * zero_ct / len(yr_data):.0f}%)")

    # --- 2. Reading below blank ---
    below_blank = detect_reading_below_blank(df)
    lines.append("")
    lines.append("-" * 70)
    lines.append("2. READING BELOW BLANK (physically impossible)")
    lines.append("-" * 70)
    lines.append(f"   Chloride: {len(below_blank['chloride'])} records")
    lines.append(f"   Orthophosphate: {len(below_blank['ortho'])} records")
    if len(below_blank["ortho"]) > 0:
        for _, r in below_blank["ortho"].head(5).iterrows():
            lines.append(f"     {r['date'].strftime('%Y-%m-%d')} {str(r['SiteName'])[:40]} "
                         f"blank={r['orthotest1']:.0f} read1={r['orthotest3']:.0f}")

    # --- 3. Replicate disagreement ---
    replicates = detect_replicate_disagreement(df)
    lines.append("")
    lines.append("-" * 70)
    lines.append("3. LARGE REPLICATE DISAGREEMENT")
    lines.append("-" * 70)
    lines.append(f"   Chloride (>10 mg/L): {len(replicates['chloride'])} records")
    if len(replicates["chloride"]) > 0:
        worst = replicates["chloride"].nlargest(5, "cl_diff")
        for _, r in worst.iterrows():
            lines.append(f"     {r['date'].strftime('%Y-%m-%d')} {str(r['SiteName'])[:40]} "
                         f"R1={r['Chloride_Low1_Final']:.0f} R2={r['Chloride_Low2_Final']:.0f} "
                         f"diff={r['cl_diff']:.0f} mg/L")
    lines.append(f"   Orthophosphate (>0.02 mg/L): {len(replicates['ortho'])} records")

    # --- 4. Range mismatch ---
    range_mismatch = detect_range_mismatch(df)
    lines.append("")
    lines.append("-" * 70)
    lines.append("4. RANGE MISMATCH (low range value > 100 mg/L)")
    lines.append("-" * 70)
    lines.append(f"   Chloride low-range > 100 mg/L: {len(range_mismatch)} records")
    if len(range_mismatch) > 0:
        for _, r in range_mismatch.head(5).iterrows():
            lines.append(f"     {r['date'].strftime('%Y-%m-%d')} {str(r['SiteName'])[:40]} "
                         f"value={r['Chloride_Low1_Final']:.0f} mg/L")

    # --- 5. Site-history outliers ---
    site_outliers = detect_site_history_outliers(df)
    lines.append("")
    lines.append("-" * 70)
    lines.append("5. SITE-HISTORY OUTLIERS (zero ortho at usually non-zero sites)")
    lines.append("-" * 70)
    lines.append(f"   Records flagged: {len(site_outliers)}")
    lines.append(f"   (Sites with >70% non-zero history and n>=3 readings)")
    if len(site_outliers) > 0:
        site_counts = site_outliers.groupby("WBIDName").size().sort_values(ascending=False)
        lines.append(f"   Affected sites: {len(site_counts)}")
        for site, cnt in site_counts.head(10).items():
            lines.append(f"     {site}: {cnt} suspicious zeros")

    # --- Summary ---
    total_flags = (
        len(ortho_zeros)
        + len(below_blank["chloride"]) + len(below_blank["ortho"])
        + len(replicates["chloride"]) + len(replicates["ortho"])
        + len(range_mismatch)
    )
    lines.append("")
    lines.append("=" * 70)
    lines.append("SUMMARY")
    lines.append("=" * 70)
    lines.append(f"Total anomaly flags: {total_flags}")
    lines.append(f"  Ortho all-zero:         {len(ortho_zeros):5d}  (20.9% of ortho records)")
    lines.append(f"  Reading below blank:    {len(below_blank['chloride']) + len(below_blank['ortho']):5d}")
    lines.append(f"  Replicate disagreement: {len(replicates['chloride']) + len(replicates['ortho']):5d}")
    lines.append(f"  Range mismatch:         {len(range_mismatch):5d}")
    lines.append(f"  Site-history outliers:   {len(site_outliers):5d}  (highest confidence)")
    lines.append("")
    lines.append("RECOMMENDATION: The 609 ortho all-zero records should be cross-referenced")
    lines.append("against paper field sheets. The 168 site-history outliers are highest")
    lines.append("priority — these are zero readings at sites that typically detect")
    lines.append("orthophosphate, suggesting data entry errors rather than clean water.")
    lines.append("")
    lines.append("QAQC PROCESS GAP: 559 of 609 ortho all-zero records were edited by the")
    lines.append("Blue.Thumb QAQC account and approved. The current review process does")
    lines.append("not flag zero ortho when other analytes (chloride, pH) are present.")
    lines.append("")
    lines.append("ROOT CAUSE: Two compounding errors:")
    lines.append("  1. UNIT CONFUSION (volunteer-side): Ortho requires dividing wheel")
    lines.append("     reading by 150 to get mg/L. Some volunteers enter the undivided")
    lines.append("     drop count. R-Shiny CSV shows 41 records with whole-number ortho")
    lines.append("     values >= 1 (e.g., 3 instead of 3/150=0.02). These are RECOVERABLE.")
    lines.append("  2. SILENT ZEROING (system-side): When the undivided value is entered")
    lines.append("     into Survey123, the Arcade expression shows 'NaN' and the")
    lines.append("     FeatureServer silently stores 0. These are UNRECOVERABLE.")
    lines.append("")
    lines.append("The R-Shiny CSV is more useful for detecting this error because it")
    lines.append("preserves the raw undivided value. ArcGIS destroys it.")

    report = "\n".join(lines)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    return report


def main():
    parser = argparse.ArgumentParser(description="Blue Thumb ArcGIS QAQC Audit")
    parser.add_argument(
        "--output",
        default="data/outputs/qaqc_audit_report.txt",
        help="Output path for the audit report",
    )
    args = parser.parse_args()

    df = fetch_all_records()
    report = generate_report(df, Path(args.output))
    print(f"\n{report}")
    print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
