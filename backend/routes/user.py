from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from database.db import SessionLocal
from database.crud import create_user, get_user_by_email, get_user_by_id, update_user
from auth import hash_password, verify_password
from schemas.request_models import SignupRequest, LoginRequest, UpdateProfileRequest

router = APIRouter(prefix="/users", tags=["User Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def user_signup(data: SignupRequest, db: Session = Depends(get_db)):
    """
    Registers a new user and hashes their password.
    """
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="A user with this email already exists.")
    
    # Hash the password before storage
    data.password = hash_password(data.password)
    
    try:
        new_user = create_user(db, data)
        return {
            "message": "Registration successful", 
            "user_id": new_user.id,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error during signup: {str(e)}")

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # This line will crash with a 500 error if you haven't deleted the .db file
    if not getattr(user, 'is_active', True):
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    return {"user_id": user.id, "name": user.name}

@router.get("/profile/{user_id}")
def get_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the full medical and personal profile of a user.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found.")
    
    return {
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "emergency_contact": user.emergency_contact,
        "blood_group": user.blood_group,
        "medical_notes": user.medical_notes,
        "allow_location_tracking": user.allow_location_tracking
    }

@router.put("/profile/{user_id}")
def update_profile_data(user_id: str, data: UpdateProfileRequest, db: Session = Depends(get_db)):
    """
    Feature 6: Edit Profile logic.
    Updates specific fields in the user's medical or personal profile.
    Uses exclude_unset to ensure existing data is not overwritten by nulls.
    """
    # Convert Pydantic model to dict, keeping only values actually sent by user
    update_dict = data.model_dump(exclude_unset=True)
    
    if not update_dict:
        return {"message": "No changes requested.", "success": True}

    updated_user = update_user(db, user_id, update_dict)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {
        "message": "Profile updated successfully.", 
        "success": True,
        "updated_fields": list(update_dict.keys())
    }
