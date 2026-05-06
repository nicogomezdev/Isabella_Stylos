from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models.users import UserRole

# how is a user?
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# how should return the user to frontend?
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token:str
    token_type: str = "bearer"
    user: UserResponse