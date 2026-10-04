from pydantic import BaseModel



class CategoryCreate(BaseModel):
    name: str


class ProductInCategory(BaseModel):
    id: int
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    products: list[ProductInCategory]