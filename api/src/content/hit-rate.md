# The Hit Rate

The **hit rate** is the fraction of searches that actually turn up contraband
or evidence. It is a key disparity metric because it measures whether searches
of one group are held to a lower standard of suspicion than searches of
another: if searches of Black drivers succeed less often than searches of
White drivers, officers are on average searching Black drivers on weaker
evidence.

[TOC]

## What the hit rate measures

Most disparity metrics on this site describe how often something happens to
people who are stopped: how often they are searched, handcuffed, or arrested.
Those rates can differ across groups for many reasons, and agencies often
respond to disparities by pointing to differences in where and when they
patrol, or in the behavior officers encounter.

The hit rate asks a different question: *when officers decided a search was
justified, how often were they right?* A search is a "hit" if the officer
found contraband or evidence. Because the hit rate conditions on the officer's
own decision to search, it is an **outcome test**: it evaluates the quality of
the decisions themselves rather than the raw frequency of enforcement.

The logic of interpretation is **inverted** relative to the other columns in
the disparities table. For search, force, and arrest rates, a *higher* rate
for a group is a potential sign of over-enforcement. For the hit rate, a
*lower* rate for a group is the warning sign: it means searches of that group
were less likely to be justified by what they found. A group with a hit-rate
disparity ratio *below* 1.0 relative to White individuals is being searched on
comparatively weaker evidence.

## Where the idea comes from

The outcome test traces back to the economist Gary Becker's *The Economics of
Discrimination* (University of Chicago Press, 1957), which modeled
discrimination as a "taste" that decision-makers indulge at a cost. Becker's
insight was that a prejudiced decision-maker will accept worse outcomes from
the group they disfavor: a lender who dislikes some group of borrowers will
hold them to a higher bar, so the marginal loans they *do* make to that group
will perform better, not worse. Comparing outcomes across groups can therefore
reveal a discriminatory bar even when the decision-making process is
unobservable.

[Knowles, Persico, and Todd
(2001)](https://pricetheory.uchicago.edu/levitt/Papers/KnowlesPersicoTodd2001.pdf)
("Racial Bias in Motor Vehicle Searches: Theory and Evidence," *Journal of
Political Economy* 109(1): 203–229) brought this logic to police searches.
In their model, officers who care only about finding contraband will allocate
searches so that hit rates equalize across groups; persistently lower hit
rates for one group indicate that officers are applying a lower threshold of
suspicion to that group. [Ayres
(2002)](https://journals.sagepub.com/doi/abs/10.3818/JRP.4.1.2002.131)
("Outcome Tests of Racial Disparities in Police Practices," *Justice Research
and Policy* 4(1–2): 131–142) generalized the argument and applied it to
police data, and [Anwar and Fang
(2006)](https://www.aeaweb.org/articles?id=10.1257/000282806776157579) ("An
Alternative Test of Racial Prejudice in Motor Vehicle Searches," *American
Economic Review* 96(1): 127–151) developed related tests that are robust to
some of the original model's assumptions.

## Recent applications

The hit rate has become a standard tool in large-scale empirical studies of
police stops:

- The Stanford Open Policing Project analyzed nearly 100 million traffic
  stops nationwide ([Pierson et al. 2020](https://www.nature.com/articles/s41562-020-0858-1),
  "A large-scale analysis of racial disparities in police stops across the
  United States," *Nature Human Behaviour* 4: 736–745) and found that
  searches of Black and Hispanic drivers turned up contraband at lower rates
  than searches of White drivers, evidence that the bar for searching those
  drivers was lower.
- California's own [RIPA Board annual
  reports](https://oag.ca.gov/ab953/board/reports) have used the metric in
  every report since the Board began analyzing stop data --- see the next
  section.
- Researchers at Stanford also developed the "threshold test"
  ([Simoiu, Corbett-Davies, and Goel 2017](https://5harad.com/papers/threshold-test.pdf),
  "The Problem of Infra-marginality in Outcome Tests for Discrimination,"
  *Annals of Applied Statistics* 11(3): 1193–1216), a Bayesian refinement
  that jointly estimates search thresholds and risk distributions rather than
  comparing average hit rates directly.

## How the RIPA Board defines and uses it

The RIPA Board --- the state body that publishes the annual reports this data
comes from --- has relied on this metric from the start, though its name has
shifted: "hit rates" (2019), "search yield rates" (2020), and "discovery
rates" (2021 onward).

The Board's [2019
report](https://oag.ca.gov/sites/all/files/agweb/pdfs/ripa/ripa-board-report-2019.pdf),
which laid out the methodology it planned to apply once data arrived,
introduced the outcome test in the academic literature's own terms:

> Outcome tests compare the discrepancies between the percentages of
> successful searches conducted on stopped individuals. These percentages are
> also referred to as "hit rates." For discretionary searches based upon
> consent, reasonable suspicion, or probable cause, equal hit rates across
> identity groups may signify a lack of bias, whereas differences may imply
> differential standards in conducting a search. (p. 25, citing Knowles et
> al. 2001)

The [2020
report](https://oag.ca.gov/sites/all/files/agweb/pdfs/ripa/ripa-board-report-2020.pdf),
the first to analyze actual stop data (July--December 2018, from the eight
largest agencies), operationalized the metric as the "search yield rate":
"proportion of searched individuals found in possession of contraband or
evidence" (p. 36), "a measure of search efficacy" (p. 37). Its executive
summary reported that "when officers searched individuals, contraband or
evidence was generally found on White individuals at higher rates than
individuals from all other groups," and that for the highest-discretion
searches --- those based only on consent --- "yield rates for racial/ethnic
groups of color were lower than for White individuals" (pp. 9--10).

The [2021
report](https://oag.ca.gov/sites/all/files/agweb/pdfs/ripa/ripa-board-report-2021.pdf)
(2019 data) settled on the current name, explaining that the analyses "are
also often referred to in research literature as 'hit rates,'" but that
"'discovery rates' is a more transparent term" because it matches the
"Contraband or Evidence Discovered" data element in the RIPA regulations
(p. 48). The same page states the test's logic in the Board's words:

> One assumption of the test is that if officers are less likely to find
> contraband after searching people of a particular identity group, then
> those individuals are objectively less suspicious and may be searched, at
> least in part, because of their perceived identity. (p. 48)

Its headline finding: "individuals perceived as Black, Hispanic, and Native
American had higher search rates despite having lower rates of discovering
contraband compared to individuals perceived as White" (p. 11).

Discovery-rate disparities have also driven the Board's policy
recommendations. The [2022
report](https://oag.ca.gov/system/files/media/ripa-board-report-2022.pdf)
found that consent-only searches of Black, Hispanic/Latine(x), and
Multiracial individuals "resulted in lower rates of discovery of contraband
(8.5%, 11.3%, and 13.0% respectively) than searches of all other
racial/ethnic groups" (p. 11), and partly on that basis the Board
"recommends severely limiting or ending the practice of consent searches"
(p. 12).

The metric remains central in the most recent report: the [2026
report](https://oag.ca.gov/system/files/media/ripa-board-report-2026.pdf),
analyzing the 2024 data, found that "consent searches yielded lower
discovery rates (20.30%) than non-discretionary searches (26.40%)" and that
"[o]fficers reported the lowest discovery rates in consent searches of
individuals perceived as Black (16.59%) and Native American (18.29%) and
highest for individuals perceived as Pacific Islander (25.26%) and White
(24.16%)" (p. 11; detailed analysis at pp. 63--64). Those 2024 figures
exclude Terry frisks, a break from earlier years explained in the next
section.

## The 2024 break: frisks split out of the discovery rate

Starting with the 2024 data, the RIPA form gives officers a separate box for a
Terry frisk --- a pat-down of outer clothing for weapons --- rather than
folding it into "search of person." That schema change forced a
methodological break in the Board's own discovery-rate analyses, and it
matters for reading any 2024 hit rate.

The Board did not drop frisks from its search *counts*. Its
actions-during-stop analyses use a combined "Search & Terry Frisk" measure,
and appendix Table A38 gives a "Total Search Count" of 607,762 that includes
frisk-only records --- the same denominator behind the statement that
frisks were 14.59% "of all searches" (2026 report, p. 82). But in the
discovery-rate analyses the Board takes frisks *out*, and says so:

> In this section, the denominator is not all stops, as it is in most other
> analyses in this report, but all searches. Also, as of the 2024 RIPA data
> collection, officers are not required to record a basis for search in Terry
> frisks, so this analysis only analyzes stops in which a search of person or
> property occurred. ([2026
> report](https://oag.ca.gov/system/files/media/ripa-board-report-2026.pdf),
> p. 63, n. 76)

The reason is partly mechanical --- a frisk has no recorded basis for search,
so it cannot be sorted into "consent-only" or "non-discretionary" --- and
partly substantive: a frisk is a different act with a different purpose
(weapons, not evidence), and it turns up contraband at less than half the
rate of a full search. Appendix Table A39 reports the two separately:

| Perceived race/ethnicity | Search, no frisk | Frisk, no search |
|--------------------------|-----------------:|-----------------:|
| Asian | 23.51% | 8.22% |
| Black | 28.38% | 13.05% |
| Hispanic/Latine(x) | 25.47% | 13.37% |
| Middle Eastern/South Asian | 21.81% | 6.66% |
| Multiracial | 30.05% | 11.31% |
| Native American | 25.18% | 5.59% |
| Pacific Islander | 27.48% | 5.05% |
| White | 29.69% | 9.58% |
| **Statewide** | **27.23%** | **12.34%** |

The Board also added a standalone section on frisk disparities in this report
(2026 report, pp. 82--83), reporting frisk-only stops --- frisks with no
accompanying search --- at 3.32% of stops of individuals perceived as Black
against 1.04% for those perceived as White. Since a frisk requires only
reasonable suspicion that a person is armed ---
a lower bar than the probable cause or consent behind most searches --- who
gets frisked is itself a discretion question, and the outcome-test logic
applies to frisks on their own terms.

## Limitations

The hit rate is informative but not decisive, and it should be read with its
known weaknesses in mind:

**Infra-marginality.** The formal outcome test concerns the *marginal* search
--- the one just barely worth conducting --- but observed hit rates are
*averages* over all searches. If groups have different underlying
distributions of suspicion, average hit rates can differ even when officers
apply identical thresholds, and can even point in the wrong direction. This
is the central statistical objection to the hit-rate comparison (see
[Ayres 2002](https://journals.sagepub.com/doi/abs/10.3818/JRP.4.1.2002.131)
and [Simoiu et al. 2017](https://5harad.com/papers/threshold-test.pdf), whose
threshold test was designed specifically to mitigate it).

**Equilibrium assumptions.** [Engel and Tillyer
(2008)](https://www.tandfonline.com/doi/abs/10.1080/07418820701717243)
("Searching for Equilibrium: The Tenuous Nature of the Outcome Test,"
*Justice Quarterly* 25(1): 54–71) argue that the economic model behind the
test --- officers as rational hit-rate maximizers, motorists adjusting their
behavior in response --- is a fragile foundation for real-world enforcement
data.

**Search types are mixed.** Not all searches are discretionary. Searches
incident to arrest, inventory searches of impounded vehicles, and searches
required by warrant or parole/probation conditions happen regardless of the
officer's suspicion, and lumping them in with discretionary searches dilutes
the signal. Terry frisks, separately identifiable from 2024 onward, are a
fourth distinct type with their own much lower yield. The RIPA Board itself
makes these distinctions, comparing "non-discretionary" searches against
consent-only searches (with frisks excluded from both) --- and has repeatedly
found that consent-only searches of individuals perceived as Black had the
lowest discovery rates of any group
([2022 report](https://oag.ca.gov/system/files/media/ripa-board-report-2022.pdf),
p. 11;
[2026 report](https://oag.ca.gov/system/files/media/ripa-board-report-2026.pdf),
p. 11). The site-wide hit rate on this site makes none of these
distinctions.

**What counts as a "hit."** The measure treats all contraband equally: a
small amount of marijuana and a firearm both count. Studies that weight finds
by seriousness can reach different conclusions than raw hit rates.

**Small numbers.** For smaller agencies, or when filtering to a single year
or stop type, hit rates are computed from few searches and can swing wildly.
A hit-rate disparity based on a handful of searches is weak evidence either
way.

## How this site computes it

In the disparities table, the hit rate is **searches that found contraband or
evidence ÷ all searches**, computed per perceived racial/ethnic group from
the RIPA contraband-or-evidence-discovered fields. All search types
(discretionary and non-discretionary) are included. The "Disp." column next
to the hit rate is the ratio of a group's hit rate to the White hit rate ---
and unlike the other disparity columns, values *below* 1.0 are the potential
sign of bias.

For 2024, and unlike the Board's discovery-rate analyses, the denominator
here **includes frisk-only records**. That keeps the metric comparable across
years --- before 2024 a frisk was recorded as a search of the person, so
every pre-2024 hit rate on this site already has frisks in it --- at the cost
of departing from the Board's 2024 figures. The effect on levels is about a
point (statewide 2024: 26.13% including frisks, 27.23% excluding them). The
effect on the disparity ratios that the table actually highlights is smaller
still: the Black/White ratio is 0.94 on the combined measure against 0.96 on
the Board's search-only measure, and the Hispanic/White ratio is 0.86 either
way. See [Methodology](methodology) for the exact field definitions.
