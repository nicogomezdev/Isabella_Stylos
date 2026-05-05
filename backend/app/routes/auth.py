from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import register_user, login_user
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session= Depends(get_db)):
    user = register_user(db, data)
    token = login_user(db, data.email, data.password)
    return token

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session= Depends(get_db)):
    return login_user(db,data.email, data.password)

@router.post("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user