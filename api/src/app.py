"""FastAPI application for the RIPA agency explorer."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db, queries

APP_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = APP_DIR / "src" / "templates"
STATIC_DIR = APP_DIR / "static"
CONTENT_DIR = APP_DIR / "src" / "content"
RENDERED_DIR = CONTENT_DIR / "rendered"

ROOT_PATH = os.environ.get("ROOT_PATH", "").rstrip("/")


def _load_articles():
    """Load article metadata from YAML."""
    yaml_path = CONTENT_DIR / "articles.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return data.get("articles", [])


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.articles = _load_articles()
    db.init_pool()
    yield
    db.close_pool()


app = FastAPI(title="RIPA Agency Explorer", root_path=ROOT_PATH, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals["root_path"] = ROOT_PATH


# -- Jinja2 filters --

def format_number(value):
    if value is None:
        return ""
    return f"{value:,}"

templates.env.filters["commas"] = format_number


# -- HTML routes --

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    agencies = queries.search_agencies(limit=50)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "agencies": agencies,
    })


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    agencies = queries.search_agencies(q=q, limit=50)
    return templates.TemplateResponse("partials/agency_list.html", {
        "request": request,
        "agencies": agencies,
    })


@app.get("/agency/{ori}", response_class=HTMLResponse)
async def agency_detail(request: Request, ori: str):
    agency = queries.get_agency(ori)
    if not agency:
        return HTMLResponse("<h1>Agency not found</h1>", status_code=404)

    years = queries.get_agency_years(ori)
    stops_by_year = queries.get_agency_stops_by_year(ori)
    jurisdiction = queries.get_agency_jurisdiction(ori)

    return templates.TemplateResponse("agency.html", {
        "request": request,
        "agency": agency,
        "ori": ori,
        "years": years,
        "stops_by_year": stops_by_year,
        "jurisdiction": jurisdiction,
    })


@app.get("/agency/{ori}/overview", response_class=HTMLResponse)
async def agency_overview(request: Request, ori: str):
    stops_by_year = queries.get_agency_stops_by_year(ori)
    return templates.TemplateResponse("partials/agency_overview.html", {
        "request": request,
        "ori": ori,
        "stops_by_year": stops_by_year,
    })


def _parse_year(year: str | None) -> int | None:
    """Parse year query param — empty string or None → None."""
    if not year:
        return None
    try:
        return int(year)
    except ValueError:
        return None


@app.get("/agency/{ori}/demographics", response_class=HTMLResponse)
async def agency_demographics(
    request: Request, ori: str,
    year: str = Query(default=""),
):
    yr = _parse_year(year)
    race = queries.get_agency_demographics_race(ori, yr)
    gender = queries.get_agency_demographics_gender(ori, yr)
    age = queries.get_agency_demographics_age(ori, yr)
    years = queries.get_agency_years(ori)
    census = queries.get_agency_demographics_census(ori)

    # Merge census population % into race data by code
    if census:
        census_by_code = {c["code"]: c for c in census}
        for r in race:
            c = census_by_code.get(r["code"])
            r["pop_pct"] = c["pct"] if c else None
            r["stop_pop_ratio"] = (
                round(float(r["pct"]) / c["pct"], 1)
                if c and c["pct"] and c["pct"] > 0 else None
            )
    else:
        for r in race:
            r["pop_pct"] = None
            r["stop_pop_ratio"] = None

    return templates.TemplateResponse("partials/agency_tabs.html", {
        "request": request,
        "tab": "demographics",
        "race": race,
        "gender": gender,
        "age": age,
        "years": years,
        "selected_year": yr,
        "ori": ori,
        "has_census": census is not None,
    })


@app.get("/agency/{ori}/disparities", response_class=HTMLResponse)
async def agency_disparities(
    request: Request, ori: str,
    year: str = Query(default=""),
    stop_type: str = Query(default="all"),
):
    yr = _parse_year(year)
    if stop_type not in queries.STOP_TYPE_VIEWS:
        stop_type = "all"
    disparities = queries.get_agency_disparities(ori, yr, stop_type)
    years = queries.get_agency_years(ori)
    census = queries.get_agency_demographics_census(ori)

    # Merge census population % into disparities by race code
    if census:
        census_by_code = {c["code"]: c for c in census}
        for d in disparities:
            c = census_by_code.get(d["code"])
            d["pop_pct"] = c["pct"] if c else None
            d["stop_pop_ratio"] = (
                round(float(d["pct_share"]) / c["pct"], 1)
                if c and c["pct"] and c["pct"] > 0 else None
            )
    else:
        for d in disparities:
            d["pop_pct"] = None
            d["stop_pop_ratio"] = None

    return templates.TemplateResponse("partials/agency_tabs.html", {
        "request": request,
        "tab": "disparities",
        "disparities": disparities,
        "years": years,
        "selected_year": yr,
        "stop_type": stop_type,
        "stop_types": queries.STOP_TYPE_LABELS,
        "ori": ori,
        "has_census": census is not None,
    })


# -- Article routes --

@app.get("/articles", response_class=HTMLResponse)
async def article_list(request: Request):
    return templates.TemplateResponse("articles.html", {
        "request": request,
        "articles": request.app.state.articles,
    })


@app.get("/articles/{slug}", response_class=HTMLResponse)
async def article_detail(request: Request, slug: str):
    articles = request.app.state.articles
    article = next((a for a in articles if a["slug"] == slug), None)
    if not article:
        return HTMLResponse("<h1>Article not found</h1>", status_code=404)

    html_path = RENDERED_DIR / f"{slug}.html"
    if not html_path.exists():
        return HTMLResponse("<h1>Article not built</h1>", status_code=404)

    content = html_path.read_text()
    return templates.TemplateResponse("article.html", {
        "request": request,
        "article": article,
        "content": content,
    })


# -- JSON API routes --

@app.get("/api/agency/{ori}/chart-data")
async def chart_data(ori: str):
    stops = queries.get_agency_stops_by_year(ori)
    return JSONResponse({
        "labels": [s["year"] for s in stops],
        "person_stops": [s["n_person_stops"] for s in stops],
        "stops": [s["n_stops"] for s in stops],
    })
