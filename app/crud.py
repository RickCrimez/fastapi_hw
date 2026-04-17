from sqlalchemy.orm import Session
from app import models, schemas, auth
from typing import Optional, Dict, Any


# User CRUD
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=models.UserRole.USER
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user_by_id(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = auth.get_password_hash(update_data.pop("password"))
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Advertisement CRUD
def create_advertisement(db: Session, advertisement: schemas.AdvertisementCreate,
                         author_id: int) -> models.Advertisement:
    db_ad = models.Advertisement(
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author_id=author_id
    )
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


def get_advertisement(db: Session, advertisement_id: int) -> Optional[models.Advertisement]:
    return db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()


def get_advertisements_by_author(db: Session, author_id: int):
    return db.query(models.Advertisement).filter(models.Advertisement.author_id == author_id).all()


def update_advertisement(db: Session, advertisement_id: int, advertisement_update: schemas.AdvertisementUpdate) -> \
Optional[models.Advertisement]:
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
        author_name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20,
        offset: int = 0
) -> Dict[str, Any]:
    """Поиск объявлений с фильтрацией и пагинацией"""
    query = db.query(models.Advertisement).join(models.User)

    if title:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if author_name:
        query = query.filter(models.User.username.ilike(f"%{author_name}%"))
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