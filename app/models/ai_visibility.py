from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class AIPlatform(Base):
    __tablename__ = "ai_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # ChatGPT, Gemini, Claude, Copilot, Perplexity
    access_method = Column(String(50), default="api") # api, manual
    website_url = Column(String(255), nullable=True)
    
    runs = relationship("AIRun", back_populates="platform")

class AIQuestion(Base):
    __tablename__ = "ai_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(500), nullable=False)
    category = Column(String(100), default="General Overview") # Overview, Leadership, Ventures, Internships
    expected_facts = Column(JSON, nullable=False) # List of exact fact strings that must be in the answer
    is_active = Column(Boolean, default=True)
    
    runs = relationship("AIRun", back_populates="question")

class AIRun(Base):
    __tablename__ = "ai_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("ai_questions.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(Integer, ForeignKey("ai_platforms.id", ondelete="CASCADE"), nullable=False)
    run_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    model_or_version = Column(String(100), nullable=True) # e.g. "GPT-4o", "Claude 3.5 Sonnet", "Gemini 1.5 Pro"
    answer_text = Column(Text, nullable=False)
    score = Column(Integer, nullable=False, default=0) # 0 = wrong/missing, 1 = partly correct/incomplete, 2 = fully correct
    checker = Column(String(100), default="Automated Rule") # Automated Rule or Reviewer Name
    notes = Column(Text, nullable=True)
    
    question = relationship("AIQuestion", back_populates="runs")
    platform = relationship("AIPlatform", back_populates="runs")
