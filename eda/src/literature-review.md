# Literature Review: Equipment Violation Stops and Racial Disparities

## Narrative Synthesis

### 1. The Investigatory Stop Framework

The conceptual foundation for studying equipment violation stops as a
distinct category comes from **Epp, Maynard-Moody, and Haider-Markel
(2014)**, who distinguish "investigatory stops" (equipment violations,
license/registration checks) from "traffic-safety stops" (speeding, DUI).
Their Kansas City survey found that racial disparities were concentrated
almost entirely in investigatory stops — Black drivers were stopped at
nearly 3x the rate of White drivers for investigatory reasons, while safety
stop rates showed minimal racial gaps. **Baumgartner, Epp, and Shoub
(2018)** confirmed this pattern at scale using 20 million North Carolina
traffic stops, showing that stops for regulatory and equipment violations
exhibited far larger racial disparities than safety-motivated stops. Hit
rates (contraband found per search) were consistently lower for Black
drivers, undermining the justification for disparate search rates.

This investigatory/safety distinction maps directly onto the RIPA data
structure: equipment violations (`reason_for_stop=1`,
`rfs_traffic_violation_type=2`) correspond to investigatory stops, while
moving violations correspond to safety stops.

**Fliss et al. (2020)** added a public-health dimension, showing that stop
types with the *largest* racial disparities (equipment, regulatory) are
those *least* associated with traffic crash reduction. Fayetteville, NC's
shift away from equipment stops toward safety stops simultaneously reduced
crashes by 13%, fatalities by 28%, and the Black-to-White stop rate ratio
by 21%. **Camp, Williamson, and Bhatt (2025)** confirmed that stops of
Black drivers are more likely to be for high-discretion equipment
violations, and demonstrated that a simple directive from a police chief to
curtail "stops for the sake of making stops" produced a large reduction in
racial disparities.

### 2. Measuring Discrimination: Outcome Tests and Threshold Tests

The **outcome test** (Knowles, Persico, and Todd 2001) provides the
theoretical framework for hit-rate analysis: if police are unbiased
optimizers, they should search drivers of all races at the same evidentiary
threshold, producing equalized contraband discovery rates. Lower hit rates
for minority drivers suggest a lower search threshold — i.e., bias.

However, **Simoiu, Corbett-Davies, and Goel (2017)** identified the
critical **infra-marginality problem**: aggregate hit rates can differ
across racial groups even absent discrimination if groups have different
underlying risk distributions. They proposed the **threshold test**, a
Bayesian hierarchical model that estimates race-specific search thresholds
directly. Applied to North Carolina data, the threshold test revealed that
the bar for searching Black and Hispanic drivers was considerably lower
than for White drivers — had police applied the same standard, ~30,000
fewer Black drivers would have been searched over six years.

The most recent methodological advance is **Gaebler, Imai, Laughlin, and
Goel (2025)** in PNAS, who introduce the **robust outcome test** — which
combines outcome rate and decision rate tests for stronger statistical
guarantees. Critically, they apply this to **California RIPA data** and
find that the naive outcome test alone indicates discrimination *against
White individuals* in a third of large agencies — a counterintuitive
result that demonstrates the danger of relying on simple hit rate
comparisons. Their code is publicly available on GitHub.

**Feigenberg and Miller (2022)** addressed the policy-relevant question of
whether equalizing searches would reduce contraband yields. Using Florida
Highway Patrol data, they showed that officers could equalize search rates
across races, maintain the status quo total search rate, and *increase*
contraband yield — racial disparities in searches cannot be justified on
efficiency grounds.

### 3. Veil of Darkness

**Grogger and Ridgeway (2006)** proposed the veil-of-darkness test,
exploiting seasonal variation in sunset times: the same clock time is light
in summer and dark in winter. If officers profile based on race visibility,
the racial composition of stopped drivers should change after dark.

The method has been critiqued and refined substantially. **Horrace and
Rohlin (2016)** showed that artificial lighting erodes the
daylight/darkness distinction. **Kalinowski, Ross, and Ross (2024)** in
the *Journal of Human Resources* raised a fundamental challenge:
endogenous driving behavior. If minority motorists drive more cautiously in
daylight (knowing they face profiling), this confounds the test. Using
traffic fatality data, they found evidence consistent with this behavioral
adaptation. **Knode, Wolfe, and Carter (2024)** in *Criminology* provide a
methodological roadmap addressing inconsistencies across VoD studies.

Two California-specific VoD analyses exist. **Lofstrom et al. (2022)** at
PPIC applied VoD to 2019 RIPA data from the 15 largest agencies, finding
evidence of racial bias for Black and Latino drivers. **Owens and Anderson
(2024)** at the California Policy Lab used an innovative variant for CHP
data: comparing stops initiated via aircraft/radar (race not observable)
vs. close observation (race visible), finding non-White drivers were more
likely stopped when officers could observe driver identity. The San Diego
Union-Tribune also conducted a publicly available VoD replication for SDPD
using RIPA data (GitHub: `sdut-datadesk/veil-of-darkness-sdpd`).

### 4. Policy Evaluation: Pretextual Stop Bans

A growing quasi-experimental literature evaluates pretextual stop
restrictions:

**Rushin and Edwards (2021)** in the *Stanford Law Review* provide the
cleanest natural experiment: Washington State's *Arreola* decision
*expanded* pretextual stop authority, and the diff-in-diff showed a
significant increase in stops of drivers of color, concentrated during
daytime hours.

Three studies evaluate **LAPD's March 2022 policy** (Special Order No. 3):
- **Boehme and Mourtgos (2024)** found stops and arrests decreased, but
  the racial composition of stops changed minimally.
- **Beland, Huh, and Kim (2024)** using regression discontinuity found
  reduced search rates and force for Black individuals specifically.
- **Weller et al. (2025)** found that officers gradually reverted to
  pre-policy behavior, highlighting implementation challenges.

**San Francisco's DGO 9.07** (effective July 2024) shows early promise:
stops of Black drivers for non-moving violations declined 10%, and Black
drivers are no longer the most commonly stopped group for non-moving
violations — the first time since 2019.

**Philadelphia's Driving Equality Law** (2022) reduced targeted-violation
stops of Black drivers by 54%, but overall racial composition of stops was
unchanged — highlighting the need for comprehensive policy design.

**Ramsey County, MN** (prosecution-side approach) saw the most dramatic
results: non-safety stops dropped 86%, searches dropped 92%, with no
discernible public safety effect (Braman et al. 2024). **Parker, Ross, and
Ross (2024)** found Connecticut's collaborative statewide intervention
reduced minority stops 23.5%, driven primarily by fewer pretextual stops.

### 5. Hierarchical and Agency-Level Modeling

**Gelman, Fagan, and Kiss (2007)** established the hierarchical Bayesian
approach for analyzing stop disparities across jurisdictions, using
overdispersed Poisson models with precinct-level random effects and
race-specific crime rates as benchmarks. **Shoub et al. (2022)** found
that discriminatory stops are systemic rather than confined to "bad apple"
officers, suggesting agency-level analysis is appropriate. **Goncalves and
Mello (2021)** used a bunching estimation design to identify individual
officer-level bias, finding 42% of Florida Highway Patrol officers showed
some degree of discrimination.

### 6. Legal Context

**Whren v. United States** (1996) held that officers' subjective
motivations are irrelevant to Fourth Amendment analysis — any observed
traffic violation provides constitutional grounds for a stop regardless of
pretext. **Carbado (2017)** argues Whren "effectively constitutionalized
racial profiling." **Woods (2021)** in the *Stanford Law Review* proposes
removing police from routine traffic enforcement entirely. Several states
(Washington, New Mexico) have departed from Whren under their state
constitutions.

The **RIPA Board's 2026 Annual Report** (covering 2024 data, 5.1M stops
from 533 agencies) finds that Black individuals were stopped 128% more
often than expected, and recommends limiting or eliminating pretextual
stops statewide.

### 7. Gaps and Opportunities

The literature has several gaps our analysis can address:

1. **Equipment violations specifically**: Most studies use broad
   "investigatory" or "non-safety" categories. RIPA's
   `rfs_traffic_violation_type` field enables precise isolation of
   equipment violations from other non-moving violations.

2. **Statewide scale with agency variation**: The PPIC reports analyzed
   only the 15 largest agencies. We have all 555 agencies across 7 years.

3. **Matched-comparison designs**: Comparing equipment vs. moving violation
   stops *within the same agency, time, and location* would provide a
   stronger identification strategy than cross-group comparisons.

4. **Post-2022 policy evaluation**: The LAPD and SFPD bans occurred during
   our data window (2018-2024), enabling difference-in-differences.

5. **The robust outcome test** (Gaebler et al. 2025) has been applied to
   RIPA data but not specifically to equipment violation stops.

6. **VoD applied to equipment stops specifically**: Testing whether the
   racial composition of equipment stops changes after dark would be a
   novel contribution — if equipment stops are pretextual, the effect
   should be especially pronounced.

---

## Annotated Bibliography

### Foundational / Conceptual

**Epp, C. R., Maynard-Moody, S., & Haider-Markel, D. P. (2014).**
*Pulled Over: How Police Stops Define Race and Citizenship.* University of
Chicago Press.
- Establishes the investigatory vs. safety stop distinction via Kansas City
  survey (n=2,329). Black drivers stopped at ~3x the rate of White drivers
  for investigatory reasons; no racial gap in safety stops. Investigatory
  stops erode trust and perceived legitimacy.
- DOI: 10.7208/chicago/9780226114040.001.0001

**Baumgartner, F. R., Epp, D. A., & Shoub, K. (2018).** *Suspect
Citizens: What 20 Million Traffic Stops Tell Us About Policing and Race.*
Cambridge University Press.
- 20M North Carolina stops (2002-2016). Racial disparities concentrated in
  equipment/regulatory stops. Hit rates lower for Black drivers. Disparities
  widespread across officers, not confined to "bad apples."
- DOI: 10.1017/9781108553698

**Baumgartner, F. R., Christiani, L., Epp, D. A., Roach, K., & Shoub, K.
(2017).** Racial Disparities in Traffic Stop Outcomes. *Duke Forum for Law
& Social Change*, 9, 21-53.
- North Carolina stop-type breakdown: search rate disparities much larger
  for investigatory stops than safety stops. Template for presenting
  disparity findings by stop category.
- URL: https://scholarship.law.duke.edu/dflsc/vol9/iss1/2/

**Fliss, M. D., Baumgartner, F. R., et al. (2020).** Re-Prioritizing
Traffic Stops to Reduce Motor Vehicle Crash Outcomes and Racial
Disparities. *Injury Epidemiology*, 7, 3.
- Fayetteville, NC synthetic control: shifting from equipment to safety
  stops reduced crashes 13%, fatalities 28%, and B/W stop ratio 21%. No
  crime increase.
- DOI: 10.1186/s40621-019-0227-6

**Camp, N. P., Williamson, V., & Bhatt, M. P. (2025).** Racial
Disparities in the Discretionary Context of Traffic Stops. *Journal of
Social Issues*, 81(1).
- Stops of Black drivers more likely to be high-discretion equipment
  violations. Chief's directive to curtail "stops for the sake of making
  stops" reduced disparities.
- DOI: 10.1111/josi.70017

**Shoub, K., Christiani, L., Baumgartner, F. R., et al. (2022).**
Comparing Systemic and Individual Sources of Racially Disparate Traffic
Stop Outcomes. *JPART*, 32(2), 236-251.
- 2M stops: discriminatory stops are systemic, not "bad apples." Equity
  better served by eliminating consent searches than disciplining
  individuals.
- DOI: 10.1093/jopart/muab028

### Outcome Test / Hit Rate Methods

**Knowles, J., Persico, N., & Todd, P. (2001).** Racial Bias in Motor
Vehicle Searches: Theory and Evidence. *Journal of Political Economy*,
109(1), 203-229.
- Seminal outcome test: if police are unbiased, contraband hit rates should
  equalize across races. Maryland data showed roughly equal hit rates;
  statewide data suggested bias against Hispanic drivers.
- DOI: 10.1086/318603

**Simoiu, C., Corbett-Davies, S., & Goel, S. (2017).** The Problem of
Infra-Marginality in Outcome Tests for Discrimination. *Annals of Applied
Statistics*, 11(3), 1193-1216.
- Identifies the infra-marginality problem in outcome tests. Proposes the
  threshold test — a Bayesian hierarchical model estimating race-specific
  search thresholds. NC data: search threshold for Black drivers
  substantially lower.
- DOI: 10.1214/17-AOAS1058

**Gaebler, J. D., Imai, K., Laughlin, S. T., & Goel, S. (2025).** A
Simple, Statistically Robust Test of Discrimination. *PNAS*, 122(10).
- Robust outcome test combining outcome and decision rate tests. **Applied
  to California RIPA data.** Naive outcome test misleadingly indicates
  discrimination *against Whites* in 1/3 of agencies. Code on GitHub:
  `jgaeb/outcomepp`.
- DOI: 10.1073/pnas.2416348122

**Feigenberg, B. & Miller, C. (2022).** Would Eliminating Racial
Disparities in Motor Vehicle Searches Have Efficiency Costs? *QJE*,
137(1), 49-113.
- Florida data: equalizing search rates would *increase* contraband yield.
  Racial disparities in searches cannot be justified on efficiency grounds.
- DOI: 10.1093/qje/qjab018

**Anwar, S. & Fang, H. (2006).** An Alternative Test of Racial Prejudice
in Motor Vehicle Searches. *AER*, 96(1), 127-151.
- Officer-race interaction test. Florida Highway Patrol: evidence of racial
  prejudice against Black drivers by officers of both races.
- DOI: 10.1257/000282806776157579

**Antonovics, K. & Knight, B. G. (2009).** A New Look at Racial
Profiling: Evidence from the Boston Police Department. *Review of Economics
and Statistics*, 91(1), 163-177.
- Officers more likely to search when race differs from driver's.
  Cross-race searches have lower hit rates.
- DOI: 10.1162/rest.91.1.163

**Goncalves, F. & Mello, S. (2021).** A Few Bad Apples? Racial Bias in
Policing. *AER*, 111(5), 1406-1441.
- Bunching design: 42% of FL Highway Patrol officers practice
  discrimination in ticket leniency. Officers favor own-race drivers.
- DOI: 10.1257/aer.20181607

**Shea, J. (2024).** Testing for Racial Bias in Police Traffic Searches.
Working paper, University of Illinois.
- Refined threshold test addressing officer heterogeneity.
- URL: https://jkcshea.github.io/files/bias.pdf

### Veil of Darkness

**Grogger, J. & Ridgeway, G. (2006).** Testing for Racial Profiling in
Traffic Stops from Behind a Veil of Darkness. *JASA*, 101(475), 878-887.
- Original VoD test. Oakland data: limited evidence of profiling. Avoids
  the benchmarking problem.
- DOI: 10.1198/016214506000000168

**Horrace, W. C. & Rohlin, S. M. (2016).** How Dark Is Dark? Bright
Lights, Big City, Racial Profiling. *Review of Economics and Statistics*,
98(2), 226-232.
- Incorporates streetlight data. Profiling more pronounced in well-lit
  areas even after dark. Standard VoD underestimates bias in urban areas.
- DOI: 10.1162/REST_a_00543

**Kalinowski, J. J., Ross, M. B., & Ross, S. L. (2024).** Endogenous
Driving Behavior in Tests of Racial Profiling. *Journal of Human
Resources*, 59(2).
- Fundamental VoD critique: if minorities drive more cautiously in daylight
  (knowing they face profiling), this confounds the test. Traffic fatality
  data supports behavioral adaptation.
- DOI: 10.3368/jhr.0822-12513R1

**Knode, J. L., Wolfe, S. E., & Carter, T. M. (2024).** Pulling Back the
Veil of Darkness: A Proposed Road Map. *Criminology*, 62(2), 364-375.
- Methodological roadmap standardizing VoD analytical choices. Novel
  weighting procedure for seasonal driving population differences.
- DOI: 10.1111/1745-9125.12366

**Vito, A. G., Rocheleau, G., Teed, E., & Dent, L. (2026).** Daylight,
Race, Gender, and Age. *European Journal of Criminology*.
- Chicago VoD with intersectional analysis: profiling only evident for
  young Black male drivers. Aggregate VoD masks heterogeneity.
- DOI: 10.1177/14613557251409947

### Large-Scale / Multi-Method

**Pierson, E., Simoiu, C., et al. (2020).** A Large-Scale Analysis of
Racial Disparities in Police Stops across the United States. *Nature Human
Behaviour*, 4(7), 736-745.
- ~100M stops, 21 state + 35 municipal agencies. VoD + threshold test.
  Black drivers less likely stopped after dark; lower search thresholds for
  Black/Hispanic drivers. Data at openpolicing.stanford.edu.
- DOI: 10.1038/s41562-020-0858-1

**Gelman, A., Fagan, J., & Kiss, A. (2007).** An Analysis of the NYPD's
Stop-and-Frisk Policy in the Context of Claims of Racial Bias. *JASA*,
102(479), 813-823.
- Hierarchical overdispersed Poisson model. Precinct-level random effects
  with race-specific arrest rates as benchmarks. Black stopped at 2.5x
  even after controls.
- DOI: 10.1198/016214506000001040

**Ba, B. A., Knox, D., Mummolo, J., & Rivera, R. (2021).** The Role of
Officer Race and Gender in Police-Civilian Interactions in Chicago.
*Science*, 371(6530), 696-702.
- Quasi-random officer assignment. Black/Hispanic officers make fewer
  stops, less force. Disparities concentrated in discretionary stops.
- DOI: 10.1126/science.abd8694

### Policy Evaluation

**Rushin, S. & Edwards, G. S. (2021).** An Empirical Assessment of
Pretextual Stops and Racial Profiling. *Stanford Law Review*, 73(3),
637-737.
- WA State diff-in-diff: *Arreola* decision expanding pretextual stop
  authority → significant increase in stops of drivers of color,
  concentrated in daylight. 8.25M stops.
- URL: https://www.stanfordlawreview.org/print/article/an-empirical-assessment-of-pretextual-stops-and-racial-profiling/

**Boehme, H. M. & Mourtgos, S. M. (2024).** The Effect of Formal
De-Policing on Police Traffic Stop Behavior and Crime. *Criminology &
Public Policy*, 23(3), 517-542.
- LAPD March 2022 policy: stops and arrests decreased, but % non-White
  stopped declined minimally. Possible property crime increase.
- DOI: 10.1111/1745-9133.12673

**Beland, L.-P., Huh, J., & Kim, D. (2024).** Curbing Pretextual Stops.
SSRN Working Paper 4888255.
- LAPD regression discontinuity: reduced search/force rates for Black
  individuals; improved response times; increased arrest rates in remaining
  stops (higher-quality stops).
- URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4888255

**Weller, N. et al. (2025).** Street-Level Bureaucrats and Political
Control. SSRN Working Paper 5288326.
- LAPD body-worn video + admin data: officers misunderstood policy, lacked
  sanctions; pretextual stops reverted to pre-policy levels. Key finding on
  implementation failure.
- URL: https://www.arnoldventures.org/stories/evaluating-pretextual-stop-reform-in-the-lapd-with-bodyworn-video-and-administrative-data

**Parker, S., Ross, M. B., & Ross, S. L. (2024).** Driving Change:
Evaluating Connecticut's Collaborative Approach. NBER Working Paper 32692.
- Statewide intervention: 23.5% reduction in minority stops, 85% from
  fewer pretextual stops. No crash increase; modest property crime
  clearance decline.
- URL: https://www.nber.org/papers/w32692

**Braman, D., Fishman, J., et al. (2024).** Prosecutors in the Passing
Lane. *San Diego Law Review*, 61(1).
- Ramsey County, MN: prosecution-side declination → non-safety stops -86%,
  searches -92%, no public safety effect.
- URL: https://digital.sandiego.edu/sdlr/vol61/iss1/4/

### California RIPA

**Lofstrom, M., Hayes, J., Martin, B., & Premkumar, D. (2022).** Racial
Disparities in Traffic Stops. PPIC.
- 2019 RIPA, 15 largest agencies. Black drivers 2x+ search rate, lower hit
  rates. VoD with DST: 1.4-2.8pp shift for Black/Latino drivers. Equipment
  stops show largest disparities.
- URL: https://www.ppic.org/publication/racial-disparities-in-traffic-stops/

**Lofstrom, M., et al. (2024).** Racial Disparities in Law Enforcement
Stops. PPIC.
- Updated analysis covering all agencies post-2022 rollout.
- URL: https://www.ppic.org/publication/racial-disparities-in-law-enforcement-stops/

**Owens, E. & Anderson, E. H. (2024).** The California Highway Patrol:
Analysis of RIPA Stop Data. California Policy Lab, UC Berkeley.
- VoD variant: airplane/radar vs. close observation. Non-White drivers more
  likely stopped when officer could observe identity.
- URL: https://capolicylab.org/wp-content/uploads/2024/11/California-Highway-Patrol-RIPA-report.pdf

**RIPA Board (2026).** 2026 Annual Report. CA DOJ.
- 5.1M stops, 533 agencies. Black stopped 128% more than expected. Consent
  searches of Black individuals least likely to yield contraband.
  Recommends limiting pretextual stops statewide.
- URL: https://oag.ca.gov/system/files/media/ripa-board-report-2026.pdf

**LA County OIG (2022).** The Sheriff's Department's Underreporting of
Civilian Stop Data. LA County Office of Inspector General.
- LASD failed to report 50,000+ stops, 18,000+ consent searches. CAD vs.
  RIPA comparison methodology.
- URL: https://assets-us-01.kc-usercontent.com/0234f496-d2b7-00b6-17a4-b43e949b70a2/cfe6d276-13c8-4e41-afc4-3e0db72ca166/The%20Sheriff%E2%80%99s%20Department%E2%80%99s%20Underreporting%20of%20Civilian%20Stop%20Data%20to%20the%20California%20Attorney%20General.pdf

**Catalyst California & ACLU (2021-2023).** Reimagining Community Safety
(series). LA, Riverside, Sacramento, San Diego counties.
- 80% of LA deputy stops for traffic violations; Black/Latinx searched 4:1
  / 3:1 vs. White. Cost: ~$35-44M/yr on low-yield traffic enforcement.
- URL: https://www.catalystcalifornia.org/campaign-tools/publications/reimagining-community-safety-in-california

### Legal / Policy

**Whren v. United States, 517 U.S. 806 (1996).** Officers' subjective
motivations irrelevant to Fourth Amendment; any observed traffic violation
justifies a stop regardless of pretext.

**Woods, J. B. (2021).** Traffic Without the Police. *Stanford Law
Review*, 73, 1471-1549.
- Proposes removing police from routine traffic enforcement. Reviews
  disparities by stop type and discretion level. Framework for
  categorizing stops.
- URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3702680

**Carbado, D. W. (2017).** Predatory Policing. *UCLA Law Review*, 64.
- Whren "constitutionalized racial profiling." Minor infractions become
  gateway to invasive searches via pretextual stops.
- URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3008713

**Harris, D. A. (1999).** The Stories, the Statistics, and the Law: Why
"Driving While Black" Matters. *Minnesota Law Review*, 84, 265-326.
- Early documentation of racial profiling; coined "Driving While Black."
  Equipment violations serve as the "objective basis" shielding
  racially-motivated stops post-Whren.

### Other Empirical

**Stelter, M., Essien, I., et al. (2022).** Racial Bias in Police Traffic
Stops: County-Level Prejudice and Disproportionate Stopping.
*Psychological Science*, 33(3), 483-496.
- 130M+ stops linked to 2M+ Project Implicit respondents. Disproportionate
  stopping of Black drivers higher in counties with higher White racial
  prejudice.
- DOI: 10.1177/09567976211051272

**Iwama, J. & McDevitt, J. (2025).** Racial Profiling in Traffic Stops: An
Investigation of Race/Ethnicity and Minor Traffic Violations. *Race and
Justice*.
- 18K+ stops, Douglas County KS. Direct examination of the minor-violation
  pathway.
- DOI: 10.1177/21533687251346502

**Luh, E. (2022).** Not So Black and White: Uncovering Racial Bias from
Systematically Masked Police Reports. Working paper.
- Texas data: officers strategically misreport stop reasons. Structural
  model shows disparities larger than naive analysis suggests.
- URL: https://elizabethluh.com/jmp

**Goel, S., Rao, J. M., & Shroff, R. (2016).** Precinct or Prejudice?
Understanding Racial Disparities in NYPD's Stop-and-Frisk. *Annals of
Applied Statistics*, 10(1), 365-394.
- Precinct-level hit rate analysis: 40%+ of CPW stops had <1% weapon
  probability. Black/Hispanic disproportionately stopped in low-hit-rate
  contexts.
- DOI: 10.1214/15-AOAS897
