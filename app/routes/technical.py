from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.company import Company, Venture
from app.services.seo_service import SEOService
from app.config import settings

router = APIRouter()

@router.get("/robots.txt", response_class=Response)
def robots_txt():
    content = SEOService.generate_robots_txt()
    return Response(content=content, media_type="text/plain; charset=utf-8")

@router.get("/llms.txt", response_class=Response)
def llms_txt(db: Session = Depends(get_db)):
    company = db.query(Company).first()
    ventures = db.query(Venture).order_by(Venture.display_order).all()
    content = SEOService.generate_llms_txt(company, ventures)
    return Response(content=content, media_type="text/plain; charset=utf-8")

@router.get("/sitemap.xml", response_class=Response)
def sitemap_xml(db: Session = Depends(get_db)):
    ventures = db.query(Venture).filter(Venture.is_published == True).order_by(Venture.display_order).all()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    static_routes = [
        ("/", "1.0", "weekly"),
        ("/about", "0.9", "monthly"),
        ("/ventures", "0.9", "weekly"),
        ("/leadership", "0.8", "monthly"),
        ("/achievements", "0.8", "monthly"),
        ("/products-services", "0.8", "monthly"),
        ("/insights", "0.9", "weekly"),
        ("/faq", "0.8", "weekly"),
        ("/careers", "0.7", "monthly"),
        ("/contact", "0.7", "monthly"),
    ]
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for route, priority, freq in static_routes:
        xml_lines.append(f"""  <url>
    <loc>{settings.BASE_URL}{route}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    for v in ventures:
        xml_lines.append(f"""  <url>
    <loc>{settings.BASE_URL}/ventures/{v.slug}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>""")

    xml_lines.append('</urlset>')
    
    return Response(content="\n".join(xml_lines), media_type="application/xml; charset=utf-8")
