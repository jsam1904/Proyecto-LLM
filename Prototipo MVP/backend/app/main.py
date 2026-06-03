from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import users, tasks, plan, chat, exams, progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear todas las tablas al iniciar (incluye Exam)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="StudyPilot AI API",
    description="Backend para la aplicación de planificación académica con IA",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router,    prefix="/api/users",    tags=["Usuarios"])
app.include_router(tasks.router,    prefix="/api/tasks",    tags=["Tareas"])
app.include_router(plan.router,     prefix="/api/plan",     tags=["Plan de estudio"])
app.include_router(chat.router,     prefix="/api/chat",     tags=["Asistente IA"])
app.include_router(exams.router,    prefix="/api/exams",    tags=["Exámenes"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progreso"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.1.0"}
