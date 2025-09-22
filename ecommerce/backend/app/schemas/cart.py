from pydantic import BaseModel, Field
from typing import List


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItem(BaseModel):
    cart_item_id: int
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItem]
    total: float
