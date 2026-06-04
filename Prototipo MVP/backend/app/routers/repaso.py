from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai import AsyncOpenAI
from app.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class RepasoRequest(BaseModel):
    topic: str
    tipo: str          # "preguntas" | "fichas" | "cuestionario"
    num_items: Optional[int] = 5


PROMPTS = {
    "preguntas": """Genera {n} preguntas de repaso abiertas sobre el tema: "{topic}".
Devuelve SOLO un JSON válido con esta estructura exacta:
{{
  "tipo": "preguntas",
  "tema": "{topic}",
  "items": [
    {{"pregunta": "...", "respuesta": "..."}}
  ]
}}
Sin texto adicional fuera del JSON.""",

    "fichas": """Genera {n} fichas de estudio (flashcards) sobre el tema: "{topic}".
Devuelve SOLO un JSON válido con esta estructura exacta:
{{
  "tipo": "fichas",
  "tema": "{topic}",
  "items": [
    {{"frente": "Término o concepto", "reverso": "Definición o explicación"}}
  ]
}}
Sin texto adicional fuera del JSON.""",

    "cuestionario": """Genera {n} preguntas de opción múltiple sobre el tema: "{topic}".
Devuelve SOLO un JSON válido con esta estructura exacta:
{{
  "tipo": "cuestionario",
  "tema": "{topic}",
  "items": [
    {{
      "pregunta": "...",
      "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correcta": "A",
      "explicacion": "..."
    }}
  ]
}}
Sin texto adicional fuera del JSON.""",
}


@router.post("/generate")
async def generate_repaso(req: RepasoRequest):
    if req.tipo not in PROMPTS:
        raise HTTPException(status_code=400, detail="Tipo debe ser: preguntas, fichas o cuestionario")

    num = max(1, min(req.num_items or 5, 15))
    prompt = PROMPTS[req.tipo].format(topic=req.topic, n=num)

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Eres un asistente educativo. Responde SOLO con JSON válido, sin markdown ni texto adicional."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        raw = response.choices[0].message.content.strip()
        # Limpiar markdown code blocks si el modelo los incluye
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        import json
        data = json.loads(raw)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error generando repaso: {str(e)}")
