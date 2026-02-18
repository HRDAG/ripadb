"""FastAPI application for the RIPA agency explorer."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db, queries

APP_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = APP_DIR / "src" / "templates"
STATIC_DIR = APP_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_pool()
    yield
    db.close_pool()


app = FastAPI(title="RIPA Agency Explorer", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


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

    return templates.TemplateResponse("agency.html", {
        "request": request,
        "agency": agency,
        "years": years,
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

    return templates.TemplateResponse("partials/agency_tabs.html", {
        "request": request,
        "tab": "demographics",
        "race": race,
        "gender": gender,
        "age": age,
        "years": years,
        "selected_year": yr,
        "ori": ori,
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

    return templates.TemplateResponse("partials/agency_tabs.html", {
        "request": request,
        "tab": "disparities",
        "disparities": disparities,
        "years": years,
        "selected_year": yr,
        "stop_type": stop_type,
        "stop_types": queries.STOP_TYPE_LABELS,
        "ori": ori,
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
