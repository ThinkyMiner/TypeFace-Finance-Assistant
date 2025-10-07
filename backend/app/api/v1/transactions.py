from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from app.db import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.core.security import get_current_user_id
from sqlalchemy import func

router = APIRouter()

@router.post("", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    txn = Transaction(user_id=current_user_id, **payload.model_dump())
    db.add(txn); db.commit(); db.refresh(txn)
    return txn

@router.get("", response_model=list[TransactionOut])
def list_transactions(
    response: Response,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    kind: str | None = Query(None),
    category_id: int | None = Query(None),
    limit: int = 20,
    offset: int = 0,
):
    if kind and kind not in {"income","expense"}:
        raise HTTPException(status_code=422, detail="kind must be 'income' or 'expense'")

    base = db.query(Transaction).where(Transaction.user_id == current_user_id)
    if start_date: base = base.filter(Transaction.occurred_on >= start_date)
    if end_date:   base = base.filter(Transaction.occurred_on <= end_date)
    if kind:       base = base.filter(Transaction.kind == kind)
    if category_id is not None: base = base.filter(Transaction.category_id == category_id)

    total = base.with_entities(func.count()).scalar() or 0
    items = (
        base.order_by(Transaction.occurred_on.desc(), Transaction.id.desc())
            .offset(offset).limit(limit).all()
    )
    response.headers["X-Total-Count"] = str(total)
    return items