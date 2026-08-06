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

PAGE_SIZE = 50


def _agency_list_context(q: str, page: int):
    total = queries.count_agencies(q=q)
    pages = max(1, -(-total // PAGE_SIZE))
    page = max(1, min(page, pages))
    agencies = queries.search_agencies(
        q=q, limit=PAGE_SIZE, offset=(page - 1) * PAGE_SIZE)
    return {
        "agencies": agencies,
        "q": q,
        "total": total,
        "page": page,
        "pages": pages,
        "start": (page - 1) * PAGE_SIZE + 1 if total else 0,
        "end": min(page * PAGE_SIZE, total),
    }


def _parse_page(page: str) -> int:
    try:
        return max(1, int(page))
    except ValueError:
        return 1


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, q: str = "", page: str = "1"):
    ctx = _agency_list_context(q, _parse_page(page))
    return templates.TemplateResponse(request, "index.html", ctx)


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", page: str = "1"):
    ctx = _agency_list_context(q, _parse_page(page))
    if not _is_htmx(request):
        return templates.TemplateResponse(request, "index.html", ctx)
    return templates.TemplateResponse(request, "partials/agency_list.html", ctx)


def _is_htmx(request: Request) -> bool:
    """True for htmx partial requests (but not history restores, which
    expect a full page)."""
    return (
        request.headers.get("hx-request") == "true"
        and request.headers.get("hx-history-restore-request") != "true"
    )


def _full_page(request: Request, ori: str, tab: str, ctx: dict):
    """Render the full agency page with the given tab active."""
    agency = queries.get_agency(ori)
    if not agency:
        return HTMLResponse("<h1>Agency not found</h1>", status_code=404)

    return templates.TemplateResponse(request, "agency.html", {
        "agency": agency,
        "ori": ori,
        "tab": tab,
        "jurisdiction": queries.get_agency_jurisdiction(ori),
        **ctx,
    })


@app.get("/agency/{ori}", response_class=HTMLResponse)
async def agency_detail(request: Request, ori: str):
    stops_by_year = queries.get_agency_stops_by_year(ori)
    return _full_page(request, ori, "overview", {
        "stops_by_year": stops_by_year,
    })


@app.get("/agency/{ori}/overview", response_class=HTMLResponse)
async def agency_overview(request: Request, ori: str):
    stops_by_year = queries.get_agency_stops_by_year(ori)
    if not _is_htmx(request):
        return _full_page(request, ori, "overview", {
            "stops_by_year": stops_by_year,
        })
    return templates.TemplateResponse(request, "partials/agency_overview.html", {
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


def _parse_year_range(year_from: str, year_to: str, year: str):
    """Parse a year range; a legacy single `year` param maps to from=to.
    A reversed range is swapped."""
    yf, yt = _parse_year(year_from), _parse_year(year_to)
    if yf is None and yt is None:
        yr = _parse_year(year)
        if yr is not None:
            yf = yt = yr
    if yf is not None and yt is not None and yf > yt:
        yf, yt = yt, yf
    return yf, yt


@app.get("/agency/{ori}/demographics", response_class=HTMLResponse)
async def agency_demographics(
    request: Request, ori: str,
    year_from: str = Query(default=""),
    year_to: str = Query(default=""),
    year: str = Query(default=""),
):
    yf, yt = _parse_year_range(year_from, year_to, year)
    race = queries.get_agency_demographics_race(ori, yf, yt)
    gender = queries.get_agency_demographics_gender(ori, yf, yt)
    age = queries.get_agency_demographics_age(ori, yf, yt)
    years = queries.get_agency_years(ori)
    census = queries.get_agency_demographics_census(ori)

    # Merge census population % into race data by code
    if census:
        census_by_code = {c["code"]: c for c in census}
        for r in race:
            c = census_by_code.get(r["code"])
            r["pop_pct"] = c["pct"] if c else None
            r["stop_pop_ratio"] = (
                round(r["share"] / c["share"], 1)
                if c and c["share"] and r["share"] is not None else None
            )
    else:
        for r in race:
            r["pop_pct"] = None
            r["stop_pop_ratio"] = None

    ctx = {
        "tab": "demographics",
        "race": race,
        "gender": gender,
        "age": age,
        "years": years,
        "year_from": yf,
        "year_to": yt,
        "ori": ori,
        "has_census": census is not None,
    }
    if not _is_htmx(request):
        return _full_page(request, ori, "demographics", ctx)
    return templates.TemplateResponse(request, "partials/agency_tabs.html", ctx)


@app.get("/agency/{ori}/disparities", response_class=HTMLResponse)
async def agency_disparities(
    request: Request, ori: str,
    year_from: str = Query(default=""),
    year_to: str = Query(default=""),
    year: str = Query(default=""),
    stop_type: str = Query(default="all"),
):
    yf, yt = _parse_year_range(year_from, year_to, year)
    if stop_type not in queries.STOP_TYPE_VIEWS:
        stop_type = "all"
    disparities = queries.get_agency_disparities(ori, yf, yt, stop_type)
    years = queries.get_agency_years(ori)
    census = queries.get_agency_demographics_census(ori)

    # Merge census population % into disparities by race code
    if census:
        census_by_code = {c["code"]: c for c in census}
        for d in disparities:
            c = census_by_code.get(d["code"])
            d["pop_pct"] = c["pct"] if c else None
            d["stop_pop_ratio"] = (
                round(d["share"] / c["share"], 1)
                if c and c["share"] and d["share"] is not None else None
            )
    else:
        for d in disparities:
            d["pop_pct"] = None
            d["stop_pop_ratio"] = None

    ctx = {
        "tab": "disparities",
        "disparities": disparities,
        "years": years,
        "year_from": yf,
        "year_to": yt,
        "stop_type": stop_type,
        "stop_types": queries.STOP_TYPE_LABELS,
        "ori": ori,
        "has_census": census is not None,
    }
    if not _is_htmx(request):
        return _full_page(request, ori, "disparities", ctx)
    return templates.TemplateResponse(request, "partials/agency_tabs.html", ctx)


# -- Article routes --

@app.get("/articles", response_class=HTMLResponse)
async def article_list(request: Request):
    return templates.TemplateResponse(request, "articles.html", {
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
    return templates.TemplateResponse(request, "article.html", {
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
