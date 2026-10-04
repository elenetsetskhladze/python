from fastapi import FastAPI
from app.routers import categories
from app.routers import subcategories
from app.routers import brands
from app.routers import products
from app.routers import users
from app.routers import reviews
from app.routers import carts

app = FastAPI(title="Online Shop")


app.include_router(categories.router)


app.include_router(subcategories.router)


app.include_router(brands.router)


app.include_router(products.router)


app.include_router(users.router)


app.include_router(reviews.router)


app.include_router(carts.router)