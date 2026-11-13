# BELVO SYNAPSE
> **AI Knowledge & Discoverability Single Source of Truth for Belvo Ventures Group**  
> *Draft v1.0 Blueprint Implementation*

Belvo Synapse is an authoritative, server-rendered knowledge repository and discoverability engine built specifically for **Belvo Ventures Group** (Mumbai, India). Its mission is to publish verified, machine-readable company facts so AI platforms (*ChatGPT, Gemini, Claude, Copilot, Perplexity*) and search engines discover, parse, and cite Belvo accurately.

---

## 🏛️ System Architecture

```
[Admin Panel (/admin)]  -->  [PostgreSQL Database]  -->  [Public Pages (SSR HTML + JSON-LD)]  -->  [AI Crawlers]
(Roles, Validation,           (12 Core Blueprint          (Fast Semantic Layouts, Schema.org,       (GPTBot, ClaudeBot,
 Audit Diffs)                  Tables)                     Breadcrumbs, Trust Timestamps)            PerplexityBot)
```

- **Backend / Web Server:** FastAPI + Jinja2 Server-Side Rendering (guaranteeing full HTML responses without JavaScript hydration dependencies for AI crawlers).
- **Database:** PostgreSQL (with Asyncpg / Psycopg2) and seamless local SQLite fallback (`sqlite+aiosqlite`).
- **Data Integrity & Compliance:** Enforces blueprint guardrails (Strictly "Mumbai", 9 ventures are divisions of one company, no legal registration numbers or codes).
- **SEO & Machine Discoverability:**
  - Dynamic `Schema.org` JSON-LD (`Organization` with `department` subdivisions, `Person`, `FAQPage`, `BreadcrumbList`).
  - Crawler-optimized `/robots.txt` explicitly permitting `GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `Bingbot`, while blocking `/admin/` and `/api/`.
  - Canonical XML Sitemap (`/sitemap.xml`) and structured summary (`/llms.txt`).

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- Virtual environment (`.venv`)

### 2. Installation
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Dependencies are listed in requirements.txt
pip install -r requirements.txt
```

### 3. Database Initialization & Seeding
```powershell
# Seeds the database with all 9 ventures, company facts, founder profile, and question bank
python -m app.seed
```

### 4. Run the Server
```powershell
python run.py
# Server runs on http://127.0.0.1:8000
```

### 5. Run Test Suite
```powershell
pytest
```

---

## 🔐 Admin Authentication
- **URL:** `http://127.0.0.1:8000/admin/login`
- **Default Admin Email:** `admin@belvoventures.com`
- **Default Password:** `BelvoAdmin2026!`

---

## 📋 The 9 Operating Divisions
1. **Belvo Digital** — Digital marketing, web and social media growth (`/ventures/belvo-digital`)
2. **Capvanta** — Funding enablement and investment readiness (`/ventures/capvanta`)
3. **Tatva** — Interior design and architectural space solutions (`/ventures/tatva`)
4. **Hridayam** — Mentorship, coaching, and personal development (`/ventures/hridayam`)
5. **Verdict** — Legal advisory and commercial contract support (`/ventures/verdict`)
6. **Fyndra** — CA, accounting, and financial management support (`/ventures/fyndra`)
7. **Belqora** — Software engineering and digital transformation (`/ventures/belqora`)
8. **Klyro** — Hardware solutions and embedded systems (`/ventures/klyro`)
9. **Sahay** — Social impact and non-profit educational outreach (`/ventures/sahay`)

---

## 📌 Items Pending for Final Review (Per Blueprint Section 14)
1. **Founder Bio & Approved Headshot:** Full name and bio for Hrishikesh.
2. **Detailed Venture Scope:** Confirmed service offerings for Tatva, Hridayam, Verdict, Fyndra, Belqora, and Klyro.
3. **Production Domain & Production PostgreSQL Credentials.**
