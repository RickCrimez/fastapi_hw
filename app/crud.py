from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from typing import Optional, Dict, Any


def create_advertisement(db: Session, advertisement: schemas.AdvertisementCreate) -> models.Advertisement:
    db_ad = models.Advertisement(
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author=advertisement.author
    )
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


def get_advertisement(db: Session, advertisement_id: int) -> Optional[models.Advertisement]:
    return db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()


def update_advertisement(
        db: Session,
        advertisement_id: int,
        advertisement_update: schemas.AdvertisementUpdate
) -> Optional[models.Advertisement]:
    db_ad = get_advertisement(db, advertisement_id)
    if db_ad:
        update_data = advertisement_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ad, field, value)
        db.commit()
        db.refresh(db_ad)
    return db_ad


def delete_advertisement(db: Session, advertisement_id: int) -> bool:
    db_ad = get_advertisement(db, advertisement_id)
    if db_ad:
        db.delete(db_ad)
        db.commit()
        return True
    return False


def search_advertisements(
        db: Session,
        title: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20,
        offset: int = 0
) -> Dict[str, Any]:
    query = db.query(models.Advertisement)

    if title:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(models.Advertisement.author.ilike(f"%{author}%"))
    if min_price is not None:
        query = query.filter(models.Advertisement.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Advertisement.price <= max_price)

    total = query.count()

    query = query.order_by(models.Advertisement.created_at.desc())

    items = query.limit(limit).offset(offset).all()

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total,
        "has_previous": offset > 0
    }