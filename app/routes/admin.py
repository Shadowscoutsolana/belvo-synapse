from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional

from app.database import get_db
from app.models.company import Company, Venture, FAQ
from app.models.users import User, AuditLog
from app.models.ai_visibility import AIPlatform, AIQuestion, AIRun
from app.services.auth import verify_password, create_access_token, decode_access_token
from app.services.consistency import ConsistencyValidator
from app.services.audit import AuditService
from app.services.ai_evaluator import AIEvaluator

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

router = APIRouter(prefix="/admin")

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("belvo_admin_session")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    return db.query(User).filter(User.email == email).first()

# Login / Logout
@router.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"error": None}
    )

@router.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={"error": "Invalid email or credentials."}
        )
        
    token = create_access_token({"sub": user.email, "role": user.role})
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(key="belvo_admin_session", value=token, httponly=True, max_age=86400 * 7)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("belvo_admin_session")
    return response

# Admin Dashboard
@router.get("/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    ventures_count = db.query(Venture).count()
    questions_count = db.query(AIQuestion).count()
    ventures = db.query(Venture).order_by(Venture.display_order).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "current_user": user,
            "ventures_count": ventures_count,
            "questions_count": questions_count,
            "ventures": ventures
        }
    )

# Company Edit
@router.get("/company")
def company_edit_get(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    company = db.query(Company).first()

    return templates.TemplateResponse(
        request=request,
        name="admin/company_edit.html",
        context={
            "current_user": user,
            "company": company,
            "warnings": [],
            "success": False
        }
    )

@router.post("/company")
def company_edit_post(
    request: Request,
    brand_name: str = Form(...),
    founded_date: str = Form(...),
    city: str = Form(...),
    country: str = Form(...),
    tagline: str = Form(...),
    sub_line: str = Form(...),
    team_size: int = Form(...),
    interns_trained: int = Form(...),
    one_line_definition: str = Form(...),
    long_description: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    combined_text = f"{brand_name} {city} {one_line_definition} {long_description}"
    warnings = ConsistencyValidator.validate_text(combined_text)

    company = db.query(Company).first()
    
    before_state = {
        "brand_name": company.brand_name,
        "founded_date": company.founded_date,
        "city": company.city,
        "team_size": company.team_size,
        "interns_trained": company.interns_trained,
        "one_line_definition": company.one_line_definition
    }

    company.brand_name = brand_name
    company.founded_date = founded_date
    company.city = city
    company.country = country
    company.tagline = tagline
    company.sub_line = sub_line
    company.team_size = team_size
    company.interns_trained = interns_trained
    company.one_line_definition = one_line_definition
    company.long_description = long_description

    after_state = {
        "brand_name": brand_name,
        "founded_date": founded_date,
        "city": city,
        "team_size": team_size,
        "interns_trained": interns_trained,
        "one_line_definition": one_line_definition
    }

    db.commit()

    AuditService.log_action(
        db=db,
        user_id=user.id,
        table_name="company",
        record_id=company.id,
        action="UPDATE",
        before=before_state,
        after=after_state
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/company_edit.html",
        context={
            "current_user": user,
            "company": company,
            "warnings": warnings,
            "success": True
        }
    )

# Ventures List
@router.get("/ventures")
def ventures_list_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    ventures = db.query(Venture).order_by(Venture.display_order).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/ventures_list.html",
        context={
            "current_user": user,
            "ventures": ventures
        }
    )

# Venture Edit
@router.get("/ventures/edit/{v_id}")
def venture_edit_get(v_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    venture = db.query(Venture).filter(Venture.id == v_id).first()
    if not venture:
        raise HTTPException(status_code=404, detail="Venture not found")

    return templates.TemplateResponse(
        request=request,
        name="admin/venture_edit.html",
        context={
            "current_user": user,
            "venture": venture,
            "warnings": [],
            "success": False
        }
    )

@router.post("/ventures/edit/{v_id}")
def venture_edit_post(
    v_id: int,
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    sector: str = Form(...),
    one_line: str = Form(...),
    description: str = Form(...),
    display_order: int = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    venture = db.query(Venture).filter(Venture.id == v_id).first()
    if not venture:
        raise HTTPException(status_code=404, detail="Venture not found")

    combined_text = f"{name} {sector} {one_line} {description}"
    warnings = ConsistencyValidator.validate_text(combined_text)

    before_state = {
        "name": venture.name,
        "sector": venture.sector,
        "one_line": venture.one_line,
        "description": venture.description,
        "display_order": venture.display_order
    }

    venture.name = name
    venture.slug = slug
    venture.sector = sector
    venture.one_line = one_line
    venture.description = description
    venture.display_order = display_order

    after_state = {
        "name": name,
        "sector": sector,
        "one_line": one_line,
        "description": description,
        "display_order": display_order
    }

    db.commit()

    AuditService.log_action(
        db=db,
        user_id=user.id,
        table_name="ventures",
        record_id=venture.id,
        action="UPDATE",
        before=before_state,
        after=after_state
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/venture_edit.html",
        context={
            "current_user": user,
            "venture": venture,
            "warnings": warnings,
            "success": True
        }
    )

# AI Visibility Dashboard
@router.get("/ai-visibility")
def ai_visibility_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    platforms = db.query(AIPlatform).all()
    questions = db.query(AIQuestion).filter(AIQuestion.is_active == True).all()

    platform_stats = []
    for p in platforms:
        runs = db.query(AIRun).filter(AIRun.platform_id == p.id).all()
        avg_score = (sum(r.score for r in runs) / len(runs)) if runs else None
        platform_stats.append({
            "id": p.id,
            "name": p.name,
            "access_method": p.access_method,
            "avg_score": avg_score,
            "runs_count": len(runs)
        })

    recent_runs = db.query(AIRun).order_by(AIRun.run_date.desc()).limit(15).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/ai_visibility.html",
        context={
            "current_user": user,
            "platforms": platform_stats,
            "questions": questions,
            "recent_runs": recent_runs
        }
    )

@router.post("/ai-visibility/run")
def ai_visibility_record_run(
    request: Request,
    question_id: int = Form(...),
    platform_id: int = Form(...),
    model_or_version: Optional[str] = Form(None),
    answer_text: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    question = db.query(AIQuestion).filter(AIQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    score, notes = AIEvaluator.score_response(question.expected_facts, answer_text)

    new_run = AIRun(
        question_id=question_id,
        platform_id=platform_id,
        model_or_version=model_or_version or "Benchmark Model",
        answer_text=answer_text,
        score=score,
        checker=user.name,
        notes=notes
    )
    db.add(new_run)
    db.commit()

    return RedirectResponse(url="/admin/ai-visibility", status_code=303)

# One-Click Offline Demo Seeder
@router.post("/ai-visibility/demo-seed")
@router.get("/ai-visibility/demo-seed")
def ai_visibility_demo_seed(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    platforms = {p.name: p.id for p in db.query(AIPlatform).all()}
    questions = {q.question_text: q for q in db.query(AIQuestion).all()}

    demo_data = [
        ("What is Belvo Ventures Group?", "ChatGPT", "GPT-4o", "Belvo Ventures Group is a Mumbai-based group of ventures founded in 2022 with nine ventures working under one roof."),
        ("Who founded Belvo Ventures Group?", "Gemini", "Gemini 1.5 Flash", "Belvo Ventures Group was founded by Hrishikesh in Mumbai, India."),
        ("Does Belvo run internships?", "Claude", "Claude 3.5 Sonnet", "Yes, Belvo runs structured internship batches across India with over 1,000 interns trained so far."),
        ("What ventures does Belvo have?", "Copilot", "Copilot Web", "Belvo has nine ventures: Belvo Digital, Capvanta, Tatva, Hridayam, Verdict, Fyndra, Belqora, Klyro, and Sahay."),
        ("What does Belvo Digital do?", "Perplexity", "Perplexity Sonar", "Belvo Digital is a division of Belvo Ventures Group offering web, social media and digital marketing services to help businesses grow online.")
    ]

    for q_text, plat_name, model_ver, ans_text in demo_data:
        if q_text in questions and plat_name in platforms:
            q_obj = questions[q_text]
            plat_id = platforms[plat_name]
            score, notes = AIEvaluator.score_response(q_obj.expected_facts, ans_text)
            run = AIRun(
                question_id=q_obj.id,
                platform_id=plat_id,
                model_or_version=model_ver,
                answer_text=ans_text,
                score=score,
                checker=f"{user.name} (Offline Baseline)",
                notes=notes
            )
            db.add(run)

    db.commit()
    return RedirectResponse(url="/admin/ai-visibility", status_code=303)

# Audit Logs
@router.get("/audit-logs")
def audit_logs_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/audit_logs.html",
        context={
            "current_user": user,
            "logs": logs
        }
    )
