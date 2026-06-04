from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import Task

router = APIRouter()


class TaskCreate(BaseModel):
    user_id: int
    text: str
    subject: Optional[str] = None
    tag: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = "media"


class TaskUpdate(BaseModel):
    text: Optional[str] = None
    done: Optional[bool] = None
    subject: Optional[str] = None
    tag: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None


@router.get("/{user_id}")
async def get_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks


@router.post("/")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(**task.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.patch("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    await db.delete(task)
    await db.commit()
    return {"message": "Tarea eliminada"}
