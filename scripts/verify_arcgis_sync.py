import argparse
import os
from datetime import datetime, timedelta

import pandas as pd
import requests

# VERIFIED (2026-01-27): ArcGIS REST /query returns ground-truth records for:
# - SiteName: "Wolf Creek:  McMahon Soccer Park" (note double space after ':')
# - Dates: 2025-11-22 and 2026-01-02
# - QAQC_Complete: "X" for both
# - Raw chloride fields readable: chloridetest1, chloridetest3, chloridetest5
# Evidence CSV (sample export): data/outputs/arcgis_ground_truth_wolf_creek_sample.csv


DEFAULT_BASE_URL = "https://services5.arcgis.com/L6JGkSUcgPo1zSDi/arcgis/rest/services/bluethumb_oct2020_view/FeatureServer/0/query"
DEFAULT_FIELDS = [
    "SiteName",
    "day",
    "chloridetest1",
    "chloridetest3",
    "chloridetest5",
    "QAQC_Complete",
]
DEFAULT_TARGET_DATES = ["2025-11-22", "2026-01-02"]


def _build_params(where: str, out_fields: list[str], record_count: int | None) -> dict:
    params = {
        "where": where,
        "outFields": ",".join(out_fields),
        "f": "json",
        "orderByFields": "day DESC",
    }
    if record_count is not None:
        params["resultRecordCount"] = record_count
    return params


def _escape_sql_string(value: str) -> str:
    return value.replace("'", "''")


def _site_like_pattern(site_name: str) -> str:
    tokens = [t for t in site_name.split() if t]
    if not tokens:
        return "%"
    return "%" + "%".join(tokens) + "%"


def _build_where_for_date(date_str: str, site_name: str | None) -> str:
    start_dt = datetime.strptime(date_str, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=1)
    start_sql = start_dt.strftime("%Y-%m-%d 00:00:00")
    end_sql = end_dt.strftime("%Y-%m-%d 00:00:00")

    where_parts = [f"day >= timestamp '{start_sql}'", f"day < timestamp '{end_sql}'"]
    if site_name:
        safe_pattern = _escape_sql_string(_site_like_pattern(site_name))
        where_parts.append(f"SiteName LIKE '{safe_pattern}'")
    return " AND ".join(where_parts)


def _fetch_features(base_url: str, params: dict, timeout_seconds: int) -> list[dict]:
    response = requests.get(base_url, params=params, timeout=timeout_seconds)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict) and "error" in data:
        err = data.get("error")
        raise ValueError(f"ArcGIS error response: {err}")

    if not isinstance(data, dict) or "features" not in data:
        raise ValueError(f"No 'features' in response. Top-level keys: {sorted(list(data.keys())) if isinstance(data, dict) else type(data)}")

    features = data["features"]
    if not isinstance(features, list):
        raise ValueError(f"Expected 'features' to be a list, got {type(features)}")

    return features


def _features_to_dataframe(features: list[dict]) -> pd.DataFrame:
    records = []
    for f in features:
        attrs = f.get("attributes") if isinstance(f, dict) else None
        if isinstance(attrs, dict):
            records.append(attrs)

    df = pd.DataFrame(records)
    if df.empty:
        return df

    if "day" in df.columns:
        df["Sampling_Date"] = pd.to_datetime(df["day"], unit="ms", errors="coerce")
    else:
        df["Sampling_Date"] = pd.NaT

    return df


def _normalize_whitespace(value: str) -> str:
    return " ".join(str(value).split())


def _verify_dates(df: pd.DataFrame, target_dates: list[str], site_name: str | None) -> None:
    if df.empty:
        print("No records to verify.")
        return

    if "Sampling_Date" not in df.columns:
        print("Sampling_Date column missing; cannot verify dates.")
        return

    df_work = df.copy()

    if site_name:
        if "SiteName" not in df_work.columns:
            print("SiteName field not present in returned payload; cannot apply site filter.")
        else:
            target_norm = _normalize_whitespace(site_name)
            df_work = df_work[
                df_work["SiteName"].astype(str).map(_normalize_whitespace) == target_norm
            ]

    df_work["Sampling_Date_Str"] = df_work["Sampling_Date"].dt.strftime("%Y-%m-%d")

    for target_date in target_dates:
        matches = df_work[df_work["Sampling_Date_Str"] == target_date]
        if matches.empty:
            print(f"Not found in retrieved sample: {target_date}")
            continue

        cols = [c for c in ["SiteName", "Sampling_Date", "QAQC_Complete"] if c in matches.columns]
        print(f"Found {len(matches)} record(s) for {target_date}:")
        print(matches[cols].to_string(index=False))


def _print_matching_rows(df: pd.DataFrame, date_str: str, site_name: str | None, fields_to_print: list[str]) -> None:
    if df.empty:
        print(f"No rows returned for {date_str}.")
        return

    df_work = df.copy()
    if "Sampling_Date" in df_work.columns:
        df_work["Sampling_Date_Str"] = df_work["Sampling_Date"].dt.strftime("%Y-%m-%d")

    if site_name and "SiteName" in df_work.columns:
        target_norm = _normalize_whitespace(site_name)
        df_work = df_work[
            df_work["SiteName"].astype(str).map(_normalize_whitespace) == target_norm
        ]

    if "Sampling_Date_Str" in df_work.columns:
        df_work = df_work[df_work["Sampling_Date_Str"] == date_str]

    if df_work.empty:
        print(f"No matching rows after filtering for {date_str}.")
        return

    cols = [c for c in fields_to_print if c in df_work.columns]
    print(df_work[cols].to_string(index=False))


def verify_arcgis_connection(
    base_url: str = DEFAULT_BASE_URL,
    out_fields: list[str] | None = None,
    record_count: int = 50,
    timeout_seconds: int = 30,
    target_dates: list[str] | None = None,
    site_name: str | None = None,
    export_csv_path: str | None = None,
) -> pd.DataFrame:
    out_fields = out_fields or DEFAULT_FIELDS
    target_dates = target_dates or DEFAULT_TARGET_DATES

    print(f"Connecting to: {base_url}")
    print(f"Requested fields: {', '.join(out_fields)}")
    if site_name:
        print(f"Site filter: {site_name}")

    all_dfs: list[pd.DataFrame] = []

    print("Targeted date queries")
    for date_str in target_dates:
        where = _build_where_for_date(date_str=date_str, site_name=site_name)
        params = _build_params(where=where, out_fields=out_fields, record_count=None)
        print(f"Query: {date_str} | where={where}")

        features = _fetch_features(base_url=base_url, params=params, timeout_seconds=timeout_seconds)
        df = _features_to_dataframe(features)
        all_dfs.append(df)

        print(f"Returned rows: {len(df)}")
        _print_matching_rows(
            df=df,
            date_str=date_str,
            site_name=site_name,
            fields_to_print=[
                "SiteName",
                "Sampling_Date",
                "QAQC_Complete",
                "chloridetest1",
                "chloridetest3",
                "chloridetest5",
                "Chloride_Blank_Final",
                "Chloride_Low1_Final",
                "Chloride_Low2_Final",
            ],
        )

    df_all = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    df_all = df_all.drop_duplicates() if not df_all.empty else df_all

    if df_all.empty:
        print("No rows returned across targeted queries.")
    else:
        print(f"Total unique rows across targeted queries: {len(df_all)}")

        print("Raw field presence check (on returned rows)")
        for field in out_fields:
            if field in df_all.columns:
                sample_values = df_all[field].head(5).tolist()
                print(f"Present: {field} | sample: {sample_values}")
            else:
                print(f"Missing: {field}")

        print("Date verification (on returned rows)")
        _verify_dates(df=df_all, target_dates=target_dates, site_name=site_name)

    if export_csv_path:
        df_all.to_csv(export_csv_path, index=False)
        print(f"Exported CSV: {export_csv_path}")

    return df_all


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ground-truth ArcGIS REST verification for raw titration records")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--fields",
        default="")
    parser.add_argument("--record-count", type=int, default=50)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument(
        "--target-dates",
        default="")
    parser.add_argument("--site-name", default=None)
    parser.add_argument("--export-csv", default=None)
    return parser.parse_args()


def _split_csv_arg(value: str, fallback: list[str]) -> list[str]:
    value = (value or "").strip()
    if not value or value == ",":
        return fallback
    return [v.strip() for v in value.split(",") if v.strip()]


if __name__ == "__main__":
    args = _parse_args()

    env_site_name = os.getenv("ARCGIS_SITE_NAME")
    site_name = args.site_name or env_site_name

    out_fields = _split_csv_arg(args.fields, DEFAULT_FIELDS)
    target_dates = _split_csv_arg(args.target_dates, DEFAULT_TARGET_DATES)

    verify_arcgis_connection(
        base_url=args.base_url,
        out_fields=out_fields,
        record_count=args.record_count,
        timeout_seconds=args.timeout_seconds,
        target_dates=target_dates,
        site_name=site_name,
        export_csv_path=args.export_csv,
    )
