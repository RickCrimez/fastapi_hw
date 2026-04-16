from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/advertisement", tags=["advertisements"])


@router.post(
    "/",
    response_model=schemas.AdvertisementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать объявление",
    description="Создает новое объявление с указанными заголовком, описанием, ценой и автором"
)
def create_advertisement(
        advertisement: schemas.AdvertisementCreate,
        db: Session = Depends(get_db)
):

    return crud.create_advertisement(db, advertisement)


@router.patch(
    "/{advertisement_id}",
    response_model=schemas.AdvertisementResponse,
    summary="Обновить объявление",
    description="Обновляет существующее объявление по ID"
)
def update_advertisement(
        advertisement_id: int,
        advertisement_update: schemas.AdvertisementUpdate,
        db: Session = Depends(get_db)
):
    """
    Обновление объявления

    - **advertisement_id**: ID объявления для обновления
    - Можно обновить любое из полей: title, description, price, author
    """

    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advertisement with id {advertisement_id} not found"
        )


    if advertisement_update.price is not None and advertisement_update.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )

    updated_ad = crud.update_advertisement(db, advertisement_id, advertisement_update)
    return updated_ad


@router.delete(
    "/{advertisement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить объявление",
    description="Удаляет объявление по ID. Возвращает пустой ответ при успехе."
)
def delete_advertisement(
        advertisement_id: int,
        db: Session = Depends(get_db)
):

    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advertisement with id {advertisement_id} not found"
        )

    crud.delete_advertisement(db, advertisement_id)


@router.get(
    "/{advertisement_id}",
    response_model=schemas.AdvertisementResponse,
    summary="Получить объявление по ID",
    description="Возвращает объявление с указанным ID"
)
def get_advertisement(
        advertisement_id: int,
        db: Session = Depends(get_db)
):

    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advertisement with id {advertisement_id} not found"
        )
    return db_ad


@router.get(
    "/",
    response_model=schemas.PaginatedAdvertisementResponse,
    summary="Поиск объявлений",
    description="Поиск объявлений с фильтрацией по полям и пагинацией"
)
def search_advertisements(
        title: Optional[str] = Query(None, description="Поиск по заголовку (частичное совпадение)"),
        author: Optional[str] = Query(None, description="Поиск по автору (частичное совпадение)"),
        min_price: Optional[float] = Query(None, gt=0, description="Минимальная цена"),
        max_price: Optional[float] = Query(None, gt=0, description="Максимальная цена"),
        limit: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
        offset: int = Query(0, ge=0, description="Смещение для пагинации"),
        db: Session = Depends(get_db)
):

    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price"
        )

    result = crud.search_advertisements(
        db, title, author, min_price, max_price, limit, offset
    )

    return schemas.PaginatedAdvertisementResponse(
        items=result["items"],
        pagination=schemas.PaginationMetadata(
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_next=result["has_next"],
            has_previous=result["has_previous"]
        )
    )