from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut
from app.core.security import get_current_user_id

router = APIRouter()

@router.post("", response_model=CategoryOut)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    cat = Category(user_id=current_user_id, name=payload.name, kind=payload.kind)
    db.add(cat); db.commit(); db.refresh(cat)
    return cat

@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return db.query(Category).filter_by(user_id=current_user_id).all()