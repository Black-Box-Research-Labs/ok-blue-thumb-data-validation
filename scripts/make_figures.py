#!/usr/bin/env python3
"""
make_figures.py - Generate the two figures added in revision:
  - primary_result_subsampling.png  (manuscript Figure fig:subsampling)
  - coverage_curve.png              (manuscript Figure fig:coverage)

Also writes data/outputs/phase2_lme/subsample_pvalues.csv, the committed per-draw
distribution behind the primary-result figure, so verify.py can check it.

Deterministic: fixed seed. Usage: python scripts/make_figures.py [n_iter] [seed]
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")

ROOT = Path(__file__).resolve().parent.parent
PHASE2 = ROOT / "data" / "outputs" / "phase2_lme"
LME_DF = PHASE2 / "lme_analysis_df.csv"
COVER = PHASE2 / "coverage_distances.csv"
PVALS = PHASE2 / "subsample_pvalues.csv"
FORMULA = "LogChloride ~ IsVolunteer + JulianSin + JulianCos + Longitude"
N_ITER = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 42


def prep(df):
    df = df.copy()
    df["IsVolunteer"] = (df["ObserverType"] == "Volunteer").astype(int)
    df["LogChloride"] = np.log(df["Chloride_mgL"])
    return df


def fit_isvol(df):
    m = smf.mixedlm(FORMULA, data=df, groups=df["Site"]).fit(reml=True)
    return m.params["IsVolunteer"], m.pvalues["IsVolunteer"]


def run_subsampling(df, n_iter, seed):
    pro = df[df.IsVolunteer == 0]
    vol = df[df.IsVolunteer == 1]
    vs = vol.groupby("Site")["Longitude"].mean().reset_index()
    vs["q"] = pd.qcut(vs["Longitude"], 4, labels=False)
    rng = np.random.default_rng(seed)
    ps, bs = [], []
    for _ in range(n_iter):
        picks = []
        for q in range(4):
            sq = vs.loc[vs.q == q, "Site"].to_numpy()
            picks += list(rng.choice(sq, size=min(3, len(sq)), replace=False))
        sub = pd.concat([pro, vol[vol.Site.isin(picks)]], ignore_index=True)
        try:
            m = smf.mixedlm(FORMULA, data=sub, groups=sub["Site"]).fit(reml=True)
            ps.append(m.pvalues["IsVolunteer"])
            bs.append(m.params["IsVolunteer"])
        except Exception:
            pass
    return np.array(ps), np.array(bs)


def fig_primary(df):
    full_beta, full_p = fit_isvol(df)
    if PVALS.exists():
        d = pd.read_csv(PVALS)
        pv, bv = d["p_value"].to_numpy(), d["coef"].to_numpy()
    else:
        pv, bv = run_subsampling(df, N_ITER, SEED)
        pd.DataFrame({"p_value": pv, "coef": bv}).to_csv(PVALS, index=False)
    frac_ns = float(np.mean(pv >= 0.05))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.5))
    a1.hist(pv, bins=40, range=(0, 1), color="#4c72b0", edgecolor="white")
    a1.axvspan(0, 0.05, color="#c44e52", alpha=0.15)
    a1.axvline(0.05, color="#c44e52", ls="--", lw=1.5, label="p = 0.05 threshold")
    a1.axvline(np.median(pv), color="black", ls=":", lw=1.5,
               label=f"median p = {np.median(pv):.2f}")
    a1.set_xlabel("IsVolunteer p-value (geographically balanced subsample)")
    a1.set_ylabel("Number of subsamples")
    a1.set_title(f"(A) {100*frac_ns:.1f}% of {len(pv):,} balanced subsamples non-significant")
    a1.legend(fontsize=8, loc="upper center")
    a1.text(0.97, 0.97, f"unbalanced regional model: p = {full_p:.3f}",
            transform=a1.transAxes, ha="right", va="top", fontsize=8, color="#c44e52")

    a2.hist(bv, bins=40, color="#55a868", edgecolor="white")
    a2.axvline(0, color="black", lw=1.2, label="no effect")
    a2.axvline(full_beta, color="#c44e52", ls="--", lw=1.5,
               label=f"unbalanced model ({full_beta:.2f})")
    a2.axvline(np.median(bv), color="black", ls=":", lw=1.5,
               label=f"median ({np.median(bv):.2f})")
    a2.set_xlabel("IsVolunteer coefficient (geographically balanced subsample)")
    a2.set_ylabel("Number of subsamples")
    a2.set_title("(B) Effect shrinks toward zero after geographic balancing")
    a2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(PHASE2 / "primary_result_subsampling.png", dpi=300)
    plt.close(fig)
    print(f"wrote primary_result_subsampling.png (N={len(pv)}, frac non-sig={frac_ns:.3f})")


def fig_coverage():
    cov = pd.read_csv(COVER)
    d = np.sort(cov["nearest_professional_km"].to_numpy())
    n = len(d)
    grid = np.linspace(0, min(float(d.max()), 60), 500)
    frac = np.array([100 * np.mean(d > g) for g in grid])

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.5))
    a1.plot(grid, frac, color="#4c72b0", lw=2)
    for t in (1, 5, 10):
        f = 100 * np.mean(d > t)
        a1.plot(t, f, "o", color="#c44e52")
        a1.annotate(f"{f:.0f}% > {t} km", (t, f),
                    textcoords="offset points", xytext=(8, 4), fontsize=8)
    a1.set_xlabel("Distance to nearest professional monitor (km)")
    a1.set_ylabel("% of volunteer sites beyond this distance")
    a1.set_title(f"(A) Geographic coverage: {n} Blue Thumb chloride sites")
    a1.set_ylim(0, 100)
    a1.grid(alpha=0.3)

    a2.hist(d[d <= 60], bins=40, color="#4c72b0", edgecolor="white")
    a2.axvline(1, color="#c44e52", ls="--", lw=1.5, label="1 km")
    a2.set_xlabel("Distance to nearest professional monitor (km)")
    a2.set_ylabel("Number of volunteer sites")
    a2.set_title("(B) Distribution of nearest-professional distance")
    a2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(PHASE2 / "coverage_curve.png", dpi=300)
    plt.close(fig)
    print(f"wrote coverage_curve.png ({n} sites)")


def main():
    df = prep(pd.read_csv(LME_DF))
    fig_primary(df)
    fig_coverage()


if __name__ == "__main__":
    main()
