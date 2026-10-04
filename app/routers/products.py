from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category, Subcategory
from app.models.brand import Brand
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from typing import Optional
from app.security import require_admin
from app.models.user import User


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if subcategory_id:
        query = query.filter(Product.subcategory_id == subcategory_id)

    if brand_id:
        query = query.filter(Product.brand_id == brand_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(Product.rating <= max_rating)

    return query.all()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    subcategory = db.query(Subcategory).filter(Subcategory.id == product.subcategory_id).first()

    if not subcategory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

    if subcategory.category_id != product.category_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subcategory not found")

    brand = db.query(Brand).filter(Brand.id == product.brand_id).first()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_202_ACCEPTED)
def update_product(
    product_id: int,
    product: ProductCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    product_to_update = db.query(Product).filter(Product.id == product_id).first()

    if not product_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    category = db.query(Category).filter(Category.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    subcategory = db.query(Subcategory).filter(Subcategory.id == product.subcategory_id).first()

    if not subcategory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

    if subcategory.category_id != product.category_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subcategory not found")

    brand = db.query(Brand).filter(Brand.id == product.brand_id).first()

    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    data = product.model_dump(exclude_unset=True).items()

    for field, value in data:
        setattr(product_to_update, field, value)

    db.commit()
    db.refresh(product_to_update)

    return product_to_update


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()