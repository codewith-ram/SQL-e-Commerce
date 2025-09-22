from pydantic import BaseModel
from typing import List


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float


class OrderResponse(BaseModel):
    order_id: int
    total_amount: float
    status: str


class OrderSummary(BaseModel):
    order_id: int
    order_date: str
    total_amount: float
    status: str


class OrderHistoryResponse(BaseModel):
    orders: List[OrderSummary]
