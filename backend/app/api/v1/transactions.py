from fastapi import APIRouter, Depends, Query, Response, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from app.db import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.core.security import get_current_user_id
from sqlalchemy import func
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

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

@router.get("/export/pdf")
def export_transactions_pdf(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    kind: str | None = Query(None),
):
    """Export transactions to PDF with formatted table"""
    if kind and kind not in {"income","expense"}:
        raise HTTPException(status_code=422, detail="kind must be 'income' or 'expense'")

    # Query transactions
    base = db.query(Transaction).where(Transaction.user_id == current_user_id)
    if start_date: base = base.filter(Transaction.occurred_on >= start_date)
    if end_date:   base = base.filter(Transaction.occurred_on <= end_date)
    if kind:       base = base.filter(Transaction.kind == kind)

    transactions = base.order_by(Transaction.occurred_on.desc()).all()

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.kind == 'income')
    total_expense = sum(t.amount for t in transactions if t.kind == 'expense')
    balance = total_income - total_expense

    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=30,
        alignment=1  # Center
    )

    # Title
    title = Paragraph("Transaction Report", title_style)
    elements.append(title)

    # Date range info
    date_info = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if start_date or end_date:
        date_range = f"Period: {start_date or 'Beginning'} to {end_date or 'Present'}"
        date_info = f"{date_range}<br/>{date_info}"

    info = Paragraph(date_info, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 20))

    # Summary table
    summary_data = [
        ['Summary', 'Amount (INR)'],
        ['Total Income', f'₹{total_income:,.2f}'],
        ['Total Expense', f'₹{total_expense:,.2f}'],
        ['Balance', f'₹{balance:,.2f}']
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFF5EB')),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Transactions table
    if transactions:
        # Header
        trans_data = [['Date', 'Type', 'Merchant', 'Amount (INR)', 'Payment Method']]

        # Data rows
        for txn in transactions:
            trans_data.append([
                str(txn.occurred_on),
                txn.kind.capitalize(),
                txn.merchant or '-',
                f'₹{txn.amount:,.2f}',
                txn.payment_method or '-'
            ])

        trans_table = Table(trans_data, colWidths=[1.3*inch, 0.9*inch, 2*inch, 1.3*inch, 1.3*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        elements.append(Paragraph(f"<b>Transactions ({len(transactions)} total)</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(trans_table)
    else:
        elements.append(Paragraph("No transactions found for the selected period.", styles['Normal']))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    # Generate filename
    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )