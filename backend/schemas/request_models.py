from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SignupRequest(BaseModel):
    """
    Schema for new user registration.
    """
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    password: str = Field(..., min_length=8)
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    medical_notes: Optional[str] = None

class LoginRequest(BaseModel):
    """
    Schema for user authentication.
    """
    email: EmailStr
    password: str

class UpdateProfileRequest(BaseModel):
    """
    Schema for the Profile Editing feature.
    Allows partial updates to user information without requiring all fields.
    """
    name: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    medical_notes: Optional[str] = None
    allow_location_tracking: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+1234567890",
                "blood_group": "O+",
                "medical_notes": "Allergic to penicillin",
                "allow_location_tracking": True
            }
        }