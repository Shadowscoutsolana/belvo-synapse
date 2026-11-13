from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(100), nullable=False, default="Belvo Ventures Group")
    tagline = Column(String(200), default="Innovate · Build · Grow")
    sub_line = Column(String(200), default="By a founder, for the founders.")
    one_line_definition = Column(Text, nullable=False)
    short_description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=False)
    founded_date = Column(String(20), nullable=False, default="2022-02-14")
    city = Column(String(100), nullable=False, default="Mumbai")
    country = Column(String(100), nullable=False, default="India")
    team_size = Column(Integer, default=50)
    interns_trained = Column(Integer, default=1000)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    contact_email = Column(String(150), nullable=False, default="contact@belvoventures.com")
    logo_id = Column(Integer, ForeignKey("media.id", ondelete="SET NULL"), nullable=True)

class Venture(Base):
    __tablename__ = "ventures"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    one_line = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    sector = Column(String(100), nullable=False)
    launch_year = Column(Integer, nullable=True)
    status = Column(String(50), default="Active")
    website_url = Column(String(255), nullable=True)
    logo_id = Column(Integer, ForeignKey("media.id", ondelete="SET NULL"), nullable=True)
    display_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    
    products_services = relationship("ProductService", back_populates="venture", cascade="all, delete-orphan")
    people = relationship("Person", back_populates="venture")
    achievements = relationship("Achievement", back_populates="venture")

class Person(Base):
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(100), nullable=False)
    venture_id = Column(Integer, ForeignKey("ventures.id", ondelete="SET NULL"), nullable=True)
    bio = Column(Text, nullable=True)
    photo_id = Column(Integer, ForeignKey("media.id", ondelete="SET NULL"), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    consent_to_publish = Column(Boolean, default=True)
    
    venture = relationship("Venture", back_populates="people")
    achievements = relationship("Achievement", back_populates="person")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False) # award, partnership, launch, press, event
    description = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    venture_id = Column(Integer, ForeignKey("ventures.id", ondelete="SET NULL"), nullable=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="SET NULL"), nullable=True)
    
    venture = relationship("Venture", back_populates="achievements")
    person = relationship("Person", back_populates="achievements")

class ProductService(Base):
    __tablename__ = "products_services"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    venture_id = Column(Integer, ForeignKey("ventures.id", ondelete="CASCADE"), nullable=False)
    short_description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)
    audience = Column(String(255), nullable=True)
    features = Column(JSON, nullable=True) # List of feature strings
    link = Column(String(255), nullable=True)
    
    venture = relationship("Venture", back_populates="products_services")

class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(300), nullable=False)
    answer = Column(Text, nullable=False)
    page_scope = Column(String(100), default="global") # global, home, ventures, or specific slug
    display_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
