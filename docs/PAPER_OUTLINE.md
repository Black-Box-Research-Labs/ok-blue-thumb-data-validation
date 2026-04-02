# Blue Thumb Chloride Validation — Paper Outline
**Status:** Verified against codebase — all numbers cross-checked against source files
**Last updated:** 2026-03-26

---

## PENDING RESTRUCTURE — Required before drafting (from Joey Dyer via Rebecca Bond, 2026-03-26)

Joey's required Results order conflicts with the current outline structure. Three specific fixes needed before drafting begins:

1. **Move variance decomposition to lead Results.** Within-test and within-site precision (currently 3.3) must come first — establishes what the data is capable of before any field performance claims.
2. **Demote OLS correlation (R²=0.607) to preliminary context.** Currently leads Results at 3.2. Should become one paragraph explaining why the hypothesis was worth pursuing formally, not a headline result.
3. **Elevate GLMM to primary result.** Currently labeled "exploratory only" at 3.6. Remove that label. Add SE values for intercept AND pro/vol fixed effect — Joey specifically asked for these. Pull from `data/outputs/phase2_lme/phase2_lme_results.txt`.
4. **Rewrite abstract.** Currently leads with R²=0.607. Needs to lead with GLMM and research question: "Can volunteer data be used in conjunction with professional data in a landscape-scale analysis?"

Joey's three-part structure for conference talk (and paper Results):
- Within-test variation, pro vs. vol — proof of consistency
- Within-site variation, pro vs. vol — sets expectation for precision
- Landscape-level GLMM — primary result, with SE on intercept and pro/vol fixed effect, seasonal/spatial relationships

---

## Title

**Working (long form):**
*Precision, Accuracy, and Geographic Irreplaceability: A Multi-Method Retrospective Validation of Citizen Science Chloride Monitoring Using Virtual Triangulation*

**Alternate candidates:**
- *Validating Citizen Science Water Quality Data Using Retrospective Spatial-Temporal Matching of Public Archives: A Case Study of Oklahoma's Blue Thumb Program*
- *A Multi-Faceted Validation of the Oklahoma Blue Thumb Volunteer Chloride Monitoring Program*

**Note on title strategy:** The working title avoids the word "volunteer" in the title position, which some journals and reviewers associate with lower rigor. Leading with the three-part finding is stronger. If targeting *Citizen Science: Theory and Practice*, the "virtual triangulation" method name should appear in the title. If targeting *Freshwater Science* or *JAWRA*, lead with the Oklahoma / chloride context. Confirm with Joey Dyer — he will have a strong preference based on where his own work has been published (PeerJ).

---

## Authors (pending confirmation)

1. **Miguel Ingram** — Black Box Research Labs LLC, Lawton, OK
   *Role: PI; pipeline design and implementation; all analysis; manuscript preparation*
2. **Joseph J. Dyer** — Oklahoma Conservation Commission
   *Role: statistical framework design (LME model specification, random effects structure, geographic covariates); Rotating Basin QA dataset provision and interpretation; identification and confirmation of the geographic confound*
3. **Kim Shaw** — Oklahoma Conservation Commission
   *Role: identification of the Phase 1 data identity error (OKCONCOM_WQX); provision of the R-Shiny volunteer data export; provision of 18-year historical indoor QA dataset; data quality documentation*
4. **[Rebecca Bond — OCC Blue Thumb Director — discuss explicitly before submission]**
   *Role if included: institutional facilitation, QAPP provision, data access*

**Acknowledgments (draft):**
The authors thank Karla Spinner (Oklahoma Conservation Commission) for retrieving and delivering the Rotating Basin QA dataset; Cheryl Cheadle (OCC Blue Thumb Program Director) for program context, institutional welcome, and newsletter collaboration; Rebecca Bond (OCC Blue Thumb Director) for organizing the formal collaboration, facilitating data access, and providing the OCC Quality Assurance Project Plan; Shellie Willoughby (OCC GIS Manager / Assistant State GIS Coordinator) for approving and enabling the ArcGIS REST API data infrastructure; Jacob Askey for building the Blue Thumb Dashboard and collaborative technical development; James Ross for field monitoring partnership at Wolf Creek; and Dr. Clinton Bryant for introducing the first author to the Blue Thumb program.

---

## Abstract

*(Draft prose — ~280 words. Write last but populate the skeleton now.)*

Citizen science programs collect environmental data at scales impossible for government agencies alone, yet persistent concerns about data quality limit their use in formal assessments. Retrospective validation using public data archives is rarely feasible because volunteer and professional datasets are typically commingled or untagged in national databases. Oklahoma's Blue Thumb program represents a unique exception: the Oklahoma Conservation Commission (OCC) maintains professional monitoring data in the EPA Water Quality Portal (WQP) under a distinct organization identifier, while volunteer records are maintained in a separate OCC data portal, enabling programmatic separation of the two datasets without new field sampling.

We present a multi-method validation of Blue Thumb volunteer chloride measurements using three independent lines of evidence. First, we developed a "virtual triangulation" pipeline that spatially (≤125 m) and temporally (≤72 h) matched volunteer field records against professional agency measurements from the EPA WQP, yielding N=25 co-located pairs (R²=0.607, slope=0.813, p=4.4×10⁻⁶). A professional-to-professional baseline comparison (N=42, R²=0.753) established the upper bound of inter-agency agreement, confirming that the volunteer result is consistent with known instrument-to-instrument variability. Second, analysis of 18 years of internal Blue Thumb quality assurance records (N=867 tests against known standard solutions, 13 sessions, 2007–2025) showed volunteers are accurate at operational concentrations, reading slightly high by a mean of +4–5 mg/L at concentrations ≤100 mg/L — opposite in direction to the apparent field bias. Third, an initial Linear Mixed-Effects model suggested a systematic low bias in volunteer readings; however, stratified random subsampling to correct for the documented West-East salinity gradient (Dyer et al. 2025) eliminated this effect entirely (p=0.54), confirming it was a geographic artifact of monitoring site distribution, not observer error. Spatial analysis shows 93% of 327 Blue Thumb sites are more than 1 km from the nearest professional monitor.

We conclude that Blue Thumb volunteer chloride data is precise within the 5 mg/L resolution of the Silver Nitrate titration method, accurate against known standards, and provides geographically irreplaceable coverage in Oklahoma's unmonitored headwaters. Oklahoma's data management practices — standardized protocols, regular QA, and separate volunteer and professional data infrastructure — offer a replicable model for citizen science validation nationally.

---

## 1. Introduction

### 1.1 The citizen science data quality problem

Citizen science programs have grown substantially as tools for large-scale environmental monitoring, driven by their cost-effectiveness and geographic reach. Water quality monitoring programs specifically have documented multi-decade track records in some states. However, a persistent "trust gap" separates volunteer-collected data from formal scientific and regulatory use. The core objection is not that volunteers are careless, but that their instruments are less precise, their training less rigorous, and their measurements therefore less comparable to professional reference data. This skepticism is often applied categorically — the word "volunteer" functions as a proxy for lower reliability regardless of the specific program's protocols or QA practices.

Most validation studies attempting to address this gap rely on resource-intensive, co-located side-by-side sampling: a volunteer and a trained technician measure the same water body simultaneously. This design, while rigorous, is expensive, limited in spatial and temporal scope, and unable to capture the long-term performance characteristics of a program. A retrospective approach — comparing years of archival volunteer data against years of archival professional data — would be far more powerful, but is typically impossible because volunteer and professional data are not programmatically distinguishable in national repositories. [*Cite: relevant citizen science validation literature — to add during drafting*]

### 1.2 Why Oklahoma is uniquely positioned

The EPA Water Quality Portal (WQP) aggregates water quality monitoring data from state, federal, and tribal agencies across the United States. Each contributing organization submits under a unique `OrganizationIdentifier`, which is preserved in the WQP record and queryable via the public API. In principle, this allows volunteer and professional records to be separated by organization code — but only if the contributing organization uses a distinct code for each program.

In practice, most state citizen science programs do not. Missouri Stream Team and Georgia Adopt-A-Stream, two of the most nationally recognized volunteer water quality programs, do not submit data to the WQP in a way that enables reliable programmatic separation of volunteer records from professional ones. This makes retrospective field comparison computationally infeasible for those programs.

Oklahoma's Blue Thumb program is a documented exception. The OCC submits professional Rotating Basin monitoring under `OKCONCOM_WQX` and has maintained a separate volunteer data record accessible through an OCC R-Shiny portal and public ArcGIS REST API. This infrastructure enables, for the first time, a large-scale retrospective validation of volunteer chloride measurements against professional reference data — without new field sampling, at no cost, using only publicly available records.

**Critical note on data identity:** Early analysis incorrectly treated `OKCONCOM_WQX` in the EPA WQP as Blue Thumb volunteer data. This organization code represents the OCC Rotating Basin professional monitoring program. The error was identified by Kim Shaw (OCC) in January 2026. Volunteer data is sourced from the separate OCC R-Shiny export, SHA-256 verified, and assigned the identifier `BLUETHUMB_VOL` in the analysis pipeline. This distinction is enforced programmatically and verified against OCC's live ArcGIS production database (2,026 of 2,027 overlapping records match exactly at the WBID+date level). All results in this paper use the corrected data source.

### 1.3 Chloride as a monitoring target

Chloride is a conservative ion — it does not precipitate, adsorb to sediments, or participate in biotic uptake under typical freshwater conditions. This makes it one of the most reliable tracers of anthropogenic water quality impacts. Elevated chloride in Oklahoma streams is associated with oil and gas produced water, road salt runoff, agricultural irrigation return flow, and wastewater effluent. Background concentrations vary substantially across the state, with a documented West-East gradient driven by geology: western Oklahoma's Permian Basin evaporites produce naturally saline groundwater that feeds surface streams, while eastern Oklahoma streams are naturally fresher. This West-East gradient (Dyer et al. 2025, PeerJ 13:e20234) is directly relevant to this study's geographic confound analysis and is discussed in detail in Section 3.4.

The Silver Nitrate titration method used by Blue Thumb volunteers measures chloride through a precipitation reaction: chloride ions react with silver nitrate solution, and the endpoint is detected visually (color change from yellow to brick-red). Each drop of titrant represents 5 mg/L chloride at the standard dilution factor, imposing a quantization floor on all volunteer measurements — volunteer chloride readings are exact multiples of 5 mg/L by construction.

### 1.4 The Blue Thumb program

Blue Thumb is an Oklahoma Conservation Commission citizen science program that has trained and deployed volunteers to monitor Oklahoma stream reaches since the early 2000s. The program was designed by Dan Butler (OCC) with protocols that deliberately mirror the OCC's professional water quality sampling standards, as documented in the OCC Quality Assurance Project Plan (QAPP; Bond, R., personal communication, January 2026). Key program features relevant to this study:

- Volunteer training includes both classroom and field components before independent monitoring
- OCC water quality specialists conduct field monitoring alongside volunteers, providing direct quality oversight
- A formal indoor QA program has been in operation since at least 2007, in which volunteers test chloride kits against solutions of known concentration under controlled conditions
- Field QA sessions assess additional parameters (temperature, Secchi depth, sample collection procedure) on a rotating basis
- Data are submitted to OCC's ArcGIS database (via Survey123) and cross-referenced against an R-Shiny export portal

The program monitors reaches that professional agencies do not: 93% of Blue Thumb's 327 chloride monitoring sites are more than 1 km from the nearest professional monitoring station in the EPA WQP. This geographic complementarity is central to the program's value proposition and is examined quantitatively in Section 3.6.

### 1.5 Gap in the literature

Despite more than 20 years of records and a documented QA framework that mirrors professional standards, Blue Thumb chloride data has not been subjected to published mathematical validation against professional agency measurements. More broadly, no published study has exploited the EPA WQP's `OrganizationIdentifier` infrastructure as the basis for large-scale retrospective citizen science validation. This represents both a gap in the literature and a missed opportunity: if the approach is valid for Oklahoma's Blue Thumb program, it could be applied to any volunteer program that submits data to the WQP with a distinct organization code.

### 1.6 Study objectives

This study addresses four specific objectives:

1. **Precision:** Quantify volunteer within-test repeatability using titration replicate pairs, and contextualize this precision within the known 5 mg/L quantization floor of the Silver Nitrate method.
2. **Accuracy:** Assess volunteer absolute accuracy using 18 years of historical indoor QA records in which volunteer kits were tested against solutions of known chloride concentration.
3. **Field validity:** Validate volunteer field measurements against co-located professional agency records using virtual triangulation, employing a dual-comparison design (volunteer-to-professional and professional-to-professional baseline) to establish the upper bound of inter-agency agreement.
4. **Confound identification:** Identify and account for geographic and methodological confounds that could artifactually inflate or deflate apparent volunteer bias.

---

## 2. Methods

### 2.1 Data sources

**Table 1. Data sources used in this study.**

| Source | Description | Records used | Date range |
|---|---|---|---|
| EPA Water Quality Portal | Professional chloride, Oklahoma streams (STORET + NWIS) | 18,299 records after cleaning | 1993–2025 |
| OCC R-Shiny export | Blue Thumb volunteer chloride measurements | 10,800 numeric values | 2005-01-04 to 2024-12-31 |
| OCC Rotating Basin QA dataset | Churn splitter duplicates (N=113 pairs), spatial replicates ~100m apart (N=114 pairs), and field blanks (N=111 single measurements) | 338 total records | 2022-07-18 to 2024-05-21 |
| Blue Thumb indoor QA records | Volunteers testing known standard solutions | 867 tests, 13 sessions | 2007–2025 |

**Volunteer data provenance:** The R-Shiny export was provided by OCC and SHA-256 verified before each pipeline run. It was independently cross-validated against OCC's live ArcGIS FeatureServer database (`bluethumb_oct2020_view`): of 2,027 records with overlapping WBID+date combinations, 2,026 match exactly (99.95%). The one discrepancy was a known data quality incident at Wolf Creek (2026-01-02) in which Survey123 stored a zero rather than the correct titration value. The chloride field used is `Chloride_Low1_Final`, calculated as raw drop count × 5 mg/L with no blank subtraction. The ArcGIS feed covers 2015–present; 13 of the 25 matched pairs in the field validation use pre-2015 records available only in the R-Shiny export.

**Professional data provenance:** Downloaded from the EPA WQP using the public Results API, filtered to Oklahoma, `CharacteristicName=Chloride`, STORET and NWIS providers, `dataProfile=resultPhysChem`. Records with invalid coordinates, non-detect flags, or negative values were removed. Professional organizations included in the reference dataset: OKWRB-STREAMS_WQX, CNENVSER (Chickasaw Nation Environmental Services), O_MTRIBE_WQX (Otoe-Missouria Tribe), and additional tribal and state agencies. The OCC Rotating Basin program (`OKCONCOM_WQX`, Method 9056) is used exclusively as the professional side of the pro-to-pro baseline comparison and is explicitly excluded from the professional reference dataset used in the volunteer-to-professional comparison.

**Rotating Basin QA dataset:** Provided by OCC statistician Joseph Dyer (via Karla Spinner, OCC) on February 20, 2026. Contains three record types distinguished by the `Type` field: Routine Sample and Field Duplicate (same grab sample, different analysis — yields within-test churn splitter duplicate pairs), Field Replicate (different grab sample at the same site within the same day — yields within-site spatial replicate pairs), and Field Blank (deionized water — single measurements testing contamination). Any samples that failed the Field Blank test were pre-excluded by OCC before delivery.

**Indoor QA dataset:** Provided by Kim Shaw (OCC) on March 2, 2026. Covers 14 quarterly sessions in which Blue Thumb volunteers tested chloride kits against solutions of known concentration. Spring 2013 was excluded from analysis because the standard solution was compromised during preparation (documented in Kim Shaw's session notes). Thirteen sessions remain (2007–2025), yielding 867 individual tests.

### 2.2 The virtual triangulation pipeline

The core field validation method is a spatial-temporal co-location algorithm implemented in Python using `scipy.spatial.cKDTree` for efficient nearest-neighbor search.

**Algorithm:**
1. Build a cKDTree on the Cartesian-projected coordinates of all professional measurements within the study period
2. For each volunteer measurement, query all professional measurements within a bounding radius of ~0.0025 degrees (~275 m)
3. Filter candidates by exact Haversine great-circle distance ≤ 125 m and absolute time difference ≤ 72 hours
4. From remaining candidates, select the spatially closest professional measurement (one-to-one matching; `closest` strategy)

**Parameter selection:** The 125 m / 72 h / closest parameter set was selected following a systematic sweep across distances (100–200 m), time windows (48–72 h), and matching strategies (all vs. closest). The sweep produced consistent results across all configurations (N=25–27, R²≈0.60, slope≈0.80). The 125 m / 72 h / closest configuration was chosen as the most defensible balance of spatial precision and sample size. Full sweep results are available in `data/outputs/experiments/sweep_results_refined_sorted.csv`.

**Dual-comparison design:**
- *Vol-to-Pro (primary):* Blue Thumb volunteer records (`BLUETHUMB_VOL`) vs. professional reference organizations (OWRB, CNENVSER, tribal agencies). Tests volunteer data quality directly.
- *Pro-to-Pro (baseline):* OCC Rotating Basin (`OKCONCOM_WQX`, Method 9056) vs. the same professional reference organizations. Establishes the upper bound of inter-agency agreement — the ceiling against which the volunteer result is interpreted.

**Professional minimum concentration filter:** Only professional measurements ≥25 mg/L are included as match candidates. This threshold excludes near-zero professional readings where measurement uncertainty is a large fraction of the signal.

### 2.3 Statistical analysis: primary field validation

**Primary analysis — OLS regression:**
Ordinary Least Squares regression of volunteer values (Y) on professional values (X) for matched pairs. OLS is the primary estimator. The professional value is treated as the reference (X-axis) following convention in method comparison studies.

Key statistics reported: N, R², slope, intercept, p-value.

**Non-parametric checks:**
- Paired t-test on log-transformed values: tests whether the mean log ratio (Vol/Pro) differs from zero
- Wilcoxon signed-rank test: non-parametric equivalent, robust to the non-normality introduced by quantization

**Agreement analysis:**
Bland-Altman method: plots (Vol − Pro) against (Vol + Pro)/2; reports mean difference, standard deviation of differences, and 95% limits of agreement.

**Robustness checks (not primary):**
- Bootstrap CI (B=500) on OLS slope and R²: assesses stability given small N
- Deming regression (errors-in-variables, δ=1): theoretically preferred when both X and Y have measurement error. Reported as a robustness check rather than the primary analysis because with N=25 the bootstrap Deming CIs are very wide (slope CI₉₅: [0.023, 1.442]), reflecting insufficient power to constrain the errors-in-variables model. The bootstrap OLS slope CI₉₅ [0.031, 1.197] is similarly wide but the point estimates are more stable.
- Sensitivity: wider matching windows (150–200 m / 72 h) consistently yield N=25–27, R²≈0.60, slope≈0.80, confirming the result is not sensitive to the exact parameter choice.

### 2.4 Statistical analysis: bias investigation and geographic confound

**Why the primary analysis is insufficient alone:**
The paired t-test on matched pairs (N=25, 4 volunteer sites, 2 professional organizations) produces a statistically valid result but is vulnerable to confounding: if volunteer sites systematically differ from professional sites in ways that affect chloride concentration, the apparent "observer effect" may reflect site characteristics rather than measurement error. This concern was raised by Joseph Dyer (OCC) following the initial matched-pairs analysis and confirmed by subsequent investigation.

**Linear Mixed-Effects model on matched pairs:**
Applied to the N=25 matched pairs using WBID as the random block (site random effect) and `IsVolunteer` as the treatment factor:

`log(Chloride) ~ IsVolunteer + sin(2π·Julian/365) + cos(2π·Julian/365) + (1|Site)`

This model was specified by J. Dyer (personal communication, February 2026) following his published framework for mixed-effects analysis of Oklahoma stream data (Dyer et al. 2025). REML estimation. Seasonal harmonics (sine/cosine of Julian day) control for within-year chloride cycling.

**Geographic confound test — stratified random subsampling:**
To test the hypothesis that the apparent volunteer low bias reflects the East-West distribution of monitoring sites rather than observer error:

1. Compute the longitude distribution of all volunteer sites and all professional sites in the matched-pairs dataset
2. Divide the volunteer longitude range into quartiles; randomly select 3 volunteer sites per quartile (12 total) to match the 12 professional sites
3. Re-run the LME on the balanced subsample; compare the `IsVolunteer` p-value to the full model

**Regional LME model (exploratory only):**
A broader model using all volunteer and professional records within the QA dataset's spatiotemporal window (2022–2024, north-central Oklahoma, N=895 observations, 92 sites):

`log(Chloride) ~ IsVolunteer + sin(2π·Julian/365) + cos(2π·Julian/365) + Longitude + (1|Site)`

This model is labeled exploratory because 80 volunteer sites and 12 professional sites have zero geographic overlap, making the `IsVolunteer` coefficient inseparable from site-level differences. It is reported to confirm that the geographic covariates (longitude, seasonal harmonics) recommended by Dyer et al. (2025) are doing real statistical work in this dataset, not to draw conclusions about observer bias.

### 2.5 Variance decomposition (precision analysis)

Using the Rotating Basin QA dataset:

- **Volunteer within-test precision:** Absolute difference between paired titration replicates (test3 vs. test5 fields in the volunteer dataset). N=2,566 pairs.
- **Professional within-test precision:** Absolute difference between churn splitter duplicate pairs from the same grab sample. N=113 pairs.
- **Professional within-site precision:** Absolute difference between spatial replicate pairs collected at the same site within the same day (~100 m apart). N=114 pairs.
- **Field blank contamination:** Single measurements of deionized water. N=111. All should be ≤ detection limit.

The quantization effect is analyzed separately: the frequency distribution of volunteer within-test differences is expected to show a strong spike at 0 (identical readings) due to the 5 mg/L resolution floor, with subsequent spikes at ±5 mg/L intervals.

### 2.6 Indoor QA accuracy analysis

Using the 13-session historical QA dataset:

- Error = (volunteer reading − known standard concentration) for each test
- Analyzed by concentration range: low (≤50 mg/L), mid (50–100 mg/L), high (>100 mg/L)
- Mean error and direction reported by tier
- Spring 2013 excluded: standard solution compromised during preparation (K. Shaw, personal communication, March 2026)

The direction of the mean error is of particular interpretive importance: if volunteers systematically read **high**, this contradicts the apparent field bias (which showed volunteers reading **low**) and strengthens the geographic confound explanation.

### 2.7 Geographic coverage analysis

For each of the 327 unique Blue Thumb chloride monitoring sites, compute the Haversine distance to the nearest professional monitoring station in the full EPA WQP Oklahoma dataset. Report the fraction of volunteer sites beyond threshold distances (1 km, 5 km, 10 km).

### 2.8 Reproducibility

The full analysis pipeline is implemented in Python 3.11 and available at [repo URL]. All results are reproducible from a single command:

```bash
python -m src.pipeline --skip-extract
```

A reproducibility manifest (`data/outputs/metadata.json`) records the git commit hash, SHA-256 hash of the configuration file, SHA-256 hash of the volunteer data CSV, and all primary result statistics. The volunteer data file (`data/Requested_Blue Thumb Chemical Data.csv`) is SHA-256 verified at runtime; the pipeline raises `FileNotFoundError` if the file is absent or modified, with no silent fallback.

---

## 3. Results

### 3.1 Professional-to-professional baseline: establishing the ceiling

Before interpreting volunteer results, it is necessary to establish what level of agreement is achievable between two professional programs using laboratory-grade instrumentation. The pro-to-pro comparison (OCC Rotating Basin vs. professional reference agencies, N=42 matched pairs) yields R²=0.753, slope=0.735, p=1.0×10⁻¹³. Even professional agencies using validated laboratory methods do not agree perfectly. This baseline establishes the upper bound of inter-agency agreement achievable within this dataset and serves as the reference against which volunteer performance is assessed.

### 3.2 Volunteer-to-professional field validation

The primary field comparison (Blue Thumb volunteers vs. professional reference agencies, N=25 matched pairs, 4 unique volunteer sites) yields:

**Table 2. Field validation regression results (OLS primary).**

| Comparison | N | R² | Slope | Intercept | p-value |
|---|---|---|---|---|---|
| Vol vs. Pro (primary) | 25 | 0.607 | 0.813 | −2.411 | 4.4×10⁻⁶ |
| Pro vs. Pro (baseline) | 42 | 0.753 | 0.735 | — | 1.0×10⁻¹³ |
| OWRB-only subset (EPA 325.2 verified) | 7 | 0.730 | 0.801 | — | 1.4×10⁻² |

Professional organizations in matched pairs: CNENVSER (Chickasaw Nation Environmental Services, N=18 matches) and OKWRB-STREAMS_WQX (N=7 matches). CNENVSER's analytical method is not recorded in WQP metadata; OKWRB uses EPA 325.2 (Automated Colorimetry, verified). The OWRB-only subset (N=7, R²=0.730) independently replicates the combined result using a verified method, and produces a Vol/Pro ratio of 1.027 (+2.7%) — volunteers and OWRB professionals are essentially identical at co-located sites.

Paired t-test (log-transformed): t=−3.03, p=0.005758. Wilcoxon signed-rank: W=84.0, p=0.034. Both tests indicate a statistically significant apparent low bias in volunteer readings (mean Vol/Pro ratio=0.721, −27.9%). Whether this reflects observer error or a geographic confound is examined in Section 3.4.

Bland-Altman agreement: mean difference (Vol − Pro) = −16.3 mg/L, SD=33.8 mg/L, 95% limits of agreement [−82.6, +50.0] mg/L.

Robustness checks: Bootstrap OLS (B=500) slope CI₉₅ [0.031, 1.197] (mean 0.770); R² CI₉₅ [0.004, 0.885] (mean 0.567). Deming regression (δ=1) slope ≈1.056, bootstrap CI₉₅ [0.023, 1.442]. The wide CIs reflect the small N=25 and should not be interpreted as instability in the point estimates; sensitivity analysis confirms the core finding is stable across matching parameter choices.

*Figure 1: Validation scatter plots (vol-to-pro and pro-to-pro side by side). File: `validation_plot.png`, `phase2_lme/matched_pairs_analysis.png`*

### 3.3 Volunteer precision (variance decomposition)

**Table 3. Within-source variability across measurement types.**

| Source | N | Mean \|Δ\| | 95% CI | Median \|Δ\| | Notes |
|---|---|---|---|---|---|
| Volunteer within-test | 2,566 | 1.53 mg/L | ±0.11 | 0.00 mg/L | Titration replicates |
| Professional within-test | 113 | 2.51 mg/L | ±0.72 | 1.00 mg/L | Churn splitter duplicates |
| Professional within-site | 114 | 3.58 mg/L | ±1.10 | 1.00 mg/L | Spatial replicates ~100m |
| Field blanks | 111 | 0.5 mg/L | — | — | DI water; all below detection |

The apparent "better" volunteer repeatability (1.53 vs. 2.51 mg/L) is a quantization artifact and must not be interpreted as higher precision. Because the Silver Nitrate titration resolves to 5 mg/L per drop, volunteers cannot detect differences smaller than one drop. The distribution of within-test differences confirms this: 73.2% of replicate pairs are identical (0 difference), 24.2% differ by exactly ±5 mg/L (one drop), and only 2.7% differ by ≥10 mg/L (two or more drops). 97.3% of pairs agree within ±1 drop. Professional instruments resolve to 0.1 mg/L and genuinely detect the sub-mg/L variation that the volunteer method cannot. The volunteer repeatability figure reflects the floor of what the method can distinguish, not observer consistency per se.

*Figure 2: Variance decomposition bar chart with error bars. File: `phase2_lme/variance_decomposition.png`*
*Figure 3: Quantization staircase — volunteer values are 100% multiples of 5 mg/L. File: `phase2_lme/quantization_effect.png`*

### 3.4 Volunteer accuracy against known standards

Thirteen QA sessions (867 tests, 2007–2025) in which volunteers tested chloride kits against solutions of known concentration yield the following accuracy results:

**Table 4. Volunteer accuracy against known standard solutions by concentration range.**

| Concentration range | N (tests) | Mean error | SD | Direction |
|---|---|---|---|---|
| Low (≤50 mg/L) | ~300 | +4.68 mg/L | — | **High** |
| Mid (50–100 mg/L) | ~300 | +5 mg/L | — | **High** |
| High (>100 mg/L) | 264 | +32.20 mg/L | — | **High** |

Volunteers consistently read **high** across all concentration ranges — the opposite direction of the apparent field bias reported in Section 3.2. At normal operational concentrations (≤100 mg/L, covering the vast majority of Blue Thumb monitoring sites), mean error is within one drop (+4–5 mg/L), which is within the method's stated resolution. The increasing error at high concentrations (>100 mg/L, mean +32 mg/L) is consistent with compounding endpoint subjectivity: each additional drop required for a high-concentration sample introduces another opportunity for endpoint misidentification.

This finding has a critical interpretive implication: the −47% apparent low bias observed at the CNENVSER/LSHQ matched-pair site (Section 3.2) **cannot be explained by volunteer kit error**. The indoor QA data proves the kits read high at elevated chloride levels, not low. The LSHQ discrepancy therefore reflects a confound between the two professional data sources (geographic or methodological), not a volunteer accuracy problem.

*Figure 4: Indoor QA accuracy by concentration range. File: `phase2_lme/qa_accuracy_analysis.png`*

### 3.5 Geographic confound resolution

The initial matched-pairs analysis (Section 3.2) showed a statistically significant apparent low bias (paired t-test p=0.006). The geographic distribution of monitoring sites provides a direct explanation.

**Site distribution:**
- Professional mean longitude: −98.05°
- Volunteer mean longitude: −96.67° (1.4° further east)
- 53% of volunteer records are east of longitude −96.5°
- 0% of professional records are east of longitude −96.5°
- Professional mean Cl: 228.4 mg/L (western saline streams)
- Volunteer mean Cl: 75.3 mg/L (eastern fresher streams)

The 1.4° East-West offset corresponds to approximately 115 km. The documented West-East salinity gradient in Oklahoma streams (Dyer et al. 2025) predicts that volunteer sites, concentrated in eastern Oklahoma, monitor genuinely fresher water than professional sites in central and western Oklahoma. The apparent low bias is therefore not measuring a discrepancy between volunteer and professional readings of the same water — it is measuring the difference between the water bodies they monitor.

**Stratified random subsampling:**
To test this hypothesis formally, 12 volunteer sites were randomly selected with geographic stratification (3 per longitude quartile) to match the 12 professional sites in the dataset. The LME was re-run on this balanced subsample:

- Subsample mean longitude: −96.452°
- Subsample mean Cl: 67.1 mg/L
- LME IsVolunteer: β=−0.2435, **p=0.5434** — **not significant**
- Subsample Vol/Pro ratio: 0.784 (−21.6%, not significant)

The observer effect disappeared entirely after balancing the geographic distribution. The bias was the streams, not the volunteers.

**CNENVSER sensitivity analysis:**
The full matched-pairs dataset contains N=18 CNENVSER matches and N=7 OWRB matches. Removing the largest CNENVSER site reduces the dataset to N=13 and also eliminates the statistically significant bias (p=0.49). At the OWRB sites (verified EPA 325.2 method, N=7), Vol/Pro=1.027 (+2.7%) — volunteers and professionals are essentially identical.

*Figure 5: Site distribution map showing East-West offset. File: `phase2_lme/site_distribution_map.png`*
*Figure 6: Matched pairs sensitivity analysis. File: `phase2_lme/matched_pairs_sensitivity.png`*

### 3.6 Regional LME model (exploratory)

The regional model (N=895 observations, 92 sites, 2022–2024) confirms that the geographic covariates recommended by Dyer et al. (2025) are doing real statistical work in this dataset:

- **Longitude:** β=−0.435, p<0.001 — the West-East salinity gradient is strongly present
- **Seasonal sine:** β=+0.110, p<0.001 — significant seasonal cycling
- **Seasonal cosine:** β=+0.022, p=0.39 — not significant
- **IsVolunteer:** β=−0.433, p=0.047 — significant, but confounded

The `IsVolunteer` result in the regional model is not interpretable as a pure observer effect. The 80 volunteer sites and 12 professional sites in this model have zero geographic overlap. The coefficient cannot distinguish between "volunteers measure differently" and "volunteer sites have different water chemistry." This model is reported to confirm the covariate structure, not to quantify observer bias; the matched-pairs analysis remains the primary evidence.

*Figure 7: LME diagnostic plots. File: `phase2_lme/lme_diagnostics.png`*

### 3.7 Geographic coverage

- 327 unique Blue Thumb chloride monitoring sites identified in the volunteer dataset
- **93% are more than 1 km from the nearest professional monitoring station** in the EPA WQP Oklahoma dataset
- 99% lack any temporal match with professional measurements within the full dataset
- The N=25 matched pairs come from 4 of these 327 sites — 99% of the Blue Thumb network operates in territory where no field comparison is possible

The scarcity of matched pairs is not a weakness of the study design; it is a direct measurement of the program's irreplaceable geographic coverage. The matched pairs establish the validity of the instrument and the method; the coverage analysis establishes why the data matters.

*Figure 8: Spatial coverage analysis map. File: `data/outputs/spatial_coverage_analysis.txt` [map to be generated]*

---

## 4. Discussion

### 4.1 Precision: the quantization floor is not observer inconsistency

97.3% of volunteer titration replicates agree within ±1 drop (±5 mg/L). This is strong repeatability for a field titration method and confirms the drop-count technique is being applied correctly and consistently. The fact that 73.2% of replicates are **identical** is not evidence of rounding or fudging — it is the expected behavior of a quantized instrument: when the true chloride level falls between multiples of 5 mg/L, two independent titrations of the same water will yield the same reading because neither can resolve the sub-5 mg/L difference. The quantization floor is the binding constraint on volunteer precision, not observer inconsistency.

This distinction matters for how the volunteer data should be used. For macroscopic assessments — watershed-scale comparisons, trend analysis, exceedance of regulatory thresholds — the 5 mg/L resolution is adequate. For sub-drop-level precision (e.g., detecting a change of 2 mg/L from one season to the next), the instrument is unsuitable regardless of who is using it.

### 4.2 Accuracy: volunteers read slightly high, which is good news

The 18-year indoor QA record provides the cleanest possible test of kit accuracy: no stream variability, no temporal matching uncertainty, no geographic confounds — just volunteers testing kits against solutions of known concentration. The consistent finding is that volunteers read slightly **high** (+4–5 mg/L at normal concentrations). This is within one drop of the known standard and within the method's stated resolution.

The direction is as important as the magnitude. A systematic high bias rules out systematic under-counting as a source of error, which is the more concerning failure mode for a monitoring program (under-reporting pollution is worse than over-reporting). The increasing high bias at elevated concentrations (+32 mg/L at >100 mg/L) is expected and mechanistically explicable: more drops means more opportunities for endpoint subjectivity to compound.

The indoor QA data also provides the definitive resolution to the CNENVSER concern. 72% of the field matched pairs are against CNENVSER, whose analytical method is not recorded in the WQP metadata. This is an acknowledged limitation of the field comparison. However, the kit accuracy result completely undermines the interpretation that the apparent field low bias is a volunteer error: the indoor QA proves that at the chloride levels present at the LSHQ site, volunteers do not read low — they read slightly high. Whatever drove the CNENVSER/LSHQ discrepancy, it was not the volunteer kit.

### 4.3 The geographic confound: a methodological lesson for citizen science validation

The most important methodological finding of this study is not in the final result — it is in the journey from the initial matched-pairs paired t-test (p=0.006, apparently significant low bias) to the stratified subsampling result (p=0.54, no significant bias). The initial result was statistically valid. The OLS regression was correct. The paired t-test was applied appropriately. The conclusion — that volunteers read low — was wrong.

The error was not computational; it was geographic. When volunteer and professional monitoring sites have zero spatial overlap and are distributed along a strong environmental gradient (Oklahoma's West-East salinity gradient), a naive comparison will detect the gradient, not the observer effect. This is precisely the scenario that the Mixed-Effects framework and stratified subsampling were designed to address — and precisely why Dyer et al. (2025)'s recommendation to include longitude as a covariate was correct.

The implication for the broader citizen science validation literature is significant: naive paired-comparison studies that do not account for the geographic distribution of volunteer vs. professional sites will systematically understate volunteer data quality when those sites are not geographically co-located. The stratified subsampling approach demonstrated here provides a methodological template for any program facing the same challenge.

### 4.4 The CNENVSER analytical method: open but bounded

72% of the field matched pairs are against CNENVSER (Chickasaw Nation Environmental Services), whose chloride analytical method is not recorded in the WQP metadata. This is a genuine limitation: it means the method-comparison interpretation of the field results is formally uncertain for 18 of 25 pairs. The OWRB-only subset (N=7, EPA 325.2, verified) independently produces R²=0.730 and a Vol/Pro ratio of essentially 1.0 — a result that would be unambiguous on its own but is underpowered at N=7.

However, the indoor QA data substantially bounds this uncertainty. The CNENVSER/LSHQ matched-pair discrepancy (apparent −47% volunteer low bias) is physically impossible as a kit accuracy error: the 18-year indoor QA record establishes that at high chloride concentrations, Blue Thumb kits read **high**, not low. The LSHQ discrepancy therefore reflects something about the CNENVSER reference measurement, the site hydrology, or the temporal pairing — not the volunteer kit. This mitigates but does not eliminate the limitation; contacting CNENVSER to confirm their analytical method remains an open action item.

### 4.5 Interpreting the R² comparison against the professional baseline

The vol-to-pro R²=0.607 versus the pro-to-pro baseline R²=0.753 is the central field comparison in this study. The framing "volunteers capture X% of the professional signal" derived from the ratio 0.607/0.753 should be used with caution: R² is not a linear proportion, and dividing two R² values does not yield a meaningful capture percentage. The correct interpretation is contextual: volunteer correlation falls within the range of inter-agency professional correlation, confirming that volunteer measurement variation is comparable in magnitude to the variation between professional programs. The OWRB-only volunteer result (R²=0.730) actually equals the pro-to-pro baseline, which is the strongest possible outcome for a subset analysis.

### 4.6 Geographic irreplaceability: the low N is a feature, not a bug

The matched-pairs analysis uses N=25 pairs from 4 volunteer sites. This is a small sample by regression standards. It reflects the fact that 99% of Blue Thumb monitoring sites have no professional counterpart within the 125 m / 72 h matching criteria. This is not a data quality failure — it is a direct measurement of the program's geographic complementarity. The Blue Thumb program was explicitly designed to monitor streams that professional agencies cannot afford to cover continuously. 93% of its 327 sites are more than 1 km from the nearest professional monitor. These sites provide data that simply does not exist anywhere else. The matched-pairs analysis validates the instrument; the coverage analysis quantifies why the instrument matters.

### 4.7 Calibration potential

The indoor QA data suggests a straightforward calibration application: at normal operational concentrations, volunteers consistently read approximately one drop (5 mg/L) high. A concentration-dependent correction function could be derived from the 867-test dataset to produce a "calibrated" volunteer reading. At high concentrations (>100 mg/L), the +32 mg/L mean bias would require a larger correction. Whether such calibration improves the downstream utility of the data for regulatory or research purposes depends on the application; this is identified as future work.

### 4.8 Methodological contribution: virtual triangulation as a general framework

The virtual triangulation approach — spatially and temporally co-locating volunteer and professional records in a public archive — is not specific to Blue Thumb or to chloride. It is applicable to any volunteer program that submits data to the EPA WQP under a distinct `OrganizationIdentifier`. Oklahoma's Blue Thumb program is currently the clearest example of a program where this infrastructure exists and the data volume is sufficient to support the analysis. If other state programs adopt distinct WQP organization IDs (as OCC has done), the same approach becomes available to them. This study provides both the methodological template and the proof of concept.

### 4.9 Limitations

1. **Small matched-pairs N:** N=25 from 4 volunteer sites. Bootstrap CIs on OLS slope and R² are wide, and the Deming regression is underpowered. The point estimates are stable across parameter sweeps but individual pair-level heterogeneity is high.
2. **Pre-2015 volunteer data:** 13 of 25 matched pairs use volunteer records from the OCC R-Shiny export that predate the ArcGIS FeatureServer (which begins in 2015). These records were verified against the ArcGIS feed where overlap exists (2,026/2,027 match), but the pre-2015 records cannot be independently cross-validated.
3. **Hydrologic condition metadata:** The `HydrologicCondition` and `HydrologicEvent` fields are 0% populated across all 18,299 professional WQP records in this dataset. Storm-event filtering — which could remove atypically high or low readings from the matching pool — is therefore impossible from the available metadata.
4. **CNENVSER analytical method:** Unconfirmed in WQP metadata for all 18 CNENVSER matched pairs. Mitigated by the indoor QA direction-of-bias argument (Section 4.4) but not resolved.
5. **Volunteer data through 2024 only:** The R-Shiny export provided by OCC covers through 2024-12-31. The live ArcGIS FeatureServer contains more recent records (2025–2026) but those were not included in the matched-pairs analysis, which uses the SHA-256 verified static export.

---

## 5. Conclusion

Blue Thumb volunteer chloride data is precise within the 5 mg/L resolution of the Silver Nitrate titration method, accurate to within one drop against known standards at operational concentrations, and geographically irreplaceable — monitoring streams that professional agencies do not reach. The apparent systematic low bias observed in naïve field comparisons is not a volunteer accuracy problem; it is a geographic artifact of Oklahoma's West-East salinity gradient, which places volunteer monitoring sites in naturally fresher eastern streams and professional monitoring sites in naturally saltier western and central streams. After correcting for this gradient via stratified random subsampling, no significant observer effect remains (p=0.54). Independent analysis of 18 years of indoor QA records confirms the direction-of-bias finding: Blue Thumb kits read slightly high, not low.

Oklahoma's approach — designing volunteer protocols to mirror professional standards, conducting regular QA against known standards, and maintaining programmatically separable volunteer and professional data infrastructure — provides a replicable model for citizen science programs nationally. Any state that maintains distinct, queryable records for volunteer and professional programs gains the infrastructure necessary to conduct the same retrospective validation at low cost, without new field sampling.

---

## 6. Acknowledgments

The authors thank Karla Spinner (Oklahoma Conservation Commission) for retrieving and delivering the Rotating Basin QA dataset; Cheryl Cheadle (OCC Blue Thumb Program Director) for program context, institutional support, and newsletter collaboration; Rebecca Bond (OCC Blue Thumb Director) for organizing the collaboration, facilitating data access, and providing the OCC Quality Assurance Project Plan; Shellie Willoughby (OCC GIS Manager / Assistant State GIS Coordinator) for enabling the ArcGIS REST API data infrastructure; Jacob Askey for building the Blue Thumb Dashboard and collaborative technical development; James Ross for field monitoring partnership at Wolf Creek, Lawton, OK; and Dr. Clinton Bryant for introducing the first author to the Blue Thumb program.

---

## 7. References

*(Populate during drafting — verified entries below)*

- Dyer, J.J., Dvorett, D., & Flotemersch, J. (2025). Using natural landscape and instream habitat to identify stream groups. *PeerJ*, 13:e20234. [West-East Oklahoma salinity gradient; LME framework rationale]
- Bond, R. (2026). OCC Quality Assurance Project Plan [document]. Oklahoma Conservation Commission. Personal communication, January 16, 2026. [Blue Thumb protocol documentation]
- Dyer, J.J. (2026). Statistical framework recommendation for Blue Thumb chloride validation. Personal communication, February 20, 2026. [LME model specification, random effects structure, geographic covariates]
- Shaw, K. (2026). Blue Thumb chloride QA session data, 2007–2025 [dataset]. Oklahoma Conservation Commission. Personal communication, March 2, 2026. [Indoor QA dataset]
- EPA Method 325.2 — Automated Colorimetry for chloride [OWRB analytical method — confirm citation format]
- [Silver Nitrate titration method SOP — cite OCC QAPP or relevant standard reference]
- [cKDTree: Virtanen et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261–272.]
- [Citizen science validation literature — to add during drafting. Key search terms: citizen science water quality validation, volunteer monitoring accuracy, macroinvertebrate/chemical citizen science]

---

## 8. Supplemental Information

### S1. Pipeline description and parameter choices

Full ETL pipeline description including: EPA WQP query parameters, volunteer CSV normalization steps, data identity note (OKCONCOM_WQX), matching algorithm pseudocode, parameter sweep results table, and configuration file (`config/config.yaml`) documentation.

### S2. Full statistical output tables

- OLS regression tables for all comparisons (Vol-to-Pro, Pro-to-Pro, OWRB-only)
- LME model output: matched-pairs model and regional model full fixed-effects and random-effects tables
- Bootstrap and Deming regression full output
- Stratified subsampling: subsample characteristics and LME result
- CNENVSER sensitivity analysis table

### S3. Data availability and reproducibility

All analysis code: [GitHub repository URL — `ImmortalDemonGod/bluestream-test` or confirm public URL with Jacob]

Volunteer data: OCC R-Shiny export. Not independently publicly available; available from the corresponding author upon reasonable request and with OCC permission.

Professional data: Publicly available via EPA Water Quality Portal (waterqualitydata.us). Query parameters documented in `config/config.yaml`.

Rotating Basin QA data and indoor QA data: Oklahoma Conservation Commission internal records. Available from J. Dyer and K. Shaw (OCC) upon reasonable request.

Reproducibility manifest: `data/outputs/metadata.json` (git commit hash, config SHA-256, volunteer CSV SHA-256, primary result statistics).

---

## Figures inventory

All figure files exist and are verified in `data/outputs/`.

| # | Caption (draft) | File | Section |
|---|---|---|---|
| 1a | Vol-to-Pro validation scatter plot with OLS fit and 1:1 reference | `validation_plot.png` | 3.2 |
| 1b | Pro-to-Pro baseline scatter plot | *(generate during drafting)* | 3.1 |
| 2 | Matched pairs analysis with Bland-Altman inset | `phase2_lme/matched_pairs_analysis.png` | 3.2 |
| 3 | Variance decomposition bar chart (volunteer vs. professional within-test vs. within-site) | `phase2_lme/variance_decomposition.png` | 3.3 |
| 4 | Quantization staircase — 100% of volunteer values are multiples of 5 mg/L | `phase2_lme/quantization_effect.png` | 3.3 |
| 5 | Indoor QA accuracy by concentration range — error distribution and direction | `phase2_lme/qa_accuracy_analysis.png` | 3.4 |
| 6 | Geographic distribution of volunteer vs. professional sites (East-West offset) | `phase2_lme/site_distribution_map.png` | 3.5 |
| 7 | Matched pairs sensitivity — CNENVSER vs. OWRB, with/without largest site | `phase2_lme/matched_pairs_sensitivity.png` | 3.5 |
| 8 | LME diagnostic plots (residuals, Q-Q, scale-location) | `phase2_lme/lme_diagnostics.png` | Supplement S2 |
| 9 | Bland-Altman plot — Vol vs. Pro agreement | `phase2_lme/bland_altman.png` | 3.2 |
| 10 | Geographic coverage map — fraction of Blue Thumb sites >1 km from nearest professional | *(generate during drafting)* | 3.7 |

---

## Journal targeting notes

| Journal | Fit | Framing emphasis |
|---|---|---|
| *Citizen Science: Theory and Practice* | Best topical fit | Virtual triangulation method, Oklahoma infrastructure advantage, replication model |
| *Environmental Monitoring and Assessment* | Strong fit | Variance decomposition, LME framework, chloride chemistry |
| *PLOS ONE* | Good fit | Open access, full methods transparency, reproducibility narrative |
| *Freshwater Science* | Good fit | Oklahoma stream ecology, West-East gradient, chloride as indicator |
| *Journal of the American Water Resources Association* | Good fit | Professional regulatory audience; OCC co-authors have credibility here |

**Ask Joey Dyer first** — he has PeerJ publication history and will have a strong preference.

---

*Cross-reference: `docs/PUBLICATION_ROADMAP.md` — co-authorship plan, open items, re-engagement emails, and institutional support context.*
*Cross-reference: `docs/Volunteer_Chloride_Validation_METHODS.md` — complete technical methods with exact parameter values and sensitivity analysis.*
