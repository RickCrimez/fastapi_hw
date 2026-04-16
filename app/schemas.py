from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Any


# Схемы для объявлений
class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Заголовок объявления")
    description: str = Field(..., min_length=1, max_length=5000, description="Описание объявления")
    price: float = Field(..., gt=0, description="Цена (должна быть больше 0)")
    author: str = Field(..., min_length=1, max_length=100, description="Автор объявления")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Заголовок не может быть пустым или состоять только из пробелов')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Описание не может быть пустым или состоять только из пробелов')
        return v.strip()

    @field_validator('author')
    @classmethod
    def validate_author(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Имя автора не может быть пустым или состоять только из пробелов')
        return v.strip()


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Заголовок объявления")
    description: Optional[str] = Field(None, min_length=1, max_length=5000, description="Описание объявления")
    price: Optional[float] = Field(None, gt=0, description="Цена (должна быть больше 0)")
    author: Optional[str] = Field(None, min_length=1, max_length=100, description="Автор объявления")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Заголовок не может быть пустым или состоять только из пробелов')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Описание не может быть пустым или состоять только из пробелов')
        return v.strip() if v else v

    @field_validator('author')
    @classmethod
    def validate_author(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Имя автора не может быть пустым или состоять только из пробелов')
        return v.strip() if v else v


class AdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author: str
    created_at: datetime

    class Config:
        from_attributes = True  # Для Pydantic v2


# Пагинация
class PaginationParams(BaseModel):
    limit: int = Field(20, ge=1, le=100, description="Количество элементов на странице")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")


class PaginationMetadata(BaseModel):
    total: int = Field(..., description="Общее количество элементов")
    limit: int = Field(..., description="Лимит на странице")
    offset: int = Field(..., description="Смещение")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_previous: bool = Field(..., description="Есть ли предыдущая страница")


class PaginatedAdvertisementResponse(BaseModel):
    items: List[AdvertisementResponse] = Field(..., description="Список объявлений")
    pagination: PaginationMetadata = Field(..., description="Метаданные пагинации")