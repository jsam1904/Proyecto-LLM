-- ============================================================
-- StudyAI — Esquema PostgreSQL (MVP)
-- Ejecutar como: psql -U postgres -f schema.sql
-- ============================================================

-- Habilitar extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- búsqueda de texto

-- ============================================================
-- TABLA: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    hashed_pw   VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users (email);

-- ============================================================
-- TABLA: tasks
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text        VARCHAR(500) NOT NULL,
    subject     VARCHAR(100),
    tag         VARCHAR(50),
    done        BOOLEAN DEFAULT FALSE,
    due_date    TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id   ON tasks (user_id);
CREATE INDEX idx_tasks_done      ON tasks (user_id, done);

-- ============================================================
-- TABLA: study_plans
-- Usa JSONB para almacenar el plan generado por IA
-- ============================================================
CREATE TABLE IF NOT EXISTS study_plans (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_data   JSONB NOT NULL,         -- Plan completo en formato JSON
    ai_prompt   TEXT,                   -- Prompt enviado a OpenAI (para auditoría)
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_plans_user_id  ON study_plans (user_id);
CREATE INDEX idx_plans_jsonb    ON study_plans USING GIN (plan_data);

-- ============================================================
-- TABLA: chat_messages
-- Historial de conversaciones con el asistente IA
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_user_id ON chat_messages (user_id, created_at DESC);

-- ============================================================
-- DATOS DE PRUEBA (seed)
-- ============================================================
INSERT INTO users (email, name, hashed_pw) VALUES
    ('maria@estudiante.edu', 'María González',
     '$2b$12$examplehashedpasswordforseeding000000000000000');

INSERT INTO tasks (user_id, text, subject, tag, done) VALUES
    (1, 'Leer cap. 5 de BD relacionales',    'Base de Datos',          'BD',      TRUE),
    (1, 'Resolver ejercicios de integrales',  'Cálculo II',             'Cálculo', FALSE),
    (1, 'Implementar CRUD en Python/Flask',   'Programación',           'Prog',    FALSE),
    (1, 'Revisar notas de IA — modelos LLM',  'Inteligencia Artificial','IA',      TRUE);

INSERT INTO study_plans (user_id, plan_data) VALUES (
    1,
    '{
        "week_start": "2025-03-24",
        "days": [
            {
                "name": "Lunes",
                "slots": [
                    {"time": "7:00 – 8:30",   "subject": "Cálculo II",         "tag": "Cálculo", "duration": 90},
                    {"time": "10:00 – 11:30",  "subject": "Programación",       "tag": "Prog",    "duration": 90},
                    {"time": "15:00 – 17:00",  "subject": "Base de Datos",      "tag": "BD",      "duration": 120}
                ]
            },
            {
                "name": "Martes",
                "slots": [
                    {"time": "8:00 – 9:30",    "subject": "Inteligencia Artificial", "tag": "IA",      "duration": 90},
                    {"time": "14:00 – 15:30",  "subject": "Cálculo II",              "tag": "Cálculo", "duration": 90}
                ]
            },
            {"name": "Miércoles", "slots": []},
            {"name": "Jueves",    "slots": []},
            {"name": "Viernes",   "slots": []},
            {"name": "Sábado",    "slots": []},
            {"name": "Domingo",   "slots": []}
        ]
    }'::jsonb
);
