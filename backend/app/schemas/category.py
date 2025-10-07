# app/schemas/category.py
from pydantic import BaseModel, field_validator

class CategoryCreate(BaseModel):
    name: str
    kind: str  # 'income' or 'expense'

    @field_validator("kind")
    @classmethod
    def _kind(cls, v: str) -> str:
        if v not in {"income", "expense"}:
            raise ValueError("kind must be 'income' or 'expense'")
        return v

class CategoryOut(BaseModel):
    id: int
    name: str
    kind: str

    class Config:
        from_attributes = True  # (Pydantic v2 replacement for orm_mode=True)