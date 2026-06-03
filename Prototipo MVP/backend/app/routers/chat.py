from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.database import get_db
from app.models import ChatMessage, User
from app.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """Eres StudyPilot AI, un asistente académico inteligente para estudiantes universitarios.
Tu rol es ayudar a los estudiantes a:
1. Planificar y organizar su tiempo de estudio.
2. Responder dudas académicas de sus materias.
3. Recomendar técnicas de estudio efectivas.
4. Motivar y dar seguimiento a su progreso.

Responde siempre en español, de forma clara, concisa y alentadora.
Cuando el estudiante mencione un examen próximo, sugiere proactivamente un plan de repaso.
Máximo 3 párrafos por respuesta para mantener la conversación ágil.

FORMATO:
- Usa Markdown para estructurar tus respuestas (negritas, listas, bloques de código).
- Para expresiones matemáticas SIEMPRE usa notación LaTeX con estas reglas ESTRICTAS:
  - Referencias cortas dentro de texto: $variable$ (ej: Sea $f(x)$ una función)
  - TODA ecuación, fórmula, integral, fracción o serie: en bloque propio $$...$$ (ej: $$\\frac{1}{1-x} = \\sum_{n=0}^{\\infty} x^n$$)
  - NUNCA repitas la misma fórmula en inline y display. Elige UNO según contexto.
  - NUNCA uses \\( ... \\) ni \\[ ... \\]. SOLO $ y $$.
- Nunca uses Unicode matemático (∫, √, ∑, ∞, etc.) fuera de delimitadores LaTeX."""


class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    message_id: int


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Verificar que el usuario existe
    user = await db.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Guardar mensaje del usuario
    user_msg = ChatMessage(user_id=req.user_id, role="user", content=req.message)
    db.add(user_msg)
    await db.flush()

    # Recuperar historial reciente (últimos 10 mensajes)
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == req.user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    history = list(reversed(result.scalars().all()))

    # Construir mensajes para OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})

    # Llamar a OpenAI
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al contactar OpenAI: {str(e)}")

    # Guardar respuesta del asistente
    ai_msg = ChatMessage(user_id=req.user_id, role="assistant", content=reply_text)
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    return ChatResponse(reply=reply_text, message_id=ai_msg.id)


@router.get("/history/{user_id}")
async def get_history(user_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]


@router.delete("/history/{user_id}")
async def clear_history(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage).where(ChatMessage.user_id == user_id))
    for msg in result.scalars().all():
        await db.delete(msg)
    await db.commit()
    return {"message": "Historial eliminado"}
