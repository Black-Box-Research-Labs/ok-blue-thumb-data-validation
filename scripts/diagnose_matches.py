#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

OUT_DIR = Path('data/outputs')
MATCHES = OUT_DIR / 'matched_pairs.csv'
VOL_PROCESSED = Path('data/processed/volunteer_chloride.csv')
PRO_PROCESSED = Path('data/processed/professional_chloride.csv')
BT_CSV = Path('data/Requested_Blue Thumb Chemical Data.csv')

def pct(x):
    return 100.0 * float(x)

def summarize_matches():
    if not MATCHES.exists():
        print(f'ERROR: {MATCHES} does not exist')
        return 1
    m = pd.read_csv(MATCHES)
    print('\n=== MATCHED PAIRS SUMMARY ===')
    print('rows:', len(m))
    print('vol_orgs:', dict(m['Vol_Organization'].value_counts()))
    print('pro_orgs_top:', dict(m['Pro_Organization'].value_counts().head(10)))
    print('distance_m: min/median/max =', m['Distance_m'].min(), m['Distance_m'].median(), m['Distance_m'].max())
    print('time_h:     min/median/max =', m['Time_Diff_hours'].min(), m['Time_Diff_hours'].median(), m['Time_Diff_hours'].max())

    # Basic correlation
    if len(m) >= 2:
        slope, intercept = np.polyfit(m['Pro_Value'].values, m['Vol_Value'].values, 1)
        r = np.corrcoef(m['Pro_Value'].values, m['Vol_Value'].values)[0,1]
        print('pearson_r =', float(r))
        print('r2        =', float(r*r))
        print('slope     =', float(slope))
        print('intercept =', float(intercept))

    # Quantiles
    for col in ['Vol_Value','Pro_Value']:
        q = m[col].quantile([0,0.25,0.5,0.75,1])
        print(f'{col} quantiles:', q.to_dict())

    # Per-organization correlation to detect cohort effects
    print('\n=== PER PRO_ORG DIAGNOSTICS ===')
    for org, g in m.groupby('Pro_Organization'):
        if len(g) >= 3:
            r = float(np.corrcoef(g['Pro_Value'].values, g['Vol_Value'].values)[0,1])
            slope = float(np.polyfit(g['Pro_Value'].values, g['Vol_Value'].values, 1)[0])
            print(f'org={org:25s} n={len(g):2d} r2={r*r:.3f} slope={slope:.3f}')
        else:
            print(f'org={org:25s} n={len(g):2d} (skip correlation)')

    # Per-site quick look (top sites by count)
    print('\n=== TOP VOL_SiteID BY COUNT ===')
    counts = m['Vol_SiteID'].value_counts()
    for sid, cnt in counts.head(10).items():
        sub = m[m['Vol_SiteID'] == sid]
        if len(sub) >= 3:
            r = float(np.corrcoef(sub['Pro_Value'].values, sub['Vol_Value'].values)[0,1])
            slope = float(np.polyfit(sub['Pro_Value'].values, sub['Vol_Value'].values, 1)[0])
            print(f'site={sid:20s} n={cnt:2d} r2={r*r:.3f} slope={slope:.3f}')
        else:
            print(f'site={sid:20s} n={cnt:2d}')

    # Show table
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print('\nHEAD (all rows since n is small):')
        print(m)

    return 0


def summarize_bt_csv():
    if not BT_CSV.exists():
        print(f'WARN: {BT_CSV} not found, skip BT CSV summary')
        return
    df = pd.read_csv(BT_CSV, low_memory=False)
    # Chloride numeric mask
    chl = pd.to_numeric(df.get('Chloride'), errors='coerce')
    n_all = len(df)
    n_num = int(chl.notna().sum())
    print('\n=== BLUE THUMB CSV (Chloride) ===')
    print('rows:', n_all, 'chloride_numeric_rows:', n_num)
    if n_num > 0:
        desc = chl.dropna().describe()
        print('chloride stats:', {k: float(desc[k]) for k in ['min','25%','50%','75%','max','mean','std']})
        # Check for five-multiple rounding indicative of kit resolution
        mul5 = (chl.dropna() % 5 == 0).mean()
        print('fraction values multiple of 5mg/L:', float(mul5))


def main():
    rc = summarize_matches()
    summarize_bt_csv()
    return rc

if __name__ == '__main__':
    raise SystemExit(main())
