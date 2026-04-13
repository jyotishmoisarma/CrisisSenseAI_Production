from sqlalchemy import Column, String
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True,index=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    password = Column(String)
    emergency_contact = Column(String)
    blood_group = Column(String, nullable=True)
    medical_notes = Column(String, nullable=True)