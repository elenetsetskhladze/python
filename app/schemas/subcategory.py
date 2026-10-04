from pydantic import BaseModel



class SubcategoryCreate(BaseModel):
    name: str
    category_id: int


class SubcategoryResponse(BaseModel):
    id: int
    name: str
    category_id: int