from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_acces_token
from fastapi import HTTPException, status

def register_user(db:Session, data: UserRegister) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Este email ya está registrado"
        )
    
    user = User(
        name = data.name,
        email = data.email,
        password_hash = hash_password(data.password),
        phone= data.phone,

    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db:Session, email: str, password:str) -> dict:
    user= db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciales inválidas"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    token = create_acces_token(data={"sub":str(user.id), "role":user.role})
    return {"acces_token":token, "token_type": "bearer", "user": user}