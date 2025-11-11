from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    price: float = Field(gt=0, description="Price must be greater than 0")

class OrderBase(BaseModel):
    user_id: int
    items: List[OrderItem]
    shipping_address: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shipping_address: Optional[str] = None

class Order(OrderBase):
    id: int
    total_amount: float
    status: str  # pending, processing, shipped, delivered, cancelled
    created_at: datetime
    updated_at: datetime
