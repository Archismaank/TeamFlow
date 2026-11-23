# ⚡ TeamFlow — Real-Time Collaborative Workspace & Project Management Engine

> **High-velocity collaborative workspace designed to streamline sprint execution, organize multi-tenant projects, and synchronize Kanban boards in real time.**

---

## 📖 Overview

**TeamFlow** bridges the gap between high-level project roadmaps and day-to-day agile execution. It brings your entire team into a unified, high-contrast, real-time workspace:
- Create and organize multi-tenant workspaces with granular **Role-Based Access Control (RBAC)**.
- Manage initiatives across milestone-driven projects with live completion analytics.
- Coordinate tasks effortlessly on an interactive **Kanban Board** with drag-and-drop state transitions.
- Collaborate synchronously with teammate status updates and discussions powered by **native WebSockets**.
- Enjoy a responsive, distraction-free **Editorial UI** with seamless **Dark/Light** theme switching.

---

## ✨ Key Features

### 🏢 Multi-Tenant Workspaces & RBAC
- Create multiple independent team workspaces.
- Invite members by email and assign granular permissions: **Owner**, **Admin**, **Member**, and **Viewer**.
- Enforce strict route-level permission dependencies and cascade deletions.

### 📊 Project Tracking & Live Progress Metrics
- Group work into projects with descriptions and target completion deadlines.
- Real-time computation of project health: total tasks, status stage distribution, overdue task counts, and completion percentage.

### 📋 Interactive Kanban Board
- Drag-and-drop tasks across four distinct stages: `To Do`, `In Progress`, `In Review`, and `Done`.
- Prioritize tasks with color-coded urgency: `LOW`, `MEDIUM`, `HIGH`, and `URGENT`.
- Assign teammates and set deadline timestamps.

### ⚡ Real-Time WebSocket Synchronization
- Dedicated per-project WebSocket channels (`/api/ws/projects/{project_id}`).
- Instant state propagation: when a teammate creates, edits, moves a task, or posts a comment, all connected clients update immediately without a page refresh.

### 💬 In-Task Collaboration
- Built-in contextual commenting stream for continuous discussion and feedback on each task.

### 🔒 Enterprise-Grade Security
- Password hashing using `Passlib` and `Bcrypt`.
- Stateless authentication using cryptographically signed **JWT (JSON Web Tokens)**.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12) | Asynchronous RESTful API, dependency injection, and native WebSockets. |
| **Database & ORM** | [PostgreSQL](https://www.postgresql.org/) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Async ORM powered by the `asyncpg` driver for maximum I/O concurrency. |
| **Database Migrations**| [Alembic](https://alembic.sqlalchemy.org/) | Version-controlled, reproducible schema migrations. |
| **Real-Time Pub/Sub** | Native WebSockets | In-memory `ProjectConnectionManager` for broadcast messaging. |
| **Authentication** | [python-jose](https://github.com/mpdavis/python-jose) + [passlib](https://passlib.readthedocs.io/) | JWT bearer tokens & Bcrypt password hashing. |
| **Frontend** | Vanilla ES6+ JavaScript, HTML5, CSS3 | Custom CSS variable design tokens, responsive layout, Dark/Light modes. |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | Lightning-fast ASGI web server implementation. |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer ["Client Layer (Browser)"]
        UI["Web UI (HTML5, CSS3, ES6+ JS)"]
        WS_Client["WebSocket Client"]
        HTTP_Client["Fetch REST API Client"]
    end

    subgraph ServerLayer ["Application Layer (FastAPI / Uvicorn)"]
        Router["FastAPI App Core & Static Files Mount"]
        AuthMiddleware["JWT Auth & RBAC Guard"]
        APIs["API Routers: Auth | Workspaces | Projects | Tasks"]
        WS_Manager["WebSocket Connection Manager"]
    end

    subgraph DataLayer ["Data & Persistence Layer"]
        AsyncSession["SQLAlchemy 2.0 (AsyncSession / asyncpg)"]
        Postgres[("PostgreSQL Database")]
    end

    UI --> HTTP_Client
    UI --> WS_Client
    HTTP_Client -->|HTTP / REST (Bearer JWT)| Router
    WS_Client <-->|Full-Duplex WS Connection| WS_Manager
    Router --> AuthMiddleware
    AuthMiddleware --> APIs
    APIs --> AsyncSession
    AsyncSession <-->|SQL Queries / Transactions| Postgres
    APIs -->|Broadcast Events| WS_Manager
    WS_Manager -->|Live Sync Events| WS_Client
```

---

## 🗄️ Database Schema (Entity Relationship)

```mermaid
erDiagram
    User ||--o{ WorkspaceMember : "has memberships"
    User ||--o{ Workspace : "owns"
    User ||--o{ Task : "assigned to"
    User ||--o{ Comment : "authors"

    Workspace ||--o{ WorkspaceMember : "contains"
    Workspace ||--o{ Project : "organizes"

    Project ||--o{ Task : "tracks"
    Task ||--o{ Comment : "contains"

    User {
        UUID id PK
        string email UK
        string password_hash
        string full_name
        datetime created_at
    }

    Workspace {
        UUID id PK
        string name
        UUID owner_id FK
        datetime created_at
    }

    WorkspaceMember {
        UUID workspace_id PK,FK
        UUID user_id PK,FK
        enum role "OWNER, ADMIN, MEMBER, VIEWER"
    }

    Project {
        UUID id PK
        UUID workspace_id FK
        string name
        text description
        date target_end_date
        datetime created_at
    }

    Task {
        UUID id PK
        UUID project_id FK
        string title
        text description
        enum status "TODO, IN_PROGRESS, IN_REVIEW, DONE"
        enum priority "LOW, MEDIUM, HIGH, URGENT"
        UUID assignee_id FK
        datetime due_date
        int position
        datetime created_at
    }

    Comment {
        UUID id PK
        UUID task_id FK
        UUID author_id FK
        text content
        datetime created_at
    }
```

---

## 📁 Project Directory Structure

```text
TeamFlow/
├── alembic/                 # Database migration scripts & environment
│   ├── versions/            # Migration revisions (initial schema, etc.)
│   └── env.py               # Async Alembic runner
├── app/
│   ├── api/                 # REST API & WebSocket route handlers
│   │   ├── auth.py          # User registration, login, JWT token issue
│   │   ├── workspaces.py    # Workspace CRUD, membership & role management
│   │   ├── projects.py      # Project tracking, progress analytics
│   │   └── tasks.py         # Task CRUD, status updates, comments, WS endpoint
│   ├── core/                # Application configuration & core utilities
│   │   ├── config.py        # Pydantic BaseSettings (.env loading)
│   │   ├── database.py      # Async SQLAlchemy engine & session factory
│   │   ├── permissions.py   # RBAC & workspace membership security guards
│   │   ├── security.py      # Bcrypt password hashing & JWT token verification
│   │   └── ws.py            # Central WebSocket ProjectConnectionManager
│   ├── models/              # SQLAlchemy ORM declarative models
│   │   └── models.py        # Users, Workspaces, Members, Projects, Tasks, Comments
│   ├── schemas/             # Pydantic schemas for request/response validation
│   │   ├── auth.py
│   │   ├── workspace.py
│   │   ├── project.py
│   │   └── task.py
│   └── main.py              # FastAPI application factory & static files mount
├── frontend/                # Single-Page Application (SPA) client
│   ├── css/
│   │   └── styles.css       # Editorial styling, animations, dark/light theme
│   ├── js/
│   │   ├── api.js           # REST API client & auth token interceptor
│   │   ├── app.js           # View router, state management, modal controllers
│   │   ├── board.js         # Interactive Kanban drag-and-drop & WebSocket listener
│   │   └── ui.js            # Toast notifications, theme toggles, helpers
│   └── index.html           # Main application HTML interface
├── .env.example             # Template for environment variables
├── alembic.ini              # Alembic migration configuration
├── pyproject.toml           # Project dependencies & metadata
├── requirements.txt         # Pip dependency manifest
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.12+**
- **PostgreSQL** (running locally or via Docker/cloud provider)
- **uv** (recommended) or standard `pip`

---

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/your-username/TeamFlow.git
cd TeamFlow

# Create and activate a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# OR with uv:
uv pip install -r requirements.txt
```

---

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database connection (PostgreSQL + asyncpg driver)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/teamflow

# Cryptographically secure random secret key for JWT signing
SECRET_KEY=e83a9f4c0b62d85b1a774620f49a62c5c46e3d12f1e6b8c9d0124a5e3f789ab1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Tip:** You can generate a fresh secret key anytime using:  
> `python -c "import secrets; print(secrets.token_hex(32))"`

---

### 4. Run Database Migrations

Apply the initial schema to your PostgreSQL database using Alembic:

```bash
alembic upgrade head
```

---

### 5. Launch the Application

Start the Uvicorn ASGI server:

```bash
uvicorn app.main:app --reload --port 8000
```

- 🌐 **Web Interface:** Open [http://localhost:8000](http://localhost:8000) in your browser.
- 📚 **Interactive API Docs (Swagger UI):** Open [http://localhost:8000/docs](http://localhost:8000/docs).
- 📖 **Alternative API Docs (ReDoc):** Open [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 📡 REST API Reference

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register a new user account |
| `POST` | `/api/auth/login` | Authenticate with credentials and receive a JWT access token |
| `GET` | `/api/auth/me` | Fetch currently authenticated user profile |

### Workspaces (`/api/workspaces`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/workspaces` | Create a new workspace (creator automatically becomes `OWNER`) |
| `GET` | `/api/workspaces` | List all workspaces the current user belongs to |
| `GET` | `/api/workspaces/{id}/members` | List members of a workspace |
| `POST` | `/api/workspaces/{id}/members` | Invite a member by email and assign role (`ADMIN`, `MEMBER`, `VIEWER`) |
| `PATCH`| `/api/workspaces/{id}/members/{user_id}` | Update a member's role (`OWNER`/`ADMIN` only) |
| `DELETE`| `/api/workspaces/{id}/members/{user_id}` | Remove a member from the workspace (`OWNER`/`ADMIN` only) |

### Projects (`/api`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/workspaces/{id}/projects` | Create a new project within a workspace |
| `GET` | `/api/workspaces/{id}/projects` | List projects with real-time completion progress metrics |
| `GET` | `/api/projects/{id}` | Get detailed project view with task lists and progress |
| `PATCH`| `/api/projects/{id}` | Update project metadata or target end date |
| `DELETE`| `/api/projects/{id}` | Delete project and cascade-delete all associated tasks |

### Tasks & Real-Time Sync (`/api`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/projects/{id}/tasks` | Create a task and broadcast event to all connected peers |
| `PATCH`| `/api/tasks/{id}` | Update status (`TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`), priority, or details |
| `DELETE`| `/api/tasks/{id}` | Delete task and broadcast deletion |
| `POST` | `/api/tasks/{id}/comments` | Post a comment on a task card and broadcast to project |
| `WS` | `/api/ws/projects/{id}` | Full-duplex WebSocket connection for real-time live board synchronization |

---

## 🔮 Roadmap / Future Enhancements

- [ ] **Cloud File Attachments**: Asset uploads and design attachments powered by Amazon S3 / Cloudflare R2.
- [ ] **Sprint Burndown & Gantt Timeline**: Dynamic charts tracking team velocity and milestones.
- [ ] **Push & Email Alerts**: Real-time notifications for task assignments and upcoming deadlines.
- [ ] **GitHub / GitLab Integration**: Automatically transition tasks to `Done` upon pull request merge.
- [ ] **Mobile Application**: Native React Native / Flutter client with offline synchronization.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
