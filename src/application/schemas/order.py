from pydantic import BaseModel

from src.core.enums.order import OrderStatus


class OrderSchemaCreate(BaseModel):
    user_id: int
    delivery_method_id: int
    client_name: str
    client_number: str
    client_address: str


class OrderItemSchema(BaseModel):
    product_name: str
    quantity: int
    unit_price: int

class OrderFullInfoSchema(BaseModel):
    user_id: int
    order_id: str
    order_status: OrderStatus
    delivery_method_name: str
    client_name: str
    client_number: str
    client_address: str
    items: list[OrderItemSchema]


class OrderListSchema(BaseModel):
    orders: list[str]
    page: int
    per_page: int
    total_count: int