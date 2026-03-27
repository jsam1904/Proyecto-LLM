from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import json
from openai import AsyncOpenAI
from app.database import get_db
from app.models import StudyPlan, Task, User
from app.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class PlanRequest(BaseModel):
    user_id: int
    week_start: str          # "2025-03-24"
    available_hours: dict    # {"monday": 4, "tuesday": 3, ...}
    subjects: list[str]      # ["Cálculo II", "Programación", ...]
    priorities: Optional[list[str]] = None   # Materias prioritarias


@router.post("/generate")
async def generate_plan(req: PlanRequest, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Recuperar tareas pendientes del usuario
    result = await db.execute(
        select(Task).where(Task.user_id == req.user_id, Task.done == False)
    )
    pending_tasks = result.scalars().all()
    tasks_summary = [f"- {t.text} ({t.subject or 'Sin materia'})" for t in pending_tasks]

    prompt = f"""Genera un plan de estudio semanal estructurado para un estudiante universitario.

Semana: {req.week_start}
Materias: {', '.join(req.subjects)}
Materias prioritarias: {', '.join(req.priorities or req.subjects[:2])}
Horas disponibles por día: {json.dumps(req.available_hours, ensure_ascii=False)}
Tareas pendientes:
{chr(10).join(tasks_summary) if tasks_summary else '- Sin tareas pendientes registradas'}

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


@router.get("/{user_id}/all")
async def get_all_plans(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [{"plan_id": p.id, "created_at": p.created_at, "week_start": p.plan_data.get("week_start")} for p in plans]
