"""SQL queries for the agency explorer."""

from .db import get_conn


def search_agencies(q: str = "", limit: int = 50):
    """Search agencies by name or ORI. Returns list of dicts."""
    with get_conn() as conn:
        if q:
            rows = conn.execute("""
                SELECT a.agency_ori, a.agency_name, a.county,
                       a.first_year, a.last_year, a.total_person_stops
                FROM agencies a
                WHERE a.agency_name ILIKE %s OR a.agency_ori ILIKE %s
                ORDER BY a.total_person_stops DESC
                LIMIT %s
            """, (f"%{q}%", f"%{q}%", limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT agency_ori, agency_name, county,
                       first_year, last_year, total_person_stops
                FROM agencies
                ORDER BY total_person_stops DESC
                LIMIT %s
            """, (limit,)).fetchall()

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
            SELECT data_year, SUM(n_person_stops) AS n_person_stops,
                   SUM(n_stops) AS n_stops
            FROM mv_agency_year_race
            WHERE agency_ori = %s
            GROUP BY data_year
            ORDER BY data_year
        """, (ori,)).fetchall()

    return [
        {"year": int(r[0]), "n_person_stops": int(r[1]), "n_stops": int(r[2])}
        for r in rows
    ]


def get_agency_demographics_race(ori: str, year: int | None = None):
    """Race breakdown for an agency. Optionally filtered by year."""
    with get_conn() as conn:
        if year:
            rows = conn.execute("""
                SELECT r.race_code, rl.label,
                       SUM(r.n_person_stops) AS n_person_stops
                FROM mv_agency_year_race r
                JOIN rae_labels rl ON r.race_code = rl.code
                WHERE r.agency_ori = %s AND r.data_year = %s
                GROUP BY r.race_code, rl.label
                ORDER BY SUM(r.n_person_stops) DESC
            """, (ori, year)).fetchall()
        else:
            rows = conn.execute("""
                SELECT r.race_code, rl.label,
                       SUM(r.n_person_stops) AS n_person_stops
                FROM mv_agency_year_race r
                JOIN rae_labels rl ON r.race_code = rl.code
                WHERE r.agency_ori = %s
                GROUP BY r.race_code, rl.label
                ORDER BY SUM(r.n_person_stops) DESC
            """, (ori,)).fetchall()

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


def get_agency_demographics_gender(ori: str, year: int | None = None):
    """Gender breakdown for an agency."""
    with get_conn() as conn:
        if year:
            rows = conn.execute("""
                SELECT g.gender_code, gl.label,
                       SUM(g.n_person_stops) AS n_person_stops
                FROM mv_agency_year_gender g
                JOIN gender_labels gl ON g.gender_code = gl.code
                WHERE g.agency_ori = %s AND g.data_year = %s
                GROUP BY g.gender_code, gl.label
                ORDER BY SUM(g.n_person_stops) DESC
            """, (ori, year)).fetchall()
        else:
            rows = conn.execute("""
                SELECT g.gender_code, gl.label,
                       SUM(g.n_person_stops) AS n_person_stops
                FROM mv_agency_year_gender g
                JOIN gender_labels gl ON g.gender_code = gl.code
                WHERE g.agency_ori = %s
                GROUP BY g.gender_code, gl.label
                ORDER BY SUM(g.n_person_stops) DESC
            """, (ori,)).fetchall()

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


def get_agency_demographics_age(ori: str, year: int | None = None):
    """Age group breakdown for an agency."""
    with get_conn() as conn:
        if year:
            rows = conn.execute("""
                SELECT a.age_group, al.label,
                       SUM(a.n_person_stops) AS n_person_stops
                FROM mv_agency_year_age a
                JOIN age_group_labels al ON a.age_group = al.code
                WHERE a.agency_ori = %s AND a.data_year = %s
                GROUP BY a.age_group, al.label
                ORDER BY a.age_group
            """, (ori, year)).fetchall()
        else:
            rows = conn.execute("""
                SELECT a.age_group, al.label,
                       SUM(a.n_person_stops) AS n_person_stops
                FROM mv_agency_year_age a
                JOIN age_group_labels al ON a.age_group = al.code
                WHERE a.agency_ori = %s
                GROUP BY a.age_group, al.label
                ORDER BY a.age_group
            """, (ori,)).fetchall()

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


def get_agency_disparities(ori: str, year: int | None = None):
    """Disparity table: race × outcome rates with ratios vs White."""
    with get_conn() as conn:
        if year:
            rows = conn.execute("""
                SELECT r.race_code, rl.label,
                       SUM(r.n_person_stops) AS n_person_stops,
                       SUM(r.n_searched) AS n_searched,
                       SUM(r.n_force_used) AS n_force_used,
                       SUM(r.n_arrested) AS n_arrested,
                       SUM(r.n_contraband_found) AS n_contraband_found,
                       SUM(r.n_no_contraband) AS n_no_contraband
                FROM mv_agency_year_race r
                JOIN rae_labels rl ON r.race_code = rl.code
                WHERE r.agency_ori = %s AND r.data_year = %s
                GROUP BY r.race_code, rl.label
                ORDER BY SUM(r.n_person_stops) DESC
            """, (ori, year)).fetchall()
        else:
            rows = conn.execute("""
                SELECT r.race_code, rl.label,
                       SUM(r.n_person_stops) AS n_person_stops,
                       SUM(r.n_searched) AS n_searched,
                       SUM(r.n_force_used) AS n_force_used,
                       SUM(r.n_arrested) AS n_arrested,
                       SUM(r.n_contraband_found) AS n_contraband_found,
                       SUM(r.n_no_contraband) AS n_no_contraband
                FROM mv_agency_year_race r
                JOIN rae_labels rl ON r.race_code = rl.code
                WHERE r.agency_ori = %s
                GROUP BY r.race_code, rl.label
                ORDER BY SUM(r.n_person_stops) DESC
            """, (ori,)).fetchall()

    total_stops = sum(r[2] for r in rows)

    results = []
    for r in rows:
        n_stops = int(r[2])
        n_searched = int(r[3])
        n_force = int(r[4])
        n_arrested = int(r[5])
        n_contraband = int(r[6])

        results.append({
            "code": r[0],
            "label": r[1],
            "n_stops": n_stops,
            "pct_share": round(n_stops / total_stops * 100, 1) if total_stops > 0 else 0,
            "search_rate": round(n_searched / n_stops * 100, 1) if n_stops > 0 else 0,
            "hit_rate": round(n_contraband / n_searched * 100, 1) if n_searched > 0 else None,
            "force_rate": round(n_force / n_stops * 100, 1) if n_stops > 0 else 0,
            "arrest_rate": round(n_arrested / n_stops * 100, 1) if n_stops > 0 else 0,
        })

    # Compute disparity ratios vs White (code=7)
    white = next((r for r in results if r["code"] == 7), None)
    for r in results:
        r["search_disp"] = _ratio(r["search_rate"], white["search_rate"] if white else None)
        r["hit_disp"] = _ratio(r["hit_rate"], white["hit_rate"] if white else None)
        r["force_disp"] = _ratio(r["force_rate"], white["force_rate"] if white else None)
        r["arrest_disp"] = _ratio(r["arrest_rate"], white["arrest_rate"] if white else None)

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
