# StudyAI

Asistente de estudio inteligente con planificación impulsada por IA. Permite a los estudiantes gestionar tareas, generar planes de estudio personalizados y consultar un asistente conversacional basado en OpenAI.

## Stack

| Capa           | Tecnología              |
| -------------- | ----------------------- |
| Frontend       | Vue 3 + Vite            |
| Backend        | FastAPI (Python)        |
| Base de datos  | PostgreSQL 16           |
| IA             | OpenAI API (gpt-4o-mini)|
| Infraestructura| Docker + Docker Compose |

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Clave de API de OpenAI

## Inicio rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd "Proyecto-LLM/Prototipo MVP"
```

### 2. Configurar variables de entorno

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env` y reemplaza tu clave de OpenAI:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Levantar los contenedores

```bash
docker compose up -d
```

### 4. Abrir la app

| Servicio        | URL                                      |
| --------------- | ---------------------------------------- |
| Frontend        | <http://localhost:5173>                  |
| Backend (docs)  | <http://localhost:8000/docs>             |

## Estructura del proyecto

```text
Prototipo MVP/
├── backend/
│   ├── app/
│   │   ├── routers/       # Endpoints: users, tasks, plan, chat
│   │   ├── config.py      # Variables de entorno
│   │   ├── database.py    # Conexión async a PostgreSQL
│   │   ├── main.py        # App FastAPI
│   │   └── models.py      # Modelos SQLAlchemy
│   ├── .env.example
│   └── requirements.txt
├── database/
│   └── schema.sql         # Esquema inicial + datos de prueba
├── frontend/
│   ├── src/
│   │   ├── components/    # MetricCard, TaskItem, WeekHeatmap, iconos
│   │   ├── views/         # Dashboard, StudyPlan, AIAssistant, Progress
│   │   ├── App.vue
│   │   └── main.js
│   └── vite.config.js
└── docker-compose.yml
```

## Variables de entorno

| Variable                      | Descripción                     | Default            |
| ----------------------------- | ------------------------------- | ------------------ |
| `OPENAI_API_KEY`              | Clave de la API de OpenAI       | —                  |
| `OPENAI_MODEL`                | Modelo a usar                   | `gpt-4o-mini`      |
| `SECRET_KEY`                  | Clave para firmar tokens JWT    | —                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token de sesión    | `10080` (7 días)   |
| `DATABASE_URL`                | Cadena de conexión a PostgreSQL | ver `.env.example` |

## Comandos útiles

```bash
# Ver logs de un servicio
docker compose logs backend
docker compose logs frontend
docker compose logs db

# Reiniciar un servicio
docker compose restart backend

# Apagar y borrar volúmenes (resetea la base de datos)
docker compose down -v
```
