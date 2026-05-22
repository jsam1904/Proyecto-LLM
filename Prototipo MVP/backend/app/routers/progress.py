from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.database import get_db
from app.models import Task, StudyPlan, Exam

router = APIRouter()


@router.get("/{user_id}")
async def get_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Agrega estadísticas reales del usuario:
    - Tareas: total, completadas, pendientes, % por materia
    - Horas de estudio planeadas (de los últimos 4 planes)
    - Próximo examen
    """

    # ── Tareas ──────────────────────────────────────────────
    tasks_result = await db.execute(
        select(Task).where(Task.user_id == user_id)
    )
    tasks = tasks_result.scalars().all()

    total_tasks = len(tasks)
    done_tasks  = sum(1 for t in tasks if t.done)
    completion_pct = round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0)

    # Agrupar por materia
    subject_tasks: dict = {}
    for t in tasks:
        subj = t.subject or "Sin materia"
        if subj not in subject_tasks:
            subject_tasks[subj] = {"total": 0, "done": 0}
        subject_tasks[subj]["total"] += 1
        if t.done:
            subject_tasks[subj]["done"] += 1

    # ── Horas planeadas (últimos 4 planes) ──────────────────
    plans_result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
        .limit(4)
    )
    plans = plans_result.scalars().all()

    subject_hours: dict = {}
    for plan in plans:
        for day in plan.plan_data.get("days", []):
            for slot in day.get("slots", []):
                # Usar el tag como clave (más corto, ej: "Cálculo")
                key = slot.get("tag") or slot.get("subject", "Otro")
                hours = slot.get("duration", 0) / 60.0
                subject_hours[key] = subject_hours.get(key, 0.0) + hours

    total_hours = sum(subject_hours.values())

    # ── Próximo examen ───────────────────────────────────────
    now = datetime.now(timezone.utc)
    exam_result = await db.execute(
        select(Exam)
        .where(Exam.user_id == user_id, Exam.exam_date >= now)
        .order_by(Exam.exam_date.asc())
        .limit(1)
    )
    next_exam = exam_result.scalar_one_or_none()
    next_exam_data = None
    if next_exam:
        exam_dt = next_exam.exam_date
        if exam_dt.tzinfo is None:
            exam_dt = exam_dt.replace(tzinfo=timezone.utc)
        days_remaining = max(0, (exam_dt - now).days)
        next_exam_data = {
            "id": next_exam.id,
            "subject": next_exam.subject,
            "exam_date": next_exam.exam_date,
            "days_remaining": days_remaining,
        }

    # ── Respuesta consolidada ────────────────────────────────
    return {
        "tasks": {
            "total":          total_tasks,
            "done":           done_tasks,
            "pending":        total_tasks - done_tasks,
            "completion_pct": completion_pct,
            "by_subject":     subject_tasks,
        },
        "study_hours": {
            "total":      round(total_hours, 1),
            "by_subject": {k: round(v, 1) for k, v in subject_hours.items()},
        },
        "next_exam": next_exam_data,
    }
