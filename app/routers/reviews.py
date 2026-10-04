from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.models.product import Product
from app.models.user import User
from app.security import get_current_user


router = APIRouter(prefix="/reviews", tags=["reviews"])


def update_product_rating(product_id: int, db: Session):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()

    product = db.query(Product).filter(Product.id == product_id).first()

    if not reviews:
        product.rating = 0
    else:
        total_rating = sum(review.rating for review in reviews)
        product.rating = total_rating / len(reviews)

    db.commit()
    db.refresh(product)


@router.get("/", response_model=list[ReviewResponse], status_code=status.HTTP_200_OK)
def get_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).all()
    return reviews


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    new_review = Review(**review.model_dump(), user_id=current_user.id, product_id=product_id)

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    update_product_rating(product_id, db)

    return new_review


@router.get("/product/{product_id}", response_model=list[ReviewResponse], status_code=status.HTTP_200_OK)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    reviews = db.query(Review).filter(Review.product_id == product_id).all()

    return reviews


@router.put("/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_202_ACCEPTED)
def update_review(
    review_id: int,
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review_to_update = db.query(Review).filter(Review.id == review_id).first()

    if not review_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if review_to_update.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this review")

    data = review.model_dump().items()

    for field, value in data:
        setattr(review_to_update, field, value)

    db.commit()
    db.refresh(review_to_update)

    update_product_rating(review_to_update.product_id, db)

    return review_to_update


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review_to_delete = db.query(Review).filter(Review.id == review_id).first()

    if not review_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if review_to_delete.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete this review")

    product_id = review_to_delete.product_id

    db.delete(review_to_delete)
    db.commit()

    update_product_rating(product_id, db)