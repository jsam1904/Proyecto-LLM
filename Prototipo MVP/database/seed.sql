-- ============================================================
-- StudyAI — Datos de prueba (seed)
-- Ejecutar DESPUÉS de schema.sql
--
-- Usuarios demo:
--   alumno@demo.com  /  demo1234
--   carlos@demo.com  /  demo1234
--
-- Cómo ejecutarlo:
--   psql -U studyai -d studyai_db -f database/seed.sql
--   o con Docker:
--   docker exec -i studyai_db psql -U studyai -d studyai_db < database/seed.sql
-- ============================================================

-- pgcrypto para generar hashes bcrypt directamente en SQL
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Limpiar datos previos (orden inverso por foreign keys)
TRUNCATE TABLE chat_messages, exams, study_plans, tasks, users
    RESTART IDENTITY CASCADE;

-- ─────────────────────────────────────────────────────────────
-- USUARIOS
-- ─────────────────────────────────────────────────────────────
INSERT INTO users (email, name, hashed_pw, created_at) VALUES
(
    'alumno@demo.com',
    'Ana García',
    crypt('demo1234', gen_salt('bf', 12)),
    NOW() - INTERVAL '30 days'
),
(
    'carlos@demo.com',
    'Carlos López',
    crypt('demo1234', gen_salt('bf', 12)),
    NOW() - INTERVAL '15 days'
);

-- ─────────────────────────────────────────────────────────────
-- TAREAS  (user_id = 1 → Ana, user_id = 2 → Carlos)
-- ─────────────────────────────────────────────────────────────
INSERT INTO tasks (user_id, text, subject, tag, done, due_date, created_at) VALUES

-- Ana García
(1, 'Resolver ejercicios del capítulo 5 de integrales',   'Cálculo II',      'ejercicio', FALSE, NOW() + INTERVAL '2 days',  NOW() - INTERVAL '3 days'),
(1, 'Leer páginas 80-110 de Mecánica Clásica',            'Física',          'lectura',   FALSE, NOW() + INTERVAL '4 days',  NOW() - INTERVAL '2 days'),
(1, 'Entregar práctica de laboratorio — circuitos RC',    'Física',          'tarea',     TRUE,  NOW() - INTERVAL '1 day',   NOW() - INTERVAL '7 days'),
(1, 'Estudiar teoremas de límites para el parcial',       'Cálculo II',      'repaso',    FALSE, NOW() + INTERVAL '1 day',   NOW() - INTERVAL '1 day'),
(1, 'Avanzar módulo 3 del curso de Python',               'Programación',    'proyecto',  FALSE, NOW() + INTERVAL '6 days',  NOW() - INTERVAL '5 days'),
(1, 'Hacer resumen de la Revolución Industrial',          'Historia',        'lectura',   TRUE,  NOW() - INTERVAL '3 days',  NOW() - INTERVAL '10 days'),
(1, 'Practicar problemas de estequiometría',              'Química',         'ejercicio', FALSE, NOW() + INTERVAL '3 days',  NOW() - INTERVAL '1 day'),

-- Carlos López
(2, 'Resolver 20 problemas de derivadas implícitas',      'Cálculo I',       'ejercicio', FALSE, NOW() + INTERVAL '3 days',  NOW() - INTERVAL '2 days'),
(2, 'Leer capítulo 4 de Introducción a la Economía',      'Microeconomía',   'lectura',   FALSE, NOW() + INTERVAL '5 days',  NOW() - INTERVAL '1 day'),
(2, 'Entregar reporte de lectura — El proceso penal',     'Derecho Procesal','tarea',     TRUE,  NOW() - INTERVAL '2 days',  NOW() - INTERVAL '9 days'),
(2, 'Repasar tablas de verdad y lógica proposicional',    'Matemáticas',     'repaso',    FALSE, NOW() + INTERVAL '2 days',  NOW() - INTERVAL '3 days'),
(2, 'Terminar ensayo sobre oferta y demanda',             'Microeconomía',   'proyecto',  FALSE, NOW() + INTERVAL '7 days',  NOW() - INTERVAL '4 days'),
(2, 'Ver tutoriales de álgebra lineal (matrices)',        'Álgebra Lineal',  'lectura',   TRUE,  NOW() - INTERVAL '5 days',  NOW() - INTERVAL '12 days');

-- ─────────────────────────────────────────────────────────────
-- PLANES DE ESTUDIO
-- ─────────────────────────────────────────────────────────────
INSERT INTO study_plans (user_id, plan_data, ai_prompt, created_at) VALUES
(
    1,
    '{
        "week_start": "2026-05-18",
        "days": [
            {
                "name": "Lunes",
                "slots": [
                    {"time": "7:00–8:30",  "subject": "Cálculo II",   "tag": "ejercicio", "duration": 90},
                    {"time": "19:00–20:00","subject": "Programación",  "tag": "proyecto",  "duration": 60}
                ]
            },
            {
                "name": "Martes",
                "slots": [
                    {"time": "8:00–9:30",  "subject": "Física",        "tag": "lectura",   "duration": 90},
                    {"time": "18:00–19:00","subject": "Historia",       "tag": "repaso",    "duration": 60}
                ]
            },
            {
                "name": "Miércoles",
                "slots": [
                    {"time": "7:00–9:00",  "subject": "Cálculo II",   "tag": "repaso",    "duration": 120},
                    {"time": "19:00–20:00","subject": "Química",       "tag": "ejercicio", "duration": 60}
                ]
            },
            {
                "name": "Jueves",
                "slots": [
                    {"time": "8:00–9:30",  "subject": "Física",        "tag": "ejercicio", "duration": 90},
                    {"time": "18:30–19:30","subject": "Programación",  "tag": "proyecto",  "duration": 60}
                ]
            },
            {
                "name": "Viernes",
                "slots": [
                    {"time": "7:00–8:00",  "subject": "Química",       "tag": "lectura",   "duration": 60},
                    {"time": "17:00–18:30","subject": "Cálculo II",   "tag": "ejercicio", "duration": 90}
                ]
            },
            {
                "name": "Sábado",
                "slots": [
                    {"time": "9:00–11:00", "subject": "Repaso general","tag": "repaso",    "duration": 120}
                ]
            },
            {
                "name": "Domingo",
                "slots": []
            }
        ]
    }',
    'Tengo parcial de Cálculo II el viernes y entrega de práctica de Física el martes. Prefiero estudiar en las mañanas entre 7am y 9am, y en las noches después de las 6pm. No puedo el domingo.',
    NOW() - INTERVAL '7 days'
),
(
    2,
    '{
        "week_start": "2026-05-18",
        "days": [
            {
                "name": "Lunes",
                "slots": [
                    {"time": "9:00–10:30", "subject": "Cálculo I",      "tag": "ejercicio", "duration": 90},
                    {"time": "20:00–21:00","subject": "Microeconomía",  "tag": "lectura",   "duration": 60}
                ]
            },
            {
                "name": "Martes",
                "slots": [
                    {"time": "10:00–11:30","subject": "Derecho Procesal","tag": "lectura",  "duration": 90},
                    {"time": "19:00–20:00","subject": "Álgebra Lineal", "tag": "repaso",    "duration": 60}
                ]
            },
            {
                "name": "Miércoles",
                "slots": [
                    {"time": "9:00–10:30", "subject": "Cálculo I",      "tag": "repaso",    "duration": 90},
                    {"time": "20:00–21:30","subject": "Microeconomía",  "tag": "proyecto",  "duration": 90}
                ]
            },
            {
                "name": "Jueves",
                "slots": [
                    {"time": "10:00–11:00","subject": "Álgebra Lineal", "tag": "ejercicio", "duration": 60},
                    {"time": "19:00–20:00","subject": "Derecho Procesal","tag": "repaso",   "duration": 60}
                ]
            },
            {
                "name": "Viernes",
                "slots": [
                    {"time": "9:00–11:00", "subject": "Cálculo I",      "tag": "ejercicio", "duration": 120}
                ]
            },
            {
                "name": "Sábado",
                "slots": [
                    {"time": "10:00–12:00","subject": "Repaso general", "tag": "repaso",    "duration": 120}
                ]
            },
            {
                "name": "Domingo",
                "slots": []
            }
        ]
    }',
    'Tengo examen de Cálculo I la próxima semana. Estudio mejor en las mañanas a partir de las 9am. Los miércoles en la noche quiero avanzar el ensayo de Microeconomía.',
    NOW() - INTERVAL '5 days'
);

-- ─────────────────────────────────────────────────────────────
-- MENSAJES DE CHAT
-- ─────────────────────────────────────────────────────────────
INSERT INTO chat_messages (user_id, role, content, created_at) VALUES

-- Ana García — conversación sobre Cálculo
(1, 'user',      '¿Me puedes explicar qué es una integral impropia?', NOW() - INTERVAL '5 days'),
(1, 'assistant', 'Claro, Ana. Una integral impropia es una integral definida donde el intervalo de integración es infinito o donde la función tiene una discontinuidad infinita dentro del intervalo. Por ejemplo, ∫₁^∞ (1/x²) dx es impropia porque el límite superior es infinito. Para resolverla, la reescribimos como un límite: lím(b→∞) ∫₁^b (1/x²) dx = lím(b→∞) [-1/x]₁^b = lím(b→∞) (-1/b + 1) = 1. ¿Quieres que practiquemos más ejemplos?', NOW() - INTERVAL '5 days' + INTERVAL '1 minute'),
(1, 'user',      'Sí por favor, dame un ejemplo de integral impropia con discontinuidad.', NOW() - INTERVAL '5 days' + INTERVAL '3 minutes'),
(1, 'assistant', 'Perfecto. Considera ∫₀^1 (1/√x) dx. La función 1/√x tiene una discontinuidad en x=0 (tiende a infinito). La resolvemos así:\n\nlím(a→0⁺) ∫ₐ^1 x^(-1/2) dx\n= lím(a→0⁺) [2√x]ₐ^1\n= lím(a→0⁺) (2√1 - 2√a)\n= 2 - 0 = 2\n\nEsta integral converge a 2. Cuando el límite existe y es finito, decimos que la integral impropia converge. ¿Te queda más claro?', NOW() - INTERVAL '5 days' + INTERVAL '4 minutes'),

-- Ana García — conversación sobre el parcial
(1, 'user',      'Tengo parcial de Cálculo II en 3 días, ¿qué temas debería repasar primero?', NOW() - INTERVAL '1 day'),
(1, 'assistant', '¡Claro que sí! Basándome en los temas típicos de Cálculo II, te recomiendo este orden de repaso:\n\n1. **Técnicas de integración** (sustitución, por partes, fracciones parciales) — estas son la base de todo.\n2. **Integrales impropias** — que ya estuvimos viendo.\n3. **Series y sucesiones** — criterios de convergencia (razón, raíz, comparación).\n4. **Serie de Taylor y Maclaurin** — aplicaciones frecuentes.\n\nDada tu semana, te sugiero dedicar hoy a técnicas de integración y mañana a series. ¿Sobre cuál quieres empezar a practicar?', NOW() - INTERVAL '1 day' + INTERVAL '2 minutes'),

-- Carlos López — conversación sobre derivadas
(2, 'user',      '¿Cuál es la diferencia entre derivada implícita y explícita?', NOW() - INTERVAL '4 days'),
(2, 'assistant', 'Buena pregunta, Carlos. La diferencia principal está en cómo está expresada la función:\n\n**Función explícita:** y está despejada en términos de x. Ejemplo: y = x² + 3x. Derivas directamente: dy/dx = 2x + 3.\n\n**Función implícita:** y no está despejada, está mezclada con x. Ejemplo: x² + y² = 25 (círculo). Para derivar, aplicas la regla de la cadena a cada término respecto a x:\n2x + 2y(dy/dx) = 0 → dy/dx = -x/y\n\n¿Quieres practicar con algunos ejemplos de derivada implícita?', NOW() - INTERVAL '4 days' + INTERVAL '1 minute'),
(2, 'user',      'Sí, dame un ejemplo más difícil con producto de funciones.', NOW() - INTERVAL '4 days' + INTERVAL '5 minutes'),
(2, 'assistant', 'Perfecto, aquí va uno que combina producto y función implícita:\n\nDerива x²y + y³ = 10\n\nDerivamos término a término respecto a x:\n- Término x²y: usamos regla del producto → 2x·y + x²·(dy/dx)\n- Término y³: regla de la cadena → 3y²·(dy/dx)\n- Constante 10: → 0\n\nQueda: 2xy + x²(dy/dx) + 3y²(dy/dx) = 0\n\nDespejamos dy/dx:\n(dy/dx)(x² + 3y²) = -2xy\ndy/dx = -2xy / (x² + 3y²)\n\n¿Lo intentas con x³ + 2xy² = 8?', NOW() - INTERVAL '4 days' + INTERVAL '6 minutes');

-- ─────────────────────────────────────────────────────────────
-- EXÁMENES
-- ─────────────────────────────────────────────────────────────
INSERT INTO exams (user_id, subject, exam_date, notes, created_at) VALUES

-- Ana García
(1, 'Cálculo II',
    NOW() + INTERVAL '3 days',
    'Parcial 2 — Integrales impropias, técnicas de integración (sustitución trigonométrica, fracciones parciales), series numéricas. Revisar lista de fórmulas que dejó el profesor.',
    NOW() - INTERVAL '10 days'),
(1, 'Física',
    NOW() + INTERVAL '10 days',
    'Examen final — Electromagnetismo: Ley de Faraday, circuitos RLC, ondas electromagnéticas. Traer calculadora científica.',
    NOW() - INTERVAL '8 days'),
(1, 'Química',
    NOW() + INTERVAL '17 days',
    'Parcial 3 — Estequiometría avanzada y equilibrio químico. Estudiar problemas del libro de Petrucci caps. 4-6.',
    NOW() - INTERVAL '5 days'),

-- Carlos López
(2, 'Cálculo I',
    NOW() + INTERVAL '5 days',
    'Examen final — Derivadas (incluyendo implícita), aplicaciones (máximos/mínimos, regla de L''Hôpital), introducción a integrales. El 40% del examen son problemas aplicados.',
    NOW() - INTERVAL '12 days'),
(2, 'Microeconomía',
    NOW() + INTERVAL '12 days',
    'Parcial 2 — Elasticidad, estructuras de mercado (competencia perfecta, monopolio, oligopolio). Incluye ensayo breve de 1 página en el examen.',
    NOW() - INTERVAL '7 days'),
(2, 'Álgebra Lineal',
    NOW() + INTERVAL '19 days',
    'Parcial 2 — Matrices, determinantes, sistemas de ecuaciones lineales, espacios vectoriales.',
    NOW() - INTERVAL '3 days');

-- ─────────────────────────────────────────────────────────────
-- Verificación final
-- ─────────────────────────────────────────────────────────────
SELECT
    'users'         AS tabla, COUNT(*) AS filas FROM users         UNION ALL
SELECT 'tasks',                                  COUNT(*)          FROM tasks         UNION ALL
SELECT 'study_plans',                            COUNT(*)          FROM study_plans   UNION ALL
SELECT 'chat_messages',                          COUNT(*)          FROM chat_messages UNION ALL
SELECT 'exams',                                  COUNT(*)          FROM exams
ORDER BY tabla;
