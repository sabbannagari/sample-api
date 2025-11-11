from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock: int = Field(ge=0, description="Stock must be 0 or greater")
    category: str
    sku: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    sku: Optional[str] = None

class Product(ProductBase):
    id: int
