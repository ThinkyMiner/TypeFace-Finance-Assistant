from datetime import date
from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.transaction import Transaction
from app.core.security import get_current_user_id

router = APIRouter()

@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    q = select(
        Transaction.kind,
        func.sum(Transaction.amount).label("total")
    ).where(Transaction.user_id == current_user_id)

    if start_date: q = q.where(Transaction.occurred_on >= start_date)
    if end_date:   q = q.where(Transaction.occurred_on <= end_date)

    q = q.group_by(Transaction.kind)
    rows = db.execute(q).all()

    income = sum(r.total for r in rows if r.kind == "income") or 0
    expense = sum(r.total for r in rows if r.kind == "expense") or 0
    return {"income": float(income), "expense": float(expense), "net": float(income - expense)}

@router.get("/by-category")
def by_category(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    from app.models.category import Category
    q = (
        select(Category.name, func.sum(Transaction.amount).label("total"))
        .join(Category, Category.id == Transaction.category_id, isouter=True)
        .where(Transaction.user_id == current_user_id, Transaction.kind == "expense")
    )
    if start_date: q = q.where(Transaction.occurred_on >= start_date)
    if end_date:   q = q.where(Transaction.occurred_on <= end_date)

    q = q.group_by(Category.name)
    rows = db.execute(q).all()
    # Category.name can be None if uncategorized
    return [{"category": r.name or "Uncategorized", "total": float(r.total)} for r in rows]

@router.get("/by-date")
def by_date(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bucket: str = Query("day", pattern="^(day|week|month)$"),
):
    # DB-agnostic: group by actual date; then bucket in Python
    q = (
        select(Transaction.occurred_on, Transaction.kind, func.sum(Transaction.amount))
        .where(Transaction.user_id == current_user_id)
    )
    if start_date: q = q.where(Transaction.occurred_on >= start_date)
    if end_date:   q = q.where(Transaction.occurred_on <= end_date)

    q = q.group_by(Transaction.occurred_on, Transaction.kind).order_by(Transaction.occurred_on)
    rows = db.execute(q).all()

    def to_bucket(d: date) -> date:
        if bucket == "day":
            return d
        if bucket == "week":
            # ISO week start (Monday): subtract d.isoweekday()-1 days
            return d.fromordinal(d.toordinal() - (d.isoweekday() - 1))
        if bucket == "month":
            return d.replace(day=1)

    agg = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for d, kind, amt in rows:
        b = to_bucket(d)
        agg[b][kind] += float(amt)

    series = [
        {"bucket": k.isoformat(), "income": v["income"], "expense": v["expense"], "net": v["income"] - v["expense"]}
        for k, v in sorted(agg.items())
    ]
    return series