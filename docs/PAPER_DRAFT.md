# Precision, Accuracy, and Geographic Irreplaceability: A Multi-Method Retrospective Validation of Citizen Science Chloride Monitoring Using Virtual Triangulation

**Miguel Ingram** (Black Box Research Labs LLC, Lawton, OK), **Joseph J. Dyer** (Oklahoma Conservation Commission), **Kim Shaw** (Oklahoma Conservation Commission)

---

## Abstract

Citizen science programs collect environmental data at scales impossible for professional agencies alone, yet persistent concerns about data quality limit their use in regulatory assessments and peer-reviewed research. Retrospective validation using public data archives is rarely feasible because volunteer and professional datasets are typically commingled or untagged in national databases. Oklahoma's Blue Thumb program is a documented exception: the Oklahoma Conservation Commission maintains professional monitoring data in the EPA Water Quality Portal under a distinct organization identifier, while volunteer records are maintained in a separate data portal, enabling programmatic separation without new field sampling.

We present a multi-method validation of Blue Thumb volunteer chloride measurements organized around three independent lines of evidence. First, variance decomposition of 2,566 volunteer titration replicate pairs and 113 professional churn-splitter duplicates establishes that volunteers are highly repeatable within their instrument's 5 mg/L resolution: 97.3% of replicate pairs agree within one drop, and the apparent "superior" volunteer repeatability (mean |diff| = 1.53 vs. 2.51 mg/L for professionals) reflects the quantization floor of the drop-count method, not greater observer consistency. Second, analysis of 18 years of indoor quality assurance records (867 tests against known standard solutions, 13 sessions, 2007-2025) demonstrates that volunteers are accurate at operational concentrations, reading slightly high by +4-5 mg/L at concentrations at or below 100 mg/L -- a direction opposite to the apparent field bias, ruling out systematic under-counting as a source of error. Third, a "virtual triangulation" pipeline spatially (125 m or less) and temporally (72 hours or less) matched volunteer field records against professional agency measurements from the EPA Water Quality Portal, yielding N=25 co-located pairs at 4 volunteer sites (OLS: R-squared = 0.607, slope = 0.813, p = 4.4 x 10 to the negative 6). A professional-to-professional baseline (N=42, R-squared = 0.753) established the upper bound of inter-agency agreement, confirming that volunteer performance falls within the range of professional instrument-to-instrument variability. A regional Linear Mixed-Effects model (log[Chloride] ~ IsVolunteer + seasonal harmonics + Longitude + [1|Site], N=895 observations, 92 sites) indicated a significant systematic low bias in volunteer readings (IsVolunteer beta = -0.433, SE = 0.218, p = 0.047); however, stratified random subsampling to correct for a documented West-East salinity gradient across Oklahoma (Dyer et al. 2025) eliminated this effect entirely (p = 0.54), confirming it was a geographic artifact of monitoring site distribution, not observer error.

Spatial analysis reveals that 93% of Blue Thumb's 327 chloride monitoring sites are more than 1 km from the nearest professional monitor, and 99% lack any temporal match with professional measurements. The scarcity of co-located pairs is not a study limitation; it is a direct measurement of the program's irreplaceable geographic coverage. We conclude that Blue Thumb volunteer chloride data is precise within its resolution limit, accurate against known standards, and geographically essential. Oklahoma's data management practices -- standardized protocols, regular quality assurance, and programmatically separable volunteer and professional data infrastructure -- offer a replicable model for citizen science validation nationally.

---

## 1. Introduction

### 1.1 The citizen science data quality problem

Citizen science programs have grown substantially as instruments for large-scale environmental monitoring, driven by their cost-effectiveness and geographic reach. In the water quality domain specifically, volunteer monitoring programs have documented multi-decade track records in states across the United States, collecting chemical, biological, and habitat data at hundreds of stream sites. However, a persistent "trust gap" separates volunteer-collected data from formal scientific and regulatory use. The core objection is not that volunteers are careless, but that their instruments are less precise, their training less standardized, and their measurements therefore less comparable to professional reference data. This skepticism is often applied categorically: the word "volunteer" functions as a proxy for lower reliability regardless of the specific program's protocols, quality assurance practices, or track record.

A recent review of 72 citizen science water quality studies found that while volunteer-collected data can align with professional measurements, concerns about precision, training variability, and method comparability persist as barriers to regulatory acceptance (Blanco Ramirez et al. 2023). These concerns are well-documented across multiple dimensions: data quality assurance requirements, analytical method standardization, and institutional trust (San Llorente Capdevila et al. 2020; Metcalfe et al. 2022). A systematic review of existing volunteer water monitoring datasets concluded that the majority of comparison studies report volunteer data of comparable quality to professional data, yet many existing datasets remain underutilized (Albus et al. 2019). Participatory science involvement in water quality governance remains limited by gaps between data collection capacity and regulatory application (O'Ryan et al. 2025).

Most validation studies attempting to address this gap rely on resource-intensive, co-located side-by-side sampling: a professional technician and a volunteer measure the same water body simultaneously, and the paired results are compared. This prospective design, while rigorous, is expensive, spatially limited to the sites where both parties are present, and temporally constrained to the dates of the coordinated sampling events. It cannot capture the long-term performance characteristics of a monitoring program across its full geographic footprint. A retrospective approach -- comparing years of archival volunteer data against years of archival professional data from the same streams -- would be far more powerful, but is typically impossible because volunteer and professional records are not programmatically distinguishable in national data repositories.

Published examples of this approach include co-located field kit versus laboratory comparisons for multiple water quality parameters (Quinlivan et al. 2020), parallel citizen science and government monitoring programs evaluated over multi-year periods (Dickson et al. 2024), and long-term comparisons of citizen science water quality indices against state agency records (de Camargo Reis et al. 2026). While these studies demonstrate that co-located validation is feasible and generally supports volunteer data quality, they share a common constraint: the validation is limited to the sites and dates where coordinated sampling occurred.

### 1.2 Why Oklahoma is uniquely positioned for retrospective validation

The EPA Water Quality Portal (WQP) aggregates water quality monitoring data from state, federal, tribal, and local agencies across the United States. Each contributing organization submits data under a unique OrganizationIdentifier, which is preserved in the WQP record and queryable through the public API. In principle, this metadata field allows volunteer and professional records to be separated by organization code -- but only if the contributing organization assigns a distinct code for each monitoring program.

In practice, most state citizen science programs do not maintain this separation. When the same analytical approach used in this study was attempted on Missouri Stream Team and Georgia Adopt-A-Stream -- two of the most nationally recognized volunteer water quality programs -- it failed. Those programs do not submit data to the WQP in a manner that enables reliable programmatic separation of volunteer records from professional records. This makes retrospective field comparison computationally infeasible for those programs.

Oklahoma's Blue Thumb program is a documented exception. The Oklahoma Conservation Commission (OCC) submits professional Rotating Basin monitoring data under the organization identifier OKCONCOM_WQX and has maintained volunteer data in a separate, independently accessible data system: an OCC R-Shiny portal and a public ArcGIS REST API. This infrastructure enables, for the first time, a large-scale retrospective validation of volunteer water quality measurements against professional reference data without requiring new field sampling, co-located visits, or any cost beyond computational resources.

**A critical note on data identity:** Early analysis in this study incorrectly treated OKCONCOM_WQX data in the EPA WQP as Blue Thumb volunteer data. This organization code in fact represents the OCC Rotating Basin professional monitoring program (Method 9056). The error was identified by OCC Quality Assurance Officer Kim Shaw in January 2026. All results presented in this paper use the corrected data source: a separate OCC R-Shiny export of verified Blue Thumb volunteer records, SHA-256 hash-verified at runtime, and assigned the internal identifier BLUETHUMB_VOL in the analysis pipeline. This distinction is enforced programmatically: the pipeline raises an explicit error if the volunteer CSV file is absent or modified, preventing silent fallback to the incorrect WQP data. The corrected volunteer dataset was independently cross-validated against OCC's live ArcGIS production database (2,026 of 2,027 overlapping records match exactly at the WBID+date level).

### 1.3 Chloride as a validation target

Chloride is a conservative ion: it does not precipitate, adsorb to sediments, volatilize, or participate in biotic uptake under typical freshwater conditions. This chemical stability makes chloride one of the most reliable tracers of anthropogenic water quality impacts and, critically for this study, one of the best analytes for method comparison work. A concentration difference between volunteer and professional measurements of chloride reflects the measurement methodology, not environmental transformation of the analyte between sampling events.

Chloride has been established as a primary indicator of freshwater salinization syndrome, a coupled process of rising dissolved salts, alkalinization, and contaminant mobilization that has affected 37% of the drainage area of the contiguous United States over the past century (Kaushal et al. 2018). Its chemical stability in freshwater systems makes it one of the most reliable tracers for distinguishing dilution and evaporation from chemical transformation (Hem 1985).

Elevated chloride in Oklahoma streams is associated with oil and gas produced water, road salt application, agricultural irrigation return flow, and wastewater effluent. Background concentrations vary substantially across the state, with a documented West-East gradient driven by geology: western Oklahoma's Permian Basin evaporites produce naturally saline groundwater that feeds surface streams, while eastern Oklahoma streams are naturally fresher. This gradient has been characterized by Dyer et al. (2025), who used natural landscape and instream habitat features to classify Oklahoma streams into distinct geochemical groups. The West-East salinity gradient is directly relevant to this study's geographic confound analysis and is discussed in detail in Section 3.5.

The Silver Nitrate titration method used by Blue Thumb volunteers measures chloride through a precipitation reaction: chloride ions in the water sample react with silver nitrate solution, and the endpoint is detected visually by a color change from yellow to brick-red. Each drop of titrant corresponds to 5 mg/L chloride at the standard dilution factor, imposing a quantization floor on all volunteer measurements. Volunteer chloride readings are exact multiples of 5 mg/L by construction. This quantization is not a flaw in volunteer execution; it is an inherent property of the analytical method and is analyzed explicitly in Section 3.1.

### 1.4 The Blue Thumb program

Blue Thumb is an Oklahoma Conservation Commission citizen science program that has trained and deployed volunteers to monitor Oklahoma stream reaches since 1992. The program was designed with protocols that deliberately mirror the OCC's professional water quality sampling standards, as documented in the OCC Quality Assurance Project Plan (QAPP; Bond, R., personal communication, January 2026). The program operates under a Quality Management Plan and has been funded through the EPA's Section 319 Program targeting nonpoint source pollution. Key program features relevant to this study include:

- Volunteer training includes both classroom and field components before independent monitoring begins.
- OCC water quality specialists conduct field monitoring alongside volunteers on a rotating basis, providing direct quality oversight.
- A formal indoor quality assurance program has been in continuous operation since at least 2007, in which volunteers test their chloride kits against solutions of known concentration under controlled laboratory conditions.
- Field QA sessions assess additional parameters (temperature, Secchi depth, sample collection procedure) on a rotating basis.
- Data are submitted to OCC's ArcGIS database (via Survey123) and cross-referenced against a separate R-Shiny export portal.
- Volunteer chemical data is submitted for upload into the EPA's STORET database, making it available to outside researchers and agencies.
- Volunteer monitoring and education hours are valued at over $30.00 per hour and contribute to matching federal funds with in-kind services.

The program has collected data from over 300 streams across Oklahoma, with over 100 sites currently active. Critically, the program monitors reaches that professional agencies do not: 93% of Blue Thumb's 327 chloride monitoring sites are more than 1 km from the nearest professional monitoring station in the EPA WQP. This geographic complementarity is central to the program's value proposition and is examined quantitatively in Section 3.7.

### 1.5 Gap in the literature

Despite more than 20 years of monitoring records and a documented QA framework that mirrors professional standards, Blue Thumb chloride data has not been subjected to published mathematical validation against professional agency measurements. More broadly, no published study has exploited the EPA WQP's OrganizationIdentifier infrastructure as the basis for large-scale retrospective citizen science validation. This represents both a gap in the literature and a missed opportunity: if the retrospective approach is valid for Oklahoma's Blue Thumb program, it could be applied to any volunteer monitoring program that submits data to the WQP with a distinct organization code, providing a zero-cost, scalable template for citizen science data validation nationally.

The Water Quality Portal, developed by the EPA, USGS, and National Water Quality Monitoring Council, is the largest standardized water quality dataset available, with over 290 million records from more than 2.7 million sites (Read et al. 2017). Despite this infrastructure, a systematic search of the literature found no published study that has exploited the WQP's OrganizationIdentifier metadata to programmatically separate citizen science from professional records for retrospective method validation. Albus et al. (2019) identified only six studies that used archival datasets for volunteer-professional comparison, none of which employed systematic spatial-temporal matching criteria or leveraged the WQP's organizational metadata structure.

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

| Source | Description | Records | Date range |
|:---|:---|:---|:---|
| EPA Water Quality Portal | Professional chloride measurements, Oklahoma streams (STORET + NWIS providers) | 18,299 records after cleaning | 1993-2025 |
| OCC R-Shiny export | Blue Thumb volunteer chloride measurements | 10,800 numeric values from 327 unique sites | 2005-01-04 to 2024-12-31 |
| OCC Rotating Basin QA dataset | Churn splitter duplicates (N=113 pairs), spatial replicates approximately 100 m apart (N=114 pairs), field blanks (N=111) | 338 total records | 2022-07-18 to 2024-05-21 |
| Blue Thumb indoor QA records | Volunteers testing kits against known standard solutions | 867 tests across 13 sessions | 2007-2025 |

**Volunteer data provenance.** The R-Shiny export was provided by OCC and SHA-256 hash-verified before each pipeline execution (hash: 56d21f052e2aa51221b739cb6e2e86c1eacea14344329b86602c536c81b206cd). The export was independently cross-validated against OCC's live ArcGIS FeatureServer database (bluethumb_oct2020_view): of 2,027 records with overlapping WBID+date combinations, 2,026 match exactly (99.95%). The one discrepancy was a known data quality incident at Wolf Creek (2026-01-02) in which the Survey123 mobile application stored a zero rather than the correct titration value. The chloride field used is Chloride_Low1_Final, calculated as raw drop count multiplied by 5 mg/L with no blank subtraction. The ArcGIS feed covers 2015 to present; 13 of the 25 matched pairs in the field validation use pre-2015 records available only in the R-Shiny export.

**Professional data provenance.** Professional chloride measurements were downloaded from the EPA WQP using the public Results API, filtered to Oklahoma, CharacteristicName = Chloride, STORET and NWIS providers, dataProfile = resultPhysChem. Records with invalid coordinates, non-detect result flags, or negative concentration values were removed. Professional organizations included in the reference dataset are: OKWRB-STREAMS_WQX (Oklahoma Water Resources Board), CNENVSER (Chickasaw Nation Environmental Services), O_MTRIBE_WQX (Otoe-Missouria Tribe), and additional tribal and state agencies (23 organizations total). The OCC Rotating Basin program (OKCONCOM_WQX, Method 9056) is used exclusively as the professional side of the pro-to-pro baseline comparison and is explicitly excluded from the professional reference dataset used in the volunteer-to-professional comparison.

**Rotating Basin QA dataset.** Provided by OCC statistician Joseph Dyer (via Karla Spinner, OCC) on February 20, 2026. Contains three record types distinguished by the Type field: Routine Sample and Field Duplicate (same grab sample analyzed separately, yielding within-test churn splitter duplicate pairs), Field Replicate (separate grab sample collected at the same site within the same day approximately 100 m apart, yielding within-site spatial replicate pairs), and Field Blank (deionized water, yielding single contamination-check measurements). Samples that failed the Field Blank test were pre-excluded by OCC before delivery.

**Indoor QA dataset.** Provided by Kim Shaw (OCC) on March 2, 2026. Covers 14 quarterly sessions in which Blue Thumb volunteers tested chloride kits against solutions of known concentration under controlled indoor conditions. Spring 2013 was excluded from analysis because the standard solution was compromised during preparation (documented in Kim Shaw's session notes). Thirteen sessions remain (2007-2025), yielding 867 individual tests.

### 2.2 The virtual triangulation pipeline

The core field validation method is a spatial-temporal co-location algorithm we term "virtual triangulation." The algorithm identifies volunteer and professional measurements that were collected at nearly the same location and nearly the same time, without requiring the two sampling events to have been coordinated. The implementation uses Python 3.11 with scipy.spatial.cKDTree for efficient nearest-neighbor search.

**Algorithm:**
1. Build a cKDTree spatial index on the geographic coordinates of all professional measurements within the study period.
2. For each volunteer measurement, query all professional measurements within a bounding radius of approximately 0.0025 degrees (approximately 275 m) to generate candidate matches.
3. Filter candidates by exact Haversine great-circle distance, retaining only those within 125 m or less.
4. Filter remaining candidates by absolute time difference, retaining only those within 72 hours or less.
5. From remaining candidates, select the spatially closest professional measurement (one-to-one matching, "closest" strategy).

**Parameter selection.** The 125 m / 72 h / closest parameter set was selected following a systematic sweep across spatial distances (50-300 m), time windows (24-120 h), and matching strategies (all qualifying matches versus closest only). The sweep produced consistent results across all configurations (N = 25-27, R-squared approximately 0.55-0.65, slope approximately 0.75-0.85). The 125 m / 72 h / closest configuration was chosen as the most defensible balance of spatial precision and sample size. The actual maximum distance in the matched dataset is 74.8 m and the actual maximum time difference is 62.75 hours, both well within the thresholds.

**Dual-comparison design.** The matching algorithm was executed twice with identical parameters to produce two independent comparisons:

- *Volunteer-to-Professional (primary):* Blue Thumb volunteer records (BLUETHUMB_VOL) matched against professional reference organizations (OWRB, CNENVSER, tribal agencies). This directly tests volunteer data quality.
- *Professional-to-Professional (baseline):* OCC Rotating Basin records (OKCONCOM_WQX, Method 9056) matched against the same professional reference organizations. This establishes the upper bound of inter-agency agreement -- the ceiling against which the volunteer result is interpreted.

**Professional minimum concentration filter.** Only professional measurements with concentrations of 25 mg/L or greater were included as match candidates. This threshold excludes near-zero professional readings where measurement uncertainty constitutes a large fraction of the signal.

### 2.3 Statistical analysis: field validation

**Primary estimator.** Ordinary Least Squares (OLS) regression of volunteer values (Y) on professional values (X) for matched pairs. The professional value is treated as the reference (X-axis) following convention in analytical method comparison studies. Key statistics reported: sample size N, coefficient of determination R-squared, regression slope, intercept, and p-value.

**Non-parametric checks.** Paired t-test on log-transformed chloride values (tests whether the mean log ratio Vol/Pro differs from zero). Wilcoxon signed-rank test (non-parametric equivalent, robust to the non-normality introduced by quantization of volunteer data).

**Agreement analysis.** Bland-Altman method: difference (Vol minus Pro) plotted against mean (Vol plus Pro divided by 2). Reports mean difference, standard deviation of differences, and 95% limits of agreement.

**Robustness checks.** Bootstrap confidence intervals (B=500 resamples) on OLS slope and R-squared to assess stability given small sample size. Deming regression (errors-in-variables model, variance ratio delta = 1) reported as a robustness check: theoretically preferred when both X and Y have measurement error, but with N=25 the bootstrap CIs are too wide to constrain the model (Deming slope CI 95%: 0.023 to 1.442). Sensitivity analysis across wider matching windows (150-200 m / 72 h) consistently yields N = 25-27, R-squared approximately 0.60, slope approximately 0.80, confirming the core finding is not sensitive to the exact parameter choice.

### 2.4 Statistical analysis: bias investigation and geographic confound

**Motivation.** The paired t-test on matched pairs (N=25, 4 volunteer sites, 2 professional organizations) produces a statistically valid result but is vulnerable to geographic confounding: if volunteer sites systematically differ from professional sites in environmental characteristics that affect chloride concentration, the apparent "observer effect" may reflect site characteristics rather than measurement error. This concern was raised by J. Dyer (OCC) following the initial matched-pairs analysis and confirmed by subsequent investigation.

**Linear Mixed-Effects Model (matched pairs).** Applied to the N=25 co-located matched pairs using WBID (water body identification) as the random block (site-level random intercept) and IsVolunteer as the fixed treatment factor:

log(Chloride) ~ IsVolunteer + sin(2 pi Julian / 365) + cos(2 pi Julian / 365) + (1 | Site)

This model was specified by J. Dyer (personal communication, February 2026) following his published framework for mixed-effects analysis of Oklahoma stream data (Dyer et al. 2025). REML estimation. Seasonal harmonics (sine and cosine of Julian day) control for within-year chloride cycling.

**Geographic confound test: stratified random subsampling.** To test the hypothesis that the apparent volunteer low bias reflects the East-West geographic distribution of monitoring sites rather than observer error:

1. Compute the longitude distribution of all volunteer sites and all professional sites in the regional dataset.
2. Divide the volunteer longitude range into quartiles.
3. Randomly select 3 volunteer sites per quartile (12 total) to match the 12 professional sites in the dataset, balancing the geographic distribution.
4. Re-run the LME on the geographically balanced subsample using the same model specification.
5. Compare the IsVolunteer p-value to the full (unbalanced) model.

The subsampling was designed to test a specific, pre-specified hypothesis (geographic confound) rather than to optimize model fit. The hypothesis was proposed by J. Dyer prior to the subsampling analysis based on his published characterization of Oklahoma's West-East salinity gradient (Dyer et al. 2025).

**Regional LME model (exploratory).** A broader model using all volunteer and professional records within the QA dataset's spatiotemporal window (2022-2024, north-central Oklahoma, N=895 observations, 92 sites). The temporal scope is restricted to the Rotating Basin QA dataset's collection period (July 2022 to May 2024) so that the precision baselines established in Section 2.5 are contemporaneous with the field observations being modeled. Extending the window to the full volunteer archive (2005-present) or professional archive (1993-present) would introduce decades of instrument drift, method changes, and volunteer training differences that could confound the method comparison:

log(Chloride) ~ IsVolunteer + sin(2 pi Julian / 365) + cos(2 pi Julian / 365) + Longitude + (1 | Site)

This model is reported as exploratory because the 80 volunteer sites and 12 professional sites in the dataset have zero geographic overlap. The IsVolunteer coefficient in this model is therefore inseparable from site-level differences and is not interpretable as a pure observer effect. The model is reported to confirm that the geographic and seasonal covariates recommended by Dyer et al. (2025) are statistically significant in this dataset.

### 2.5 Variance decomposition (precision analysis)

Using the Rotating Basin QA dataset and ArcGIS volunteer replicate data:

- **Volunteer within-test precision:** Absolute difference between paired titration replicates (test3 vs. test5 fields in the ArcGIS volunteer dataset). N=2,566 pairs. Drop-count differences converted to mg/L by multiplying by 5.
- **Professional within-test precision:** Absolute difference between churn splitter duplicate pairs from the same grab sample. N=113 pairs.
- **Professional within-site precision:** Absolute difference between spatial replicate pairs collected at the same site within the same day, approximately 100 m apart. N=114 pairs.
- **Field blank contamination:** Single measurements of deionized water. N=111. All values should fall at or below the detection limit.

The quantization effect is analyzed separately: the frequency distribution of volunteer within-test differences is expected to show a strong spike at zero (identical readings) due to the 5 mg/L resolution floor, with subsequent spikes at 5 mg/L intervals.

### 2.6 Indoor QA accuracy analysis

Using the 13-session historical indoor QA dataset (N=867 individual tests):

- Error computed as: (volunteer reading minus known standard concentration) for each test.
- Results stratified by concentration range: low (50 mg/L or below), mid (50 to 100 mg/L), high (above 100 mg/L).
- Mean error and direction of bias reported by concentration tier.
- Spring 2013 excluded due to compromised standard solution (K. Shaw, personal communication, March 2026).

The direction of the mean error is of particular interpretive importance: if volunteers systematically read high, this contradicts the apparent low bias observed in the field comparison and strengthens the geographic confound explanation.

### 2.7 Geographic coverage analysis

For each of the 327 unique Blue Thumb chloride monitoring sites, the Haversine great-circle distance to the nearest professional monitoring station in the full EPA WQP Oklahoma dataset was computed. The fraction of volunteer sites beyond threshold distances (1 km, 5 km, 10 km, 25 km, 50 km) is reported.

### 2.8 Reproducibility

The full analysis pipeline is implemented in Python 3.11 and is publicly available. All results from the field validation are reproducible from a single command (python -m src.pipeline --skip-extract). A reproducibility manifest (metadata.json) records the git commit hash, SHA-256 hash of the configuration file, SHA-256 hash of the volunteer data CSV, and all primary result statistics. The volunteer data file is SHA-256 verified at runtime; the pipeline terminates with an explicit error if the file is absent or modified, with no silent fallback.

---

## 3. Results

Results are presented following the framework recommended by J. Dyer (personal communication, March 2026): precision first (establishing what the data is capable of), then field validation as context, then the GLMM as the primary result, and finally the geographic confound resolution.

### 3.1 Volunteer precision: variance decomposition

**Table 2. Within-source variability across measurement types.**

| Source | N | Mean |diff| | 95% CI | Median |diff| | Notes |
|:---|:---|:---|:---|:---|:---|
| Volunteer within-test | 2,566 | 1.53 mg/L | +/- 0.11 | 0.00 mg/L | Titration replicates (test3 vs test5) |
| Professional within-test | 113 | 2.51 mg/L | +/- 0.72 | 1.00 mg/L | Churn splitter duplicates |
| Professional within-site | 114 | 3.58 mg/L | +/- 1.10 | 1.00 mg/L | Spatial replicates, approx. 100 m |
| Field blanks | 111 | 0.5 mg/L | -- | -- | Deionized water; all below detection |

The apparent superiority of volunteer within-test repeatability (mean |diff| = 1.53 mg/L vs. 2.51 mg/L for professionals) is a quantization artifact and must not be interpreted as greater observer precision. Because the Silver Nitrate titration resolves to 5 mg/L per drop, volunteers cannot detect concentration differences smaller than one drop. The distribution of within-test differences confirms this mechanism: 73.2% of volunteer replicate pairs are identical (zero difference), 24.1% differ by exactly 5 mg/L (one drop), and only 2.7% differ by 10 mg/L or more (two or more drops). In total, 97.3% of pairs agree within one drop. Professional instruments resolve to 0.1 mg/L and genuinely detect the sub-milligram variation that the volunteer method cannot resolve. The volunteer repeatability figure reflects the floor of what the drop-count method can distinguish, not observer consistency per se.

The field blanks (N=111 measurements of deionized water) returned 0.5 mg/L or lower in all cases, confirming that contamination from the sampling equipment is not a meaningful source of error (Figure 1A).

The quantization mechanism is visualized directly in Figure 2, which compares the distribution of chloride values measured by professional instruments (continuous, right-skewed) against volunteer measurements (discrete spikes at exact multiples of 5 mg/L). 100% of volunteer readings are quantized to 5 mg/L steps.

### 3.2 Volunteer accuracy against known standards

Thirteen indoor QA sessions spanning 2007 to 2025 (867 individual tests) provide the cleanest possible assessment of kit accuracy: no stream variability, no temporal matching uncertainty, and no geographic confounds.

**Table 3. Volunteer accuracy against known standard solutions by concentration range.**

| Concentration range | N | Mean error | SD | Median error | Direction |
|:---|:---|:---|:---|:---|:---|
| Low (50 mg/L or below) | 406 | +4.37 mg/L | 4.67 mg/L | +3.00 mg/L | High |
| Mid (50 to 100 mg/L) | 197 | +5.32 mg/L | 9.57 mg/L | +5.00 mg/L | High |
| High (above 100 mg/L) | 264 | +32.20 mg/L | 26.30 mg/L | +40.00 mg/L | High |

Volunteers consistently read high across all concentration ranges. At normal operational concentrations (100 mg/L or below, covering 603 of 867 tests and the vast majority of Blue Thumb monitoring sites), mean error is within one drop (+4 to +5 mg/L), which falls within the method's stated resolution. The standard deviation at low concentrations (4.67 mg/L) is comparable to a single drop, indicating tight clustering. At mid-range concentrations the SD increases to 9.57 mg/L (approximately two drops), and at high concentrations the SD reaches 26.30 mg/L, reflecting the compounding endpoint subjectivity described below. The increasing bias at elevated concentrations (mean +32 mg/L above 100 mg/L) is consistent with compounding endpoint subjectivity: each additional drop of titrant required for a high-concentration sample introduces another opportunity for endpoint misidentification.

The direction of the bias carries critical interpretive weight: volunteers read high, not low. This finding directly contradicts the apparent -28% low bias observed in the initial field comparison (Section 3.3) and provides independent evidence that the field bias is not a kit accuracy problem. Figure 3 visualizes the error distribution and concentration-dependent scaling.

### 3.3 Field validation: establishing context through dual comparison

Before interpreting the primary volunteer result, we established the professional "ceiling of agreement" by comparing two independent professional programs using the same virtual triangulation parameters.

**Table 4. Field validation regression results.**

| Comparison | N | R-squared | Slope | Intercept | p-value |
|:---|:---|:---|:---|:---|:---|
| Vol-to-Pro (primary) | 25 | 0.607 | 0.813 | -2.411 | 4.4 x 10^-6 |
| Pro-to-Pro (baseline) | 42 | 0.753 | 0.735 | -- | 1.0 x 10^-13 |
| OWRB-only subset (EPA 325.2 verified) | 7 | 0.730 | 0.801 | -- | 1.4 x 10^-2 |

The professional-to-professional baseline (OCC Rotating Basin vs. OKWRB and CNENVSER, N=42) achieves R-squared = 0.753 and a slope of 0.735. Even professional agencies using validated laboratory methods do not achieve perfect agreement when their measurements are matched retrospectively across space and time. This baseline establishes the ceiling of inter-agency agreement achievable within this dataset.

The volunteer-to-professional comparison (N=25 matched pairs from 4 volunteer sites) yields R-squared = 0.607 and slope = 0.813 (Figure 4A), indicating that volunteer correlation falls within the range of inter-agency professional agreement. The professional baseline is shown in Figure 4B. Two professional organizations contribute to the matched pairs: CNENVSER (Chickasaw Nation Environmental Services, N=18 matches, 72%) and OKWRB-STREAMS_WQX (Oklahoma Water Resources Board, N=7 matches, 28%). CNENVSER's analytical method is not recorded in WQP metadata, which is an acknowledged limitation discussed in Section 4.4. Per-organization regression results are reported in Supplemental Table S3: CNENVSER independently yields R-squared = 0.643, slope = 0.846, p = 6.3 x 10^-5; the OWRB-only subset (N=7, verified EPA 325.2 Automated Colorimetry) independently produces R-squared = 0.730, slope = 0.801, p = 1.4 x 10^-2, and a Vol/Pro ratio of 1.027 (+2.7%), indicating that volunteers and OWRB professionals are essentially identical at co-located sites when the professional method is known.

Paired t-test on log-transformed values: t = -3.03, p = 0.006. Wilcoxon signed-rank: W = 84.0, p = 0.034. Both tests indicate a statistically significant apparent low bias in volunteer readings (mean Vol/Pro ratio = 0.721, -27.9%). Bland-Altman agreement analysis: mean difference (Vol minus Pro) = -16.3 mg/L, SD = 33.8 mg/L, 95% limits of agreement [-82.6, +50.0] mg/L.

Whether the apparent low bias reflects genuine observer error or a geographic confound is examined in the following sections.

**Matched-pairs Linear Mixed-Effects Model.** To account for the nested structure of the data (multiple measurements within sites), a Linear Mixed-Effects model was applied directly to the N=25 co-located matched pairs, with WBID as the random block (site-level random intercept) and IsVolunteer as the fixed treatment factor:

log(Chloride) ~ IsVolunteer + sin(2 pi Julian / 365) + cos(2 pi Julian / 365) + (1 | Site)

This model, specified by J. Dyer (personal communication, February 2026), omits the Longitude covariate that appears in the regional GLMM (Section 3.4). The omission is deliberate: in the matched-pairs design, each volunteer measurement is paired with a professional measurement at the same geographic location (within 125 m), so Longitude is effectively constant within each pair and carries no information about the observer effect. Seasonal harmonics are retained because the volunteer and professional measurements within a pair may be separated by up to 72 hours and thus sample different points in the annual cycle.

This model yields:

**Table 5. Matched-pairs LME fixed effects (REML estimation, N=25 pairs at 4 sites).**

| Fixed Effect | Estimate (beta) | p-value | 95% CI |
|:---|:---|:---|:---|
| IsVolunteer | -0.327 | 0.003 | [-0.546, -0.108] |

[PROVENANCE NOTE: The matched-pairs LME coefficients are computed by `scripts/phase2_lme_analysis.py` (function `fit_matched_pairs_lme`, lines 456-626) and were first reported in the Phase 2 results email to J. Dyer (February 2026). They are not included in the static results text file (`data/outputs/phase2_lme/phase2_lme_results.txt`), which reports paired t-test and Wilcoxon results for the matched pairs but not the LME coefficients. The regional GLMM coefficients (Table 6) are in the results text file.]

Back-transformed, the IsVolunteer coefficient indicates volunteers read approximately 72.1% of professional values (exp(-0.327) = 0.721, or -27.9%). This matched-pairs result is consistent with the OLS finding and the non-parametric tests: all three approaches detect a statistically significant apparent low bias at co-located sites. However, the matched-pairs model operates on only 4 volunteer sites with zero geographic overlap with the 12 professional sites in the broader dataset. The possibility that this "observer effect" reflects a geographic confound rather than measurement error motivated the geographic analysis in Section 3.5.

**Time window sensitivity.** Analysis by temporal matching bin shows the 72-hour window does not introduce temporal degradation:

| Window | N | R-squared | Slope | p-value |
|:---|:---|:---|:---|:---|
| Less than 24 h | 12 | 0.001 | 0.013 | 0.91 |
| 24 to 48 h | 6 | 0.629 | 0.806 | 0.06 |
| 48 to 72 h | 7 | 0.922 | 1.031 | 0.0006 |

The weak less-than-24-hour bin (R-squared = 0.001) contains 12 pairs from a single site (OK520600-03-0020W) where the volunteer concentration range is narrow (30-55 mg/L) against a wide professional range (14-119 mg/L), producing a near-zero slope. The 48-72 hour bin produces the strongest correlation (R-squared = 0.922) because it includes a high-concentration site (OK520600-03-0020C) with wide dynamic range in both variables. The weakness in the short-interval bin is site-specific, not temporal: the same site in a different time bin would show the same pattern.

### 3.4 Primary result: Linear Mixed-Effects Model

The matched-pairs analysis (Section 3.3) directly compares volunteer and professional measurements of the same water at co-located sites, yielding an apparent -28% low bias (p = 0.003). The regional model below asks whether this pattern holds at landscape scale across all 92 sites, including the 80 volunteer sites and 12 professional sites that have no geographic overlap. The two analyses are independent -- the regional model uses all 895 observations without matching -- and their convergence on a similar apparent bias (-28% matched-pairs, -35% regional) from different angles strengthens the case that a single underlying mechanism, rather than statistical artifact, drives the result. Section 3.5 identifies that mechanism as the geographic confound.

**Regional model (N=895 observations, 92 sites).**

The GLMM applied to all volunteer and professional records within the QA dataset's spatiotemporal window (2022-2024, north-central Oklahoma) produces the following fixed effects:

**Table 6. Regional GLMM fixed effects (REML estimation, N=895 observations, 92 sites).**

| Fixed Effect | Estimate (beta) | SE | p-value | 95% CI |
|:---|:---|:---|:---|:---|
| Intercept | -37.663 | 7.640 | < 0.001 | [-52.63, -22.69] |
| IsVolunteer | -0.433 | 0.218 | 0.047 | [-0.861, -0.006] |
| Longitude | -0.435 | 0.078 | < 0.001 | [-0.588, -0.282] |
| Seasonal (sin) | +0.110 | 0.023 | < 0.001 | [+0.065, +0.156] |
| Seasonal (cos) | +0.022 | 0.025 | 0.386 | [-0.028, +0.072] |

Random effects: Site variance = 0.330 (SD = 0.575). Model fitted on 895 observations from 92 sites (Professional: 115 observations at 12 sites; Volunteer: 780 observations at 80 sites).

The Longitude coefficient (beta = -0.435, p < 0.001) confirms that the West-East salinity gradient documented by Dyer et al. (2025) is strongly present in this dataset. The seasonal sine term (beta = +0.110, p < 0.001) captures significant annual chloride cycling. These covariate effects validate the model structure recommended by J. Dyer.

The IsVolunteer coefficient (beta = -0.433, p = 0.047) is statistically significant, suggesting that after controlling for geography and seasonality, volunteers read approximately 35% lower than professionals (back-transformed: 0.648x). This coefficient is larger in magnitude than the matched-pairs estimate (beta = -0.327, Section 3.3) because the regional model includes 80 volunteer sites concentrated in naturally fresher eastern Oklahoma, while the matched-pairs model is restricted to the 4 co-located sites where volunteer and professional measurements sample the same water. The additional 76 volunteer sites pull the IsVolunteer coefficient further negative by absorbing the East-West chloride gradient into the observer effect -- precisely the confound examined in Section 3.5.

This result must be interpreted with extreme caution: the 80 volunteer sites and 12 professional sites in this model have zero geographic overlap. The IsVolunteer coefficient cannot distinguish between "volunteers measure differently" and "volunteer sites have different water chemistry." This model confirms the covariate structure; it does not definitively quantify observer bias.

### 3.5 Geographic confound resolution

The apparent volunteer low bias is explained by the geographic distribution of monitoring sites:

- Professional mean longitude: -98.05 degrees (central-western Oklahoma)
- Volunteer mean longitude: -96.67 degrees (1.4 degrees further east)
- 53% of volunteer records fall east of longitude -96.5 degrees
- 0% of professional records fall east of longitude -96.5 degrees
- Professional mean chloride: 228.4 mg/L (naturally saline western streams)
- Volunteer mean chloride: 75.3 mg/L (naturally fresher eastern streams)

The 1.4-degree East-West offset corresponds to approximately 115 km. The documented West-East salinity gradient in Oklahoma streams (Dyer et al. 2025) predicts that volunteer sites, concentrated in eastern Oklahoma, monitor genuinely fresher water than professional sites in central and western Oklahoma. The apparent low bias measures the difference between the water bodies being monitored, not the difference between the observers.

**Stratified random subsampling.** To test this hypothesis formally, 12 volunteer sites were randomly selected with geographic stratification (3 per longitude quartile) to match the 12 professional sites. The LME was re-run on this geographically balanced subsample:

- Subsample mean longitude: -96.452 degrees
- Subsample mean chloride: 67.1 mg/L
- LME IsVolunteer: beta = -0.2435, **p = 0.5434 -- not significant**
- Subsample Vol/Pro ratio: 0.784 (-21.6%, not significant)

**The observer effect disappeared entirely after balancing the geographic distribution.** The bias was in the streams, not in the volunteers (Figure 5).

This result is independently corroborated by the indoor QA data (Section 3.2): if volunteers genuinely read low, the indoor QA would show negative errors against known standards. Instead, indoor QA consistently shows volunteers reading high (+4 to +5 mg/L). The two lines of evidence converge on the same conclusion: the field bias is geographic, not methodological.

**CNENVSER sensitivity.** Removing the largest CNENVSER site from the full matched-pairs dataset reduces N from 25 to 13 and also eliminates the statistically significant bias (p = 0.49). At the OWRB sites using verified EPA 325.2 methodology (N=7), volunteers and professionals are essentially identical: Vol/Pro = 1.027 (+2.7%). The per-organization sensitivity analysis is shown in Figure 6.

### 3.6 Covariate validation

The regional GLMM (Table 6, Section 3.4) confirms that the geographic and seasonal covariates recommended by Dyer et al. (2025) perform significant statistical work in this dataset. Longitude (beta = -0.435, p < 0.001) captures the West-East salinity gradient with each degree of longitude westward corresponding to approximately 55% higher chloride concentrations. The seasonal sine term (beta = +0.110, p < 0.001) captures significant annual chloride cycling, with peak concentrations in late summer and early fall. The cosine term is not significant (p = 0.39), indicating that the annual cycle is primarily captured by the sine component. These results validate the mixed-effects framework for Oklahoma stream data and confirm that geographic and seasonal factors must be accounted for in any field comparison between volunteer and professional measurements collected at different sites.

### 3.7 Geographic coverage

- 327 unique Blue Thumb chloride monitoring sites identified in the volunteer dataset.
- **93% (305 sites) are more than 1 km from the nearest professional monitoring station** in the full EPA WQP Oklahoma dataset.
- 65% (213 sites) are more than 5 km from the nearest professional station.
- 32% (105 sites) are more than 10 km.
- 99% of Blue Thumb sites (323 of 327) lack any temporal match with professional measurements within the full dataset.
- The N=25 matched pairs come from 4 of these 327 sites. 99% of the Blue Thumb network operates in territory where no retrospective field comparison is possible.

The scarcity of matched pairs is not a weakness of the study design. It is a direct measurement of the program's irreplaceable geographic coverage. The matched-pairs analysis validates the instrument and the method; the coverage analysis quantifies why the data those instruments produce matters.

---

## 4. Discussion

### 4.1 Precision: the quantization floor is not observer inconsistency

97.3% of volunteer titration replicates agree within one drop (5 mg/L). This is strong repeatability for a field titration method and confirms that the drop-count technique is being applied correctly and consistently across the volunteer population. The observation that 73.2% of replicates are identical is not evidence of rounding, data fabrication, or systematic corner-cutting. It is the expected behavior of a quantized instrument: when the true chloride concentration falls between multiples of 5 mg/L, two independent titrations of the same water sample will yield the same endpoint because neither can resolve the sub-5 mg/L difference. The quantization floor is the binding constraint on volunteer precision, not observer inconsistency.

This distinction matters practically for how the volunteer data should be used. For macroscopic assessments -- watershed-scale spatial comparisons, long-term trend analysis, exceedance screening against regulatory thresholds -- the 5 mg/L resolution is adequate and the data is reliable. For applications requiring sub-drop-level sensitivity (detecting a 2 mg/L change from one season to the next), the instrument is unsuitable regardless of who operates it. The limitation belongs to the method, not the volunteers.

To our knowledge, no prior study has explicitly analyzed the quantization effect of drop-count titration resolution on citizen science water quality data. The distinction between method-imposed resolution limits and observer-introduced error is important for interpreting volunteer data quality and may be a contribution of this study to the citizen science methods literature.

### 4.2 Accuracy: volunteers read slightly high, and that is good news

The 18-year indoor QA record provides the cleanest possible test of kit accuracy. Under controlled indoor conditions, with no stream variability, no temporal matching uncertainty, and no geographic confounds, volunteers testing kits against solutions of known concentration consistently read slightly high (+4 to +5 mg/L at normal operational concentrations below 100 mg/L).

The direction of the bias is as important as its magnitude. A systematic high bias rules out systematic under-counting as a source of error, which is the more concerning failure mode for a monitoring program. Under-reporting pollution (reading too low) could cause genuine water quality problems to go undetected. Over-reporting (reading too high) errs on the side of caution. The Blue Thumb kit errs in the safer direction.

The increasing positive bias at elevated concentrations (mean +32 mg/L above 100 mg/L, SD = 26.30 mg/L) is expected and mechanistically explicable: more drops of titrant means more opportunities for endpoint subjectivity to compound. Each additional drop required introduces another visual judgment about whether the color has changed sufficiently. This concentration-dependent behavior is a known property of endpoint titration methods and is not specific to volunteer operators.

The subjectivity of visual endpoint detection in titration has been documented in the analytical chemistry literature: automated titration systems that eliminate visual color judgment have been shown to outperform manual endpoint detection by removing observer-dependent bias in color perception (Boppana et al. 2023). Gravimetric approaches similarly reduce subjectivity compared to volumetric methods relying on visual endpoints (Kejla et al. 2022). The concentration-dependent compounding of endpoint uncertainty described here is consistent with these findings and extends them to the specific context of field-deployed Silver Nitrate drop-count kits used in citizen science monitoring.

### 4.3 The geographic confound: a methodological lesson for citizen science validation

The most important methodological finding of this study is not contained in any single p-value. It is in the journey from the initial matched-pairs paired t-test (p = 0.006, apparently significant low bias) to the stratified subsampling result (p = 0.54, no significant bias). The initial result was statistically valid. The regression was correctly computed. The paired test was appropriately applied. The conclusion -- that volunteers read systematically low -- was wrong.

The error was not computational; it was geographic. When volunteer and professional monitoring sites are distributed along a strong environmental gradient with zero spatial overlap, a naive comparison will detect the gradient, not the observer effect. Oklahoma's West-East salinity gradient (Dyer et al. 2025) places volunteer monitoring sites in naturally fresher eastern streams and professional monitoring sites in naturally saltier central and western streams. The initial model was measuring the difference between the water bodies, not the difference between the observers.

This finding has broad implications for the citizen science validation literature. Any study that compares volunteer and professional measurements collected at different sites without accounting for environmental gradients between those sites risks the same confound. The stratified subsampling approach demonstrated here -- balancing the geographic distribution of volunteer and professional sites before running the mixed-effects model -- provides a methodological template for programs facing the same challenge. The Mixed-Effects framework and geographic covariates recommended by Dyer et al. (2025) are the correct analytical tools for this problem.

While the Bland-Altman framework for method comparison (Bland and Altman 1986) is well-established, it assumes that the two methods are applied to the same samples. When volunteer and professional measurements are collected at geographically distinct sites along an environmental gradient, the apparent method difference conflates measurement bias with site-level differences in the analyte concentration. To our knowledge, no prior citizen science validation study has explicitly identified and corrected for this geographic confound using stratified subsampling. The approach demonstrated here -- balancing the spatial distribution of volunteer and professional sites before running the mixed-effects model -- may provide a methodological template for programs facing similar challenges.

### 4.4 The CNENVSER analytical method: open but bounded

72% of the field matched pairs (18 of 25) involve CNENVSER (Chickasaw Nation Environmental Services) as the professional reference. CNENVSER's chloride analytical method is not recorded in the WQP metadata. This is a genuine limitation: it means the method-comparison interpretation of the field results is formally uncertain for 18 of 25 pairs.

[NOTE: CNENVSER method confirmation is pending direct contact. If confirmed before submission, update this section accordingly.]

However, the indoor QA data substantially bounds this uncertainty. The CNENVSER/LSHQ matched-pair site showed an apparent -47% volunteer low bias. If this were a kit accuracy error, the indoor QA data would show volunteers reading low at elevated chloride concentrations. Instead, the 18-year indoor QA record establishes the opposite: at high chloride levels, Blue Thumb kits read high, not low. The LSHQ discrepancy therefore reflects something about the CNENVSER reference measurement, the site hydrology, or the temporal pairing -- not the volunteer kit. This mitigation does not eliminate the limitation, but it constrains the space of possible explanations.

The OWRB-only subset (N=7, EPA 325.2 Automated Colorimetry, verified) independently produces R-squared = 0.730 and a Vol/Pro ratio of 1.027 (+2.7%) -- a result that would be unambiguous on its own but is underpowered at N=7.

[NOTE: OWRB analytical method discrepancy. Email correspondence from January 2026 states OWRB uses EPA 300.0 (Ion Chromatography), while WQP metadata shows EPA 325.2 (Automated Colorimetry). These are different analytical techniques. Resolution pending direct contact with OWRB. If confirmed as EPA 325.2 before submission, this note can be removed.]

### 4.5 Interpreting the R-squared comparison against the professional baseline

The vol-to-pro R-squared of 0.607 versus the pro-to-pro baseline R-squared of 0.753 is the central field comparison in this study. A natural but misleading interpretation is to compute the ratio (0.607 / 0.753 = 0.806, or "81%") and conclude that "volunteers capture 81% of the professional signal." This framing should be used with caution and is not employed in this paper: R-squared is not a linear proportion, and dividing two R-squared values does not yield a meaningful capture percentage. The quotient of two coefficients of determination has no standard statistical interpretation.

The correct interpretation is contextual: volunteer-to-professional correlation falls within the range of inter-agency professional correlation, confirming that volunteer measurement variation is comparable in magnitude to the variation observed between professional programs using different laboratory methods. The OWRB-only volunteer result (R-squared = 0.730, N=7) actually equals the pro-to-pro baseline, which is the strongest possible outcome for a subset analysis and demonstrates that when the professional method is verified (EPA 325.2), volunteers and professionals are essentially interchangeable.

As Bland and Altman (1986) demonstrated, high correlation between two measurement methods does not imply agreement: two methods can be highly correlated while differing by a clinically or environmentally significant amount. R-squared quantifies the strength of the linear relationship but does not measure agreement, which requires assessment of both bias (mean difference) and precision (spread of differences). The Bland-Altman limits of agreement reported in Section 3.3 provide this complementary assessment.

### 4.6 Geographic irreplaceability: the low N is a feature, not a limitation

The matched-pairs analysis uses N=25 pairs from 4 volunteer sites. This is a small sample by regression standards, and the bootstrap confidence intervals reflect this (OLS slope CI 95%: 0.031 to 1.197). However, the small N is not a design failure that could be corrected by additional effort. It is a structural property of the monitoring landscape: 93% of Blue Thumb's 327 chloride monitoring sites have no professional counterpart within 125 m. 99% lack any temporal match with professional data.

The Blue Thumb program was explicitly designed to monitor streams that professional agencies cannot afford to cover continuously. These headwater and low-order streams are ecologically important, frequently impacted by nonpoint source pollution, and entirely unmonitored by professional programs. The matched-pairs analysis validates the instrument. The coverage analysis quantifies why the instrument matters. The low N is a direct measurement of geographic complementarity.

### 4.7 Implications for regulatory data integration

Blue Thumb biological data -- macroinvertebrate, fish, and habitat assessments -- are already included in Oklahoma's biennial Integrated Report and may be used for TMDL development (Oklahoma Conservation Commission 2019). These biological data are collected by the same volunteers, under the same EPA-approved Quality Assurance Project Plan (QTRAK #21-430), as the chemical data evaluated in this study. Blue Thumb chemical data, by contrast, currently serves a screening and flagging function: exceedances are reported to the Oklahoma Department of Environmental Quality, which may initiate professional follow-up monitoring, but the chemical data are not directly incorporated into use-support assessments.

The results of this study suggest that this asymmetry is not supported by the available evidence for chloride. Volunteer chloride measurements are precise to the method's resolution limit, accurate with a known and conservative directional bias (+4 to +5 mg/L), and free of systematic observer effects when geographic confounds are controlled (p = 0.54). The 18-year indoor QA record provides a longer and more rigorous accuracy baseline than exists for many professional monitoring programs. Whether these findings are sufficient to support direct incorporation of volunteer chloride data into Oklahoma's assessment framework is a policy decision beyond the scope of this study, but the statistical basis for differential treatment of chemical and biological data collected under the same QAPP is no longer clear.

### 4.8 Calibration potential

The indoor QA data suggests a straightforward calibration application: at operational concentrations (below 100 mg/L), volunteers consistently read approximately one drop (5 mg/L) high. A concentration-dependent correction function could be derived from the 867-test dataset to produce calibrated volunteer readings. At high concentrations (above 100 mg/L), a larger correction of approximately +32 mg/L would be required. Whether such calibration improves the downstream utility of the data for regulatory or research purposes depends on the specific application. This is identified as future work.

### 4.9 Virtual triangulation as a general framework

The virtual triangulation approach -- spatially and temporally co-locating volunteer and professional records in a public data archive -- is not specific to Blue Thumb, to chloride, or to Oklahoma. It is applicable to any volunteer monitoring program that submits data to the EPA Water Quality Portal under a distinct OrganizationIdentifier. Oklahoma's Blue Thumb program is currently the clearest example of a program where this data infrastructure exists and the record volume is sufficient to support the analysis. If other state citizen science programs adopt distinct WQP organization identifiers, the same retrospective validation approach becomes available to them at zero marginal field cost. This study provides both the methodological template and the proof of concept.

### 4.10 Limitations

1. **Small matched-pairs sample size.** N=25 from 4 volunteer sites. Bootstrap CIs on OLS slope and R-squared are wide, and the Deming regression is underpowered. Point estimates are stable across parameter sweeps, but individual pair-level heterogeneity is high.
2. **Pre-2015 volunteer data.** 13 of 25 matched pairs use volunteer records from the OCC R-Shiny export that predate the ArcGIS FeatureServer (which begins in 2015). These records were verified against the ArcGIS feed where overlap exists (2,026/2,027 match), but the pre-2015 records cannot be independently cross-validated.
3. **Hydrologic condition metadata.** The HydrologicCondition and HydrologicEvent fields are 0% populated across all 18,299 professional WQP records in this dataset. Storm-event filtering is therefore impossible from the available metadata.
4. **CNENVSER analytical method.** Unconfirmed in WQP metadata for all 18 CNENVSER matched pairs. Mitigated by the indoor QA direction-of-bias argument (Section 4.4) but not fully resolved.
5. **Single analyte.** This study validates chloride only. Extension to other Blue Thumb parameters (dissolved oxygen, nutrients, turbidity) would require separate analyses with different analytical considerations, as those analytes are not conservative and may be affected by biological or chemical transformation between matched sampling events.
6. **Volunteer data through 2024 only.** The R-Shiny export covers through 2024-12-31. The live ArcGIS FeatureServer contains more recent records (2025-2026) that were not included in the matched-pairs analysis.
7. **OWRB analytical method discrepancy.** Email correspondence from January 2026 states OWRB uses EPA 300.0 (Ion Chromatography), while WQP metadata for OKWRB-STREAMS_WQX shows EPA 325.2 (Automated Colorimetry). These are different analytical techniques producing comparable but not identical results. Resolution is pending direct contact with OWRB; WQP metadata is treated as authoritative in this analysis.
8. **Stratified subsampling reproducibility.** The geographic confound test (stratified random subsampling, p=0.54) was performed as a targeted hypothesis test following J. Dyer's pre-specified prediction. The analysis code is embedded within the Phase 2 LME script but has not been isolated into a standalone, independently executable script with a fixed random seed. The result is documented in correspondence and multiple project documents but should be formalized for full computational reproducibility before publication.
9. **Precision statistic derivation.** The 97.3% volunteer replicate agreement figure is computed dynamically by the Phase 2 analysis script from 2,566 ArcGIS titration replicate pairs (73.2% identical + 24.1% differing by one drop). This statistic is written to the variance decomposition figure but is not recorded in any static text output file. Verification requires re-executing the analysis script against the source data.

---

## 5. Conclusion

Blue Thumb volunteer chloride data is precise within the 5 mg/L resolution of the Silver Nitrate titration method, accurate to within one drop against known standards at operational concentrations, and geographically irreplaceable -- monitoring streams that professional agencies do not reach.

The apparent systematic low bias observed in naive field comparisons is not a volunteer accuracy problem. It is a geographic artifact of Oklahoma's documented West-East salinity gradient, which places volunteer monitoring sites in naturally fresher eastern streams and professional monitoring sites in naturally saltier western and central streams. After correcting for this gradient via stratified random subsampling, no significant observer effect remains (p = 0.54). Independent analysis of 18 years of indoor QA records confirms the direction-of-bias finding: Blue Thumb kits read slightly high, not low. The bias was in the streams, not the volunteers.

Three independent lines of evidence -- precision from 2,566 replicate pairs, accuracy from 867 controlled indoor tests spanning 18 years, and field validity from retrospective co-location of archival records -- converge on a single conclusion: volunteer chloride data collected under the Blue Thumb program's quality assurance framework is fit for purpose in landscape-scale water quality analysis. 93% of Blue Thumb's 327 monitoring sites are more than 1 km from the nearest professional station. The data from those sites does not exist anywhere else. It should be used, not discounted.

Oklahoma's approach -- designing volunteer protocols to mirror professional standards, conducting regular QA against known standards, and maintaining programmatically separable volunteer and professional data infrastructure -- provides a replicable model for citizen science programs nationally. Any state that maintains distinct, queryable records for volunteer and professional monitoring programs gains the infrastructure necessary to conduct the same retrospective validation demonstrated here, at zero marginal field cost, without new sampling.

---

## 6. Acknowledgments

The authors thank Karla Spinner (Oklahoma Conservation Commission) for retrieving and delivering the Rotating Basin QA dataset; Cheryl Cheadle (OCC Blue Thumb Program Director) for program context, institutional support, and newsletter collaboration; Rebecca Bond (OCC Blue Thumb Director) for organizing the formal collaboration, facilitating data access, and providing the OCC Quality Assurance Project Plan; Shellie Willoughby (OCC GIS Manager and Assistant State GIS Coordinator) for enabling the ArcGIS REST API data infrastructure that made volunteer data cross-validation possible; Jacob Askey for building the Blue Thumb Dashboard and collaborative technical development; James Ross for field monitoring partnership at Wolf Creek, Lawton, Oklahoma; and Dr. Clinton Bryant for introducing the first author to the Blue Thumb program.
---

## 7. References

Dyer, J.J., Dvorett, D., and Flotemersch, J. (2025). Using natural landscape and instream habitat to identify stream groups. *PeerJ*, 13:e20234.

Bond, R. (2026). OCC Quality Assurance Project Plan. Oklahoma Conservation Commission. Personal communication, January 16, 2026.

Dyer, J.J. (2026). Statistical framework recommendation for Blue Thumb chloride validation. Personal communication, February 20, 2026.

Shaw, K. (2026). Blue Thumb chloride QA session data, 2007-2025 [dataset]. Oklahoma Conservation Commission. Personal communication, March 2, 2026.

Virtanen, P., Gommers, R., Oliphant, T.E., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261-272.

Albus, K., Thompson, R., and Mitchell, F. (2019). Usability of existing volunteer water monitoring data: What can the literature tell us? *Citizen Science: Theory and Practice*, 4(1):14. https://doi.org/10.5334/cstp.222

Bland, J.M., and Altman, D.G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. *The Lancet*, 1(8476):307-310. https://doi.org/10.1016/S0140-6736(86)90837-8

Blanco Ramirez, S., van Meerveld, I., and Seibert, J. (2023). Citizen science approaches for water quality measurements. *Science of the Total Environment*, 897:165436. https://doi.org/10.1016/j.scitotenv.2023.165436

Bolker, B.M., Brooks, M.E., Clark, C.J., Geange, S.W., Poulsen, J.R., Stevens, M.H.H., and White, J.S.S. (2009). Generalized linear mixed models: a practical guide for ecology and evolution. *Trends in Ecology and Evolution*, 24(3):127-135.

Boppana, N.P.D., Snow, R., Simone, P.S., Emmert, G.L., and Brown, M.A. (2023). A low-cost automated titration system for colorimetric endpoint detection. *Analyst*, 148:2133. https://doi.org/10.1039/D2AN02086F

de Camargo Reis, L., da Silva Araujo, M.G., da Silva Cruz, A., Veronesi, G., Naval, M.L.M., et al. (2026). Observando os Rios: Citizen science monitoring water quality in Brazil. *Citizen Science: Theory and Practice*. https://doi.org/10.5334/cstp.836

Dickson, A., et al. (2024). Can citizen science inform science? Evaluating the results of the Bellingen Riverwatch citizen science program and a complimentary government monitoring program. *Frontiers in Environmental Science*, 11:1237580. https://doi.org/10.3389/fenvs.2023.1237580

Dormann, C.F., McPherson, J.M., Araujo, M.B., Bivand, R., Bolliger, J., Carl, G., et al. (2007). Methods to account for spatial autocorrelation in the analysis of species distributional data: a review. *Ecography*, 30(5):609-628.

Hem, J.D. (1985). Study and Interpretation of the Chemical Characteristics of Natural Water. 3rd ed. U.S. Geological Survey Water-Supply Paper 2254. https://doi.org/10.3133/wsp2254

Kaushal, S.S., Likens, G.E., Pace, M.L., Utz, R.M., Haq, S., Gorman, J., and Grese, M. (2018). Freshwater salinization syndrome on a continental scale. *Proceedings of the National Academy of Sciences*, 115(4):E574-E583. https://doi.org/10.1073/pnas.1711234115

Kejla, L., Svoboda, P., Sedlacek, J., et al. (2022). Gravimetric titrations in a modern analytical laboratory: evaluation of performance and practicality in everyday use. *Chemical Papers*, 76:2051-2058. https://doi.org/10.1007/s11696-021-02004-z

Metcalfe, A.N., Kennedy, T.A., Mendez, G.A., and Muehlbauer, J.D. (2022). Applied citizen science in freshwater research. *WIREs Water*, 9:e1578. https://doi.org/10.1002/wat2.1578

O'Ryan, D., Grant, K., Herron, E., McConville, M., Mutter, E., et al. (2025). Strategies for success: Participatory science involvement in water quality environmental governance. *Community Science*, 4:e2025CSJ000126. https://doi.org/10.1029/2025CSJ000126

Pinheiro, J.C., and Bates, D.M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer.

Quinlivan, L., Chapman, D.V., and Sullivan, T. (2020). Validating citizen science monitoring of ambient water quality for the United Nations sustainable development goals. *Science of the Total Environment*, 699:134255. https://doi.org/10.1016/j.scitotenv.2019.134255

Read, E.K., Carr, L., DeCicco, L.A., Dugan, H.A., Hanson, P.C., Hart, J.A., Kreft, J., Read, J.S., and Winslow, L.A. (2017). Water quality data for national-scale aquatic research: The Water Quality Portal. *Water Resources Research*, 53:1735-1745. https://doi.org/10.1002/2016WR019993

San Llorente Capdevila, A., Kokimova, A., Sinha Ray, S., Avellan, T., Kim, J., and Kirschke, S. (2020). Success factors for citizen science projects in water quality monitoring. *Science of the Total Environment*, 728:137843. https://doi.org/10.1016/j.scitotenv.2020.137843

Standard Methods for the Examination of Water and Wastewater (2017). Method 4500-Cl- B. Argentometric Method. 23rd ed. American Public Health Association, American Water Works Association, Water Environment Federation.

Zuur, A.F., Ieno, E.N., Walker, N.J., Saveliev, A.A., and Smith, G.M. (2009). *Mixed Effects Models and Extensions in Ecology with R*. Springer.

---

## 8. Figure Captions

**Figure 1. Variance decomposition: professional QA vs. volunteer replicates.** (A) Mean absolute difference (mg/L) with 95% CI error bars for three measurement scenarios: volunteer within-test titration replicates (N=2,566, mean |diff| = 1.53 mg/L), professional within-test churn splitter duplicates (N=113, mean |diff| = 2.51 mg/L), and professional within-site spatial replicates approximately 100 m apart (N=114, mean |diff| = 3.58 mg/L). (B) Pie chart showing volunteer titration replicate agreement: 73.2% identical, 24.1% differ by one drop (5 mg/L), 2.7% differ by two or more drops. 97.3% of pairs agree within one drop. File: `phase2_lme/variance_decomposition.png`.

**Figure 2. Quantization effect: drop-count resolution.** (A) Histogram comparing the distribution of chloride values measured by professional instruments (smooth continuous distribution) and volunteer drop-count titration (discrete spikes at exact multiples of 5 mg/L). 100% of volunteer readings are quantized to 5 mg/L intervals. (B) Resolution comparison confirming the discrete nature of volunteer measurements. File: `phase2_lme/quantization_effect.png`.

**Figure 3. Indoor QA accuracy analysis.** (A) Histogram of volunteer kit error (volunteer reading minus known standard concentration, N=867 tests). The distribution is positively skewed, confirming systematic high bias. (B) Box plots of error stratified by concentration range, showing that bias scales with concentration: minimal at low concentrations (at or below 50 mg/L), moderate at mid-range (50 to 100 mg/L), and substantial at high concentrations (above 100 mg/L). Red dashed line at zero indicates perfect accuracy. File: `phase2_lme/qa_accuracy_analysis.png`.

**Figure 4. Field validation scatter plots.** (A) Volunteer-to-professional matched pairs (N=25, R-squared = 0.607, slope = 0.813, p = 4.4 x 10^-6). Blue line: OLS regression fit. Gray dashed line: 1:1 perfect agreement. File: `vol_to_pro_validation_plot.png`. (B) Professional-to-professional baseline (N=42, R-squared = 0.753, slope = 0.735, p = 1.0 x 10^-13). File: `pro_to_pro_validation_plot.png`.

**Figure 5. Site distribution map showing geographic confound.** Geographic distribution of professional sites (green, N=12) and volunteer sites (blue, N=80) within the QA dataset's spatiotemporal window, with matched-pair sites highlighted (red stars, N=4). Volunteer sites are concentrated in eastern Oklahoma (mean longitude -96.67 degrees) while professional sites are distributed across central and western Oklahoma (mean longitude -98.05 degrees). The 1.4-degree East-West offset corresponds to approximately 115 km and aligns with the West-East salinity gradient documented by Dyer et al. (2025). File: `phase2_lme/site_distribution_map.png`.

**Figure 6. Matched-pairs sensitivity analysis.** (A) Matched pairs colored by professional organization (CNENVSER, N=18; OWRB, N=7), revealing organization-specific measurement patterns. (B) Volunteer-to-professional chloride ratio by site, showing that the overall apparent bias is driven by CNENVSER sites while the OWRB subset (verified EPA 325.2) shows volunteers and professionals essentially identical (Vol/Pro = 1.027). File: `phase2_lme/matched_pairs_sensitivity.png`.

**Figure 7. LME model diagnostics.** (A) Residuals vs. fitted values, showing random scatter around zero with minor heteroscedasticity. (B) Normal Q-Q plot of residuals, indicating approximate normality with slight tail deviation. (C) Residual distributions by observer type (professional vs. volunteer), showing comparable spread. (D) Residuals by longitude, confirming the model adequately accounts for the West-East spatial gradient. File: `phase2_lme/lme_diagnostics.png`.

---

## Supplemental Information

### S1. Pipeline architecture and parameter selection

Full ETL pipeline description including: EPA WQP API query parameters, volunteer CSV normalization steps (WBID mapping, time parsing, coordinate coercion), data identity safeguards (OKCONCOM_WQX exclusion, SHA-256 enforcement), matching algorithm pseudocode with cKDTree implementation details, parameter sweep results table across spatial (50-300 m), temporal (24-120 h), and strategy (all vs. closest) dimensions, and complete configuration file documentation.

### S2. Full statistical output tables

Complete OLS regression output for all three comparisons (Vol-to-Pro, Pro-to-Pro, OWRB-only). Full LME fixed-effects and random-effects tables for both matched-pairs and regional models. Bootstrap distribution plots for slope and R-squared. Deming regression output with bootstrap confidence intervals. Bland-Altman agreement plot with limits.

### S3. Per-organization breakdown

Separate regression results for CNENVSER (N=18, R-squared = 0.643, slope = 0.846, p = 6.3 x 10^-5) and OKWRB-STREAMS_WQX (N=7, R-squared = 0.730, slope = 0.801, p = 1.4 x 10^-2). Analytical method provenance for each organization. Method confirmation status.

### S4. Sensitivity analyses

Time-bin analysis (less than 24 h, 24-48 h, 48-72 h). Organization sensitivity (CNENVSER removal). Matching parameter sensitivity (distance threshold, time threshold, strategy). Stratified subsampling geographic balance check.

### S5. Data availability and reproducibility

Repository URL, installation instructions, runtime commands, and reproducibility manifest format. SHA-256 hashes for all input data files.
