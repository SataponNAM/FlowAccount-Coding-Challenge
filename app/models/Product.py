from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ProductCategory(str, Enum):
    FOOD = "Food"

class Product(BaseModel):
    """A product available in the catalogue."""

    id: int = Field(ge=1, examples=[1])
    name: str = Field(examples=["ข้าวผัด"])
    sku: str = Field(examples=["FOOD001"])
    price: Decimal = Field(ge=0, decimal_places=2, examples=[45.00])
    stock: int = Field(ge=0, examples=[20])
    category: ProductCategory = Field(examples=["FOOD"])
    created_at: datetime

class ProductCreate(BaseModel):
    """Validated input accepted when adding a product."""

    name: str = Field(min_length=1, examples=["ข้าวผัด"])
    sku: str = Field(min_length=3, examples=["FOOD001"])
    price: Decimal = Field(gt=0, decimal_places=2, examples=[45.00])
    stock: int = Field(ge=0, examples=[20])
    category: ProductCategory

    @field_validator("name", "sku", mode="before")
    @classmethod
    def reject_blank_text(cls, value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class ProductSell(BaseModel):
    """Input used to sell units of an existing product."""

    product_id: int = Field(alias="productId", ge=1, examples=[1])
    quantity: int = Field(gt=0, examples=[2])
