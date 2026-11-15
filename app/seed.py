import os
import sys
from app.services.auth import hash_password
from app.database import Base, engine, SessionLocal
from app.models.company import Company, Venture, Person, Achievement, ProductService, FAQ
from app.models.seo import PageSEO, Media, ExternalProfile
from app.models.users import User, AuditLog
from app.models.ai_visibility import AIPlatform, AIQuestion, AIRun

def seed_database():
    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Company info if empty
        existing_company = db.query(Company).first()
        if not existing_company:
            print("Seeding Company details...")
            company = Company(
                brand_name="Belvo Ventures Group",
                tagline="Innovate · Build · Grow",
                sub_line="By a founder, for the founders.",
                one_line_definition="Belvo Ventures Group is a Mumbai-based group of ventures founded by Hrishikesh in 2022. Its nine ventures work across digital marketing, funding support, interiors, coaching, legal support, CA support, software, hardware solutions and social impact, all under one ecosystem.",
                short_description="Belvo Ventures Group began on 14 February 2022 in Mumbai. It started as freelance work, and as founder Hrishikesh built a network of founders, professionals and clients, it grew into a group of ventures.",
                long_description="Belvo Ventures Group began on 14 February 2022 in Mumbai. It started as freelance work, and as founder Hrishikesh built a network of founders, professionals and clients, it grew into a group of ventures. Each venture is a division of Belvo that covers a specific business need, from marketing and funding to software and social impact. Our goal is building a stronger ecosystem for founders.\n\nBelvo runs structured internship batches for learners from across India. More than 500 interns are currently part of our ongoing cohorts, with new batches opening soon, and over 1,000 interns have been trained so far.",
                founded_date="2022-02-14",
                city="Mumbai",
                country="India",
                team_size=50,
                interns_trained=1000,
                mission="Empowering founders, professionals, and learners with dedicated multi-disciplinary ecosystem support.",
                vision="To build India's most cohesive founder-first venture ecosystem across technology, services, and social impact.",
                contact_email="contact@belvoventures.com"
            )
            db.add(company)
            db.commit()
            
        # 2. Seed 9 Approved Ventures
        existing_ventures = db.query(Venture).count()
        if existing_ventures == 0:
            print("Seeding 9 Approved Ventures...")
            ventures_data = [
                {
                    "name": "Belvo Digital",
                    "slug": "belvo-digital",
                    "sector": "Digital Marketing",
                    "one_line": "Web, social media and digital marketing services to help businesses grow online.",
                    "description": "Belvo Digital is the digital marketing and web solutions division of Belvo Ventures Group. It helps founders, emerging startups, and enterprises establish a high-impact digital presence through performance marketing, strategic social media management, brand positioning, and modern web experiences.",
                    "display_order": 1
                },
                {
                    "name": "Capvanta",
                    "slug": "capvanta",
                    "sector": "Funding Support",
                    "one_line": "Helping founders and businesses get the funds they need to grow.",
                    "description": "Capvanta is the funding enablement division of Belvo Ventures Group. It assists high-potential ventures with investment readiness, pitch architecture, financial modeling advisory, and connecting founders with capital avenues.",
                    "display_order": 2
                },
                {
                    "name": "Tatva",
                    "slug": "tatva",
                    "sector": "Interior Design & Space Solutions",
                    "one_line": "Interior design and space solutions.",
                    "description": "Tatva is the architecture and space design division of Belvo Ventures Group, delivering human-centric spatial planning, modern commercial workspace designs, and aesthetic residential interiors.",
                    "display_order": 5
                },
                {
                    "name": "Hridayam",
                    "slug": "hridayam",
                    "sector": "Coaching & Personal Development",
                    "one_line": "Coaching to help people learn, grow and build confidence.",
                    "description": "Hridayam is the mentorship and personal coaching division of Belvo Ventures Group, offering targeted guidance to empower young founders, professionals, and students to unlock leadership potential.",
                    "display_order": 8
                },
                {
                    "name": "Verdict",
                    "slug": "verdict",
                    "sector": "Legal Support",
                    "one_line": "Legal support for founders and businesses.",
                    "description": "Verdict is the legal advisory support division of Belvo Ventures Group. It assists early-stage and growing enterprises with foundational contracts, compliance hygiene, vendor agreements, and commercial documentation support.",
                    "display_order": 4
                },
                {
                    "name": "Fyndra",
                    "slug": "fyndra",
                    "sector": "CA & Financial Support",
                    "one_line": "CA support to help businesses manage their accounts and finances.",
                    "description": "Fyndra is the chartered accountancy and financial management support division of Belvo Ventures Group, providing business accounting advisory, bookkeeping frameworks, and tax compliance assistance.",
                    "display_order": 3
                },
                {
                    "name": "Belqora",
                    "slug": "belqora",
                    "sector": "Software Solutions",
                    "one_line": "Software solutions for businesses.",
                    "description": "Belqora is the software engineering and digital transformation division of Belvo Ventures Group, engineering reliable cloud platforms, web applications, custom enterprise tools, and workflow automations.",
                    "display_order": 6
                },
                {
                    "name": "Klyro",
                    "slug": "klyro",
                    "sector": "Hardware Solutions",
                    "one_line": "Hardware solutions for businesses.",
                    "description": "Klyro is the hardware and embedded systems division of Belvo Ventures Group, helping commercial clients with tailored hardware integration, smart device prototypes, and technical infrastructure setups.",
                    "display_order": 7
                },
                {
                    "name": "Sahay",
                    "slug": "sahay",
                    "sector": "Social Impact / NGO",
                    "one_line": "Belvo's NGO division, working for social good.",
                    "description": "Sahay is the non-profit and community impact division of Belvo Ventures Group, spearheading educational outreach, grassroot youth upliftment, and skill development across India.",
                    "display_order": 9
                }
            ]
            for v_data in ventures_data:
                v = Venture(**v_data, status="Active", is_published=True)
                db.add(v)
            db.commit()

        # 3. Seed Founder (Hrishikesh - strictly only Hrishikesh as confirmed)
        existing_founder = db.query(Person).filter(Person.slug == "hrishikesh").first()
        if not existing_founder:
            print("Seeding Founder profile...")
            founder = Person(
                slug="hrishikesh",
                full_name="Hrishikesh",
                role="Founder",
                bio="Hrishikesh is the Founder of Belvo Ventures Group. Beginning with freelance advisory in February 2022 in Mumbai, he built an expansive ecosystem connecting founders, creative professionals, and students across 9 dedicated divisions in Mumbai, India.",
                linkedin_url="https://linkedin.com/company/belvoventures",
                consent_to_publish=True
            )
            db.add(founder)
            db.commit()

        # 3.1 Seed Confirmed Products & Services
        if db.query(ProductService).count() == 0:
            print("Seeding confirmed division offerings...")
            services_map = [
                ("belvo-digital", "Digital Marketing & Web Services", "Web, social media and digital marketing services to help businesses grow online.", ["Performance Marketing", "SEO & Organic Growth", "E-commerce Partnerships", "Social Media Design", "Brand Strategy & PR", "Influencer Marketing", "Web & App Development"]),
                ("capvanta", "Business Advisory & Funding", "Helping founders and businesses get the funds they need to grow.", ["Strategic Business Advisory", "Corporate Registration", "Legal & Equity Advisory", "Startup Valuation & Financial Modelling", "Due Diligence & Audit", "Co-founder Search & Leadership", "Fundraising Support", "Venture Partnerships"]),
                ("tatva", "Interior Design & Space Solutions", "Interior design and space solutions.", ["Residential Interiors", "Commercial Interiors", "Renovation", "Space Planning"]),
                ("hridayam", "Coaching & Personal Development", "Coaching to help people learn, grow and build confidence.", ["Career Courses", "Business & Entrepreneurship", "Accounting & Finance", "Graphic & Video Skills", "Personal Development", "Certifications"]),
                ("verdict", "Legal Services", "Legal support for founders and businesses.", ["Corporate & Startup Law", "IPR Services", "Business & Regulatory Support", "Contract Management Legal Support", "Litigation & Disputes", "HR & Employment Law", "Legal Tech Solutions"]),
                ("fyndra", "Finance & Accounting", "CA support to help businesses manage their accounts and finances.", ["Accounting & Bookkeeping", "Taxation Services", "Corporate Registration", "Financial Consulting", "Payroll & HR Financing", "Audit & Compliance", "Startup Finance", "Personal Finance"]),
                ("belqora", "Software Solutions", "Software solutions for businesses.", ["Custom Software Development", "Cloud Architecture", "Workflow Automation"]),
                ("klyro", "Digital Solutions", "Hardware solutions for businesses.", ["Attendo (Attendance Device)", "Clario Beat (Meeting Device)"]),
                ("sahay", "NGO & Social Impact", "Belvo's NGO division, working for social good.", ["Education for Underprivileged Children", "Community Welfare", "Social Impact Initiatives"]),
            ]
            for v_slug, s_name, s_desc, feats in services_map:
                vent = db.query(Venture).filter(Venture.slug == v_slug).first()
                if vent:
                    ps = ProductService(
                        slug=f"{v_slug}-services",
                        name=s_name,
                        venture_id=vent.id,
                        short_description=s_desc,
                        audience="Founders, businesses, and learners",
                        features=feats
                    )
                    db.add(ps)
            db.commit()

        # 4. Seed FAQs
        if db.query(FAQ).count() == 0:
            print("Seeding Core FAQs...")
            faqs = [
                ("What is Belvo Ventures Group?", "Belvo Ventures Group is a Mumbai-based group of ventures founded by Hrishikesh in 2022. Its nine ventures work across digital marketing, funding support, interiors, coaching, legal support, CA support, software, hardware solutions and social impact, all under one ecosystem."),
                ("When was Belvo Ventures Group founded?", "Belvo Ventures Group began on 14 February 2022 in Mumbai, India."),
                ("Who founded Belvo Ventures Group?", "Belvo Ventures Group was founded by Hrishikesh."),
                ("Where is Belvo Ventures Group based?", "Belvo Ventures Group is headquartered in Mumbai, India."),
                ("Are the 9 ventures separate companies?", "No. The nine ventures are specialized divisions of one company (Belvo Ventures Group), operating cohesively under one roof."),
                ("Does Belvo run an internship programme?", "Yes. Belvo runs structured internship batches for learners from across India. More than 500 interns are currently part of our ongoing cohorts, with new batches opening soon, and over 1,000 interns have been trained so far."),
                ("How large is the Belvo team?", "Belvo has approximately 50 team members across its operations and divisions in Mumbai, India."),
                ("What are the nine ventures under Belvo?", "The nine divisions are Belvo Digital, Capvanta, Tatva, Hridayam, Verdict, Fyndra, Belqora, Klyro, and Sahay."),
                ("How can businesses contact Belvo Ventures Group?", "Inquiries can be sent directly to our official group inbox at contact@belvoventures.com.")
            ]
            for idx, (q, a) in enumerate(faqs, start=1):
                f = FAQ(question=q, answer=a, page_scope="global", display_order=idx, is_published=True)
                db.add(f)
            db.commit()

        # 5. Seed External Profiles
        if db.query(ExternalProfile).count() == 0:
            print("Seeding External Profiles...")
            profiles = [
                ("LinkedIn", "https://www.linkedin.com/company/belvo.buzz/posts/"),
                ("Twitter/X", "https://x.com/belvoventures"),
                ("Instagram", "https://instagram.com/belvoventures")
            ]
            for platform, url in profiles:
                p = ExternalProfile(platform=platform, url=url)
                db.add(p)
            db.commit()

        # 6. Seed AI Platforms & Question Bank
        if db.query(AIPlatform).count() == 0:
            print("Seeding AI Platforms...")
            platforms = [
                ("ChatGPT", "api", "https://chatgpt.com"),
                ("Gemini", "api", "https://gemini.google.com"),
                ("Claude", "api", "https://claude.ai"),
                ("Copilot", "manual", "https://copilot.microsoft.com"),
                ("Perplexity", "api", "https://perplexity.ai")
            ]
            for name, method, url in platforms:
                plat = AIPlatform(name=name, access_method=method, website_url=url)
                db.add(plat)
            db.commit()

        if db.query(AIQuestion).count() == 0:
            print("Seeding AI Visibility Question Bank...")
            questions = [
                ("What is Belvo Ventures Group?", "General Overview", ["Mumbai-based group of ventures", "founded 2022", "nine ventures"]),
                ("Who founded Belvo Ventures Group?", "Leadership", ["Hrishikesh"]),
                ("When was Belvo Ventures Group founded?", "Founding History", ["2022", "14 February 2022"]),
                ("Where is Belvo Ventures Group based?", "Location", ["Mumbai", "India"]),
                ("What ventures does Belvo have?", "Ventures Scope", ["Belvo Digital", "Capvanta", "Tatva", "Hridayam", "Verdict", "Fyndra", "Belqora", "Klyro", "Sahay"]),
                ("What does Belvo Digital do?", "Ventures Scope", ["Web", "social media", "digital marketing"]),
                ("What is Capvanta?", "Ventures Scope", ["Belvo division", "funds", "grow"]),
                ("What is Sahay?", "Ventures Scope", ["Belvo's NGO division", "social good"]),
                ("Does Belvo run internships?", "Internship Programme", ["structured internship batches", "1,000+ interns trained", "India"]),
                ("How big is the Belvo team?", "Team Scale", ["50 team members"]),
                ("What is Tatva in Belvo Ventures Group?", "Ventures Scope", ["interior design", "space solutions"]),
                ("What is Hridayam in Belvo Ventures Group?", "Ventures Scope", ["coaching", "build confidence"]),
                ("What is Verdict in Belvo Ventures Group?", "Ventures Scope", ["legal support", "founders and businesses"]),
                ("What is Fyndra in Belvo Ventures Group?", "Ventures Scope", ["CA support", "accounts and finances"]),
                ("What is Belqora in Belvo Ventures Group?", "Ventures Scope", ["software solutions", "businesses"]),
                ("What is Klyro in Belvo Ventures Group?", "Ventures Scope", ["hardware solutions", "businesses"])
            ]
            for q_text, cat, facts in questions:
                q = AIQuestion(question_text=q_text, category=cat, expected_facts=facts, is_active=True)
                db.add(q)
            db.commit()

        # 7. Seed Admin User
        admin_user = db.query(User).filter(User.email == "admin@belvoventures.com").first()
        if not admin_user:
            print("Seeding default Administrator user...")
            admin = User(
                name="Belvo Admin",
                email="admin@belvoventures.com",
                hashed_password=hash_password("BelvoAdmin2026!"),
                role="admin"
            )
            db.add(admin)
            db.commit()

        print("Database seeding completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
