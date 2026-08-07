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

This page describes the data itself --- where it comes from, how it is
collected, and what it does and does not contain. For how this site turns that
data into the numbers you see on each agency page --- race categories, what
counts as a search, force, or arrest, how disparity ratios and population
benchmarks are computed --- see [Methodology: How the Metrics Are
Defined](methodology).

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

### Instances of data fabrication or misreporting

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

Each year's data release comes with a README documenting "known errors" ---
records that failed the DOJ's logic checks but were never corrected by the
agency and entered the dataset anyway. The 2024 README notes that roughly
**1% of reported records have errors and are not resubmitted by the
reporting deadline**. Rather than transcribing every year's list, here are
the recurring categories, with the range of affected records per year, and
links to each README:
[2018](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2023-03/RIPA%20Dataset%20Read%20Me%202018%20Final.pdf),
[2019](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2023-03/RIPA%20Dataset%20Read%20Me%202019%20Final.pdf),
[2020](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2023-03/RIPA%20Dataset%20Read%20Me%202020%20Final.pdf),
[2021](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2023-03/RIPA%20Dataset%20Read%20Me%202021%20Final.pdf),
[2022](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2025-05/RIPA%20Dataset%20Read%20Me%202022.pdf),
[2023](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2025-05/RIPA%20Dataset%20Read%20Me%202023.pdf),
[2024](https://data-openjustice.doj.ca.gov/sites/default/files/dataset/2025-12/ripa-stop-dataset-readme-2024.pdf).

**Contradictory reason/action combinations.** The two largest recurring
errors are stops coded "consensual encounter resulting in search" with no
search recorded (28,148 records in 2018 --- likely officers misunderstanding
the form --- falling to 5,011 in 2019 and between 1 and 34 per year since),
and searches justified as "incident to arrest" where no arrest was recorded
(5,404 in 2018; 13,649 in 2019; 12,251 in 2020; 11,144 in 2021; this check
no longer appears in the 2022--2024 READMEs).

**Missing required subfields.** Every year includes records where a reason
for stop was given but its required subcategory was not: reasonable-suspicion
subcategories missing (from 2 records in 2018 up to 1,642 in 2019), traffic
violation type or offense code missing (roughly 15--65 records per year).

**Search and seizure inconsistencies.** Searches with no basis-for-search
recorded (2--424 per year), basis-for-search completed with no search
indicated, and property-seizure fields that contradict the actions-taken
flags (single digits to ~600 records per year).

**Missing or impossible values.** Small numbers of records each year are
missing race (1--3), gender (1--4), actions taken (up to 99 in 2022; 677
non-force and 1,279 force-action records in 2024), or result of stop (300
in 2024); others report impossible ages (0, 120, 445, -120, 1336, 9999) or
K-12 students perceived to be older than 22.

Beyond these record-level errors, the READMEs document several
**systematic, agency-level problems**:

- **CHP's missing transgender records (2020)**: a transmission bug caused
  "nearly all individuals perceived to be transgender" to be excluded from
  CHP's successfully submitted 2020 data (over 1,000 records). CHP fixed the
  issue starting with 2021 data.
- **Missing December 31, 2022 records**: 4,066 corrected records from the
  last day of 2022 (0.09% of that year's records) failed to load into the
  DOJ's analysis table and are excluded from the 2022 data file and the 2024
  Board Report; the DOJ publishes them as a separate supplement file on
  OpenJustice.
- **Placeholder citation codes**: several agencies --- including the LA
  County Sheriff, LAPD, and CHP in early years, and six agencies in 2023 ---
  submitted only a single generic value (65002) for the citation offense
  code field, making citation offense detail unusable for those agencies.
- **Community caretaking stops are not separately identifiable**: there is
  no "community caretaking" reason for stop; officers are instructed to
  select "reasonable suspicion" plus a special offense code (99990), and the
  READMEs caution that many officers may not have used the code.

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
person. From the RIPA Board's 2018 report:

>With respect to the person stopped, the officer must report his/her own
>perception, based upon personal observation only (and not through any other
>means, such as asking the person or referring to identification), regarding
>the following:
>
>1. Perceived race or ethnicity of the person stopped
>2. Perceived age of the person stopped
>3. Perceived gender of the person stopped
>4. Whether the person stopped is perceived to be lesbian, gay, bisexual or
>   transgender
>5. Whether the person stopped is perceived to have limited or no English
>   fluency
>6. Whether the person stopped is perceived or known to have a disability

For a detailed reference covering every variable group in the dataset --- and
how the schema changed over time --- see [Variable groups and schema
changes](variables-and-schema).

## Additional resources

- **Metric definitions**: [Methodology: How the Metrics Are Defined](methodology)
- **Variable-level documentation**: [Variable groups and schema changes](variables-and-schema)
- **RIPA Board**: [About the RIPA Board](https://oag.ca.gov/ab953/board)
- **RIPA Board annual reports**: [Attorney General's AB 953 page](https://oag.ca.gov/ab953/board/reports)
- **RIPA stop data downloads**: [CA DOJ OpenJustice Data Portal](https://openjustice.doj.ca.gov/data)
- **AB 953 statute**: [California Legislative Information](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201520160AB953)
- **California Penal Code
13519.4**: [CA Legislative Information](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=13519.4.)
