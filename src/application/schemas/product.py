from typing import Literal, Annotated

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class ProductSchemaCreate(BaseModel):
    category_id: int
    name: str
    description: str
    image: str | None = None
    price: int
    quantity: int


class ProductBaseInfo(BaseModel):
    id: int
    name: str
    price: int
    quantity: int

class CategoryProductsListSchema(BaseModel):
    page: int
    total_count: int
    category_id: int
    products: list[ProductBaseInfo]


class ProductListSchema(BaseModel):
    page: int
    total_count: int
    products: list[ProductBaseInfo]


class ProductFullInfo(ProductBaseInfo):
    category_id: int
    description: str
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductUpdateName(BaseModel):
    field: Literal["name"]
    value: str = Field(min_length=1, max_length=32)


class ProductUpdateDescription(BaseModel):
    field: Literal["description"]
    value: str = Field(min_length=1, max_length=128)


class ProductUpdatePrice(BaseModel):
    field: Literal["price"]
    value: int = Field(gt=0)

class ProductUpdateImage(BaseModel):
    field: Literal["image"]
    value: str

ProductUpdate = TypeAdapter(
    Annotated[
        ProductUpdateName | ProductUpdateDescription | ProductUpdatePrice | ProductUpdateImage,
        Field(discriminator="field"),
    ]
)