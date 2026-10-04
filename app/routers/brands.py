from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandResponse
from app.models.user import User
from app.security import require_admin


router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("/", response_model=list[BrandResponse], status_code=status.HTTP_200_OK)
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(Brand).all()
    return brands


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand: BrandCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing_brand = db.query(Brand).filter(Brand.name == brand.name).first()

    if existing_brand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand already exists")

    new_brand = Brand(name=brand.name)

    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)

    return new_brand


@router.get("/{brand_id}", response_model=BrandResponse, status_code=status.HTTP_200_OK)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    return brand


@router.put("/{brand_id}", response_model=BrandResponse, status_code=status.HTTP_202_ACCEPTED)
def update_brand(
    brand_id: int,
    brand: BrandCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    brand_to_update = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    existing_brand = db.query(Brand).filter(Brand.name == brand.name).first()

    if existing_brand and existing_brand.id != brand_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Brand already exists")

    brand_to_update.name = brand.name

    db.add(brand_to_update)
    db.commit()
    db.refresh(brand_to_update)

    return brand_to_update


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    brand_to_delete = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    db.delete(brand_to_delete)
    db.commit()