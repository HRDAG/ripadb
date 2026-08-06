"""SQL queries for the agency explorer."""

from .db import get_conn


def count_agencies(q: str = ""):
    """Count agencies matching a search query."""
    with get_conn() as conn:
        if q:
            row = conn.execute("""
                SELECT COUNT(*) FROM agencies
                WHERE agency_name ILIKE %s OR agency_ori ILIKE %s
            """, (f"%{q}%", f"%{q}%")).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM agencies").fetchone()
    return int(row[0])


def search_agencies(q: str = "", limit: int = 50, offset: int = 0):
    """Search agencies by name or ORI. Returns list of dicts."""
    with get_conn() as conn:
        if q:
            rows = conn.execute("""
                SELECT a.agency_ori, a.agency_name, a.county,
                       a.first_year, a.last_year, a.total_person_stops
                FROM agencies a
                WHERE a.agency_name ILIKE %s OR a.agency_ori ILIKE %s
                ORDER BY a.total_person_stops DESC
                LIMIT %s OFFSET %s
            """, (f"%{q}%", f"%{q}%", limit, offset)).fetchall()
        else:
            rows = conn.execute("""
                SELECT agency_ori, agency_name, county,
                       first_year, last_year, total_person_stops
                FROM agencies
                ORDER BY total_person_stops DESC
                LIMIT %s OFFSET %s
            """, (limit, offset)).fetchall()

    return [
        {
            "agency_ori": r[0],
            "agency_name": r[1],
            "county": r[2],
            "first_year": r[3],
            "last_year": r[4],
            "total_person_stops": r[5],
        }
        for r in rows
    ]


def get_agency(ori: str):
    """Get agency details. Returns dict or None."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT agency_ori, agency_name, county,
                   first_year, last_year, total_person_stops
            FROM agencies
            WHERE agency_ori = %s
        """, (ori,)).fetchone()

    if not row:
        return None
    return {
        "agency_ori": row[0],
        "agency_name": row[1],
        "county": row[2],
        "first_year": row[3],
        "last_year": row[4],
        "total_person_stops": row[5],
    }


def get_agency_stops_by_year(ori: str):
    """Get stop counts per year for an agency. Returns list of dicts."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT data_year, n_person_stops, n_stops
            FROM mv_agency_year
            WHERE agency_ori = %s
            ORDER BY data_year
        """, (ori,)).fetchall()

    return [
        {"year": int(r[0]), "n_person_stops": int(r[1]), "n_stops": int(r[2])}
        for r in rows
    ]


def _year_cond(alias: str, year_from: int | None, year_to: int | None):
    """Build a SQL condition + params restricting data_year to a range."""
    cond = ""
    params = []
    if year_from is not None:
        cond += f" AND {alias}.data_year >= %s"
        params.append(year_from)
    if year_to is not None:
        cond += f" AND {alias}.data_year <= %s"
        params.append(year_to)
    return cond, params


def get_agency_demographics_race(ori: str, year_from: int | None = None,
                                 year_to: int | None = None):
    """Race breakdown for an agency. Optionally filtered by year range."""
    cond, params = _year_cond("r", year_from, year_to)
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT r.race_code, rl.label,
                   SUM(r.n_person_stops) AS n_person_stops
            FROM mv_agency_year_race r
            JOIN rae_labels rl ON r.race_code = rl.code
            WHERE r.agency_ori = %s{cond}
            GROUP BY r.race_code, rl.label
            ORDER BY SUM(r.n_person_stops) DESC
        """, (ori, *params)).fetchall()

    total = int(sum(r[2] for r in rows))
    return [
        {
            "code": r[0],
            "label": r[1],
            "n_person_stops": int(r[2]),
            "pct": round(int(r[2]) / total * 100, 1) if total > 0 else 0,
            "share": int(r[2]) / total if total > 0 else None,
        }
        for r in rows
    ]


def get_agency_demographics_gender(ori: str, year_from: int | None = None,
                                   year_to: int | None = None):
    """Gender breakdown for an agency."""
    cond, params = _year_cond("g", year_from, year_to)
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT g.gender_code, gl.label,
                   SUM(g.n_person_stops) AS n_person_stops
            FROM mv_agency_year_gender g
            JOIN gender_labels gl ON g.gender_code = gl.code
            WHERE g.agency_ori = %s{cond}
            GROUP BY g.gender_code, gl.label
            ORDER BY SUM(g.n_person_stops) DESC
        """, (ori, *params)).fetchall()

    total = sum(r[2] for r in rows)
    return [
        {
            "code": r[0],
            "label": r[1],
            "n_person_stops": int(r[2]),
            "pct": round(int(r[2]) / total * 100, 1) if total > 0 else 0,
        }
        for r in rows
    ]


def get_agency_demographics_age(ori: str, year_from: int | None = None,
                                year_to: int | None = None):
    """Age group breakdown for an agency."""
    cond, params = _year_cond("a", year_from, year_to)
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT a.age_group, al.label,
                   SUM(a.n_person_stops) AS n_person_stops
            FROM mv_agency_year_age a
            JOIN age_group_labels al ON a.age_group = al.code
            WHERE a.agency_ori = %s{cond}
            GROUP BY a.age_group, al.label
            ORDER BY a.age_group
        """, (ori, *params)).fetchall()

    total = sum(r[2] for r in rows)
    return [
        {
            "code": r[0],
            "label": r[1],
            "n_person_stops": int(r[2]),
            "pct": round(int(r[2]) / total * 100, 1) if total > 0 else 0,
        }
        for r in rows
    ]


def _jd_table_ready(conn):
    """Check if jurisdiction_demographics table exists with expected schema."""
    row = conn.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jurisdiction_demographics'
          AND column_name = 'geography_name'
    """).fetchone()
    return row is not None


def get_agency_demographics_census(ori: str,
                                    source: str = "acs5_2023_residential"):
    """Get census demographics for an agency's jurisdiction.

    Returns list of dicts with code, label, population, pct (rounded, for
    display), and share (raw fraction, for ratio computation) — or None
    if no demographics are available for this agency.
    """
    with get_conn() as conn:
        if not _jd_table_ready(conn):
            return None

        rows = conn.execute("""
            SELECT jd.rae_code, rl.label, jd.population, jd.pct,
                   tot.population AS total_pop
            FROM jurisdiction_demographics jd
            LEFT JOIN jurisdiction_demographics tot
              ON tot.agency_ori = jd.agency_ori
             AND tot.source = jd.source AND tot.rae_code = 0
            LEFT JOIN rae_labels rl ON jd.rae_code = rl.code
            WHERE jd.agency_ori = %s AND jd.source = %s AND jd.rae_code > 0
            ORDER BY jd.population DESC
        """, (ori, source)).fetchall()

    if not rows:
        return None

    return [
        {
            "code": r[0],
            "label": r[1] or "Middle Eastern/South Asian",
            "population": int(r[2]),
            "pct": round(float(r[3]), 1) if r[3] is not None else None,
            "share": int(r[2]) / int(r[4]) if r[4] else None,
        }
        for r in rows
    ]


def get_agency_jurisdiction(ori: str, source: str = "acs5_2023_residential"):
    """Get jurisdiction name and total population for an agency.

    Returns dict with geography_name, total_pop, source — or None.
    """
    with get_conn() as conn:
        if not _jd_table_ready(conn):
            return None

        row = conn.execute("""
            SELECT jd.population, jd.geography_name
            FROM jurisdiction_demographics jd
            WHERE jd.agency_ori = %s AND jd.source = %s AND jd.rae_code = 0
        """, (ori, source)).fetchone()

    if not row:
        return None

    return {
        "total_pop": int(row[0]),
        "geography_name": row[1],
        "source": source,
    }


STOP_TYPE_VIEWS = {
    "all": "mv_agency_year_race",
    "equip": "mv_agency_year_race_equip",
}

STOP_TYPE_LABELS = {
    "all": "All stops",
    "equip": "Equipment violations",
}


def get_agency_disparities(ori: str, year_from: int | None = None,
                           year_to: int | None = None,
                           stop_type: str = "all"):
    """Disparity table: race × outcome rates with ratios vs White."""
    view = STOP_TYPE_VIEWS.get(stop_type, "mv_agency_year_race")
    cond, params = _year_cond("r", year_from, year_to)

    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT r.race_code, rl.label,
                   SUM(r.n_person_stops) AS n_person_stops,
                   SUM(r.n_searched) AS n_searched,
                   SUM(r.n_force_used) AS n_force_used,
                   SUM(r.n_arrested) AS n_arrested,
                   SUM(r.n_contraband_found) AS n_contraband_found,
                   SUM(r.n_no_contraband) AS n_no_contraband
            FROM {view} r
            JOIN rae_labels rl ON r.race_code = rl.code
            WHERE r.agency_ori = %s{cond}
            GROUP BY r.race_code, rl.label
            ORDER BY SUM(r.n_person_stops) DESC
        """, (ori, *params)).fetchall()

    total_stops = int(sum(r[2] for r in rows))

    # Raw (unrounded) rates per race; ratios are taken from these, and
    # rounding happens only at display time.
    raw = []
    for r in rows:
        n_stops = int(r[2])
        n_searched = int(r[3])
        n_force = int(r[4])
        n_arrested = int(r[5])
        n_contraband = int(r[6])

        raw.append({
            "code": r[0],
            "label": r[1],
            "n_stops": n_stops,
            "search_rate": n_searched / n_stops if n_stops > 0 else 0,
            "hit_rate": n_contraband / n_searched if n_searched > 0 else None,
            "force_rate": n_force / n_stops if n_stops > 0 else 0,
            "arrest_rate": n_arrested / n_stops if n_stops > 0 else 0,
        })

    # Disparity ratios vs White (code=7), from raw rates
    white = next((r for r in raw if r["code"] == 7), None)
    results = []
    for r in raw:
        row = {
            "code": r["code"],
            "label": r["label"],
            "n_stops": r["n_stops"],
            "pct_share": round(r["n_stops"] / total_stops * 100, 1) if total_stops > 0 else 0,
            "share": r["n_stops"] / total_stops if total_stops > 0 else None,
        }
        for key in ("search", "hit", "force", "arrest"):
            rate = r[f"{key}_rate"]
            row[f"{key}_rate"] = round(rate * 100, 1) if rate is not None else None
            row[f"{key}_disp"] = _ratio(rate, white[f"{key}_rate"] if white else None)
        results.append(row)

    return results


def get_agency_years(ori: str):
    """Get available years for an agency."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT DISTINCT data_year
            FROM mv_agency_year_race
            WHERE agency_ori = %s
            ORDER BY data_year
        """, (ori,)).fetchall()
    return [r[0] for r in rows]


def _ratio(rate, ref_rate):
    """Compute disparity ratio. Returns None if reference is zero/None."""
    if rate is None or ref_rate is None or ref_rate == 0:
        return None
    return round(rate / ref_rate, 2)
