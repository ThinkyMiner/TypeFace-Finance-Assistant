from datetime import date, datetime
from pydantic import BaseModel, field_validator


class TransactionCreate(BaseModel):
    kind: str  # 'income' or 'expense'
    amount: float
    occurred_on: date
    category_id: int | None = None
    merchant: str | None = None
    note: str | None = None
    payment_method: str | None = None
    receipt_path: str | None = None

    @field_validator("kind")
    @classmethod
    def _kind(cls, v: str) -> str:
        if v not in {"income", "expense"}:
            raise ValueError("kind must be 'income' or 'expense'")
        return v


class TransactionOut(BaseModel):
    id: int
    user_id: int
    category_id: int | None
    kind: str
    amount: float
    occurred_on: date
    merchant: str | None
    note: str | None
    payment_method: str | None
    receipt_path: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


