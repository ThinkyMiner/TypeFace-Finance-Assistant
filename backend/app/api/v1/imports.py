from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any
import tempfile
import os
from app.core.security import get_current_user_id
from app.db import get_db
from app.models.transaction import Transaction
from app.services.statement_parser import StatementParser
from app.schemas.transaction import TransactionOut

router = APIRouter()

# Store preview data temporarily (in production, use Redis or database)
preview_cache = {}

@router.post("/bank-statement")
async def import_bank_statement(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    # Check file size (limit to 20MB for PDFs)
    max_size = 20 * 1024 * 1024  # 20MB
    file_content = await file.read()

    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB")

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name

    try:
        parser = StatementParser()
        result = await parser.parse_statement(tmp_file_path, current_user_id)

        if not result["success"]:
            raise HTTPException(status_code=422, detail=result["message"])

        # Store preview data in cache (use user_id as key)
        preview_key = f"preview_{current_user_id}"
        preview_cache[preview_key] = result["transactions"]

        return {
            "preview": result["transactions"][:10],  # Show first 10 for preview
            "total_count": len(result["transactions"]),
            "method": result["method"],
            "message": f"Preview ready. Found {len(result['transactions'])} transactions. Use /confirm to import all."
        }

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@router.post("/confirm", response_model=List[TransactionOut])
async def confirm_import(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> List[TransactionOut]:

    preview_key = f"preview_{current_user_id}"

    if preview_key not in preview_cache:
        raise HTTPException(status_code=400, detail="No preview data found. Please upload a statement first.")

    transactions_data = preview_cache[preview_key]

    try:
        created_transactions = []

        for txn_data in transactions_data:
            # Check for potential duplicates based on date + amount + description
            existing = db.query(Transaction).filter(
                Transaction.user_id == current_user_id,
                Transaction.occurred_on == txn_data["occurred_on"],
                Transaction.amount == txn_data["amount"],
                Transaction.merchant == txn_data["merchant"]
            ).first()

            if existing:
                continue  # Skip duplicates

            # Create transaction
            transaction = Transaction(
                user_id=current_user_id,
                **txn_data
            )
            db.add(transaction)
            created_transactions.append(transaction)

        db.commit()

        # Refresh all transactions to get IDs
        for txn in created_transactions:
            db.refresh(txn)

        # Clear preview cache
        del preview_cache[preview_key]

        return created_transactions

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import transactions: {str(e)}")


@router.get("/preview")
async def get_preview(
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:

    preview_key = f"preview_{current_user_id}"

    if preview_key not in preview_cache:
        raise HTTPException(status_code=404, detail="No preview data found")

    transactions = preview_cache[preview_key]

    return {
        "transactions": transactions,
        "total_count": len(transactions),
        "message": "Preview data available"
    }