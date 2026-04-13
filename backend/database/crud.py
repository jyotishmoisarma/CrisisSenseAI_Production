from sqlalchemy.orm import Session
from models.user_model import User
import uuid

def create_user(db: Session, data):
    user = User(
        id=str(uuid.uuid4()),
        name=data.name,
        email=data.email,
        phone=data.phone,
        password=data.password,
        emergency_contact=data.emergency_contact,
        blood_group=data.blood_group,
        medical_notes=data.medical_notes,
        is_active=True,
        profile_completed=False,
        allow_location_tracking=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: str, update_data: dict):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in update_data.items():
        # Only update if the value is provided (not null)
        if value is not None:
            setattr(user, key, value)
            
    db.commit()
    db.refresh(user)
    return user