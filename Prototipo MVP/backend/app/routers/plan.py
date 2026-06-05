from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime, timezone
from openai import AsyncOpenAI
from app.database import get_db
from app.models import StudyPlan, Task, User, Exam
from app.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class PlanRequest(BaseModel):
    user_id: int
    week_start: str          # "2025-03-24"
    available_hours: dict    # {"monday": 4, "tuesday": 3, ...}
    subjects: list[str]      # ["Cálculo II", "Programación", ...]
    priorities: Optional[list[str]] = None   # Materias prioritarias


def _normalize_subject(subject: Optional[str]) -> str:
    clean = " ".join((subject or "").strip().split())
    return clean or "Sin materia"


def _aware(dt):
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def build_plan_context(user_id: int, db: AsyncSession):
    now = datetime.now(timezone.utc)
    tasks_result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id, Task.done == False)
        .order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
    )
    pending_tasks = tasks_result.scalars().all()

    exams_result = await db.execute(
        select(Exam)
        .where(Exam.user_id == user_id, Exam.exam_date >= now)
        .order_by(Exam.exam_date.asc())
    )
    upcoming_exams = exams_result.scalars().all()

    subject_scores = {}
    subject_display = {}
    task_items = []

    for task in pending_tasks:
        subject = _normalize_subject(task.subject)
        key = subject.lower()
        subject_display.setdefault(key, subject)
        due_dt = _aware(task.due_date)
        days_until = max(0, (due_dt - now).days) if due_dt else None

        score = 2
        if task.priority == "alta":
            score += 3
        elif task.priority == "media":
            score += 1
        if days_until is not None:
            if days_until <= 1:
                score += 4
            elif days_until <= 3:
                score += 3
            elif days_until <= 7:
                score += 1

        subject_scores[key] = subject_scores.get(key, 0) + score
        task_items.append({
            "text": task.text,
            "subject": subject,
            "priority": task.priority or "media",
            "due_text": f"vence en {days_until} dia(s)" if days_until is not None else "sin fecha limite",
        })

    exam_items = []
    for exam in upcoming_exams:
        subject = _normalize_subject(exam.subject)
        key = subject.lower()
        subject_display.setdefault(key, subject)
        exam_dt = _aware(exam.exam_date)
        days_until = max(0, (exam_dt - now).days) if exam_dt else None

        score = 4
        if days_until is not None:
            if days_until <= 3:
                score += 8
            elif days_until <= 7:
                score += 5
            elif days_until <= 14:
                score += 2

        subject_scores[key] = subject_scores.get(key, 0) + score
        exam_items.append({
            "subject": subject,
            "days_until": days_until,
            "notes": exam.notes,
            "exam_date": exam.exam_date,
        })

    suggested_subjects = [
        subject_display[key]
        for key, _score in sorted(subject_scores.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "pending_tasks": task_items,
        "upcoming_exams": exam_items,
        "suggested_subjects": suggested_subjects,
        "suggested_priorities": suggested_subjects[:3],
    }


@router.get("/context/{user_id}")
async def get_plan_context(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await build_plan_context(user_id, db)


@router.post("/generate")
async def generate_plan(req: PlanRequest, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    context = await build_plan_context(req.user_id, db)
    subjects = list(dict.fromkeys([*req.subjects, *context["suggested_subjects"]]))
    priorities = req.priorities or context["suggested_priorities"] or subjects[:2]

    tasks_summary = [
        f"- {t['text']} ({t['subject']}, prioridad {t['priority']}, {t['due_text']})"
        for t in context["pending_tasks"]
    ]
    exams_summary = []
    for exam in context["upcoming_exams"]:
        days = exam["days_until"]
        days_text = f"en {days} dia(s)" if days is not None else "fecha pendiente"
        notes = f" - notas: {exam['notes']}" if exam["notes"] else ""
        exams_summary.append(f"- {exam['subject']} {days_text}{notes}")

    prompt = f"""Genera un plan de estudio semanal estructurado para un estudiante universitario.

Semana: {req.week_start}
Materias: {', '.join(subjects)}
Materias prioritarias: {', '.join(priorities)}
Horas disponibles por día: {json.dumps(req.available_hours, ensure_ascii=False)}
Tareas pendientes:
{chr(10).join(tasks_summary) if tasks_summary else '- Sin tareas pendientes registradas'}
Examenes proximos:
{chr(10).join(exams_summary) if exams_summary else '- Sin examenes proximos registrados'}

Genera el plan en formato JSON con esta estructura exacta (sin markdown, solo JSON puro):
{{
  "week_start": "{req.week_start}",
  "days": [
    {{
      "name": "Lunes",
      "slots": [
        {{
          "time": "7:00 – 8:30",
          "subject": "Nombre de la materia",
          "tag": "Etiqueta corta",
          "duration": 90
        }}
      ]
    }}
  ]
}}

Reglas:
- Distribuye las materias según las horas disponibles de cada día
- Prioriza las materias marcadas como prioritarias
- Los bloques deben ser de 60-120 minutos máximo
- Incluye descansos implícitos entre bloques
- Si un día tiene 0 horas disponibles, el arreglo slots debe estar vacío
"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Eres un planificador académico experto. Responde solo con JSON válido, sin texto adicional."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        plan_json = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="La IA retornó un formato inválido")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al generar plan: {str(e)}")

    # Guardar plan en PostgreSQL como JSONB
    new_plan = StudyPlan(
        user_id=req.user_id,
        plan_data=plan_json,
        ai_prompt=prompt,
    )
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)

    return {"plan_id": new_plan.id, "plan": plan_json}


@router.get("/{user_id}/latest")
async def get_latest_plan(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
        .limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="No hay plan generado aún")
    return {"plan_id": plan.id, "plan": plan.plan_data, "created_at": plan.created_at}


class PlanUpdateRequest(BaseModel):
    plan_data: dict


class PlanModifyRequest(BaseModel):
    user_id: int
    plan_id: int
    instruction: str


@router.post("/modify")
async def modify_plan(req: PlanModifyRequest, db: AsyncSession = Depends(get_db)):
    plan = await db.get(StudyPlan, req.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    prompt = f"""Tienes el siguiente plan de estudio semanal en JSON:
{json.dumps(plan.plan_data, ensure_ascii=False, indent=2)}

El estudiante quiere hacer este cambio: "{req.instruction}"

Aplica el cambio solicitado al plan y devuelve el plan completo modificado en el mismo formato JSON exacto (sin markdown, solo JSON puro). Mantén todos los días y la estructura intacta."""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Eres un planificador académico experto. Modifica el plan según la instrucción del estudiante y devuelve solo JSON válido con la misma estructura."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        modified_data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="La IA retornó un formato inválido")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al modificar plan: {str(e)}")

    plan.plan_data = modified_data
    await db.commit()
    await db.refresh(plan)
    return {"plan_id": plan.id, "plan": plan.plan_data}


@router.put("/{plan_id}")
async def update_plan(plan_id: int, req: PlanUpdateRequest, db: AsyncSession = Depends(get_db)):
    plan = await db.get(StudyPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    plan.plan_data = req.plan_data
    await db.commit()
    await db.refresh(plan)
    return {"plan_id": plan.id, "plan": plan.plan_data}


@router.get("/{user_id}/all")
async def get_all_plans(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [{"plan_id": p.id, "created_at": p.created_at, "week_start": p.plan_data.get("week_start")} for p in plans]
