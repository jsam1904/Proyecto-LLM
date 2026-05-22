from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models import Exam

router = APIRouter()


class ExamCreate(BaseModel):
    user_id: int
    subject: str
    exam_date: datetime
    notes: Optional[str] = None


class ExamUpdate(BaseModel):
    subject: Optional[str] = None
    exam_date: Optional[datetime] = None
    notes: Optional[str] = None


class ExamResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    exam_date: datetime
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/{user_id}", response_model=list[ExamResponse])
async def get_exams(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Exam)
        .where(Exam.user_id == user_id)
        .order_by(Exam.exam_date.asc())
    )
    return result.scalars().all()


@router.get("/{user_id}/next")
async def get_next_exam(user_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna el próximo examen futuro del usuario."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Exam)
        .where(Exam.user_id == user_id, Exam.exam_date >= now)
        .order_by(Exam.exam_date.asc())
        .limit(1)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        return None

    days_remaining = (exam.exam_date.replace(tzinfo=timezone.utc) - now).days

    return {
        "id": exam.id,
        "subject": exam.subject,
        "exam_date": exam.exam_date,
        "days_remaining": days_remaining,
        "notes": exam.notes,
    }


@router.post("/", response_model=ExamResponse, status_code=201)
async def create_exam(data: ExamCreate, db: AsyncSession = Depends(get_db)):
    exam = Exam(**data.model_dump())
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.patch("/{exam_id}", response_model=ExamResponse)
async def update_exam(exam_id: int, data: ExamUpdate, db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(exam, field, value)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.delete("/{exam_id}")
async def delete_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    await db.delete(exam)
    await db.commit()
    return {"message": "Examen eliminado"}
