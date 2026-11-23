
# ⚡ TeamFlow — Real-Time Collaborative Workspace & Project Management Engine

> **High-velocity collaborative workspace designed to streamline sprint execution, organize multi-tenant projects, and synchronize Kanban boards in real time.**

---

## 📖 Overview

**TeamFlow** bridges the gap between high-level project roadmaps and day-to-day agile execution. It brings your entire team into a unified, high-contrast, real-time workspace:

- Create and organize multiple independent team workspaces with granular **Role-Based Access Control (RBAC)**.
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
- Real-time computation of project health:
  - Total tasks.
  - Status stage distribution.
  - Overdue task counts.
  - Completion percentage.

### 📋 Interactive Kanban Board

- Drag-and-drop tasks across four distinct stages:
  - `To Do`
  - `In Progress`
  - `In Review`
  - `Done`
- Prioritize tasks with color-coded urgency:
  - `LOW`
  - `MEDIUM`
  - `HIGH`
  - `URGENT`
- Assign teammates and set deadline timestamps.

### ⚡ Real-Time WebSocket Synchronization

- Dedicated per-project WebSocket channels: `/api/ws/projects/{project_id}`.
- Instant state propagation: when a teammate creates, edits, moves a task, or posts a comment, all connected clients update immediately without a page refresh.

### 💬 In-Task Collaboration

- Built-in contextual commenting stream for continuous discussion and feedback on each task.
- Keep conversations organized around individual tasks.

### 🔒 Enterprise-Grade Security

- Password hashing using `Passlib` and `Bcrypt`.
- Stateless authentication using cryptographically signed **JWT (JSON Web Tokens)**.
- Role-based access control for workspace operations.
- Protected API endpoints using authentication and authorization dependencies.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.12) | Asynchronous RESTful API, dependency injection, and native WebSockets. |
| **Database & ORM** | PostgreSQL + SQLAlchemy 2.0 | Async ORM powered by the `asyncpg` driver for I/O concurrency. |
| **Database Migrations** | Alembic | Version-controlled, reproducible schema migrations. |
| **Real-Time Communication** | Native WebSockets | In-memory `ProjectConnectionManager` for broadcast messaging. |
| **Authentication** | python-jose + Passlib | JWT bearer tokens and Bcrypt password hashing. |
| **Frontend** | Vanilla ES6+ JavaScript, HTML5, CSS3 | Custom CSS variable design tokens, responsive layout, and Dark/Light modes. |
| **ASGI Server** | Uvicorn | ASGI web server implementation. |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["Client Layer - Browser"]
        UI["Web UI - HTML5, CSS3, ES6+ JS"]
        WS_Client["WebSocket Client"]
        HTTP_Client["Fetch REST API Client"]
    end

    subgraph ServerLayer["Application Layer - FastAPI / Uvicorn"]
        Router["FastAPI App Core and Static Files"]
        AuthMiddleware["JWT Authentication and RBAC Guard"]
        APIs["API Routers: Auth, Workspaces, Projects, Tasks"]
        WS_Manager["WebSocket Connection Manager"]
    end

    subgraph DataLayer["Data and Persistence Layer"]
        AsyncSession["SQLAlchemy 2.0 AsyncSession / asyncpg"]
        Postgres[("PostgreSQL Database")]
    end

    UI --> HTTP_Client
    UI --> WS_Client

    HTTP_Client -->|"HTTP REST - Bearer JWT"| Router
    WS_Client <-->|"Full-Duplex WebSocket"| WS_Manager

    Router --> AuthMiddleware
    AuthMiddleware --> APIs

    APIs --> AsyncSession
    AsyncSession <-->|"SQL Queries and Transactions"| Postgres

    APIs -->|"Broadcast Events"| WS_Manager
    WS_Manager -->|"Live Sync Events"| WS_Client
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
├── alembic/
│   ├── versions/              # Migration revision scripts
│   └── env.py                 # Async Alembic runner
├── app/
│   ├── api/
│   │   ├── auth.py            # Registration, login, JWT issuance
│   │   ├── workspaces.py      # Workspace CRUD and membership management
│   │   ├── projects.py        # Project CRUD and progress analytics
│   │   └── tasks.py           # Task CRUD, comments, WebSocket endpoint
│   ├── core/
│   │   ├── config.py          # Pydantic settings and environment loading
│   │   ├── database.py        # Async SQLAlchemy engine and sessions
│   │   ├── permissions.py     # RBAC and workspace permission guards
│   │   ├── security.py        # Password hashing and JWT verification
│   │   └── ws.py              # ProjectConnectionManager
│   ├── models/
│   │   └── models.py          # SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── auth.py            # Authentication schemas
│   │   ├── workspace.py       # Workspace schemas
│   │   ├── project.py         # Project schemas
│   │   └── task.py            # Task and comment schemas
│   └── main.py                # FastAPI application entry point
├── frontend/
│   ├── css/
│   │   └── styles.css         # Responsive UI and theme styling
│   ├── js/
│   │   ├── api.js             # REST API client and auth handling
│   │   ├── app.js             # View routing and state management
│   │   ├── board.js           # Kanban drag-and-drop and WebSocket listener
│   │   └── ui.js              # Toasts, theme toggles, UI helpers
│   └── index.html             # Main application interface
├── .env.example               # Environment variable template
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Project dependencies and metadata
├── requirements.txt           # Pip dependency manifest
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have the following installed:

- **Python 3.12+**
- **PostgreSQL** (running locally or through Docker/cloud provider)
- **Git**
- **uv** (recommended) or standard `pip`

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/your-username/TeamFlow.git

# Navigate into the project
cd TeamFlow

# Create a virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Alternatively, using `uv`:

```bash
uv venv
uv pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL connection
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/teamflow

# JWT configuration
SECRET_KEY=your_generated_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure secret key using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Important:** Never commit your actual `.env` file or production secret keys to GitHub.

### 4. Create the PostgreSQL Database

Open PostgreSQL and create the database:

```sql
CREATE DATABASE teamflow;
```

Ensure your PostgreSQL username and password match the `DATABASE_URL` in your `.env` file.

### 5. Run Database Migrations

Apply the database schema using Alembic:

```bash
alembic upgrade head
```

### 6. Launch the Application

Start the Uvicorn ASGI server:

```bash
uvicorn app.main:app --reload --port 8000
```

Open the following URLs in your browser:

- 🌐 **Web Interface:** http://localhost:8000
- 📚 **Swagger API Documentation:** http://localhost:8000/docs
- 📖 **ReDoc API Documentation:** http://localhost:8000/redoc

---

## 📡 REST API Reference

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/auth/register` | Register a new user account. |
| POST | `/api/auth/login` | Authenticate and receive a JWT access token. |
| GET | `/api/auth/me` | Fetch the currently authenticated user profile. |

### Workspaces (`/api/workspaces`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/workspaces` | Create a workspace; creator becomes OWNER. |
| GET | `/api/workspaces` | List workspaces the current user belongs to. |
| GET | `/api/workspaces/{id}/members` | List workspace members. |
| POST | `/api/workspaces/{id}/members` | Invite a member by email and assign a role. |
| PATCH | `/api/workspaces/{id}/members/{user_id}` | Update a member's role. |
| DELETE | `/api/workspaces/{id}/members/{user_id}` | Remove a member from the workspace. |

### Projects (`/api`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/workspaces/{id}/projects` | Create a project within a workspace. |
| GET | `/api/workspaces/{id}/projects` | List projects with completion metrics. |
| GET | `/api/projects/{id}` | Retrieve project details and tasks. |
| PATCH | `/api/projects/{id}` | Update project details or target end date. |
| DELETE | `/api/projects/{id}` | Delete a project and associated tasks. |

### Tasks & Real-Time Synchronization (`/api`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/projects/{id}/tasks` | Create a task and broadcast an event. |
| PATCH | `/api/tasks/{id}` | Update task details, status, priority, or assignment. |
| DELETE | `/api/tasks/{id}` | Delete a task and broadcast deletion. |
| POST | `/api/tasks/{id}/comments` | Add a comment and broadcast it to project members. |
| WS | `/api/ws/projects/{id}` | Establish a full-duplex WebSocket connection for live board synchronization. |

---

## 🔮 Roadmap / Future Enhancements

- [ ] **Cloud File Attachments:** Asset uploads and design attachments powered by Amazon S3 or Cloudflare R2.
- [ ] **Sprint Burndown & Gantt Timeline:** Dynamic charts tracking team velocity and milestones.
- [ ] **Push & Email Alerts:** Notifications for task assignments and upcoming deadlines.
- [ ] **GitHub / GitLab Integration:** Automatically transition tasks to Done upon pull request merge.
- [ ] **Mobile Application:** Native React Native or Flutter client with offline synchronization.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
