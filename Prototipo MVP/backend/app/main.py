from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import users, tasks, plan, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al iniciar
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="StudyAI API",
    description="Backend para la aplicación de planificación académica con IA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users",  tags=["Usuarios"])
app.include_router(tasks.router, prefix="/api/tasks",  tags=["Tareas"])
app.include_router(plan.router,  prefix="/api/plan",   tags=["Plan de estudio"])
app.include_router(chat.router,  prefix="/api/chat",   tags=["Asistente IA"])

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
