from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pathlib import Path
import os

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.seed import seed_database
from app.routes.public import router as public_router
from app.routes.technical import router as technical_router
from app.routes.admin import router as admin_router

BASE_DIR = Path(__file__).parent

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI Knowledge & Discoverability Single Source of Truth for Belvo Ventures Group"
)

# Ensure static directories exist
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "css").mkdir(parents=True, exist_ok=True)
(static_dir / "js").mkdir(parents=True, exist_ok=True)
(static_dir / "img").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount Routers
# Technical files at root: /robots.txt, /sitemap.xml, /llms.txt
app.include_router(technical_router)
# Admin Panel: /admin/...
app.include_router(admin_router)
# Public SSR Knowledge Pages: /, /about, /ventures, etc.
app.include_router(public_router)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="public/about.html",
        context={
            "seo_title": "Page Not Found | Belvo Synapse",
            "meta_description": "The requested verified record was not found.",
            "canonical_url": f"{settings.BASE_URL}/"
        },
        status_code=404
    )
