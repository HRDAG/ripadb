#!/usr/bin/env python3
"""
EDA: Equipment violation stops vs. other vehicular stops.

Compares racial disparities in stop composition, search rates, hit rates,
force rates, and arrest rates between equipment violation stops and
other vehicular stops (moving + non-moving violations).

Equipment violations (reason_for_stop=1, rfs_traffic_violation_type=2) are
widely considered a high-discretion pretextual stop indicator.
"""

import os
import psycopg
from tabulate import tabulate

CONNINFO = os.environ.get("DATABASE_URL", "dbname=ripadb")

RACE_LABELS = {
    1: "Asian",
    2: "Black",
    3: "Hispanic/Latino",
    4: "Middle Eastern/South Asian",
    5: "Native American",
    6: "Pacific Islander",
    7: "White",
    8: "Multiracial",
}

# For compact tables, short labels
RACE_SHORT = {
    1: "Asian",
    2: "Black",
    3: "Hispanic",
    4: "MESA",
    5: "Native Am.",
    6: "Pac. Isl.",
    7: "White",
    8: "Multiracial",
}


def query(sql, params=None):
    with psycopg.connect(CONNINFO) as conn:
        return conn.execute(sql, params).fetchall()


def pct(n, d, decimals=1):
    if d == 0:
        return None
    return round(n / d * 100, decimals)


def ratio(rate, ref):
    if rate is None or ref is None or ref == 0:
        return None
    return round(rate / ref, 2)


def fmt(val, suffix="%"):
    if val is None:
        return "—"
    return f"{val}{suffix}"


# ── 1. Statewide overview by traffic violation type ──────────────────

def statewide_overview():
    """How many traffic stops are equipment vs. moving vs. non-moving?"""
    print("=" * 70)
    print("1. STATEWIDE TRAFFIC STOPS BY VIOLATION TYPE AND YEAR")
    print("=" * 70)

    rows = query("""
        SELECT data_year,
               rfs_traffic_violation_type AS vtype,
               COUNT(*) AS n
        FROM stops
        WHERE reason_for_stop = 1
          AND rfs_traffic_violation_type IS NOT NULL
        GROUP BY data_year, rfs_traffic_violation_type
        ORDER BY data_year, rfs_traffic_violation_type
    """)

    # Pivot: year -> {vtype: count}
    data = {}
    for year, vtype, n in rows:
        data.setdefault(year, {})[vtype] = n

    vtype_labels = {1: "Moving", 2: "Equipment", 3: "Non-moving"}
    table = []
    for year in sorted(data):
        total = sum(data[year].values())
        row = [year, total]
        for vt in [1, 2, 3]:
            n = data[year].get(vt, 0)
            row.extend([n, pct(n, total)])
        table.append(row)

    headers = ["Year", "Total Traffic",
               "Moving", "Mov %", "Equipment", "Equip %",
               "Non-moving", "Non-mov %"]
    print(tabulate(table, headers=headers, tablefmt="simple",
                   intfmt=",", floatfmt=".1f"))
    print()


# ── 2. Racial composition: equipment vs. other vehicular ─────────────

def racial_composition():
    """Race breakdown comparing equipment vs. non-equipment traffic stops."""
    print("=" * 70)
    print("2. RACIAL COMPOSITION: EQUIPMENT vs. OTHER VEHICULAR STOPS")
    print("   (all years pooled)")
    print("=" * 70)

    rows = query("""
        SELECT
            rae_full,
            SUM(CASE WHEN rfs_traffic_violation_type = 2 THEN 1 ELSE 0 END) AS n_equip,
            SUM(CASE WHEN rfs_traffic_violation_type != 2 THEN 1 ELSE 0 END) AS n_other,
            COUNT(*) AS n_total
        FROM stops
        WHERE reason_for_stop = 1
          AND rfs_traffic_violation_type IS NOT NULL
          AND rae_full IS NOT NULL
        GROUP BY rae_full
        ORDER BY rae_full
    """)

    total_equip = sum(r[1] for r in rows)
    total_other = sum(r[2] for r in rows)

    table = []
    for race_code, n_equip, n_other, n_total in rows:
        label = RACE_SHORT.get(race_code, f"Code {race_code}")
        pct_equip = pct(n_equip, total_equip)
        pct_other = pct(n_other, total_other)
        # Overrepresentation ratio
        over = ratio(pct_equip, pct_other)
        table.append([label, n_equip, pct_equip, n_other, pct_other, over])

    headers = ["Race", "Equip Stops", "Equip %", "Other Stops", "Other %",
               "Overrep. Ratio"]
    print(tabulate(table, headers=headers, tablefmt="simple",
                   intfmt=",", floatfmt=".2f"))
    print(f"\nTotal equipment: {total_equip:,}  |  "
          f"Total other vehicular: {total_other:,}")
    print()


# ── 3. Search rate disparities ───────────────────────────────────────

def search_rate_disparities():
    """Search rates by race: equipment vs. other vehicular stops."""
    print("=" * 70)
    print("3. SEARCH RATES BY RACE: EQUIPMENT vs. OTHER VEHICULAR")
    print("   (all years pooled, disparity ratio vs. White)")
    print("=" * 70)

    rows = query("""
        SELECT
            rae_full,
            rfs_traffic_violation_type = 2 AS is_equip,
            COUNT(*) AS n_stops,
            SUM(CASE
                WHEN data_year < 2024 THEN
                    GREATEST(COALESCE(ads_search_person, 0),
                             COALESCE(ads_search_property, 0))
                ELSE
                    GREATEST(COALESCE(nfa_search_person, 0),
                             COALESCE(nfa_search_property, 0),
                             COALESCE(nfa_terry_frisk, 0))
            END) AS n_searched,
            SUM(CASE
                WHEN CASE
                    WHEN data_year < 2024 THEN
                        GREATEST(COALESCE(ads_search_person, 0),
                                 COALESCE(ads_search_property, 0))
                    ELSE
                        GREATEST(COALESCE(nfa_search_person, 0),
                                 COALESCE(nfa_search_property, 0),
                                 COALESCE(nfa_terry_frisk, 0))
                END = 1
                THEN GREATEST(
                    COALESCE(ced_firearm, 0), COALESCE(ced_ammunition, 0),
                    COALESCE(ced_weapon, 0), COALESCE(ced_drugs, 0),
                    COALESCE(ced_alcohol, 0), COALESCE(ced_money, 0),
                    COALESCE(ced_drug_paraphernalia, 0),
                    COALESCE(ced_stolen_prop, 0),
                    COALESCE(ced_elect_device, 0),
                    COALESCE(ced_other_contraband, 0))
                ELSE 0
            END) AS n_contraband
        FROM stops
        WHERE reason_for_stop = 1
          AND rfs_traffic_violation_type IS NOT NULL
          AND rae_full IS NOT NULL
        GROUP BY rae_full, (rfs_traffic_violation_type = 2)
        ORDER BY rae_full
    """)

    # Organize: {race: {is_equip: {n_stops, n_searched, n_contraband}}}
    data = {}
    for race, is_equip, n_stops, n_searched, n_contraband in rows:
        key = "equip" if is_equip else "other"
        data.setdefault(race, {})[key] = {
            "n": n_stops, "searched": n_searched, "contraband": n_contraband
        }

    # Build table
    table = []
    white_equip_sr = None
    white_other_sr = None
    white_equip_hr = None
    white_other_hr = None

    # First pass: compute White rates
    if 7 in data:
        w = data[7]
        if "equip" in w:
            white_equip_sr = pct(w["equip"]["searched"], w["equip"]["n"])
            white_equip_hr = pct(w["equip"]["contraband"],
                                 w["equip"]["searched"])
        if "other" in w:
            white_other_sr = pct(w["other"]["searched"], w["other"]["n"])
            white_other_hr = pct(w["other"]["contraband"],
                                 w["other"]["searched"])

    for race in sorted(data):
        label = RACE_SHORT.get(race, f"Code {race}")
        e = data[race].get("equip", {"n": 0, "searched": 0, "contraband": 0})
        o = data[race].get("other", {"n": 0, "searched": 0, "contraband": 0})

        e_sr = pct(e["searched"], e["n"])
        o_sr = pct(o["searched"], o["n"])
        e_hr = pct(e["contraband"], e["searched"])
        o_hr = pct(o["contraband"], o["searched"])

        table.append([
            label,
            f'{e["n"]:,}', fmt(e_sr), fmt(ratio(e_sr, white_equip_sr), "x"),
            fmt(e_hr), fmt(ratio(e_hr, white_equip_hr), "x"),
            f'{o["n"]:,}', fmt(o_sr), fmt(ratio(o_sr, white_other_sr), "x"),
            fmt(o_hr), fmt(ratio(o_hr, white_other_hr), "x"),
        ])

    headers = ["Race",
               "Eq Stops", "Eq Srch%", "Eq S.Disp",
               "Eq Hit%", "Eq H.Disp",
               "Oth Stops", "Oth Srch%", "Oth S.Disp",
               "Oth Hit%", "Oth H.Disp"]
    print(tabulate(table, headers=headers, tablefmt="simple"))
    print()


# ── 4. Force and arrest rate disparities ─────────────────────────────

def force_arrest_disparities():
    """Force and arrest rates by race: equipment vs. other vehicular."""
    print("=" * 70)
    print("4. FORCE & ARREST RATES BY RACE: EQUIPMENT vs. OTHER VEHICULAR")
    print("   (all years pooled, disparity ratio vs. White)")
    print("=" * 70)

    rows = query("""
        SELECT
            rae_full,
            rfs_traffic_violation_type = 2 AS is_equip,
            COUNT(*) AS n_stops,
            SUM(CASE
                WHEN data_year < 2024 THEN GREATEST(
                    COALESCE(ads_handcuffed, 0), COALESCE(ads_firearm_point, 0),
                    COALESCE(ads_firearm_discharge, 0),
                    COALESCE(ads_elect_device, 0),
                    COALESCE(ads_impact_discharge, 0),
                    COALESCE(ads_canine_bite, 0),
                    COALESCE(ads_baton, 0), COALESCE(ads_chem_spray, 0),
                    COALESCE(ads_other_contact, 0))
                ELSE GREATEST(
                    COALESCE(ofa_handcuffed, 0), COALESCE(ofa_firearm_point, 0),
                    COALESCE(ofa_firearm_discharge, 0),
                    COALESCE(ofa_baton_used, 0),
                    COALESCE(ofa_chem_spray, 0), COALESCE(ofa_canine_bite, 0),
                    COALESCE(ofa_elect_device_stun, 0),
                    COALESCE(ofa_elect_device_dart, 0),
                    COALESCE(ofa_impact_projectile_discharge, 0),
                    COALESCE(ofa_physical_compliance, 0),
                    COALESCE(ofa_use_vehicle, 0),
                    COALESCE(ofa_removed_vehicle_phycontact, 0))
            END) AS n_force,
            SUM(GREATEST(COALESCE(ros_custodial_warrant, 0),
                         COALESCE(ros_custodial_without_warrant, 0))
            ) AS n_arrested,
            SUM(CASE
                WHEN data_year < 2024 THEN COALESCE(ros_warning, 0)
                ELSE GREATEST(COALESCE(ros_written_warning, 0),
                              COALESCE(ros_verbal_warning, 0))
            END) AS n_warned
        FROM stops
        WHERE reason_for_stop = 1
          AND rfs_traffic_violation_type IS NOT NULL
          AND rae_full IS NOT NULL
        GROUP BY rae_full, (rfs_traffic_violation_type = 2)
        ORDER BY rae_full
    """)

    data = {}
    for race, is_equip, n, force, arrested, warned in rows:
        key = "equip" if is_equip else "other"
        data.setdefault(race, {})[key] = {
            "n": n, "force": force, "arrested": arrested, "warned": warned
        }

    # White reference rates
    w_e = data.get(7, {}).get("equip", {})
    w_o = data.get(7, {}).get("other", {})
    w_e_fr = pct(w_e.get("force", 0), w_e.get("n", 0)) if w_e else None
    w_o_fr = pct(w_o.get("force", 0), w_o.get("n", 0)) if w_o else None
    w_e_ar = pct(w_e.get("arrested", 0), w_e.get("n", 0)) if w_e else None
    w_o_ar = pct(w_o.get("arrested", 0), w_o.get("n", 0)) if w_o else None

    table = []
    for race in sorted(data):
        label = RACE_SHORT.get(race, f"Code {race}")
        e = data[race].get("equip", {"n": 0, "force": 0, "arrested": 0, "warned": 0})
        o = data[race].get("other", {"n": 0, "force": 0, "arrested": 0, "warned": 0})

        e_fr = pct(e["force"], e["n"])
        o_fr = pct(o["force"], o["n"])
        e_ar = pct(e["arrested"], e["n"])
        o_ar = pct(o["arrested"], o["n"])
        e_wr = pct(e["warned"], e["n"])
        o_wr = pct(o["warned"], o["n"])

        table.append([
            label,
            fmt(e_fr), fmt(ratio(e_fr, w_e_fr), "x"),
            fmt(e_ar), fmt(ratio(e_ar, w_e_ar), "x"),
            fmt(e_wr),
            fmt(o_fr), fmt(ratio(o_fr, w_o_fr), "x"),
            fmt(o_ar), fmt(ratio(o_ar, w_o_ar), "x"),
            fmt(o_wr),
        ])

    headers = ["Race",
               "Eq Force%", "Eq F.Dsp",
               "Eq Arrest%", "Eq A.Dsp",
               "Eq Warn%",
               "Oth Force%", "Oth F.Dsp",
               "Oth Arrest%", "Oth A.Dsp",
               "Oth Warn%"]
    print(tabulate(table, headers=headers, tablefmt="simple"))
    print()


# ── 5. Top agencies by racial disparity in equipment stops ───────────

def top_agencies_equip_disparity():
    """Agencies with the largest Black/White disparity in equip stop share."""
    print("=" * 70)
    print("5. TOP 25 AGENCIES: BLACK/WHITE DISPARITY IN EQUIPMENT STOPS")
    print("   (agencies with 1000+ equip stops, all years)")
    print("   Disparity = (Black equip share / Black other share)")
    print("             ÷ (White equip share / White other share)")
    print("=" * 70)

    rows = query("""
        WITH race_stop_type AS (
            SELECT
                agency_ori,
                rae_full,
                SUM(CASE WHEN rfs_traffic_violation_type = 2
                         THEN 1 ELSE 0 END) AS n_equip,
                SUM(CASE WHEN rfs_traffic_violation_type != 2
                         THEN 1 ELSE 0 END) AS n_other
            FROM stops
            WHERE reason_for_stop = 1
              AND rfs_traffic_violation_type IS NOT NULL
              AND rae_full IN (2, 7)  -- Black and White
            GROUP BY agency_ori, rae_full
        ),
        agency_totals AS (
            SELECT
                agency_ori,
                SUM(n_equip) AS total_equip,
                SUM(n_other) AS total_other
            FROM race_stop_type
            GROUP BY agency_ori
            HAVING SUM(n_equip) >= 1000
        ),
        pivoted AS (
            SELECT
                r.agency_ori,
                a.agency_name,
                at.total_equip,
                at.total_other,
                MAX(CASE WHEN r.rae_full = 2 THEN r.n_equip END) AS black_equip,
                MAX(CASE WHEN r.rae_full = 2 THEN r.n_other END) AS black_other,
                MAX(CASE WHEN r.rae_full = 7 THEN r.n_equip END) AS white_equip,
                MAX(CASE WHEN r.rae_full = 7 THEN r.n_other END) AS white_other
            FROM race_stop_type r
            JOIN agencies a ON a.agency_ori = r.agency_ori
            JOIN agency_totals at ON at.agency_ori = r.agency_ori
            GROUP BY r.agency_ori, a.agency_name, at.total_equip, at.total_other
        )
        SELECT
            agency_ori, agency_name, total_equip,
            black_equip, white_equip, black_other, white_other,
            -- Black share of equip vs. other
            CASE WHEN total_equip > 0
                 THEN black_equip::float / total_equip END AS black_equip_share,
            CASE WHEN total_other > 0
                 THEN black_other::float / total_other END AS black_other_share,
            CASE WHEN total_equip > 0
                 THEN white_equip::float / total_equip END AS white_equip_share,
            CASE WHEN total_other > 0
                 THEN white_other::float / total_other END AS white_other_share
        FROM pivoted
        WHERE black_equip > 0 AND white_equip > 0
          AND black_other > 0 AND white_other > 0
        ORDER BY
            (black_equip::float / NULLIF(black_other, 0))
            / NULLIF(white_equip::float / NULLIF(white_other, 0), 0) DESC NULLS LAST
        LIMIT 25
    """)

    table = []
    for r in rows:
        ori, name, total_eq, b_eq, w_eq, b_oth, w_oth, \
            b_eq_sh, b_oth_sh, w_eq_sh, w_oth_sh = r

        # Black equip-to-other ratio / White equip-to-other ratio
        b_ratio = b_eq / b_oth if b_oth else None
        w_ratio = w_eq / w_oth if w_oth else None
        disp = b_ratio / w_ratio if w_ratio else None

        table.append([
            name[:35],
            f"{total_eq:,}",
            f"{b_eq_sh*100:.1f}%" if b_eq_sh else "—",
            f"{b_oth_sh*100:.1f}%" if b_oth_sh else "—",
            f"{w_eq_sh*100:.1f}%" if w_eq_sh else "—",
            f"{w_oth_sh*100:.1f}%" if w_oth_sh else "—",
            f"{disp:.2f}" if disp else "—",
        ])

    headers = ["Agency", "Equip Stops",
               "Blk Eq%", "Blk Oth%",
               "Wht Eq%", "Wht Oth%",
               "B/W Disp."]
    print(tabulate(table, headers=headers, tablefmt="simple"))
    print()


# ── 6. Trend: equipment stop share over time by race ─────────────────

def equip_share_trend():
    """Fraction of traffic stops that are equipment, by race and year."""
    print("=" * 70)
    print("6. EQUIPMENT STOP SHARE OF ALL TRAFFIC STOPS, BY RACE AND YEAR")
    print("   (what % of each race's traffic stops are equipment violations)")
    print("=" * 70)

    rows = query("""
        SELECT
            data_year,
            rae_full,
            SUM(CASE WHEN rfs_traffic_violation_type = 2
                     THEN 1 ELSE 0 END) AS n_equip,
            COUNT(*) AS n_total
        FROM stops
        WHERE reason_for_stop = 1
          AND rfs_traffic_violation_type IS NOT NULL
          AND rae_full IS NOT NULL
        GROUP BY data_year, rae_full
        ORDER BY data_year, rae_full
    """)

    # Pivot: year -> race -> equip_share
    data = {}
    for year, race, n_equip, n_total in rows:
        data.setdefault(year, {})[race] = pct(n_equip, n_total)

    # Compute overall per year
    overall = {}
    for year, race, n_equip, n_total in rows:
        ov = overall.setdefault(year, {"equip": 0, "total": 0})
        ov["equip"] += n_equip
        ov["total"] += n_total

    show_races = [2, 3, 7, 1, 4]  # Black, Hispanic, White, Asian, MESA
    headers = ["Year"] + [RACE_SHORT[r] for r in show_races] + ["Overall"]

    table = []
    for year in sorted(data):
        row = [year]
        for r in show_races:
            row.append(fmt(data[year].get(r)))
        ov = overall[year]
        row.append(fmt(pct(ov["equip"], ov["total"])))
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="simple"))
    print()


# ── 7. Search rate gap: equip vs other, by race ────────────────────

def search_rate_gap():
    """How much higher are search rates in equipment stops vs other?"""
    print("=" * 70)
    print("7. SEARCH RATE GAP: EQUIPMENT vs. OTHER VEHICULAR, BY RACE")
    print("   (search rate in equip stops minus search rate in other stops)")
    print("=" * 70)

    rows = query("""
        SELECT
            rae_full,
            rfs_traffic_violation_type = 2 AS is_equip,
            COUNT(*) AS n_stops,
            SUM(CASE
                WHEN data_year < 2024 THEN
                    GREATEST(COALESCE(ads_search_person, 0),
                             COALESCE(ads_search_property, 0))
                ELSE
                    GREATEST(COALESCE(nfa_search_person, 0),
                             COALESCE(nfa_search_property, 0),
                             COALESCE(nfa_terry_frisk, 0))
            END) AS n_searched
        FROM stops
        WHERE reason_for_stop = 1
          AND rfs_traffic_violation_type IS NOT NULL
          AND rae_full IS NOT NULL
        GROUP BY rae_full, (rfs_traffic_violation_type = 2)
        ORDER BY rae_full
    """)

    data = {}
    for race, is_equip, n, searched in rows:
        key = "equip" if is_equip else "other"
        data.setdefault(race, {})[key] = {"n": n, "searched": searched}

    table = []
    for race in sorted(data):
        label = RACE_SHORT.get(race, f"Code {race}")
        e = data[race].get("equip", {"n": 0, "searched": 0})
        o = data[race].get("other", {"n": 0, "searched": 0})
        e_sr = pct(e["searched"], e["n"])
        o_sr = pct(o["searched"], o["n"])
        gap = round(e_sr - o_sr, 1) if e_sr is not None and o_sr is not None else None
        mult = ratio(e_sr, o_sr)
        table.append([label, fmt(e_sr), fmt(o_sr),
                      f"+{gap}pp" if gap and gap > 0 else f"{gap}pp" if gap else "—",
                      fmt(mult, "x")])

    headers = ["Race", "Equip Srch%", "Other Srch%", "Gap (pp)", "Multiplier"]
    print(tabulate(table, headers=headers, tablefmt="simple"))
    print()


def main():
    print("\n" + "━" * 70)
    print("  EQUIPMENT VIOLATION STOPS: RACIAL DISPARITY ANALYSIS")
    print("  California RIPA Stop Data, 2018–2024")
    print("━" * 70 + "\n")

    statewide_overview()
    racial_composition()
    search_rate_disparities()
    force_arrest_disparities()
    top_agencies_equip_disparity()
    equip_share_trend()
    search_rate_gap()


if __name__ == "__main__":
    main()
