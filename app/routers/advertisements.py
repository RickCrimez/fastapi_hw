from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, schemas, dependencies, models
from app.database import get_db

router = APIRouter(prefix="/advertisement", tags=["advertisements"])


def enrich_advertisement_with_author(ad, author_name: str) -> schemas.AdvertisementResponse:
    """Преобразует ORM объект в Pydantic схему с именем автора"""
    return schemas.AdvertisementResponse(
        id=ad.id,
        title=ad.title,
        description=ad.description,
        price=ad.price,
        author_id=ad.author_id,
        author_name=author_name,
        created_at=ad.created_at
    )


@router.post("/", response_model=schemas.AdvertisementResponse, status_code=status.HTTP_201_CREATED)
def create_advertisement(
        advertisement: schemas.AdvertisementCreate,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_active_user)
):
    """
    Создание объявления

    Требует авторизации
    """
    db_ad = crud.create_advertisement(db, advertisement, current_user.id)
    return enrich_advertisement_with_author(db_ad, current_user.username)


@router.patch("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def update_advertisement(
        advertisement_id: int,
        advertisement_update: schemas.AdvertisementUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_active_user)
):
    """
    Обновление объявления

    Требует авторизации
    - Пользователь может обновлять только свои объявления
    - Администратор может обновлять любые объявления
    """
    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.role != models.UserRole.ADMIN and current_user.id != db_ad.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this advertisement"
        )

    if advertisement_update.price is not None and advertisement_update.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")

    updated_ad = crud.update_advertisement(db, advertisement_id, advertisement_update)
    author_name = db_ad.author_rel.username
    return enrich_advertisement_with_author(updated_ad, author_name)


@router.delete("/{advertisement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_advertisement(
        advertisement_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_active_user)
):
    """
    Удаление объявления

    Требует авторизации
    - Пользователь может удалять только свои объявления
    - Администратор может удалять любые объявления
    """
    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.role != models.UserRole.ADMIN and current_user.id != db_ad.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this advertisement"
        )

    crud.delete_advertisement(db, advertisement_id)
    return


@router.get("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def get_advertisement(
        advertisement_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_user)
):
    """
    Получение объявления по ID

    Доступно всем (не требует авторизации)
    """
    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    author_name = db_ad.author_rel.username
    return enrich_advertisement_with_author(db_ad, author_name)


@router.get("/", response_model=schemas.PaginatedAdvertisementResponse)
def search_advertisements(
        title: Optional[str] = Query(None, description="Поиск по заголовку"),
        author_name: Optional[str] = Query(None, description="Поиск по имени автора"),
        min_price: Optional[float] = Query(None, gt=0, description="Минимальная цена"),
        max_price: Optional[float] = Query(None, gt=0, description="Максимальная цена"),
        limit: int = Query(20, ge=1, le=100, description="Элементов на странице"),
        offset: int = Query(0, ge=0, description="Смещение"),
        db: Session = Depends(get_db),
        current_user=Depends(dependencies.get_current_user)
):
    """
    Поиск объявлений с фильтрацией и пагинацией

    Доступно всем (не требует авторизации)
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price"
        )

    result = crud.search_advertisements(
        db, title, author_name, min_price, max_price, limit, offset
    )

    items = [
        enrich_advertisement_with_author(ad, ad.author_rel.username)
        for ad in result["items"]
    ]

    return schemas.PaginatedAdvertisementResponse(
        items=items,
        pagination=schemas.PaginationMetadata(
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_next=result["has_next"],
            has_previous=result["has_previous"]
        )
    )