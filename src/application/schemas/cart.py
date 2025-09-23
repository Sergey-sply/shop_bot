from pydantic import BaseModel


class CartSchema(BaseModel):
    cart_id: int
    product_id: int
    quantity: int
    unit_price: int
    name: str


class UserCartSchema(BaseModel):
    page: int
    total_count: int
    total_amount: int
    items: list[CartSchema] | None
