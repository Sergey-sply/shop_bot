from pydantic import BaseModel

class CategorySchemaCreate(BaseModel):
    name: str
    description: str


class CategoryBaseInfo(BaseModel):
    id: int
    name: str

class CategoryListSchema(BaseModel):
    total_count: int
    page: int
    categories: list[CategoryBaseInfo]