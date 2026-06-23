from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import engine
from database import SessionLocal
from models import Base
from models import Product
from fastapi.responses import FileResponse


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


class ProductCreate(BaseModel):

    name: str
    category: str
    price: float


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/products")
def create_product(
    product: ProductCreate
):

    db = SessionLocal()

    try:

        new_product = Product(
            name=product.name,
            category=product.category,
            price=product.price
        )

        db.add(new_product)

        db.commit()

        db.refresh(new_product)

        return {
            "message": "Product Created",
            "id": new_product.id
        }

    finally:

        db.close()


@app.get("/products")
def get_products(
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    cursor: int = None
):

    db = SessionLocal()

    try:

        query = db.query(Product)



        # Category Filter
        if category:
            query = query.filter(
                Product.category == category
            )

        # Minimum Price Filter
        if min_price is not None:
            query = query.filter(
                Product.price >= min_price
            )

        # Maximum Price Filter
        if max_price is not None:
            query = query.filter(
                Product.price <= max_price
            )

        # Cursor Pagination
        if cursor:
            query = query.filter(
                Product.id < cursor
            )

        products = (
            query
            .order_by(
                Product.created_at.desc(),
                Product.id.desc()
            )
            .limit(20)
            .all()
        )

        result = []

        for product in products:

            result.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "price": product.price,
                    "created_at": str(product.created_at),
                    "updated_at": str(product.updated_at)
                }
            )

        next_cursor = None

        if products:
            next_cursor = products[-1].id

        return {
            "products": result,
            "next_cursor": next_cursor
        }

    finally:

        db.close()