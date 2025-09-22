from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    product_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    image_url: Optional[str] = None
