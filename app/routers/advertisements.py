from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/advertisement", tags=["advertisements"])

@router.post("/", response_model=schemas.AdvertisementResponse, status_code=201)
def create_advertisement(advertisement: schemas.AdvertisementCreate, db: Session = Depends(get_db)):
    return crud.create_advertisement(db, advertisement)

@router.patch("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def update_advertisement(advertisement_id: int, advertisement_update: schemas.AdvertisementUpdate, db: Session = Depends(get_db)):
    db_ad = crud.update_advertisement(db, advertisement_id, advertisement_update)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_ad

@router.delete("/{advertisement_id}", status_code=204)
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    if not crud.delete_advertisement(db, advertisement_id):
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return

@router.get("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_ad = crud.get_advertisement(db, advertisement_id)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_ad

@router.get("/", response_model=List[schemas.AdvertisementResponse])
def search_advertisements(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, gt=0),
    max_price: Optional[float] = Query(None, gt=0),
    db: Session = Depends(get_db)
):
    return crud.search_advertisements(db, title, author, min_price, max_price)