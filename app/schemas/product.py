from pydantic import BaseModel



class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    category_id: int
    subcategory_id: int
    brand_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category_id: int
    subcategory_id: int
    brand_id: int
    rating: float