# Population Benchmarks

A claim that a group is stopped "too often" is a comparison, and every
comparison needs something to compare against. Counting stops is easy; deciding
what the count *should* be is the hard part. That second number --- the
denominator --- is called a **benchmark**, and the choice of benchmark is an
important methodological decision in stop-data analysis.

This site uses residential population from the Census as its benchmark, in the
**Stop/Pop** columns on the Demographics and Disparities tabs and in the
jurisdiction population shown in each agency's header. This article describes
that choice, as well as limitations and possible alternatives. It also reviews
what the RIPA Board uses in its reports.

[TOC]

## Why a benchmark is needed at all

If an agency reports that 40% of the people it stopped were Hispanic/Latine(x),
that fact is uninterpretable until you know what share of the people *available
to be stopped* were Hispanic/Latine(x). The RIPA Board put it plainly in its
[2019
report](https://oag.ca.gov/sites/all/files/agweb/pdfs/ripa/ripa-board-report-2019.pdf),
written before any stop data had arrived, while it was still deciding what
methods to use:

> Benchmarks are important in the analysis of racial bias because they reflect
> what behavior would be in an unbiased world. For example, if the benchmark
> data suggest that two racial or identity groups are present at equal
> proportions, but one group constitutes the vast majority of stops, then this
> could indicate racial bias. (p. 23)

The Board also described what the gold-standard benchmark would look like, and
why nobody builds one at statewide scale:

> A typical approach to establishing benchmarks for traffic stops, for example,
> would involve human observers standing at intersections and streets in order
> to record the number and percentage of drivers from different racial or
> ethnic groups that pass through by vehicle. [...] This approach to
> establishing benchmarks is time and resource intensive. Therefore,
> establishing similar benchmarks for the entire state would be unrealistic and
> infeasible. (p. 23)

Residential population is the fallback because it is available and consistently
defined across every jurisdiction in the state. While it is a useful
comparison, it has important limitations, which are discussed below, and is
meant to be interpreted alongside other metrics rather than as a standalone
measure of bias.

## What the Stop/Pop number on this site is

The **Stop/Pop** ratio divides a group's share of an agency's stops by that
group's share of the resident population of the agency's jurisdiction. A value
of 2.0 means the group made up twice as large a share of stops as it does of
residents.

Population comes from the Census Bureau's American Community Survey 5-Year
Estimates, table B03002 (Hispanic or Latino Origin by Race), vintage 2019--2023.
Agencies are mapped to geographies the same way the RIPA Board maps them: city
police departments to their Census place, sheriff's offices to their county, and
the California Highway Patrol to the state as a whole. See the
[methodology article](methodology) for the full definition and the
[code that builds the crosswalk](https://github.com/HRDAG/ripadb/tree/main/match/ori-demographics).

## Criticisms

Samuel Walker detailed objections to residential-population benchmarking in his
2001 article ["Searching for the Denominator: Problems with Police Traffic Stop
Data and an Early Warning System
Solution"](https://www.ojp.gov/ncjrs/virtual-library/abstracts/searching-denominator-problems-police-traffic-stop-data-and-early)
(*Justice Research and Policy* 3(1): 63--95, 2001), and these problems have
continued to be discussed in the literature. The core problems:

**The people stopped are not the people who live there.** Drivers commute,
travel, and pass through. Officers patrol highways and commercial corridors.
Lance Hannon's ["Neighborhood Residence and Assessments of Racial Profiling
Using Census
Data"](https://journals.sagepub.com/doi/full/10.1177/2378023118818746)
(*Socius* 5, 2019) measured how large this gap can be in the context of
pedestrian stops: across more than 100,000 investigatory stops of pedestrians
in Chicago, only about a quarter of the people stopped in a police beat
actually lived in that beat, and in majority-white beats, restricting the
comparison to residents cut the median disparity ratio by roughly two-thirds.
Notably, substantial disparities *survived* the correction --- the benchmark
problem inflates disparity estimates, but it does not explain them away.

**The geography is approximate.** A city police department's jurisdiction is
not exactly its Census place; a sheriff patrols unincorporated areas but shares
the county with municipal departments that also report stops; and CHP, the
largest reporting agency in the state, is benchmarked against all of California
even though its enforcement is concentrated on highways. The Board flags this
in [its own
appendix](https://oag.ca.gov/system/files/media/ripa-appendix-2026.pdf#page=143):
"These comparisons are approximate since agency jurisdictions do not always map
perfectly to the boundaries of their primary city or county of service."

**Race is measured two different ways.** RIPA records the *officer's perception*
of race; the ACS records *self-identification*. Comparing them assumes the two
usually agree.

**The Census itself has error.** Undercounts are not uniform across groups, and
the Census Bureau changed its ACS methodology in response to pandemic-era
non-response, affecting estimates that include 2020.

Police-training and consulting organizations argue that census benchmarking
systematically overstates disparities and should not be used at all (see, e.g.,
the Dolan Consulting Group's ["Racial Profiling or Bad Research? We Shouldn't
Use Census
Data"](https://www.dolanconsultinggroup.com/news/racial-profiling-or-bad-research/)).
That version of the argument is often deployed to dismiss disparity findings
entirely, which is a stronger claim than the evidence supports. For instance
Hannon's result referenced above is that better denominators *shrink* measured
disparities, not that they eliminate them.

## What the RIPA Board does

The Board does three things at once, and it is worth separating them.

**It reports a residential population comparison.** Every annual report since
the data started arriving includes one. The [2026
report](https://oag.ca.gov/system/files/media/ripa-board-report-2026.pdf)
(covering 2024 stops) states that "individuals perceived to be Black were
stopped 127.87 percent more often than expected, and individuals perceived to
be Pacific Islander 57.53 percent more often than expected, given the
population of the state," while "individuals perceived to be Multiracial were
stopped 76.39 percent less often than expected, and individuals perceived to be
Asian were stopped 51.86 percent less often than expected" (p. 30). Per-agency
comparisons appear in the appendix tables, built the same way this site builds
them --- city police against their place, sheriffs against their county, CHP
against the state.

**It states the limitations explicitly.** Appendix D, Section D1 of the [2026
appendix](https://oag.ca.gov/system/files/media/ripa-appendix-2026.pdf) opens
with a list echoing the criticisms above: commuter stops ("individuals may be
stopped outside of their residential area (e.g. commuting to work, tourists)"),
differential exposure ("individuals from different groups may also engage in
activities, such as driving, with different average frequencies"), census
response bias, and the perceived-versus-self-reported race mismatch. That
appendix is the best short statement of the problem published anywhere in the
RIPA literature, and it is worth reading directly.

An important detail from that appendix: for the 2026 report the Board switched
from the Census summary table B03002 --- which is what this site uses --- to
ACS microdata via [IPUMS](https://usa.ipums.org/usa/), specifically so it could
reconstruct a Middle Eastern/South Asian category that has no equivalent in the
published Census tables, and so it could break population down by age and by
intersecting identities ([see issue
23](https://github.com/HRDAG/ripadb/issues/23)).

**It leans on methods that need no benchmark at all.** This is the more
important point. From the beginning, the Board's plan was to rely primarily on
two techniques chosen precisely because they sidestep the denominator:

- The **veil of darkness** test, which compares the racial composition of stops
  made in daylight to those made after dark during the same clock hours, using
  seasonal and daylight-saving shifts in sunset time. The 2019 report explains
  that it "is less susceptible to issues surrounding external or
  manually-collected benchmarking data because it takes advantage of daylight
  savings changes to establish a benchmark" (p. 23). The method is due to
  [Grogger and Ridgeway
  (2006)](https://www.rand.org/content/dam/rand/pubs/reprints/2007/RAND_RP1253.pdf),
  "Testing for Racial Profiling in Traffic Stops from Behind a Veil of
  Darkness," *Journal of the American Statistical Association* 101(475):
  878--887, and was first applied to Oakland stop data.
- The **outcome test** on search results --- what the Board calls the discovery
  rate. "Like the veil of darkness approach, the outcome test does not require a
  benchmark in order to work. This is because the comparisons being drawn are
  between hit rates of identity groups who are searched" (p. 25). See
  [The Hit Rate](hit-rate) for a full treatment.

The same logic applies to most of the metrics on this site's Disparities tab.
Search, force, and arrest **rates** are conditioned on being stopped --- their
denominator is stops, not population --- so they do not depend on the Census at
all. Only the Stop/Pop column does.

## Alternatives

**Daytime population.** If the problem is that residents are not the population
at risk, one fix is to adjust for who is actually present.

Gelman, Fagan, and Kiss did this in their analysis of NYPD stop-and-frisk (["An
Analysis of the New York City Police Department's 'Stop-and-Frisk' Policy in
the Context of Claims of Racial
Bias"](https://sites.stat.columbia.edu/gelman/research/published/frisk9.pdf),
*Journal of the American Statistical Association* 102(479): 813--823, 2007).
Their study used multiple benchmarks for robustness. This included a population
benchmark, but adjusted to reflect differences between daytime populations and
residential populations. Precincts with small residential populations but heavy
commercial activity had their population estimates adjusted using the Census
Bureau's "journey file," which uses commute times and job classifications to
estimate day and night populations of census tracts; tracts were aggregated to
precincts, and stop rates were computed separately for daytime and nighttime
intervals.

**Crash-involved drivers.** Another possible benchmark uses the population of
drivers who were involved in, but not at fault for, two-vehicle collisions. The
idea is that being struck by another driver is roughly independent of your own
behavior, so not-at-fault drivers approximate a random sample of who is on the
road. Geoffrey Alpert, Michael Smith, and Roger Dunham validated the approach
in ["Toward a Better Benchmark: Assessing the Utility of Not-at-Fault Traffic
Crash Data in Racial Profiling
Research"](https://journals.sagepub.com/doi/10.3818/JRP.6.1.2004.43) (*Justice
Research and Policy* 6(1): 43--69, 2004), comparing not-at-fault crash
demographics against direct roadway observation at the same Miami-Dade
intersections and finding the two agreed closely.

California has the data to do this. The Statewide Integrated Traffic Records
System (SWITRS), collected by CHP and made accessible through UC Berkeley
SafeTREC's [Transportation Injury Mapping System
(TIMS)](https://tims.berkeley.edu/), includes a party-level `RACE` field ("A -
Asian, B - Black, H - Hispanic, O - Other, W - White") and an `AT_FAULT` flag
("Y - Yes, N - No"), with crashes geocoded to specific locations. In principle
that allows a not-at-fault-driver benchmark to be built for any jurisdiction in
the state and compared against RIPA traffic stops in the same place. See
[github issue 24](https://github.com/HRDAG/ripadb/issues/24).
