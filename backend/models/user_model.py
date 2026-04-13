from sqlalchemy import Column, String, Boolean, Text
from database.db import Base

class User(Base):
    """
    SQLAlchemy model representing the 'users' table.
    This is the core data structure for CrisisSenseAI, storing both 
    authentication data and sensitive emergency medical profiles.
    """
    __tablename__ = "users"

    # Authentication & Identification
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    
    # Emergency & Medical Fields (Can be updated via Profile Edit)
    # These fields are critical for the Triage AI's decision-making process.
    emergency_contact = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    medical_notes = Column(Text, nullable=True)
    
    # System Logic & User Preferences
    allow_location_tracking = Column(Boolean, default=False)
    profile_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', blood_group='{self.blood_group}')>"