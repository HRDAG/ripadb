# About the RIPA Stop Data

[TOC]

## What is RIPA?

The Racial and Identity Profiling Act of 2015 ([AB
953](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201520160AB953))
requires California law enforcement agencies to collect and report data on
every stop they conduct ([California Penal Code
13519.4](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=13519.4.)).
Officers record who they stopped, why, what actions they took, and the outcome
--- all linked to the officer's *perception* of the stopped person's race,
gender, age, and other identity characteristics.

The data is submitted to the California Department of Justice, which publishes
it through the [OpenJustice Data Portal](https://openjustice.doj.ca.gov/data).
An independent RIPA Board, housed within the DOJ, analyzes the data and
publishes [annual reports](https://oag.ca.gov/ab953/board/reports) with
findings and policy recommendations.

This dataset covers **2018--2024** and contains approximately **26.3 million
person-stop records** from **555 law enforcement agencies** across California.

## Data collection

### How agencies report

Agencies submit stop data to the DOJ's Stop Data Collection System (SDCS)
through one of three methods: a DOJ-hosted web application, a local database
connected via web services or SFTP, or batch file upload. Records must pass
logic checks (e.g. age is non-negative) before acceptance.

### Phased rollout

Not all agencies reported from the start. RIPA required agencies to begin
reporting based on their size:

| Wave | Agency size | Collection start | First report due | Agencies |
|------|------------|-----------------|-----------------|----------|
| 1 | 1,000+ officers | July 1, 2018 | April 1, 2019 | ~8 |
| 2 | 667--999 officers | January 1, 2019 | April 1, 2020 | ~7 |
| 3 | 334--666 officers | January 1, 2021 | April 1, 2022 | ~10 |
| 4 | 1--333 officers | January 1, 2022 | April 1, 2023 | ~500 |

The 2018 data covers only July through December and only the largest agencies.
The 2019 data adds Wave 2. Wave 3 joined in 2021, and by 2022 all agencies
were reporting. Comparisons across years must account for this expanding
coverage.

### Instances of data fabrication or intentional misreporting

In 2022, the Los Angeles Office of the Inspector General (OIG) published [an
investigation into the LA Sheriff's
Department](https://assets-us-01.kc-usercontent.com/0234f496-d2b7-00b6-17a4-b43e949b70a2/cfe6d276-13c8-4e41-afc4-3e0db72ca166/The%20Sheriff%E2%80%99s%20Department%E2%80%99s%20Underreporting%20of%20Civilian%20Stop%20Data%20to%20the%20California%20Attorney%20General.pdf),
comparing stop data from CAD logs to data recorded in the Sheriff's Automated
Contact Reporting System (SACRS) that feeds into RIPA. They found the SACR
system underreported stops by at least 50,731 stops, and underreported arrests
by at least 71,462, between July 2018 and June 2019. They further found:

>the practice of not entering data into the SACR system may be pervasive and
>widespread throughout all of the Sheriff’s Department’s patrol divisions. In
>addition, the Office of Inspector General found significant differences
>between CAD system and SACR system totals relating to backseat detentions,
>consent searches, and reasonable suspicion stops.

The Sacramento Observer [reported on the story](https://sacobserver.com/2022/08/data-collecting-discrepancies-mean-police-profiling-of-african-americans-is-being-underreported/)

In June of 2024, the San Francisco Department of Police Accountability [found
one of the department's top ticket writers was systematically misreporting the
race of the people he
stopped](https://media.api.sf.gov/documents/Readacted_CSR_6-2024.pdf), causing
"irreparable harm to the integrity of SFPD’s RIPA reporting". The story was
covered in the [SF Standard](https://sfstandard.com/2024/10/10/cop-investigated-for-falsifying-race-data-in-traffic-stops-killed-himself/)

### Other known data quality issues

The 2018 report included a
[note](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2022-12/Final%202018_RIPA%20Dataset%20Read%20Me_Open%20Justice%20Supporting%20Documentation.pdf)
that "a relatively small amount of data with errors that should have been
identified and corrected reached completed status." These errors included:

- 28,148 records in the 2018 data were coded as "consensual encounter resulting
  in search" but did not indicate a search occurred
- 5,404 cases where officers listed "incident to arrest" as the basis for
  search, and no arrest was indicated.

The
[readme](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2022-12/Final%202018_RIPA%20Dataset%20Read%20Me_Open%20Justice%20Supporting%20Documentation.pdf)
reports additional errors in the 2018 data affecting small numbers of records.

### Important limitations - what's not collected

- **No fine-grained location**: The statewide data includes only
  `LOC_CLOSEST_CITY` --- no address, latitude/longitude, or beat/district. Some
  jurisdictions publish more detailed location data through their own open data
  portals.

- **No officer identifiers**: The statewide data does not include officer badge
  numbers or other identifiers, preventing analysis of individual officer
  patterns

- **Complaint data limitations**: The RIPA Board collects civilian complaint
  data alongside stop data, but the complaint system has significant
  limitations. The sustained rate for profiling complaints has been extremely
  low --- reaching 0.19% in the 2024 data (3 out of 2,282 profiling complaints
  sustained). Until November 2025, Penal Code section 148.6 imposed criminal
  sanctions for filing a "false" complaint, which the California Supreme Court
  found unconstitutional. The Board documented this as a deterrent to filing
  complaints for years before the ruling.

### Unit of observation

Each row in the dataset is a **person-stop**: one person involved in one stop.
A single stop event (identified by `DOJ_RECORD_ID`) can produce multiple rows
if the officer stopped more than one person. The composite key is
`(DOJ_RECORD_ID, PERSON_NUMBER)`.

## How demographics are recorded

All demographic data reflects the **officer's perception** of the stopped
person. The officer does not ask the person their race, gender, or age, and
does not refer to identification documents. This is by design: RIPA aims to
capture the officer's perception because profiling is based on what an officer
believes about a person, not on the person's actual identity.

The RIPA Board's inaugural report (2018) established this methodology:

> With respect to the person stopped, the officer must report his/her own
> perception, based upon personal observation only (and not through any other
> means, such as asking the person or referring to identification), regarding
> the following: perceived race or ethnicity, perceived age, perceived gender,
> whether the person is perceived to be LGBT, whether the person is perceived
> to have limited or no English fluency, and whether the person is perceived
> or known to have a disability.

## Variable groups

The dataset contains 235 columns organized into the groups described below.
Binary flag columns use 0/1 coding. Columns marked "2024 only" are NULL for
earlier years. Columns marked "2018--2023 only" are NULL for 2024 data.

In some cases, columns were combined or renamed in order to facilitate
cross-era analyses. All such transformations are recorded [in this schema
document](https://github.com/HRDAG/ripadb/blob/main/individual/RIPA-statewide/clean/hand/schema.yaml),
which is part of this project's [GitHub
repository](https://github.com/HRDAG/ripadb)

### Identifiers and stop context

| Column | Description |
|--------|-------------|
| `DOJ_RECORD_ID` | Unique stop identifier |
| `PERSON_NUMBER` | Person within the stop (1, 2, ...) |
| `AGENCY_ORI` | Agency ORI code (CJIS identifier) |
| `AGENCY_NAME` | Agency name |
| `DATE_OF_STOP` | Date of the stop |
| `TIME_OF_STOP` | Time of the stop (HH:MM) |
| `STOP_DURATION` | Duration in minutes |
| `LOC_CLOSEST_CITY` | Closest city to the stop location |

The statewide data does not include fine-grained location (latitude/longitude
or address). Some jurisdictions publish more detailed location data through
their own open data portals.

### Race and ethnicity (`RAE_*`)

`RAE_FULL` is the primary race code. Individual race flags allow for
multiracial identification.

| Code | Label |
|------|-------|
| 1 | Asian |
| 2 | Black/African American |
| 3 | Hispanic/Latino(a) |
| 4 | Middle Eastern/South Asian |
| 5 | Native American |
| 6 | Pacific Islander |
| 7 | White |
| 8 | Multiracial |

The RIPA Board has documented consistent racial disparities in stops across
all seven years of data. Black individuals are stopped at roughly 2--2.5 times
their share of California's population. In the most recent report (2026,
covering 2024 data), the Board found that Black individuals comprised 12.09%
of stops but only about 5.4% of the state's residential population---stopped
approximately 128% more frequently than expected.

### Gender (`G_*`)

`G_FULL` is the primary gender code.

| Code | Label |
|------|-------|
| 1 | Cisgender Man |
| 2 | Cisgender Woman |
| 3 | Transgender Man |
| 4 | Transgender Woman |
| 5 | Nonbinary Person |
| 6 | Multigender |

Gender column names changed between schema eras. In the raw 2018--2023 data,
the columns were `G_MALE`, `G_FEMALE`, and `G_GENDER_NONCONFORMING`. In 2024,
they became `G_CISGENDER_MAN`, `G_CISGENDER_WOMAN`, and `G_NONBINARY_PERSON`.
The cleaned dataset uses the 2024 canonical names for all years.

The RIPA Board's 2022 report (covering 2020 data) included the first
detailed analysis of stops of transgender individuals, finding that
transgender people experienced higher rates of searches and use of force
relative to cisgender individuals.

### Sexual orientation (`SOR_*`)

| Column | Description |
|--------|-------------|
| `SOR_LGB` | Perceived as lesbian, gay, or bisexual (0/1) |
| `SOR_STRAIGHT` | Perceived as straight (0/1) |

In 2018--2023, only a single `LGBT` flag was collected (renamed to `SOR_LGB`
in the cleaned data). `SOR_STRAIGHT` is derived as `1 - SOR_LGB` for those
years. Starting in 2024, both fields are collected natively.

### Age (`AGE`, `AGE_GROUP`)

`AGE` is the officer's estimate of the person's age in years. `AGE_GROUP`
provides standardized bins derived from `AGE`:

| Code | Ages |
|------|------|
| 1 | 1--9 |
| 2 | 10--14 |
| 3 | 15--17 |
| 4 | 18--24 |
| 5 | 25--34 |
| 6 | 35--44 |
| 7 | 45--54 |
| 8 | 55--64 |
| 9 | 65+ |

The raw age group bins changed across years (2023 used different breakpoints),
so `AGE_GROUP` is re-derived from `AGE` for consistency. The original
year-specific value is preserved in `age_group_orig`.

The RIPA Board's 2025 and 2026 reports focused heavily on youth, finding that
the youngest age groups (particularly ages 12--14) experienced the highest
rates of searches, handcuffing, and curbside detention. Black youth ages 12--14
had limited force used against them at a rate of 42.3% (2023 data).

### Disability (`PD_*`)

`PD_FULL` is the primary disability code. `PD_MULTI` indicates whether
multiple disabilities were perceived (0 = none, 1 = one, 2 = multiple).

| Code | Label |
|------|-------|
| 1 | Deafness/Difficulty Hearing |
| 2 | Speech Impairment |
| 3 | Blind/Visual Impairment |
| 4 | Mental Health Condition |
| 5 | Intellectual/Developmental Disability |
| 6 | Hyperactivity Disorder |
| 7 | Other Disability |
| 8 | None |

The RIPA Board's 2022 report found that officers used force against people
perceived to have a mental health condition at 5.2 times the rate of people
with no perceived disability, and searched them at 4.8 times the rate.

### Other demographics

| Column | Description |
|--------|-------------|
| `LIMITED_ENGLISH_FLUENCY` | Perceived limited English fluency (0/1) |
| `PERSON_UNHOUSED` | Perceived as unhoused (0/1; 2024 only) |

The 2026 report found that 64.8% of stops of unhoused individuals were
initiated for reasonable suspicion, higher than for any other group. People
perceived as unhoused were also subjected to search, force, and arrest at
higher rates than other group.s

### Stop type and circumstances (2024 only)

| Column | Description |
|--------|-------------|
| `TOS_VEHICULAR` | Vehicular stop |
| `TOS_BICYCLE` | Bicycle stop |
| `TOS_PEDESTRIAN` | Pedestrian stop |
| `PASSENGER_IN_VEHICLE` | Person was a passenger |
| `INSIDE_RESIDENCE` | Stop occurred inside a residence |
| `CALL_FOR_SERVICE` | Stop initiated by a call for service |
| `WELFARE_WELLNESS_CHECK` | Welfare/wellness check |

**Important limitation:** Prior to 2024, the data does not distinguish among
vehicular, bicycle, and pedestrian stops. The `TOS_*` fields are NULL for
2018--2023. This means that analyses of pedestrian or bicycle stop patterns
are only possible using 2024 data.

Similarly, the `CALL_FOR_SERVICE` field is only available for 2024, though the
2020 report noted that approximately 95% of stops were officer-initiated
(not calls for service) in the early data.

### Reason for stop (`REASON_FOR_STOP`, `RFS_*`)

`REASON_FOR_STOP` codes the primary reason the officer initiated the stop:

| Code | Label | Notes |
|------|-------|-------|
| 1 | Traffic violation | See `RFS_TRAFFIC_VIOLATION_TYPE` |
| 2 | Reasonable suspicion | See `RFS_RS_*` subcategories |
| 3 | Known to be on parole/probation/PRCS/mandatory supervision | |
| 4 | Knowledge of outstanding arrest warrant/wanted person | |
| 5 | Investigation of whether student violated school policy | |
| 6 | Consensual encounter resulting in a search | |
| 7 | Possible conduct warranting discipline under Education Code | |
| 8 | Determine whether to issue truancy-related document | |
| 9 | Probable cause to arrest | 2024 only |
| 10 | Welfare & Institutions Code 5150 | 2024 only |

#### Traffic violation subcategories (`RFS_TRAFFIC_VIOLATION_TYPE`)

| Code | Label |
|------|-------|
| 1 | Moving violation |
| 2 | Equipment violation |
| 3 | Non-moving violation (including registration) |

Equipment violations (code 2) are a key indicator of **pretextual stops**
--- stops where the stated reason is minor but the officer's actual intent
is to investigate something else. The RIPA Board has documented significant
racial disparities in equipment violation stops. In the 2022 report (covering
2020 data), non-moving and equipment violation accounted for 31.3% of stops of
people perceived as Black, compared to 19.9% for people perceived as White.

#### Reasonable suspicion subcategories (`RFS_RS_*`)

When the reason for stop is reasonable suspicion (code 2), the officer
records which factors contributed: offense witnessed, matched suspect
description, witness identification, carrying a suspicious object, actions
indicative of crime, suspect appearance/demeanor, suspected drug transaction,
violent crime suspect, or other. A CJIS code (`RFS_RS_CODE`) may also be
recorded.

#### Probable cause subcategories (`RFS_PC_*`, 2024 only)

Added in 2024 for the new "probable cause to arrest" stop reason (code 9).
Parallels the reasonable suspicion subcategories.

#### Reason given to person stopped (`RFS_RG_*`, 2024 only)

A major addition in 2024: the reason the officer *communicated to the person*
for the stop, which may differ from the officer's actual recorded reason.
This includes 22 subcategories covering traffic violations (moving, equipment,
non-moving), investigative reasons, parole/warrant status, and notably
`RFS_RG_NOT_COMMUNICATED` --- indicating that the officer did not tell the
person why they were being stopped.

### Actions taken during the stop

The data records what the officer did during the stop. The structure differs
significantly between schema eras.

#### 2018--2023: Combined actions (`ADS_*`)

In the earlier era, force and non-force actions are recorded in a single set
of `ADS_*` (Actions During Stop) flags. Key columns:

**Non-force actions:**
- `ADS_ASKED_SEARCH_PER/PROP` --- asked to search person or property
- `ADS_SEARCH_PERSON/PROPERTY` --- conducted search
- `ADS_SEARCH_PERS_CONSEN/PROP_CONSEN` --- search with consent
- `ADS_CURB_DETENT` --- curb detention
- `ADS_PATCAR_DETENT` --- placed in patrol car
- `ADS_SOBRIETY_TEST` --- field sobriety test
- `ADS_PHOTO` --- photographed
- `ADS_WRITTEN_STATEMENT` --- written statement taken
- `ADS_VEHICLE_IMPOUND` --- vehicle impounded
- `ADS_PROP_SEIZE` --- property seized
- `ADS_NO_ACTIONS` --- no actions taken

**Force actions:**
- `ADS_HANDCUFFED` --- handcuffed
- `ADS_REMOVED_VEHICLE_ORDER/PHYCONTACT` --- removed from vehicle (by order / physical contact)
- `ADS_FIREARM_POINT/DISCHARGE` --- firearm pointed or discharged
- `ADS_ELECT_DEVICE` --- conducted energy device (combined)
- `ADS_IMPACT_DISCHARGE` --- impact projectile
- `ADS_CANINE_SEARCH/BITE` --- canine used
- `ADS_BATON` --- baton used
- `ADS_CHEM_SPRAY` --- chemical spray
- `ADS_OTHER_CONTACT` --- other physical contact

#### 2024: Split into non-force (`NFA_*`) and force (`OFA_*`)

The 2024 schema separates actions into non-force actions (NFA) and officer
force actions (OFA), with more granular subcategories.

**Non-force actions (`NFA_*`)** add:
- `NFA_TERRY_FRISK` --- Terry frisk (pat-down for weapons)
- `NFA_ASKED_ID_PASSENGER` --- asked passenger for identification
- `NFA_ASKED_PAROLE` --- asked about parole status
- `NFA_RAN_NAME_PASSENGER` --- ran name check on passenger
- `NFA_SEARCH_PERS_CONSENT/PROP_CONSENT` --- consent search of person or
  property

**Force actions (`OFA_*`)** split previously combined categories:
- Conducted energy device split into `OFA_ELECT_DEVICE_POINT`,
  `OFA_ELECT_DEVICE_STUN`, and `OFA_ELECT_DEVICE_DART`
- Baton split into `OFA_BATON_DRAWN` and `OFA_BATON_USED`
- Impact projectile split into `OFA_IMPACT_PROJECTILE_POINT` and
  `OFA_IMPACT_PROJECTILE_DISCHARGE`
- New categories: `OFA_FIREARM_UNHOLSTERED`, `OFA_PHYSICAL_COMPLIANCE`,
  `OFA_USE_VEHICLE`, `OFA_CANINE_COMPLIANCE`

**Cross-era analysis note:** To compare actions across all years, you must
harmonize the `ADS_*` columns (2018--2023) with the `NFA_*` and `OFA_*`
columns (2024). For example, "was searched" for 2018--2023 is
`GREATEST(ADS_SEARCH_PERSON, ADS_SEARCH_PROPERTY)`, while for 2024 it is
`GREATEST(NFA_SEARCH_PERSON, NFA_SEARCH_PROPERTY, NFA_TERRY_FRISK)`.

### Consent searches

Officers may ask for consent to search a person or their property. Consent
search data is spread across several column groups:

- **Request**: `ADS_ASKED_SEARCH_PER/PROP` (2018--2023) or
  `NFA_ASKED_SEARCH_PER/PROP` (2024)
- **Conducted with consent**: `ADS_SEARCH_PERS_CONSEN/PROP_CONSEN`
  (2018--2023) or `NFA_SEARCH_PERS_CONSENT/PROP_CONSENT` (2024)
- **Basis**: `BFS_CONSENT_GIVEN` indicates consent as the basis for search
- **Consent type** (2024 only): `CTP_VERBAL`, `CTP_WRITTEN`, `CTP_IMPLIED`

The RIPA Board has documented that Black individuals are asked for consent to
search at 2--4 times the rate of White individuals, depending on the year and
context. Consent-only searches have lower contraband discovery rates than
other search types, and the racial gap in discovery rates is even wider for
consent searches.

The Board has questioned whether consent is truly voluntary given the power
imbalance between officer and civilian. From the 2022 report:

>While the data reflect that most people consent to a search when asked by an
>officer, research discussed in the Report reflects that this "consent" is not
>necessarily voluntarily because of the inherent power inequality between a law
>enforcement officer and a member of the public. The research shows that this
>inherent power inequality is particularly pronounced among vulnerable
>populations, such as people with mental health disabilities or youth, who may
>be more likely to succumb to authoritative pressure. Indeed, RIPA data
>reflects that for both people with mental health disabilities and youth, a
>larger proportion of their stops that began as consensual encounters resulted
>in searches, as compared to people without mental health disabilities or
>adults.

Starting with the 2022 report, the Board recommended severely limiting or
ending consent searches. By the 2023 report (covering 2021 data), the
recommendation strengthened to prohibiting consent and supervision searches
entirely and moving to a probable cause standard.

### Basis for search (`BFS_*`)

When a search is conducted, the officer records the legal basis:

| Column | Basis |
|--------|-------|
| `BFS_CONSENT_GIVEN` | Consent given |
| `BFS_OFFICER_SAFETY` | Officer safety |
| `BFS_SEARCH_WARRANT` | Search warrant |
| `BFS_PAROLE` | Parole/probation condition |
| `BFS_SUSPECT_WEAPON` | Suspected weapon |
| `BFS_VISIBLE_CONTRABAND` | Visible contraband |
| `BFS_ODOR_CONTRABAND` | Odor of contraband |
| `BFS_CANINE_DETECT` | Canine detection |
| `BFS_EVIDENCE` | Evidence of a crime |
| `BFS_INCIDENT` | Incident to arrest |
| `BFS_EXIGENT_CIRCUM` | Exigent circumstances |
| `BFS_VEHICLE_INVENT` | Vehicle inventory |
| `BFS_SCHOOL_POLICY` | School policy |

Multiple bases can be indicated for a single search.

### Contraband and evidence discovered (`CED_*`)

After a search, the officer records what was found:

| Column | Item |
|--------|------|
| `CED_NONE_CONTRABAND` | Nothing found |
| `CED_FIREARM` | Firearm |
| `CED_AMMUNITION` | Ammunition |
| `CED_WEAPON` | Other weapon |
| `CED_DRUGS` | Drugs/narcotics |
| `CED_ALCOHOL` | Alcohol |
| `CED_MONEY` | Money |
| `CED_DRUG_PARAPHERNALIA` | Drug paraphernalia |
| `CED_STOLEN_PROP` | Stolen property |
| `CED_ELECT_DEVICE` | Electronic device |
| `CED_OTHER_CONTRABAND` | Other contraband |

The **discovery rate** (also called "hit rate") --- the proportion of searches
that find contraband --- is a critical metric for assessing whether search
decisions are applied equitably across racial groups. Every RIPA Board report
since 2020 has documented the same pattern: Black and Hispanic individuals are
searched at higher rates than White individuals, but contraband is found at
*lower* rates. This pattern is consistent with a lower evidentiary threshold
for searching people of color.

### Property seizure (`BPS_*`, `TPS_*`)

When property is seized, the officer records the legal basis for seizure
(`BPS_*`: safekeeping, contraband, evidence, vehicle impound, abandoned
property, school policy violation) and the type of property (`TPS_*`: firearm,
ammunition, weapon, drugs, alcohol, money, drug paraphernalia, stolen property,
cellphone, vehicle, other contraband).

### Result of stop (`ROS_*`)

The outcome of the stop. Multiple results can apply.

| Column | Result |
|--------|--------|
| `ROS_NO_ACTION` | No action taken |
| `ROS_WARNING` | Warning (2018--2023; combined verbal and written) |
| `ROS_VERBAL_WARNING` | Verbal warning (2024 only) |
| `ROS_WRITTEN_WARNING` | Written warning (2024 only) |
| `ROS_CITATION` | Citation issued |
| `ROS_IN_FIELD_CITE_RELEASE` | In-field cite and release |
| `ROS_CUSTODIAL_WARRANT` | Custodial arrest (warrant) |
| `ROS_CUSTODIAL_WITHOUT_WARRANT` | Custodial arrest (no warrant) |
| `ROS_FIELD_INTERVIEW_CARD` | Field interview card completed |
| `ROS_NONCRIMINAL_TRANSPORT` | Noncriminal transport or caretaking |
| `ROS_CONTACT_LEGAL_GUARDIAN` | Contacted legal guardian or responsible adult |
| `ROS_PSYCH_HOLD` | Psychiatric hold (W&I Code 5150) |
| `ROS_US_HOMELAND` | Turned over to US Homeland Security |
| `ROS_REFERRAL_SCHOOL_ADMIN` | Referred to school administrator |
| `ROS_REFERRAL_SCHOOL_COUNSELOR` | Referred to school counselor |

**Cross-era note:** In 2018--2023, verbal and written warnings are combined
into `ROS_WARNING`. In 2024, they are separate (`ROS_VERBAL_WARNING`,
`ROS_WRITTEN_WARNING`). To compare warning rates across all years, combine
the two 2024 columns.

Some results have associated CJIS violation codes (`ROS_*_CDS` columns).

The RIPA Board found that Black individuals had "no action" taken during their
stops at the highest rate of any group --- 13.1% in 2020 data versus 5.6% for
White individuals --- suggesting that many stops of Black individuals lacked
enforcement justification. The 2022 report found those who were perceived to be
Transgender received field interview cards at 2--3 times the rate of perceived
cisgender people. The 2024 report found that Black individuals received field
interview cards at 4.4 times the statewide per-capita average and recommended
prohibiting field interview cards absent arrest.

### School-related fields

| Column | Description |
|--------|-------------|
| `SCHOOL_CODE` | School identifier |
| `SCHOOL_NAME` | School name |
| `STOP_STUDENT` | Person is a student (0/1) |
| `K12_SCHOOL_GROUNDS` | Stop on K-12 school grounds (0/1) |

These fields capture stops involving students and stops on school property,
relevant to the Board's education-related recommendations.


## Schema changes over time

The dataset schema has evolved across two major eras:

### 2018--2023 era (~142 raw columns)

The original schema used combined action flags (`ADS_*`), a single warning
result (`ROS_WARNING`), a single LGBT field, and did not include stop type,
call-for-service, or many of the demographic detail fields added later.

### 2024 era (~202 raw columns)

A major overhaul that:

- **Split actions** into non-force (`NFA_*`) and force (`OFA_*`) with many
  new subcategories (e.g., Terry frisks, baton drawn vs. used, firearm
  unholstered)
- **Split warnings** into verbal and written
- **Added stop type** fields (`TOS_VEHICULAR`, `TOS_BICYCLE`, `TOS_PEDESTRIAN`)
- **Added "reason given"** (`RFS_RG_*`) columns capturing what was communicated
  to the person stopped
- **Added probable cause** subcategories (`RFS_PC_*`)
- **Added consent type** (`CTP_VERBAL`, `CTP_WRITTEN`, `CTP_IMPLIED`)
- **Added** `CALL_FOR_SERVICE`, `PERSON_UNHOUSED`, `PASSENGER_IN_VEHICLE`,
  `INSIDE_RESIDENCE`, `WELFARE_WELLNESS_CHECK`
- **Expanded** `REASON_FOR_STOP` from 8 to 10 values (added probable cause
  to arrest and W&I Code 5150)
- **Renamed** demographic columns to more inclusive terminology
  (e.g., `G_MALE` to `G_CISGENDER_MAN`, `RAE_HISPANIC_LATINO` to
  `RAE_HISPANIC_LATINEX`)

### Unified schema (235 columns)

The cleaned dataset uses a union of both eras. Columns that don't exist in a
given year are filled with NULL. Column names use the 2024 canonical forms
for all years.


## Key findings from the RIPA Board

The RIPA Board has published annual reports since 2018. Below are selected
findings particularly relevant to data users.

### Search rates and discovery rates

Every report from 2020 onward documents the same pattern: Black and Hispanic
individuals are searched at higher rates than White individuals, but
contraband is found at lower rates. This is the empirical backbone of the
Board's recommendations on search policy. The 2020 report stated:

> Search discovery rate analyses showed that, when officers searched stopped
> individuals, individuals of all racial or ethnic groups of color, with the
> exception of Asian and Middle Eastern/South Asian individuals, had higher
> search rates despite having lower rates of discovering contraband compared
> to individuals perceived as White.

### Pretextual stops

The Board has called for eliminating pretextual stops since 2022 and has
documented the effectiveness of pretextual stop bans:

- **LAPD** (Policy 240.06, March 2022): The 2026 report noted reductions in
  non-moving violations, decreases in searches, and increases in contraband
  discovery rates following the policy's implementation.
- **SFPD** (Policy 9.07.04(a), adopted 2023): The 2026 report (covering 2024
  data) noted that the policy was still very recent, and the effects were
  "difficult to ascertain." A [more recent
  analysis](https://sfpublicdefender.org/2026/01/14/new-data-shows-pretext-stops-policy-has-reduced-racial-profiling-in-san-francisco/)
  including data through September 2025 found reductions in stops of Black
  drivers following the policy's going into effect.

The 2023 report estimated that in 2019, officers spent approximately **80,000 hours** on traffic stops that yielded no enforcement action, and that for local agencies, 28,000 of those hours were spent on non-moving violations yielding no action.

### Youth

The 2025 and 2026 reports highlighted youth stop patterns:

- 823,773 stops were of individuals perceived to be under 25 in 2023 (17.5% of
  all stops)
- Youth ages 12--14 experienced the highest rates of searches, handcuffing,
  and curbside detention
- Black youth 12--14: limited force used at a rate of 42.3%
- The Board recommended convening an expert panel on youth policing and
  expanding diversion programs

### Disability

The 2022 report found that people perceived to have a mental health condition
were subjected to force at 5.2 times the rate of people with no disability,
and searched at 4.8 times the rate. The Board recommended increased
crisis-intervention training.

### No-action stops

Across all years, Black individuals have the highest rate of stops resulting
in no enforcement action, suggesting that many stops lack justification. In
the 2020 data, no action was taken in 13.1% of stops of Black individuals
versus 5.6% of stops of White individuals.


## Additional resources

- **RIPA Board**: [About the RIPA Board](https://oag.ca.gov/ab953/board)
- **RIPA Board annual reports**: [Attorney General's AB 953 page](https://oag.ca.gov/ab953/board/reports)
- **RIPA stop data downloads**: [CA DOJ OpenJustice Data Portal](https://openjustice.doj.ca.gov/data)
- **AB 953 statute**: [California Legislative Information](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201520160AB953)
- **California Penal Code
13519.4**: [CA Legislative Information](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=13519.4.)
