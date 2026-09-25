from datetime import datetime, timezone
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.params import Query
from fastapi.responses import JSONResponse
from app.models.Product import Product, ProductCategory, ProductCreate, ProductSell


app = FastAPI(title="Product API", version="0.1.0")


VALIDATION_MESSAGES = {
    "name": "ชื่อสินค้าต้องไม่ว่าง",
    "sku_blank": "รหัสสินค้าต้องไม่ว่าง",
    "sku": "รหัสสินค้าต้องมีอย่างน้อย 3 ตัวอักษร",
    "price": "ราคาต้องมากกว่า 0",
    "stock": "จำนวนสินค้าไม่ต้องติดลบ",
    "category": "หมวดหมู่สินค้าไม่ถูกต้อง",
    "quantity": "จำนวนที่ต้องการขายต้องมากกว่า 0",
}

# Accept the Thai query value used by the public API while storage uses "Food".
CATEGORY_QUERY_ALIASES = {"อาหาร": ProductCategory.FOOD.value}


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return all request-body validation failures in the API error format."""
    messages: list[str] = []
    for error in exc.errors():
        field = error["loc"][-1]
        error_type = error["type"]

        if field == "sku" and error_type == "value_error":
            message = VALIDATION_MESSAGES["sku_blank"]
        else:
            message = VALIDATION_MESSAGES.get(str(field), "ข้อมูลคำขอไม่ถูกต้อง")

        if message not in messages:
            messages.append(message)

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"errors": messages})

# For demonstration purposes, we will use an in-memory list to store products.
def _product(
    product_id: int,
    name: str,
    sku: str,
    price: str,
    stock: int,
    category: ProductCategory,
    created_at: str,
) -> Product:
    return Product(
        id=product_id,
        name=name,
        sku=sku,
        price=Decimal(price),
        stock=stock,
        category=category,
        created_at=datetime.fromisoformat(created_at).replace(tzinfo=timezone.utc),
    )


products: list[Product] = [
    _product(
        product_id=1,
        name="ข้าวผัด",
        sku="FOOD001",
        price="45.00",
        stock=20,
        category=ProductCategory.FOOD,
        created_at="2024-01-01T12:00:00+00:00",
    )
]


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate) -> Product:
    """Validate and add a product to the in-memory catalogue."""
    if any(item.sku.casefold() == payload.sku.casefold() for item in products):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": ["รหัสสินค้าซ้ำกับสินค้าที่มีอยู่แล้ว"]},
        )

    product = Product(
        id=max((item.id for item in products), default=0) + 1,
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    products.append(product)
    return product


@app.post("/api/products/sell", response_model=Product)
def sell_product(payload: ProductSell) -> Product:
    """Sell units only when the requested product has sufficient stock."""
    product = next((item for item in products if item.id == payload.product_id), None)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if product.stock < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock"
        )

    product.stock -= payload.quantity
    return product


@app.get("/api/products", response_model=list[Product])
def list_products(
    category: str | None = Query(default=None, description="Filter by product category")
) -> list[Product]:
    """Return all products, or only products from the requested category."""
    if category is None:
        return products

    requested_category = CATEGORY_QUERY_ALIASES.get(category.strip(), category.strip())
    return [
        product
        for product in products
        if product.category.value.casefold() == requested_category.casefold()
    ]
