from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.crud import create_user, get_user_by_email, get_user_by_id
from auth import hash_password, verify_password
from schemas.request_models import SignupRequest, LoginRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(data.password)
    data.password = hashed_password
    create_user(db, data)

    return {"message": "User created"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return {"user_id": user.id, "name": user.name}


@router.get("/profile/{user_id}")
def profile(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)

    return {
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "emergency_contact": user.emergency_contact
    }