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

- **Variable-level documentation**: [Variable groups and schema changes](variables-and-schema)
- **RIPA Board**: [About the RIPA Board](https://oag.ca.gov/ab953/board)
- **RIPA Board annual reports**: [Attorney General's AB 953 page](https://oag.ca.gov/ab953/board/reports)
- **RIPA stop data downloads**: [CA DOJ OpenJustice Data Portal](https://openjustice.doj.ca.gov/data)
- **AB 953 statute**: [California Legislative Information](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201520160AB953)
- **California Penal Code
13519.4**: [CA Legislative Information](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=13519.4.)
