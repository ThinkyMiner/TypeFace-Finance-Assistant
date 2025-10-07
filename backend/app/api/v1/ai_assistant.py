from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models.transaction import Transaction
from app.core.security import get_current_user_id
from app.services.ai_assistant import analyze_transactions_with_ai, get_preset_insights
from datetime import datetime

router = APIRouter()


class AIQueryRequest(BaseModel):
    query: str
    preset: str | None = None  # 'overview', 'spending', 'trends', or None for custom query


class AIQueryResponse(BaseModel):
    insight: str
    chart: dict | None
    recommendations: list[str]


@router.post("/query", response_model=AIQueryResponse)
def query_ai_assistant(
    payload: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Query the AI assistant about your finances.

    - Use preset='overview' for financial overview
    - Use preset='spending' for spending analysis
    - Use preset='trends' for spending trends
    - Or provide a custom query in natural language
    """
    # Fetch user's transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user_id
    ).order_by(Transaction.occurred_on.desc()).all()

    if not transactions:
        return AIQueryResponse(
            insight="You don't have any transactions yet. Start by adding some income or expense transactions!",
            chart=None,
            recommendations=[
                "Add your first transaction to get started",
                "Track both income and expenses",
                "Be consistent with your entries"
            ]
        )

    # Convert to dict for AI processing
    transaction_dicts = [
        {
            "id": t.id,
            "kind": t.kind,
            "amount": float(t.amount),
            "occurred_on": str(t.occurred_on),
            "merchant": t.merchant,
            "note": t.note,
            "payment_method": t.payment_method
        }
        for t in transactions
    ]

    # Process query
    if payload.preset:
        result = get_preset_insights(transaction_dicts, payload.preset)
    else:
        result = analyze_transactions_with_ai(payload.query, transaction_dicts)

    return AIQueryResponse(**result)


@router.get("/suggestions")
def get_query_suggestions(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get suggested queries for the AI assistant
    """
    return {
        "suggestions": [
            {"text": "How am I doing financially?", "preset": "overview"},
            {"text": "Where am I spending the most?", "preset": "spending"},
            {"text": "Show me my spending trends", "preset": "trends"},
            {"text": "Compare my coffee vs restaurant spending", "preset": None},
            {"text": "What are my top 5 expenses this month?", "preset": None},
            {"text": "Am I spending more than I earn?", "preset": None},
        ]
    }
