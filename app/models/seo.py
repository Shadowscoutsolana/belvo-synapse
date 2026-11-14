from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from datetime import datetime, timezone
from app.database import Base

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=False) # Blueprint requirement: alt-text mandatory
    type = Column(String(50), default="image") # image, logo, svg, doc
    credit = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PageSEO(Base):
    __tablename__ = "pages_seo"
    
    id = Column(Integer, primary_key=True, index=True)
    page_slug = Column(String(100), unique=True, index=True, nullable=False) # e.g. "home", "about", "ventures", "ventures/belvo-digital"
    seo_title = Column(String(200), nullable=False)
    meta_description = Column(String(320), nullable=False)
    canonical_url = Column(String(500), nullable=True)
    og_image_id = Column(Integer, ForeignKey("media.id", ondelete="SET NULL"), nullable=True)
    schema_json = Column(JSON, nullable=True) # Custom Schema.org overrides if any
    last_verified_at = Column(String(50), nullable=False, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    verified_by = Column(String(100), nullable=False, default="Hrishikesh (Founder)")
    status = Column(String(50), default="published") # draft, in_review, published

class ExternalProfile(Base):
    __tablename__ = "external_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(100), nullable=False) # LinkedIn, Twitter/X, Crunchbase, Instagram, etc.
    url = Column(String(500), nullable=False)
