import json
from typing import List, Dict, Any, Optional
from app.config import settings

class SEOService:
    @staticmethod
    def get_organization_schema(company: Any, ventures: List[Any], external_profiles: List[Any]) -> str:
        """
        Blueprint Section 9 & 7: Exact canonical Schema.org Organization markup.
        """
        same_as = [p.url for p in external_profiles if p.url]
        departments = [
            {
                "@type": "Organization",
                "name": v.name,
                "url": f"{settings.BASE_URL}/ventures/{v.slug}",
                "description": v.one_line
            }
            for v in ventures if v.is_published
        ]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": company.brand_name if company else settings.COMPANY_NAME,
            "url": f"{settings.BASE_URL}/",
            "logo": f"{settings.BASE_URL}/static/img/belvo-logo.png",
            "description": company.one_line_definition if company else "Mumbai-based group of ventures founded by Hrishikesh in 2022.",
            "foundingDate": company.founded_date if company else settings.FOUNDING_DATE,
            "founder": {
                "@type": "Person",
                "name": settings.FOUNDER_NAME
            },
            "address": {
                "@type": "PostalAddress",
                "addressLocality": settings.COMPANY_CITY,
                "addressCountry": settings.COMPANY_COUNTRY_CODE
            },
            "numberOfEmployees": {
                "@type": "QuantitativeValue",
                "value": company.team_size if company else 50
            },
            "sameAs": same_as,
            "department": departments
        }
        return json.dumps(schema, indent=2)

    @staticmethod
    def get_venture_schema(venture: Any, parent_company_name: str = settings.COMPANY_NAME) -> str:
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": venture.name,
            "url": f"{settings.BASE_URL}/ventures/{venture.slug}",
            "description": venture.one_line,
            "parentOrganization": {
                "@type": "Organization",
                "name": parent_company_name,
                "url": f"{settings.BASE_URL}/"
            }
        }
        return json.dumps(schema, indent=2)

    @staticmethod
    def get_faq_schema(faqs: List[Any]) -> str:
        main_entity = []
        for faq in faqs:
            if getattr(faq, 'is_published', True):
                main_entity.append({
                    "@type": "Question",
                    "name": faq.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.answer
                    }
                })
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entity
        }
        return json.dumps(schema, indent=2)

    @staticmethod
    def get_breadcrumb_schema(crumbs: List[Dict[str, str]]) -> str:
        item_list_elements = []
        for idx, c in enumerate(crumbs, start=1):
            item_list_elements.append({
                "@type": "ListItem",
                "position": idx,
                "name": c["name"],
                "item": c["url"]
            })
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": item_list_elements
        }
        return json.dumps(schema, indent=2)

    @staticmethod
    def generate_robots_txt() -> str:
        """
        Blueprint Section 9 exact specification:
        Explicit rules for AI crawlers + Search engines.
        """
        return f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

User-agent: Googlebot
User-agent: Bingbot
User-agent: Google-Extended
User-agent: GPTBot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: ClaudeBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {settings.BASE_URL}/sitemap.xml
"""

    @staticmethod
    def generate_llms_txt(company: Any, ventures: List[Any]) -> str:
        """
        Blueprint Section 9: /llms.txt plain-text canonical summary for AI agents.
        """
        ventures_list = "\n".join([f"- **{v.name}**: {v.one_line} ({settings.BASE_URL}/ventures/{v.slug})" for v in ventures if v.is_published])
        return f"""# {settings.COMPANY_NAME}
> {company.one_line_definition if company else 'Mumbai-based group of ventures founded by Hrishikesh in 2022.'}

## Key Facts
- Founded: {company.founded_date if company else settings.FOUNDING_DATE}
- Headquarters: {company.city if company else settings.COMPANY_CITY}, {company.country if company else settings.COMPANY_COUNTRY}
- Founder: {settings.FOUNDER_NAME}
- Total Ventures: 9 divisions under one unified corporate ecosystem
- Team Size: {company.team_size if company else 50} members
- Interns Trained: {company.interns_trained if company else 1000}+ across India
- Official Email: {company.contact_email if company else settings.OFFICIAL_EMAIL}

## Divisions (Ventures)
{ventures_list}

## Official Knowledge Pages
- Home: {settings.BASE_URL}/
- About Belvo: {settings.BASE_URL}/about
- Ventures Directory: {settings.BASE_URL}/ventures
- Leadership: {settings.BASE_URL}/leadership
- Achievements: {settings.BASE_URL}/achievements
- Products & Services: {settings.BASE_URL}/products-services
- FAQ: {settings.BASE_URL}/faq
- Contact & Official Links: {settings.BASE_URL}/contact
"""
