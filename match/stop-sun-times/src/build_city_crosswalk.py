"""Map each (LOC_CLOSEST_CITY, source-file county) to a Census geography.

Resolution order, recorded in `match_method`:
  1. alias           -- hand/city_aliases.yaml (reviewed overrides), or
                        "excluded" for aliases marked none: true
  2. place           -- normalized name equals a Census place name (minus its
                        LSAD suffix). Partial names, e.g. VENTURA for
                        "San Buenaventura (Ventura) city" or MONTROSE for
                        La Crescenta-Montrose CDP, must be listed as aliases.
  3. unincorporated  -- "UNINCORPORATED AREA-<X> COUNTY" -> county X
  4. agency_county   -- fall back to the county of the reporting agency's
                        source file (not available for CHP / Supplement)
     agency_county_far -- a match (other than a county-scoped alias) landed
                        > --max-km from the
                        agency's county internal point, so it was replaced
                        by the agency county
  5. none            -- unresolved; sun times will be null

When a name matches several places (e.g. two Spring Valley CDPs), the one
nearest the agency county's internal point is chosen. For CHP and other
statewide files there is no agency county, so the sole incorporated city
among the candidates is chosen (MOUNTAIN VIEW -> Mountain View city, not
the Contra Costa CDP); if there is none or several, it stays "ambiguous".
"""

import argparse
import math
import unicodedata

import polars as pl
import yaml


def normalize(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.upper().replace(".", "").replace("-", " ").replace("'", "")
    words = s.split()
    out = []
    for i, w in enumerate(words):
        if w == "ST":
            w = "SAINT"
        if w == "MT":
            w = "MOUNT"
        # "MC FARLAND" -> "MCFARLAND"
        if out and out[-1] == "MC":
            out[-1] = "MC" + w
            continue
        out.append(w)
    return " ".join(out)


def place_keys(places):
    """Normalized name key for each place, LSAD suffix (city/town/CDP) dropped."""
    return places.select(
        pl.col("name").map_elements(
            lambda n: normalize(n.rsplit(" ", 1)[0]), return_dtype=pl.String
        ).alias("key"),
        "geoid",
        pl.lit("place").alias("match_method"),
    )


def dist_km(lat1, lon1, lat2, lon2):
    # Equirectangular approximation; plenty accurate at California scale
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return 6371 * math.hypot(x, y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stops", required=True, help="glob of clean RIPA parquet")
    parser.add_argument("--places", required=True)
    parser.add_argument("--counties", required=True)
    parser.add_argument("--aliases", required=True)
    parser.add_argument("--max-km", type=float, default=250,
                        help="max distance from agency county internal point")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    places = pl.read_parquet(args.places)
    counties = pl.read_parquet(args.counties).with_columns(
        county=pl.col("name").str.replace(" County$", "")
    )
    county_geoid = dict(counties.select("county", "geoid").iter_rows())
    county_by_upper = {c.upper(): g for c, g in county_geoid.items()}
    loc = {g: (lat, lon) for g, lat, lon in pl.concat([
        places.select("geoid", "lat", "lon"), counties.select("geoid", "lat", "lon")
    ]).iter_rows()}
    place_geoid = dict(places.select("name", "geoid").iter_rows())
    # LSAD 25 = city, 43 = town (incorporated); 57 = CDP
    incorporated = set(places.filter(pl.col("lsad").is_in(["25", "43"]))["geoid"])

    # Keyed by (name, agency county); agency county None = applies to all
    aliases = {}
    for raw, target in yaml.safe_load(open(args.aliases))["aliases"].items():
        for t in target if isinstance(target, list) else [target]:
            if "place" in t:
                geoid = place_geoid[t["place"]]
            elif "county" in t:
                geoid = county_geoid[t["county"]]
            else:
                geoid = None  # explicitly unresolvable
            aliases[(normalize(raw), t.get("agency_county"))] = geoid

    keys = place_keys(places)
    candidates = {}
    for key, geoid, method in keys.iter_rows():
        candidates.setdefault(key, []).append((geoid, method))

    combos = (
        pl.scan_parquet(args.stops)
        .group_by(pl.col("LOC_CLOSEST_CITY").alias("loc_closest_city"), "county")
        .agg(pl.len().alias("n_person_stops"))
        .collect()
    )

    out = []
    for city, county, n in combos.iter_rows():
        key = normalize(city or "")
        agency_geoid = county_geoid.get(county)
        geoid, method = None, "none"
        alias_key = next((k for k in [(key, county), (key, None)] if k in aliases), None)
        if alias_key:
            geoid = aliases[alias_key]
            method = "alias" if geoid else "excluded"
        elif key in candidates:
            cands = candidates[key]
            if len(cands) == 1:
                geoid, method = cands[0]
            elif agency_geoid:
                a = loc[agency_geoid]
                geoid, method = min(cands, key=lambda c: dist_km(*a, *loc[c[0]]))
            else:
                cities = [c for c in cands if c[0] in incorporated]
                if len(cities) == 1:
                    geoid, method = cities[0]
                else:
                    method = "ambiguous"
        elif key.startswith("UNINCORPORATED AREA "):
            name = key.removeprefix("UNINCORPORATED AREA ").removesuffix(" COUNTY")
            geoid = county_by_upper.get(name)
            method = "unincorporated" if geoid else "none"
        if geoid is None and method in ("none", "ambiguous") and agency_geoid:
            geoid, method = agency_geoid, "agency_county"
        elif (
            # county-scoped aliases are deliberate; unscoped ones still get
            # the distance check (e.g. Glendale PD stops coded PASO ROBLES)
            geoid and agency_geoid and not (alias_key and alias_key[1])
            and dist_km(*loc[agency_geoid], *loc[geoid]) > args.max_km
        ):
            # Same-named place elsewhere in the state (e.g. LA's WESTWOOD
            # matching Westwood CDP in Lassen County)
            geoid, method = agency_geoid, "agency_county_far"
        out.append((city, county, n, geoid, method))

    xw = pl.DataFrame(
        out,
        schema=["loc_closest_city", "county", "n_person_stops", "sun_geoid", "match_method"],
        orient="row",
    ).sort("n_person_stops", descending=True)
    xw.write_parquet(args.output)
    xw.write_csv(args.output.replace(".parquet", ".csv"))

    total = xw["n_person_stops"].sum()
    summary = xw.group_by("match_method").agg(pl.col("n_person_stops").sum()).with_columns(
        share=pl.col("n_person_stops") / total
    ).sort("n_person_stops", descending=True)
    print(summary)


if __name__ == "__main__":
    main()
