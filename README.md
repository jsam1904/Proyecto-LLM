# StudyAI

Asistente de estudio inteligente con planificación impulsada por IA. Permite a los estudiantes gestionar tareas, generar planes de estudio personalizados y consultar un asistente conversacional basado en OpenAI.

## Stack

| Capa            | Tecnología               |
| --------------- | ------------------------ |
| Frontend        | Vue 3 + Vite             |
| Backend         | FastAPI (Python)         |
| Base de datos   | PostgreSQL 16            |
| IA              | OpenAI API (gpt-4o-mini) |
| Autenticación   | JWT + bcrypt             |
| Infraestructura | Docker + Docker Compose  |

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

| Servicio       | URL                          |
| -------------- | ---------------------------- |
| Frontend       | <http://localhost:5173>      |
| Backend (docs) | <http://localhost:8000/docs> |

> La primera vez que levantes los contenedores, el backend espera a que PostgreSQL esté saludable antes de arrancar (healthcheck configurado).

---

## Estructura del proyecto

```text
Prototipo MVP/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── users.py   # Registro, login (JWT) y perfil
│   │   │   ├── tasks.py   # CRUD de tareas
│   │   │   ├── plan.py    # Generación de plan semanal con IA
│   │   │   └── chat.py    # Asistente conversacional (OpenAI)
│   │   ├── config.py      # Variables de entorno (Pydantic Settings)
│   │   ├── database.py    # Conexión async a PostgreSQL (SQLAlchemy)
│   │   ├── main.py        # App FastAPI + registro de routers
│   │   └── models.py      # Modelos ORM: User, Task, StudyPlan, ChatMessage
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── schema.sql         # Esquema inicial + datos de prueba
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MetricCard.vue      # Tarjeta de métrica en el Dashboard
│   │   │   ├── TaskItem.vue        # Ítem individual de tarea
│   │   │   ├── AddTaskModal.vue    # Modal para crear nueva tarea
│   │   │   ├── ProgressRow.vue     # Fila de progreso por materia
│   │   │   ├── WeekHeatmap.vue     # Heatmap semanal de horas de estudio
│   │   │   └── icons/             # Íconos SVG (Grid, Calendar, Chat, Chart)
│   │   ├── views/
│   │   │   ├── Login.vue          # Pantalla de login / registro
│   │   │   ├── Dashboard.vue      # Vista principal con tareas y métricas
│   │   │   ├── StudyPlan.vue      # Generador y visualizador de plan semanal
│   │   │   ├── AIAssistant.vue    # Chat con el asistente IA
│   │   │   └── Progress.vue       # Seguimiento de progreso por materia
│   │   ├── App.vue
│   │   └── main.js
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml
└── docker-compose.example.yml
```

---

## API Endpoints

### Usuarios (`/api/users`)

| Método | Ruta        | Descripción                             | Auth |
| ------ | ----------- | --------------------------------------- | ---- |
| POST   | `/register` | Crear cuenta nueva (email + contraseña) | No   |
| POST   | `/login`    | Iniciar sesión → devuelve JWT           | No   |
| GET    | `/me`       | Obtener perfil del usuario actual       | Sí   |

### Tareas (`/api/tasks`)

| Método | Ruta         | Descripción                |
| ------ | ------------ | -------------------------- |
| GET    | `/{user_id}` | Listar tareas del usuario  |
| POST   | `/`          | Crear nueva tarea          |
| PATCH  | `/{task_id}` | Actualizar tarea (parcial) |
| DELETE | `/{task_id}` | Eliminar tarea             |

### Plan de estudio (`/api/plan`)

| Método | Ruta                | Descripción                        |
| ------ | ------------------- | ---------------------------------- |
| POST   | `/generate`         | Generar plan semanal con IA        |
| GET    | `/{user_id}/latest` | Obtener el plan más reciente       |
| GET    | `/{user_id}/all`    | Listar todos los planes guardados  |

### Chat IA (`/api/chat`)

| Método | Ruta                 | Descripción                        |
| ------ | -------------------- | ---------------------------------- |
| POST   | `/message`           | Enviar mensaje al asistente        |
| GET    | `/history/{user_id}` | Obtener historial de conversación  |
| DELETE | `/history/{user_id}` | Limpiar historial                  |

---

## Variables de entorno

| Variable                        | Descripción                       | Default                   |
| ------------------------------- | --------------------------------- | ------------------------- |
| `OPENAI_API_KEY`                | Clave de la API de OpenAI         | —                         |
| `OPENAI_MODEL`                  | Modelo a usar                     | `gpt-4o-mini`             |
| `SECRET_KEY`                    | Clave para firmar tokens JWT      | —                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | Duración del token de sesión      | `10080` (7 días)          |
| `DATABASE_URL`                  | Cadena de conexión a PostgreSQL   | ver `.env.example`        |

---

## Desarrollo con hot-reload

Los contenedores tienen configurado **Docker Compose Watch** para sincronizar cambios en tiempo real sin reiniciar:

```bash
docker compose watch
```

| Servicio | Carpeta vigilada | Efecto                  |
| -------- | ---------------- | ----------------------- |
| backend  | `./backend`      | Sincroniza a `/app`     |
| frontend | `./frontend/src` | Sincroniza a `/app/src` |

---

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

# Reconstruir imágenes tras cambiar dependencias
docker compose build --no-cache
```
