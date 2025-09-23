from pydantic import BaseModel


class UserSchemaCreate(BaseModel):
    id: int
    name: str