# Methodology: How the Metrics Are Defined

Every number on this site is computed from the raw DOJ stop-level records via
[open-source code](https://github.com/HRDAG/ripadb). This page documents the
definitional choices behind the metrics that are reported, so that the results
can be independently replicated. The authoritative definitions are the
materialized views in
[`database/src/schema.sql`](https://github.com/HRDAG/ripadb/blob/main/database/src/schema.sql)
and the rate calculations in
[`api/src/queries.py`](https://github.com/HRDAG/ripadb/blob/main/api/src/queries.py).

[TOC]

## Unit of observation: person-stops

Each row in the RIPA data is a **person-stop**: one person involved in one
stop. A single stop (one `DOJ_RECORD_ID`) can involve multiple people. Unless
labeled otherwise, counts and rates on this site are computed over
person-stops; "unique stops" counts distinct stop records.

## Race/ethnicity categories mean single perceived race *alone*

RIPA officers can mark multiple perceived races. The DOJ's summary field
(`RAE_FULL`), which we use everywhere, assigns codes 1--7 only when exactly one
race was perceived; any combination of two or more becomes **Multiracial**
(code 8, about 1.1% of person-stops).

## "Searched"

A person-stop counts as searched if a search of the person **or** a search of
their property was reported:

- **2018--2023**: `ADS_SEARCH_PERSON OR ADS_SEARCH_PROPERTY`
- **2024**: `NFA_SEARCH_PERSON OR NFA_SEARCH_PROPERTY OR NFA_TERRY_FRISK`

The 2024 inclusion of Terry frisks (pat-downs) is deliberate, and matches
how the RIPA Board itself treats the data. Under the RIPA regulations, a
search "includes a pat-down search of a person's outer clothing" (Cal. Code
Regs., tit. 11, § 999.224(a)(19), quoted in the
[2025 Board report](https://oag.ca.gov/system/files/media/ripa-board-report-2025.pdf),
p. 70), so before 2024 frisks were recorded inside "search of person"; the
2024 schema split them into their own field. The Board's
[2026 annual report](https://oag.ca.gov/system/files/media/ripa-board-report-2026.pdf),
which analyzes the 2024 data, accordingly uses a combined "Search & Terry
Frisk" measure in its statewide analyses (pp. 27--28) and counts frisks as a
share of "all searches" ("officers performed Terry frisks in 88,697 stops
(1.75% of all stops, 14.59% of all searches)," p. 82). Its LAPD chapter
likewise cautions that 2024 search-only counts drop sharply because Terry
frisks became "an option officers can choose on the RIPA form separate from
searches in 2024" (pp. 145--146).

The data agree: the statewide search rate trends smoothly with frisks
included (13.8% → 12.6% → 12.0% over 2022--2024) but drops artificially to
10.25% in 2024 without them. Frisk-only records are 14.6% of 2024 searches,
so an analyst who omits `NFA_TERRY_FRISK` will undercount 2024 searches by
roughly 15%.

## "Force used"

Force is a specific subset of the action-taken flags --- physical force
applied or a weapon pointed/discharged, not mere procedural actions:

- **2018--2023** (`ADS_*`): handcuffed, firearm pointed, firearm discharged,
  electronic control device used, impact projectile discharged, canine bite,
  baton, chemical spray, or "other physical or vehicle contact"
  (`ADS_OTHER_CONTACT`).
- **2024** (`OFA_*`): handcuffed, firearm pointed, firearm discharged, baton
  used, chemical spray, canine bite, electronic device used to stun (contact
  or dart), impact projectile discharged, physical compliance techniques,
  vehicle used as force, or person removed from vehicle by physical contact.

The pre-2024 and 2024 flag sets are not perfectly 1:1 (the 2024 schema split
several combined categories), but the net effect of the mapping differences
is about 0.3 percentage points. Note that flags recording a weapon merely
*drawn* or *pointed-but-not-discharged* device (`OFA_BATON_DRAWN`,
`OFA_ELECT_DEVICE_POINT`, `OFA_FIREARM_UNHOLSTERED`,
`OFA_IMPACT_PROJECTILE_POINT`, `OFA_CANINE_COMPLIANCE`) are **not** counted,
except firearm pointed, which is counted in both eras.

## "Arrested," "cited," "warned," "no action"

- **Arrested** = custodial arrest with warrant OR without warrant
  (`ROS_CUSTODIAL_WARRANT OR ROS_CUSTODIAL_WITHOUT_WARRANT`). In-field cite
  and release is counted as a citation, not an arrest.
- **Cited** = `ROS_CITATION OR ROS_IN_FIELD_CITE_RELEASE`.
- **Warned** = the combined `ROS_WARNING` field before 2024;
  `ROS_WRITTEN_WARNING OR ROS_VERBAL_WARNING` in 2024 (the field was split).
- **No action** = `ROS_NO_ACTION`.

## Hit rate --- and why it reads *backwards*

Hit rate = **searches that discovered contraband or evidence ÷ all
searches**, per group. "Contraband or evidence" is any of the `CED_*` flags
(firearm, ammunition, weapon, drugs, alcohol, money, drug paraphernalia,
stolen property, electronic device, other), evaluated only on person-stops
counted as searched. Note one difference from the RIPA Board's "discovery
rate" analyses: for 2024 the Board reports frisks separately from other
searches there (frisks yield much lower discovery rates; see its 2026
appendix, Table A39), while our 2024 hit-rate denominator includes
frisk-only records, consistent with our "searched" definition.

Unlike search, force, and arrest rates --- where *higher* values for a group
signal more enforcement --- a **lower** hit rate is the potential sign of
bias: it means searches of that group were less often justified by what they
found. A hit-rate disparity ratio *below* 1.0 vs. White is the warning sign,
which is why that column is not color-coded like the others. See
[The Hit Rate](hit-rate) for the full explanation, history, and limitations
of this metric.

## Disparity ratios

Rates are computed per group from raw counts (not from rounded percentages),
and each group's rate is divided by the rate for **White (code 7)** as the
reference group. Ratios are shown to two decimals; rounding happens only at
display time.

## Equipment-violation stops

The "Equipment violations" stop-type filter selects person-stops with
`REASON_FOR_STOP = 1` (traffic violation) **and**
`RFS_TRAFFIC_VIOLATION_TYPE = 2` (equipment violation, e.g. broken taillight
or tinted windows). These high-discretion stops are commonly used as an
indicator of potentially pretextual enforcement.

## Stop/Pop ratios: benchmark caveats

The Stop/Pop column divides a group's share of stops by its share of the
jurisdiction's **residential population** (ACS 5-Year B03002, 2019--2023).
Read it with care --- see [Population Benchmarks](population-benchmarks) for a
detailed discussion of this choice, and its limitations:

- **Residential population is a weak denominator** for traffic enforcement:
  the people driving through a jurisdiction are not the people living in it
  (commuters, visitors, highway traffic). Daytime or driving-age population
  can look very different.
- **Geography mappings are loose for some agency types**: city police map to
  their city (Census place), sheriffs to their whole county even though city
  police also patrol there, and CHP --- the largest agency --- to the entire
  state.
- **Perceived vs. self-reported race**: stop shares use the officer's
  perception; population shares use Census self-identification. The RIPA
  category Middle Eastern/South Asian has no Census equivalent, so it has no
  population share and slightly inflates other groups' stop shares relative
  to the benchmark.

## Gender categories across eras

The 2024 schema renamed the gender fields (e.g. `G_MALE` →
`G_CISGENDER_MAN`) and relabeled code 5 from "gender nonconforming"
(2018--2023) to "nonbinary person" (2024). The demographics gender table
blends both eras under the current labels. Gender is not used in the
disparity table.

## Where to check the code

- Column harmonization across schema eras:
  [`individual/RIPA-statewide/clean/`](https://github.com/HRDAG/ripadb/tree/main/individual/RIPA-statewide/clean)
- Metric definitions (the `CASE WHEN data_year < 2024` blocks):
  [`database/src/schema.sql`](https://github.com/HRDAG/ripadb/blob/main/database/src/schema.sql)
- Rate and ratio math:
  [`api/src/queries.py`](https://github.com/HRDAG/ripadb/blob/main/api/src/queries.py)
- Census crosswalk:
  [`match/ori-demographics/`](https://github.com/HRDAG/ripadb/tree/main/match/ori-demographics)
