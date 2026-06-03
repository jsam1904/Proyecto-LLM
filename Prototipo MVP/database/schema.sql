-- ============================================================
-- StudyPilot AI — Schema inicial
-- Las tablas también se crean automáticamente via SQLAlchemy
-- en app/main.py (Base.metadata.create_all). Este archivo
-- sirve como documentación y para inicializar un contenedor
-- fresco de PostgreSQL.
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    email      VARCHAR(255) UNIQUE NOT NULL,
    name       VARCHAR(255) NOT NULL,
    hashed_pw  VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    text       VARCHAR(500) NOT NULL,
    subject    VARCHAR(100),
    tag        VARCHAR(50),
    done       BOOLEAN DEFAULT FALSE,
    due_date   TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS study_plans (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_data  JSONB NOT NULL,
    ai_prompt  TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role       VARCHAR(20) NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS exams (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subject    VARCHAR(100) NOT NULL,
    exam_date  TIMESTAMPTZ NOT NULL,
    notes      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
