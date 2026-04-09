#!/usr/bin/env python3
"""Generate an ORI → Census geography crosswalk from the agencies table.

Classifies each agency as city PD (→ Census place), county sheriff/DA
(→ county), CHP (→ state), or special district (→ skip), then attempts
to match to Census FIPS codes using the `us` library and Census API
place name lookup.

Outputs YAML to be manually reviewed before committing to hand/crosswalk.yaml.
"""

import argparse
import os
import re
from pathlib import Path

import psycopg
import yaml
from census import Census
from dotenv import load_dotenv

DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=ripadb")
CA_FIPS = "06"

# Patterns for classifying agencies
# Order matters: first match wins
SKIP_PATTERNS = [
    # Universities / colleges
    (r"\bUNIV\b", "university"),
    (r"\bCOLLEG", "college"),
    (r"\bCSU\b", "university"),
    (r"\bCAL POLY\b", "university"),
    (r"\bUC[ -]", "university"),
    (r"^UNIVERSITY", "university"),
    (r"\bCALIFORNIA MARITIME ACADEMY\b", "university"),
    # School districts
    (r"\bSCHOOL\b", "school_district"),
    (r"\bLAUSD\b", "school_district"),
    (r"\bUSD\b", "school_district"),
    (r"\bUNIF\b", "school_district"),
    # Transit
    (r"^BART\b", "transit"),
    (r"\bTRANSIT\b", "transit"),
    # Airports
    (r"\bAIRPORT\b", "airport"),
    (r"\bDEPT OF AIRPORT", "airport"),
    # Parks / rangers / harbor
    (r"\bPARK RANGER", "park"),
    (r"\bPARKS\b", "park"),
    (r"\bHARBOR PATROL", "harbor"),
    (r"\bHESPERIA PARK\b", "park"),
    # Housing
    (r"\bHOUSING\b", "housing_authority"),
    # Water district
    (r"\bWATER DIST", "water_district"),
    # Welfare
    (r"\bWELFAR", "welfare"),
    (r"\bHUMAN ASST", "welfare"),
    # County DA (district attorney) — not a primary patrol agency
    (r"\bCO DA\b", "county_da"),
    (r"\bCOUNTY DA\b", "county_da"),
    (r"\bCA DA\b", "county_da"),
    (r"\bDA INV", "county_da"),
    (r"\bDA-", "county_da"),
    # Other special
    (r"KERN COUNTY DISTRICT PARKS", "park"),
    (r"STATE CTR COMM", "college"),
    (r"CENTRAL MARIN POLICE AUTHORITY", "special"),
]

SHERIFF_PATTERNS = [
    r"\bCO S[OD]\b",       # CO SO, CO SD
    r"\bCO SHERIFF",       # CO SHERIFF'S DEPT
    r"\bCOUNTY S[OD]\b",   # COUNTY SO
    r"\bCOUNTY SHERIFF",   # COUNTY SHERIFF'S OFFICE
    r"^SONOMA SHERIFF$",
    r"^TRINITY CO SHERIFF$",
]

CHP_PATTERNS = [
    r"^CHP",
]

# Agency names that need manual city mapping (irregular names)
MANUAL_CITY_MAPPINGS = {
    "LAPD": "Los Angeles",
    "SAN FRANCISCO PD - DOC": "San Francisco",
    "SUNNYVALE DPS": "Sunnyvale",
    "LINDSAY DEPARTMENT OF PUBLIC S": "Lindsay",
    "W. SACRAMENTO PD": "West Sacramento",
    "BEAR VALLEY POLICE DEPT": "Bear Valley Springs",
    "BROADMOOR PD": "Broadmoor",
    "APPLE VALLEY DISTRICT PD": "Apple Valley",
}


def get_agencies():
    """Fetch all agencies from the database."""
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute("""
            SELECT agency_ori, agency_name, county
            FROM agencies
            ORDER BY agency_ori
        """).fetchall()
    return [{"ori": r[0], "name": r[1], "county": r[2]} for r in rows]


def classify_agency(name):
    """Classify an agency by its name. Returns (type, skip_reason) or (type, None)."""
    # Check skip patterns first
    for pattern, reason in SKIP_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return "skip", reason

    # CHP
    for pattern in CHP_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return "chp", None

    # Sheriff / county law enforcement
    for pattern in SHERIFF_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return "sheriff", None

    # Everything else is assumed to be a city PD
    return "city_pd", None


def extract_city_name(agency_name):
    """Extract city name from a city PD agency name."""
    # Check manual mappings first
    if agency_name in MANUAL_CITY_MAPPINGS:
        return MANUAL_CITY_MAPPINGS[agency_name]

    name = agency_name

    # Strip common suffixes
    for suffix in [
        " POLICE DEPARTMENT", " POLICE DEPT", " PD-COMM",
        " PD-COMMUNICATION", " PD #1", " PD",
    ]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break

    # Title case the remainder
    return name.title()


def fetch_census_places(api_key):
    """Fetch all California Census place names and FIPS codes."""
    c = Census(api_key)
    raw = c.acs5.state_place(("NAME",), CA_FIPS, Census.ALL, year=2023)

    places = {}
    for rec in raw:
        name = rec["NAME"]
        fips = rec["place"]
        # Census names look like "Los Angeles city, California"
        # Strip the state suffix and CDP/city/town designation
        clean = name.split(",")[0].strip()
        # Store both the full Census name and the clean version
        places[clean.upper()] = {"fips": fips, "census_name": name.split(",")[0].strip()}
        # Also store without " city", " town", " CDP" suffix for matching
        for suffix in [" city", " town", " CDP", " village"]:
            if clean.endswith(suffix):
                bare = clean[:-len(suffix)]
                places[bare.upper()] = {"fips": fips, "census_name": name.split(",")[0].strip()}

    return places


def fetch_county_fips():
    """Build county name → FIPS mapping for California."""
    import us
    # California county FIPS codes (3-digit)
    # We'll use the census API for this too
    county_fips = {
        "Alameda": "001", "Alpine": "003", "Amador": "005",
        "Butte": "007", "Calaveras": "009", "Colusa": "011",
        "Contra Costa": "013", "Del Norte": "015", "El Dorado": "017",
        "Fresno": "019", "Glenn": "021", "Humboldt": "023",
        "Imperial": "025", "Inyo": "027", "Kern": "029",
        "Kings": "031", "Lake": "033", "Lassen": "035",
        "Los Angeles": "037", "Madera": "039", "Marin": "041",
        "Mariposa": "043", "Mendocino": "045", "Merced": "047",
        "Modoc": "049", "Mono": "051", "Monterey": "053",
        "Napa": "055", "Nevada": "057", "Orange": "059",
        "Placer": "061", "Plumas": "063", "Riverside": "065",
        "Sacramento": "067", "San Benito": "069",
        "San Bernardino": "071", "San Diego": "073",
        "San Francisco": "075", "San Joaquin": "077",
        "San Luis Obispo": "079", "San Mateo": "081",
        "Santa Barbara": "083", "Santa Clara": "085",
        "Santa Cruz": "087", "Shasta": "089", "Sierra": "091",
        "Siskiyou": "093", "Solano": "095", "Sonoma": "097",
        "Stanislaus": "099", "Sutter": "101", "Tehama": "103",
        "Trinity": "105", "Tulare": "107", "Tuolumne": "109",
        "Ventura": "111", "Yolo": "113", "Yuba": "115",
    }
    return county_fips


def build_crosswalk(agencies, census_places, county_fips):
    """Build the crosswalk mapping each agency to Census geography."""
    entries = {}

    for ag in agencies:
        ori = ag["ori"]
        name = ag["name"]
        county = ag["county"]

        ag_type, skip_reason = classify_agency(name)

        if ag_type == "skip":
            entries[ori] = {
                "agency_name": name,
                "geography_type": "skip",
                "skip_reason": skip_reason,
                "match_method": "auto",
            }
            continue

        if ag_type == "chp":
            entries[ori] = {
                "agency_name": name,
                "geography_type": "state",
                "fips": CA_FIPS,
                "geography_name": "California",
                "match_method": "auto",
            }
            continue

        if ag_type == "sheriff":
            fips = county_fips.get(county)
            if fips:
                entries[ori] = {
                    "agency_name": name,
                    "geography_type": "county",
                    "fips": fips,
                    "geography_name": f"{county} County",
                    "match_method": "auto",
                }
            else:
                entries[ori] = {
                    "agency_name": name,
                    "geography_type": "county",
                    "fips": None,
                    "geography_name": county,
                    "match_method": "unmatched",
                }
            continue

        # City PD: extract city name and match to Census place
        city = extract_city_name(name)
        city_upper = city.upper()

        match = census_places.get(city_upper)
        if match:
            entries[ori] = {
                "agency_name": name,
                "geography_type": "place",
                "fips": match["fips"],
                "geography_name": match["census_name"],
                "match_method": "auto",
            }
        else:
            entries[ori] = {
                "agency_name": name,
                "geography_type": "place",
                "fips": None,
                "geography_name": city,
                "match_method": "unmatched",
            }

    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Output YAML path")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        raise RuntimeError("CENSUS_API_KEY not found in environment or .env")

    print("Fetching agencies from database...")
    agencies = get_agencies()
    print(f"  {len(agencies)} agencies")

    print("Fetching Census place names...")
    census_places = fetch_census_places(api_key)
    print(f"  {len(census_places)} place name variants")

    county_fips = fetch_county_fips()

    print("Building crosswalk...")
    entries = build_crosswalk(agencies, census_places, county_fips)

    # Summary stats
    by_type = {}
    unmatched = []
    for ori, entry in entries.items():
        geo = entry["geography_type"]
        by_type[geo] = by_type.get(geo, 0) + 1
        if entry.get("match_method") == "unmatched":
            unmatched.append((ori, entry["agency_name"], entry.get("geography_name")))

    print("Results:")
    for geo, count in sorted(by_type.items()):
        print(f"  {geo}: {count}")
    if unmatched:
        print(f"\nUnmatched ({len(unmatched)}):")
        for ori, name, geo_name in unmatched:
            print(f"  {ori}: {name} → {geo_name}")

    output = {"agencies": entries}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True, width=120)

    print(f"\nWrote {args.output}")
    print("Review and copy to hand/crosswalk.yaml after corrections.")


if __name__ == "__main__":
    main()
