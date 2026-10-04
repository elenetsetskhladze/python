from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.models.subcategory import Subcategory
from app.schemas.subcategory import SubcategoryCreate, SubcategoryResponse
from app.models.user import User
from app.security import require_admin


router = APIRouter(prefix="/subcategories", tags=["Subcategories"])


@router.get("/", response_model=list[SubcategoryResponse], status_code=status.HTTP_200_OK)
def get_subcategories(db: Session = Depends(get_db)):
    subcategories = db.query(Subcategory).all()
    return subcategories


@router.post("/", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subcategory(
    subcategory: SubcategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing_subcategory = db.query(Subcategory).filter(Subcategory.name == subcategory.name).first()

    if existing_subcategory:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subcategory already exists")

    category = db.query(Category).filter(Category.id == subcategory.category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")

    new_subcategory = Subcategory(name=subcategory.name, category_id=subcategory.category_id)

    db.add(new_subcategory)
    db.commit()
    db.refresh(new_subcategory)

    return new_subcategory


@router.get("/{subcategory_id}", response_model=SubcategoryResponse, status_code=status.HTTP_200_OK)
def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db)
):
    subcategory_to_update = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()

    if not subcategory_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

    return subcategory_to_update


@router.put("/{subcategory_id}", response_model=SubcategoryResponse, status_code=status.HTTP_202_ACCEPTED)
def update_subcategory(
    subcategory_id: int,
    subcategory: SubcategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    subcategory_to_update = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()

    if not subcategory_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

    existing_subcategory = db.query(Subcategory).filter(Subcategory.name == subcategory.name).first()

    if existing_subcategory and existing_subcategory.id != subcategory_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subcategory already exists")

    category = db.query(Category).filter(Category.id == subcategory.category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    subcategory_to_update.name = subcategory.name
    subcategory_to_update.category_id = subcategory.category_id

    db.commit()
    db.refresh(subcategory_to_update)

    return subcategory_to_update


@router.delete("/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subcategory(
    subcategory_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    subcategory_to_delete = db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()

    if not subcategory_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

    db.delete(subcategory_to_delete)
    db.commit()