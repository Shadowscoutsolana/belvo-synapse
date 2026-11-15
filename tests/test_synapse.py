import pytest
from starlette.requests import Request
from app.database import SessionLocal
from app.routes.public import (
    home_page,
    about_page,
    ventures_directory,
    venture_detail,
    leadership_page,
    achievements_page,
    products_services_page,
    faq_page,
    contact_page,
    insights_page,
    insight_article_detail,
    careers_page
)
from app.routes.technical import robots_txt, sitemap_xml, llms_txt
from app.services.consistency import ConsistencyValidator

def make_request(path: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
        "query_string": b"",
        "server": ("127.0.0.1", 8000),
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope)

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_home_page_renders_blueprint_facts(db):
    req = make_request("/")
    resp = home_page(req, db)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")
    
    # Assert canonical facts from blueprint
    assert "BELVO VENTURES GROUP" in html
    assert "Mumbai" in html
    assert "Bombay" not in html
    assert "2022" in html
    assert "9" in html
    assert "1,000+" in html
    assert "Innovate · Build · Grow" in html
    assert ("By a founder, for the founders" in html or "By the Founder, for the Founder" in html)
    
    # Schema.org JSON-LD
    assert 'application/ld+json' in html
    assert '"@type": "Organization"' in html
    assert 'Belvo Digital' in html

def test_all_public_pages_render(db):
    pages = [
        ("/", lambda req: home_page(req, db)),
        ("/about", lambda req: about_page(req, db)),
        ("/ventures", lambda req: ventures_directory(req, db)),
        ("/leadership", lambda req: leadership_page(req, db)),
        ("/achievements", lambda req: achievements_page(req, db)),
        ("/products-services", lambda req: products_services_page(req, db)),
        ("/faq", lambda req: faq_page(req, db)),
        ("/contact", lambda req: contact_page(req, db)),
        ("/insights", lambda req: insights_page(req, db)),
        ("/careers", lambda req: careers_page(req, db)),
    ]
    for path, handler in pages:
        req = make_request(path)
        resp = handler(req)
        assert resp.status_code == 200, f"Page {path} failed with {resp.status_code}"
        html = resp.body.decode("utf-8")
        assert "Mumbai" in html
        assert "Bombay" not in html
        assert "Last Verified" in html or "verified" in html.lower()

def test_all_nine_venture_detail_pages(db):
    slugs = [
        "belvo-digital",
        "capvanta",
        "tatva",
        "hridayam",
        "verdict",
        "fyndra",
        "belqora",
        "klyro",
        "sahay"
    ]
    for slug in slugs:
        req = make_request(f"/ventures/{slug}")
        resp = venture_detail(slug, req, db)
        assert resp.status_code == 200
        html = resp.body.decode("utf-8")
        assert "division of belvo ventures group" in html.lower()
        assert "Mumbai" in html
        assert "Bombay" not in html
        assert "Last Verified" in html

def test_technical_crawler_endpoints(db):
    # /robots.txt
    resp_robots = robots_txt()
    assert resp_robots.status_code == 200
    robots_text = resp_robots.body.decode("utf-8")
    assert "GPTBot" in robots_text
    assert "ClaudeBot" in robots_text
    assert "PerplexityBot" in robots_text
    assert "Disallow: /admin/" in robots_text
    assert "Disallow: /api/" in robots_text

    # /sitemap.xml
    resp_sitemap = sitemap_xml(db)
    assert resp_sitemap.status_code == 200
    sitemap_text = resp_sitemap.body.decode("utf-8")
    assert "<urlset" in sitemap_text
    assert "/ventures/belvo-digital" in sitemap_text

    # /llms.txt
    resp_llms = llms_txt(db)
    assert resp_llms.status_code == 200
    llms_content = resp_llms.body.decode("utf-8")
    assert "# Belvo Ventures Group" in llms_content
    assert "Divisions (Ventures)" in llms_content
    assert "Belvo Digital" in llms_content

def test_consistency_validator():
    # Detects Bombay
    w1 = ConsistencyValidator.validate_text("Our headquarters are in Bombay.")
    assert any("Bombay" in w for w in w1)

    # Detects separate company claims
    w2 = ConsistencyValidator.validate_text("Belvo Digital is an independent company.")
    assert any("independent company" in w or "division" in w for w in w2)

    # Detects forbidden registration codes
    w3 = ConsistencyValidator.validate_text("CIN: U72900MH2022PTC123456")
    assert any("registration" in w.lower() or "cin" in w.lower() for w in w3)

    # Valid text passes cleanly
    w4 = ConsistencyValidator.validate_text("Belvo Ventures Group operates 9 divisions in Mumbai, India.")
    assert len(w4) == 0

def test_admin_flow_and_audit_log(db):
    from app.routes.admin import login_post, company_edit_post
    from app.models.users import AuditLog
    
    # Test valid login
    req = make_request("/admin/login")
    resp_login = login_post(req, username="admin@belvoventures.com", password="BelvoAdmin2026!", db=db)
    assert resp_login.status_code == 303
    assert "belvo_admin_session" in resp_login.headers.get("set-cookie", "")

    # Test company update creates audit log entry
    initial_log_count = db.query(AuditLog).count()
    comp_req = make_request("/admin/company")
    # Mock authenticated user cookie
    from app.services.auth import create_access_token
    token = create_access_token({"sub": "admin@belvoventures.com", "role": "admin"})
    comp_req._cookies = {"belvo_admin_session": token}
    
    resp_edit = company_edit_post(
        request=comp_req,
        brand_name="Belvo Ventures Group",
        founded_date="2022-02-14",
        city="Mumbai",
        country="India",
        tagline="Innovate · Build · Grow",
        sub_line="By a founder, for the founders.",
        team_size=50,
        interns_trained=1000,
        one_line_definition="Belvo Ventures Group is a Mumbai-based group of ventures founded by Hrishikesh in 2022. Its nine ventures work across digital marketing, funding support, interiors, coaching, legal support, CA support, software, hardware solutions and social impact, all under one ecosystem.",
        long_description="Verified description for founders.",
        db=db
    )
    assert resp_edit.status_code == 200
    assert db.query(AuditLog).count() > initial_log_count

def test_insights_master_page_structure(db):
    req = make_request("/insights")
    resp = insights_page(req, db)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    # Brand identity & philosophy
    assert "Belvo Ventures Group" in html
    assert "Mumbai" in html
    assert "Bombay" not in html
    assert "2022" in html
    assert "Innovate · Build · Grow" in html
    assert "By a Founder, For the Founders" in html or "By a founder, for the founders" in html
    assert "You be the mind. We will be your backbone." in html

    # Exactly 9 ventures with official spelling
    nine_ventures = [
        "CAPVANTA",
        "VERDICT",
        "KLYRO",
        "FYNDRA",
        "TATTVA",
        "BELVO DIGITAL",
        "HRIDAYAM",
        "SAHAYA",
        "BELQORA"
    ]
    for v in nine_ventures:
        assert v in html, f"Venture {v} missing in Insights page"

    # Belqora 12 categories
    belqora_cats = [
        "Healthcare & Clinics",
        "Food, Café & Hospitality",
        "Beauty, Fitness & Wellness",
        "Education & Institutions",
        "Retail & Commercial",
        "Professional Services",
        "Enterprise Business",
        "Marketing & E-commerce",
        "AI & Intelligence",
        "Cybersecurity & Infrastructure",
        "Education & Productivity",
        "Advanced Business Platforms"
    ]
    for cat in belqora_cats:
        escaped_cat = cat.replace("&", "&amp;")
        assert (cat in html or escaped_cat in html), f"Belqora category {cat} missing in Insights page"

    # Founder name and leadership
    assert "Hrishikesh Mishra" in html
    assert ("Co-Founder & Chief Executive Officer" in html or "Co-Founder &amp; Chief Executive Officer" in html)
    assert "Software Engineering" in html
    assert "iOS Development" in html

    # Verified metrics
    assert "1,000+" in html
    assert "500+" in html
    assert "50" in html
    assert "100+" in html
    assert "₹10L+" in html or "10 lakh" in html.lower()

def test_insight_article_detail_page(db):
    req = make_request("/insights/why-i-started-belvo-integrated-founder-ecosystem")
    resp = insight_article_detail("why-i-started-belvo-integrated-founder-ecosystem", req, db)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "Why I Started Belvo" in html
    assert "Hrishikesh Mishra" in html
    assert "Executive Takeaways" in html
    assert "Mumbai" in html
    assert "Bombay" not in html
