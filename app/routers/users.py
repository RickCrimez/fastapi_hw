from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app import crud, schemas, dependencies, models
from app.database import get_db

router = APIRouter(prefix="/user", tags=["users"])


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя

    Доступно всем (не требует авторизации)
    """
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db, user)


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_user)
):
    """
    Получение информации о пользователе по ID

    Доступно всем (не требует авторизации)
    Но:
    - Неавторизованные пользователи не видят админов
    - Обычные пользователи не видят админов
    - Администраторы видят всех
    """
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка прав доступа к просмотру админов
    if user.role == models.UserRole.ADMIN:
        if not current_user or current_user.role != models.UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: admin profile is private"
            )

    return user


@router.get("/", response_model=List[schemas.UserResponse])
def get_all_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_active_user)
):
    """
    Получение списка всех пользователей

    Требует авторизации
    - Обычные пользователи видят только не-админов
    - Администраторы видят всех
    """
    if current_user.role != models.UserRole.ADMIN:
        users = db.query(models.User).filter(
            models.User.role != models.UserRole.ADMIN
        ).offset(skip).limit(limit).all()
    else:
        users = crud.get_all_users(db, skip, limit)

    return users


@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user(
        user_id: int,
        user_update: schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_active_user)
):
    """
    Обновление данных пользователя

    Требует авторизации
    - Пользователь может обновлять только свои данные
    - Администратор может обновлять любые данные
    """
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    if user_update.username:
        existing = crud.get_user_by_username(db, user_update.username)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken")

    if user_update.email:
        existing = crud.get_user_by_email(db, user_update.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    updated_user = crud.update_user(db, user_id, user_update)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_active_user)
):
    """
    Удаление пользователя

    Требует авторизации
    - Пользователь может удалять только свой аккаунт
    - Администратор может удалять любые аккаунты
    """
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profile"
        )

    crud.delete_user(db, user_id)
    return