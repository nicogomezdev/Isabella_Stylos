from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_acces_token
from app.models.users import User, UserRole

bearer_scheme = HTTPBearer()

def get_current_user (
        credentials:HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
        ) -> User:
    token = credentials.credentials
    payload = decode_acces_token(token)

    if not payload:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token invalido o expirado"
        )
    
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Usuario no encontrado"
        )
    return user

def require_admin(current_user: User= Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes privilegios suficientes para está acción"
        )
    return current_user