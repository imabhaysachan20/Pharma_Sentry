from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.triage import DBTriageCase
from backend.app.schemas.triage import CaseResponse

router = APIRouter(prefix="/cases", tags=["Triage Cases"])

@router.get("", response_model=List[CaseResponse])
async def list_cases(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Multi-tenant protection: return only cases for current user
    cases = (
        db.query(DBTriageCase)
        .filter(DBTriageCase.user_id == current_user["id"])
        .order_by(DBTriageCase.created_at.desc())
        .all()
    )
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case = (
        db.query(DBTriageCase)
        .filter(DBTriageCase.id == case_id, DBTriageCase.user_id == current_user["id"])
        .first()
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found or unauthorized.")
    return case
