from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    emergency_contact: str
    blood_group: str |None = None
    medical_notes: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str