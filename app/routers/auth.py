from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, auth
from app.database import get_db

router = APIRouter(prefix="/login", tags=["authentication"])


@router.post("/", response_model=schemas.TokenResponse)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя и получение токена

    - **username**: Имя пользователя
    - **password**: Пароль

    Возвращает токен, действителен 48 часов
    """
    user = crud.get_user_by_username(db, user_login.username)

    if not user or not auth.verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return schemas.TokenResponse(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        role=user.role
    )