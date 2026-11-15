from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.models.company import Company, Venture, Person, Achievement, ProductService, FAQ
from app.models.seo import ExternalProfile, PageSEO
from app.services.seo_service import SEOService
from app.services.insights_service import InsightsService
from app.config import settings

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

router = APIRouter()

STATIC_DIR = Path(__file__).parent.parent / "static"

def venture_art(slug: str) -> dict:
    """Logo files for a division, if present in static/img/ventures/.
    '<slug>-mark.*' = icon beside the name (also the dot background by default),
    '<slug>-bg.*'   = optional different image for the dot background (e.g. a full wordmark),
    '<slug>.*'      = full logo kept for reference."""
    art = {}
    for kind, stem in (("mark", f"{slug}-mark"), ("bg", f"{slug}-bg"), ("full", slug)):
        for ext in ("svg", "png", "webp", "jpg"):
            if (STATIC_DIR / "img" / "ventures" / f"{stem}.{ext}").exists():
                art[kind] = f"/static/img/ventures/{stem}.{ext}"
                break
    return art

@router.get("/")
def home_page(request: Request, db: Session = Depends(get_db)):
    company = db.query(Company).first()
    ventures = db.query(Venture).filter(Venture.is_published == True).order_by(Venture.display_order).all()
    faqs = db.query(FAQ).filter(FAQ.is_published == True).order_by(FAQ.display_order).all()
    profiles = db.query(ExternalProfile).all()

    schema_json = SEOService.get_organization_schema(company, ventures, profiles)

    return templates.TemplateResponse(
        request=request,
        name="public/index.html",
        context={
            "company": company,
            "ventures": ventures,
            "art": {v.slug: venture_art(v.slug) for v in ventures},
            "faqs": faqs,
            "schema_json": schema_json,
            "seo_title": "Belvo Synapse | Belvo Ventures Group Knowledge Base",
            "meta_description": company.one_line_definition if company else "Mumbai-based group of ventures founded by Hrishikesh in 2022.",
            "canonical_url": f"{settings.BASE_URL}/"
        }
    )

@router.get("/about")
def about_page(request: Request, db: Session = Depends(get_db)):
    company = db.query(Company).first()

    return templates.TemplateResponse(
        request=request,
        name="public/about.html",
        context={
            "company": company,
            "seo_title": "About Belvo Ventures Group | Mumbai Ecosystem",
            "meta_description": "Belvo Ventures Group began on 14 February 2022 in Mumbai, founded by Hrishikesh. Operating 9 divisions with over 1,000 interns trained.",
            "canonical_url": f"{settings.BASE_URL}/about"
        }
    )

@router.get("/ventures")
def ventures_directory(request: Request, db: Session = Depends(get_db)):
    ventures = db.query(Venture).filter(Venture.is_published == True).order_by(Venture.display_order).all()

    return templates.TemplateResponse(
        request=request,
        name="public/ventures.html",
        context={
            "ventures": ventures,
            "seo_title": "The 9 Operating Divisions | Belvo Ventures Group",
            "meta_description": "Explore the nine specialized divisions of Belvo Ventures Group across digital marketing, funding support, software, interiors, and more.",
            "canonical_url": f"{settings.BASE_URL}/ventures"
        }
    )

@router.get("/ventures/{slug}")
def venture_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    venture = db.query(Venture).filter(Venture.slug == slug, Venture.is_published == True).first()
    if not venture:
        raise HTTPException(status_code=404, detail="Division not found")

    siblings = db.query(Venture).filter(Venture.id != venture.id, Venture.is_published == True).order_by(Venture.display_order).all()
    venture_schema = SEOService.get_venture_schema(venture)

    return templates.TemplateResponse(
        request=request,
        name="public/venture_detail.html",
        context={
            "venture": venture,
            "siblings": siblings,
            "schema_json": venture_schema,
            "seo_title": f"{venture.name} | Division of Belvo Ventures Group",
            "meta_description": f"{venture.name} is the {venture.sector.lower()} division of Belvo Ventures Group in Mumbai. {venture.one_line}",
            "canonical_url": f"{settings.BASE_URL}/ventures/{venture.slug}"
        }
    )

@router.get("/leadership")
def leadership_page(request: Request, db: Session = Depends(get_db)):
    people = db.query(Person).filter(Person.consent_to_publish == True).all()

    return templates.TemplateResponse(
        request=request,
        name="public/leadership.html",
        context={
            "people": people,
            "seo_title": "Executive Leadership | Belvo Ventures Group",
            "meta_description": "Founder and leadership directory for Belvo Ventures Group. Founded by Hrishikesh in 2022 in Mumbai, India.",
            "canonical_url": f"{settings.BASE_URL}/leadership"
        }
    )

@router.get("/achievements")
def achievements_page(request: Request, db: Session = Depends(get_db)):
    achievements = db.query(Achievement).all()

    return templates.TemplateResponse(
        request=request,
        name="public/achievements.html",
        context={
            "achievements": achievements,
            "seo_title": "Milestones & Achievements | Belvo Ventures Group",
            "meta_description": "Verified operational milestones, timeline, and achievements of Belvo Ventures Group from 2022 to present.",
            "canonical_url": f"{settings.BASE_URL}/achievements"
        }
    )

@router.get("/products-services")
def products_services_page(request: Request, db: Session = Depends(get_db)):
    ORDER = [
        "belvo-digital",
        "capvanta",
        "fyndra",
        "verdict",
        "tatva",
        "belqora",
        "klyro",
        "hridayam",
        "sahay"
    ]
    order_map = {slug: idx for idx, slug in enumerate(ORDER)}
    ventures = db.query(Venture).filter(Venture.is_published == True).all()
    ventures = sorted(ventures, key=lambda v: order_map.get(v.slug, 99))

    return templates.TemplateResponse(
        request=request,
        name="public/products_services.html",
        context={
            "ventures": ventures,
            "seo_title": "Products & Services | Belvo Ventures Group",
            "meta_description": "Directory of capabilities and services offered across Belvo Ventures Group's nine divisions.",
            "canonical_url": f"{settings.BASE_URL}/products-services"
        }
    )

@router.get("/faq")
def faq_page(request: Request, db: Session = Depends(get_db)):
    faqs = db.query(FAQ).filter(FAQ.is_published == True).order_by(FAQ.display_order).all()
    faq_schema = SEOService.get_faq_schema(faqs)

    return templates.TemplateResponse(
        request=request,
        name="public/faq.html",
        context={
            "faqs": faqs,
            "schema_json": faq_schema,
            "seo_title": "Frequently Asked Questions | Belvo Ventures Group",
            "meta_description": "Official answers and verified facts about Belvo Ventures Group, its founder, operating divisions, and history.",
            "canonical_url": f"{settings.BASE_URL}/faq"
        }
    )

@router.get("/insights")
def insights_page(request: Request, db: Session = Depends(get_db)):
    company = db.query(Company).first()
    nine_ventures = InsightsService.get_nine_ventures()
    belqora_categories = InsightsService.get_belqora_categories()
    founder = InsightsService.get_founder_data()
    milestones = InsightsService.get_timeline_milestones()
    articles = InsightsService.get_articles()
    featured_article = next((a for a in articles if a.get("featured")), articles[0] if articles else None)

    return templates.TemplateResponse(
        request=request,
        name="public/insights.html",
        context={
            "company": company,
            "nine_ventures": nine_ventures,
            "belqora_categories": belqora_categories,
            "founder": founder,
            "milestones": milestones,
            "articles": articles,
            "featured_article": featured_article,
            "seo_title": "Belvo Insights | Company Story, Ecosystem & Perspectives",
            "meta_description": "Official company story, nine-venture ecosystem architecture, and founder insights from Belvo Ventures Group, Mumbai.",
            "canonical_url": f"{settings.BASE_URL}/insights"
        }
    )

@router.get("/insights/{slug}")
def insight_article_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    company = db.query(Company).first()
    article = InsightsService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    articles = InsightsService.get_articles()
    related_articles = [a for a in articles if a["slug"] != slug][:3]

    return templates.TemplateResponse(
        request=request,
        name="public/article_detail.html",
        context={
            "company": company,
            "article": article,
            "related_articles": related_articles,
            "seo_title": f"{article['title']} | Belvo Insights",
            "meta_description": article["summary"],
            "canonical_url": f"{settings.BASE_URL}/insights/{article['slug']}"
        }
    )

# Current openings — edit this list to update the careers page.
OPENINGS = [
    {"title": "Website Developer",     "team": "Technology",          "count": 10},
    {"title": "Software Developer",    "team": "Technology",          "count": 5},
    {"title": "Social Media Manager",  "team": "Marketing",           "count": 5},
    {"title": "Business Analyst",      "team": "Business",            "count": 5},
    {"title": "Graphic Designer",      "team": "Design",              "count": 3},
    {"title": "Administrative Staff",  "team": "People & Operations", "count": 3},
    {"title": "HR Executive",          "team": "People & Operations", "count": 2},
]

@router.get("/careers")
def careers_page(request: Request, db: Session = Depends(get_db)):
    ventures = db.query(Venture).filter(Venture.is_published == True).order_by(Venture.display_order).all()

    return templates.TemplateResponse(
        request=request,
        name="public/careers.html",
        context={
            "ventures": ventures,
            "openings": OPENINGS,
            "total_openings": sum(o["count"] for o in OPENINGS),
            "seo_title": "Careers & Internships | Belvo Ventures Group",
            "meta_description": "Open positions, careers and structured internship batches at Belvo Ventures Group, Mumbai. Over 1,000 interns trained across technical, design, marketing and business cohorts.",
            "canonical_url": f"{settings.BASE_URL}/careers"
        }
    )

@router.get("/contact")
def contact_page(request: Request, db: Session = Depends(get_db)):
    profiles = db.query(ExternalProfile).all()

    return templates.TemplateResponse(
        request=request,
        name="public/contact.html",
        context={
            "profiles": profiles,
            "seo_title": "Contact & Official Channels | Belvo Ventures Group",
            "meta_description": "Official communication channels and verified profiles for Belvo Ventures Group in Mumbai, India.",
            "canonical_url": f"{settings.BASE_URL}/contact"
        }
    )
