from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import crud, auth
from app.models import UserRole

security = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
):
    """Получение текущего пользователя из токена"""
    if credentials is None:
        return None

    token = credentials.credentials
    payload = auth.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud.get_user_by_id(db, payload["user_id"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    """Получение текущего пользователя"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def check_ownership_or_admin(resource_user_id: int, current_user, message: str = "Access denied"):
    """Проверка прав: админ или владелец ресурса"""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if current_user.role == UserRole.ADMIN or current_user.id == resource_user_id:
        return True

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def check_advertisement_ownership(advertisement, current_user):
    """Проверка прав на объявление"""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if current_user.role == UserRole.ADMIN or current_user.id == advertisement.author_id:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to modify this advertisement"
    )