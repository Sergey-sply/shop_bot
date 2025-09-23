from pydantic import BaseModel


class DeliveryMethodSchema(BaseModel):
    id: int
    name: str
