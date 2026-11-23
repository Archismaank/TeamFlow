import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()

# Page Setup - Normal margins
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

# Color Palette matching the template (Navy / Royal Blue accent)
COLOR_PRIMARY = RGBColor(43, 57, 144)    # #2B3990 (Royal Blue from template)
COLOR_SECONDARY = RGBColor(30, 41, 59)   # #1E293B (Dark Slate)
COLOR_MUTED = RGBColor(100, 116, 139)    # #64748B (Muted Slate)
COLOR_ACCENT = RGBColor(14, 116, 144)    # #0E7490 (Teal/Cyan accent)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_slide_header(doc, title_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(14)
    run = p.add_run(title_text)
    run.font.name = "Calibri"
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_bullet_point(doc, lead_in, text=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run_lead = p.add_run(lead_in)
    run_lead.font.name = "Calibri"
    run_lead.font.size = Pt(12)
    run_lead.font.bold = True
    run_lead.font.color.rgb = COLOR_SECONDARY
    
    if text:
        run_text = p.add_run(" " + text)
        run_text.font.name = "Calibri"
        run_text.font.size = Pt(12)
        run_text.font.color.rgb = COLOR_SECONDARY
    return p

def add_numbered_point(doc, num_str, lead_in, text=""):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    
    run_num = p.add_run(f"({num_str})  ")
    run_num.font.name = "Calibri"
    run_num.font.size = Pt(11)
    run_num.font.bold = True
    run_num.font.color.rgb = COLOR_PRIMARY

    run_lead = p.add_run(lead_in)
    run_lead.font.name = "Calibri"
    run_lead.font.size = Pt(11.5)
    run_lead.font.bold = True
    run_lead.font.color.rgb = COLOR_SECONDARY
    
    if text:
        run_text = p.add_run(" " + text)
        run_text.font.name = "Calibri"
        run_text.font.size = Pt(11.5)
        run_text.font.color.rgb = COLOR_SECONDARY
    return p

def add_section_subtitle(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_footer_label(doc, page_num, total_pages=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(f"TeamFlow — Collaborative Workspace System  |  Slide {page_num}/{total_pages}")
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.italic = True
    run.font.color.rgb = COLOR_MUTED
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# ==================== SLIDE 1: TITLE PAGE ====================
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(90)
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_title = title_p.add_run("TeamFlow")
run_title.font.name = "Calibri"
run_title.font.size = Pt(36)
run_title.font.bold = True
run_title.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_before = Pt(4)
sub_p.paragraph_format.space_after = Pt(50)
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_sub = sub_p.add_run("Real-Time Collaborative Workspace & Project Management System")
run_sub.font.name = "Calibri"
run_sub.font.size = Pt(17)
run_sub.font.bold = True
run_sub.font.color.rgb = COLOR_PRIMARY

# Submitted By
sub_by_label = doc.add_paragraph()
sub_by_label.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub_by_label.paragraph_format.space_after = Pt(2)
r_by = sub_by_label.add_run("Submitted By:")
r_by.font.name = "Calibri"
r_by.font.size = Pt(13)
r_by.font.bold = True
r_by.font.color.rgb = COLOR_SECONDARY

names = [
    "Your Name / Student 1 (Roll Number)",
    "Team Member 2 (Roll Number)",
    "Team Member 3 (Roll Number)",
    "Team Member 4 (Roll Number)"
]
for name in names:
    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_before = Pt(1)
    p_name.paragraph_format.space_after = Pt(1)
    r_name = p_name.add_run(name)
    r_name.font.name = "Calibri"
    r_name.font.size = Pt(13)
    r_name.font.bold = True
    r_name.font.color.rgb = COLOR_SECONDARY

# Submitted To
sub_to_label = doc.add_paragraph()
sub_to_label.paragraph_format.space_before = Pt(36)
sub_to_label.paragraph_format.space_after = Pt(2)
sub_to_label.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_to = sub_to_label.add_run("Submitted To:")
r_to.font.name = "Calibri"
r_to.font.size = Pt(12)
r_to.font.bold = True
r_to.font.color.rgb = COLOR_SECONDARY

details = [
    "Prof. Supervisor / Faculty Name",
    "Department of Computer Science & Engineering",
    "Institution / University Name",
    "November 2026"
]
for d in details:
    p_d = doc.add_paragraph()
    p_d.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_d.paragraph_format.space_before = Pt(1)
    p_d.paragraph_format.space_after = Pt(1)
    r_d = p_d.add_run(d)
    r_d.font.name = "Calibri"
    r_d.font.size = Pt(11.5)
    r_d.font.color.rgb = COLOR_SECONDARY

doc.add_page_break()

# ==================== SLIDE 2: INTRODUCTION ====================
add_slide_header(doc, "Introduction")
add_bullet_point(doc, "TeamFlow", "is a high-velocity, web-based collaborative workspace and project management engine designed to streamline sprint execution for modern product teams.")
add_bullet_point(doc, "Key user flows:", "workspace onboarding, multi-project navigation, drag-and-drop Kanban task execution, priority assignment, and real-time task discussions.")
add_bullet_point(doc, "Admin flows:", "multi-tenant workspace creation, granular Role-Based Access Control (Owner, Admin, Member, Viewer), member invitation via email, role modification, and member offboarding.")
add_bullet_point(doc, "Built as a modular full-stack application", "leveraging a responsive editorial frontend and an asynchronous Python/FastAPI backend backed by WebSockets.")
add_footer_label(doc, 2)
doc.add_page_break()

# ==================== SLIDE 3: TECHNOLOGY STACK ====================
add_slide_header(doc, "Technology Stack")

add_section_subtitle(doc, "Frontend")
add_bullet_point(doc, "HTML5, CSS3", "Modern design system with custom CSS variables, responsive typography, and Dark/Light mode theme switching.")
add_bullet_point(doc, "JavaScript (ES6+)", "Modular client architecture utilizing native Fetch API and full-duplex WebSockets for real-time state synchronization.")

add_section_subtitle(doc, "Backend & Services")
add_bullet_point(doc, "Python 3.12 & FastAPI", "High-performance asynchronous REST API, route dependency injection, and Pydantic schema validation.")
add_bullet_point(doc, "WebSockets Connection Manager", "In-memory per-project connection hub broadcasting live board actions across connected peers.")
add_bullet_point(doc, "Authentication & Security", "JWT (JSON Web Tokens) with cryptographically secure secret keys and Passlib/Bcrypt password hashing.")

add_section_subtitle(doc, "Database & Tools")
add_bullet_point(doc, "PostgreSQL & SQLAlchemy 2.0", "Enterprise relational database driven by SQLAlchemy AsyncSession and the asyncpg driver.")
add_bullet_point(doc, "Alembic", "Automated database schema migration engine for versioned, reproducible DDL changes.")
add_bullet_point(doc, "Environment & Configuration", ".env configuration with Pydantic BaseSettings and uv/requirements.txt dependency management.")
add_footer_label(doc, 3)
doc.add_page_break()

# ==================== SLIDE 4: METHODOLOGY ====================
add_slide_header(doc, "Methodology")

p_intro = doc.add_paragraph()
p_intro.paragraph_format.space_after = Pt(8)
r_intro = p_intro.add_run("Development followed a modular, sprint-oriented engineering approach:")
r_intro.font.size = Pt(12)
r_intro.font.color.rgb = COLOR_SECONDARY

add_numbered_point(doc, "1", "Requirement analysis:", "Identify multi-tenant workspace hierarchies, role permission matrices, Kanban board flows, and real-time collaboration requirements.")
add_numbered_point(doc, "2", "Frontend design:", "Craft clean, responsive views for workspace selection, project dashboards, drag-and-drop Kanban columns, task modals, and member administration.")
add_numbered_point(doc, "3", "Backend implementation:", "Develop asynchronous RESTful API endpoints for authentication, workspaces, projects, tasks, and task comments with strict Pydantic validation.")
add_numbered_point(doc, "4", "Database modeling:", "Design relational schemas for Users, Workspaces, Members, Projects, Tasks, and Comments with foreign key cascades using SQLAlchemy ORM.")
add_numbered_point(doc, "5", "Real-time sync layer:", "Implement a centralized WebSocket connection manager to broadcast task mutations, status transitions, and discussions across peers.")
add_numbered_point(doc, "6", "Testing & validation:", "Perform end-to-end user journey tests, RBAC access checks, concurrent WebSocket stress testing, and database constraint verification.")
add_footer_label(doc, 4)
doc.add_page_break()

# ==================== SLIDE 5: SYSTEM ARCHITECTURE (OVERVIEW) ====================
add_slide_header(doc, "System Architecture (Overview)")

add_bullet_point(doc, "Client Layer:", "Browser UI (HTML5 / CSS3 / Vanilla JS) — renders interactive Kanban boards, dispatches asynchronous HTTP requests, and maintains persistent WebSocket channels.")
add_bullet_point(doc, "Application Layer:", "FastAPI ASGI Server — coordinates business logic, enforces role-based access control (RBAC), validates payloads, and drives WebSocket pub/sub broadcasting.")
add_bullet_point(doc, "Data & Service Layer:", "PostgreSQL database running via asyncpg/SQLAlchemy ORM, managed with Alembic migrations, and backed by secure environment configurations.")
add_footer_label(doc, 5)
doc.add_page_break()

# ==================== SLIDE 6: FEATURES ====================
add_slide_header(doc, "Features")

add_section_subtitle(doc, "Member & Project Features")
add_bullet_point(doc, "Interactive Kanban Boards:", "Real-time drag-and-drop task movement across stages (To Do, In Progress, In Review, Done).")
add_bullet_point(doc, "Task Metadata & Prioritization:", "Set priority levels (Low, Medium, High, Urgent), due date tracking, rich descriptions, and assignee delegation.")
add_bullet_point(doc, "Task Discussion Stream:", "Integrated real-time commenting engine for continuous context and team feedback on specific tasks.")
add_bullet_point(doc, "Live Analytics & Metrics:", "Dynamic calculation of project completion percentage, overdue count, and task stage distribution.")

add_section_subtitle(doc, "Workspace & Admin Features")
add_bullet_point(doc, "Multi-Tenant Workspaces:", "Create and manage multiple distinct team workspaces under single user credentials.")
add_bullet_point(doc, "Granular Role Management:", "Invite collaborators via email with assigned roles: Owner, Admin, Member, or Viewer.")
add_bullet_point(doc, "Access Governance:", "Enforce strict route-level permission checks; only Owners/Admins can modify roles, add/delete projects, or manage members.")

add_section_subtitle(doc, "System Features")
add_bullet_point(doc, "Real-Time WebSocket Synchronization:", "Instant state propagation across all connected team sessions without polling.")
add_bullet_point(doc, "Security & Auth:", "Cryptographic password hashing (Bcrypt), JWT bearer tokens, and scoped API authorization.")
add_footer_label(doc, 6)
doc.add_page_break()

# ==================== SLIDE 7: WORKFLOW / TASK LIFECYCLE ====================
add_slide_header(doc, "Task Lifecycle & Real-Time Sync Flow")

add_numbered_point(doc, "1", "User loads workspace & project:", "Frontend fetches project metadata and establishes a full-duplex WebSocket connection to /api/ws/projects/{id}.")
add_numbered_point(doc, "2", "Task state mutation initiated:", "A team member creates, edits, comments on, or drags a task to a new status column.")
add_numbered_point(doc, "3", "Backend authorization & persistence:", "FastAPI validates member permissions, updates PostgreSQL via asyncpg/SQLAlchemy, and commits transaction.")
add_numbered_point(doc, "4", "WebSocket broadcast triggered:", "The server connection manager broadcasts the mutation event (task_created, task_updated, comment_added) to all active project sockets.")
add_numbered_point(doc, "5", "Instant client board sync:", "All connected peers receive the JSON payload and update their local DOM in real-time without requiring a page refresh.")
add_footer_label(doc, 7)
doc.add_page_break()

# ==================== SLIDE 8: ER DIAGRAM (DATA MODELS) ====================
add_slide_header(doc, "TeamFlow — Entity Relationship (Data Model)")

p_er_desc = doc.add_paragraph()
p_er_desc.paragraph_format.space_after = Pt(8)
r_er_desc = p_er_desc.add_run("Relational schema architecture designed with primary keys (UUID), foreign key constraints, and cascade delete rules:")
r_er_desc.font.size = Pt(11.5)
r_er_desc.font.color.rgb = COLOR_SECONDARY

# Create ER Table
table = doc.add_table(rows=1, cols=4)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False

hdr_cells = table.rows[0].cells
headers = ["Entity / Table", "Primary Key", "Foreign Keys / References", "Key Attributes & Relationships"]
widths = [Inches(1.5), Inches(1.1), Inches(2.0), Inches(2.5)]

for i, h_text in enumerate(headers):
    hdr_cells[i].width = widths[i]
    set_cell_background(hdr_cells[i], "2B3990")
    set_cell_margins(hdr_cells[i], 120, 120, 150, 150)
    p = hdr_cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(h_text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

entities_data = [
    ("users", "id (UUID)", "None", "email (unique, index), password_hash, full_name, created_at.\nRelationships: memberships (1:N)"),
    ("workspaces", "id (UUID)", "owner_id -> users.id", "name, created_at.\nRelationships: members (1:N, cascade), projects (1:N, cascade)"),
    ("workspace_members", "Composite (ws_id, user_id)", "workspace_id -> workspaces.id\nuser_id -> users.id", "role (Enum: OWNER, ADMIN, MEMBER, VIEWER).\nRelationships: workspace, user"),
    ("projects", "id (UUID)", "workspace_id -> workspaces.id", "name, description, target_end_date, created_at.\nRelationships: workspace, tasks (1:N, cascade)"),
    ("tasks", "id (UUID)", "project_id -> projects.id\nassignee_id -> users.id", "title, description, status (Enum), priority (Enum), due_date, position.\nRelationships: project, comments (1:N, cascade)"),
    ("comments", "id (UUID)", "task_id -> tasks.id\nauthor_id -> users.id", "content (Text), created_at.\nRelationships: task, author")
]

for row_idx, data in enumerate(entities_data):
    row_cells = table.add_row().cells
    bg_col = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
    for col_idx, text in enumerate(data):
        row_cells[col_idx].width = widths[col_idx]
        set_cell_background(row_cells[col_idx], bg_col)
        set_cell_margins(row_cells[col_idx], 80, 80, 120, 120)
        p = row_cells[col_idx].paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_SECONDARY

add_footer_label(doc, 8)
doc.add_page_break()

# ==================== SLIDE 9: ACTIVITY FLOW ====================
add_slide_header(doc, "TeamFlow — Collaboration Activity Flow")

p_act = doc.add_paragraph()
p_act.paragraph_format.space_after = Pt(8)
r_act = p_act.add_run("Activity flow illustrating task creation and real-time board distribution across users:")
r_act.font.size = Pt(11.5)
r_act.font.color.rgb = COLOR_SECONDARY

act_steps = [
    ("User Action (Client A)", "User clicks '+ Add Task', fills in title, priority (HIGH), due date, and submits the modal form."),
    ("API Dispatch & Auth", "Client dispatches POST /api/projects/{id}/tasks with Bearer JWT in the Authorization header."),
    ("Permission Guard Check", "FastAPI dependency verifies that User A is an active member with role OWNER, ADMIN, or MEMBER."),
    ("Database Commit", "SQLAlchemy AsyncSession executes INSERT into tasks, commits transaction, and refreshes the instance."),
    ("WebSocket Event Publishing", "Endpoint invokes ws_manager.broadcast(project_id, {'type': 'task_created', 'task': task_data})."),
    ("Real-Time Distribution", "All active WebSocket connections for that project receive the payload asynchronously."),
    ("Client DOM Update (All Clients)", "Client A and Client B (teammate) instantly append the new task card to the 'TODO' Kanban column.")
]

for step_num, (lead, desc) in enumerate(act_steps, 1):
    add_numbered_point(doc, str(step_num), f"{lead}:", desc)

add_footer_label(doc, 9)
doc.add_page_break()

# ==================== SLIDE 10: DETAILED ARCHITECTURE ====================
add_slide_header(doc, "TeamFlow System Architecture Breakdown")

p_arch_desc = doc.add_paragraph()
p_arch_desc.paragraph_format.space_after = Pt(8)
r_arch_desc = p_arch_desc.add_run("Detailed multi-tier architecture breakdown showing protocols and data flow:")
r_arch_desc.font.size = Pt(11.5)
r_arch_desc.font.color.rgb = COLOR_SECONDARY

arch_table = doc.add_table(rows=1, cols=3)
arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
arch_table.autofit = False

a_hdr = arch_table.rows[0].cells
a_headers = ["Layer", "Components & Technologies", "Responsibilities"]
a_widths = [Inches(1.8), Inches(2.4), Inches(2.9)]

for i, h_text in enumerate(a_headers):
    a_hdr[i].width = a_widths[i]
    set_cell_background(a_hdr[i], "2B3990")
    set_cell_margins(a_hdr[i], 120, 120, 150, 150)
    p = a_hdr[i].paragraphs[0]
    r = p.add_run(h_text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

arch_data = [
    ("Client Tier", "Browser Web Client\nHTML5, CSS3, ES6+ JS\nFetch API & Native WebSockets", "Renders responsive Kanban UI, Dark/Light modes, captures drag-and-drop events, manages JWT storage, and listens on live WebSocket channels."),
    ("Web & Routing Tier", "Nginx / Uvicorn ASGI Server\nFastAPI Application Core\nStatic Files Mount", "Terminates HTTP/WebSocket connections, routes REST endpoints (/api/auth, /api/workspaces, /api/projects, /api/tasks), and serves frontend assets."),
    ("Application Logic", "Security Module (JWT/Bcrypt)\nPermissions Matrix\nPydantic Schemas\nWS Connection Manager", "Authenticates tokens, verifies workspace membership and role hierarchy, validates schemas, and maintains project broadcast channels."),
    ("Persistence Tier", "PostgreSQL Database\nSQLAlchemy 2.0 Async ORM\nAlembic Migrations", "Guarantees ACID transactions, manages foreign keys with cascade constraints, and tracks database schema versioning history.")
]

for row_idx, data in enumerate(arch_data):
    row_cells = arch_table.add_row().cells
    bg_col = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
    for col_idx, text in enumerate(data):
        row_cells[col_idx].width = a_widths[col_idx]
        set_cell_background(row_cells[col_idx], bg_col)
        set_cell_margins(row_cells[col_idx], 80, 80, 120, 120)
        p = row_cells[col_idx].paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_SECONDARY

add_footer_label(doc, 10)
doc.add_page_break()

# ==================== SLIDE 11: USE CASE MATRIX ====================
add_slide_header(doc, "TeamFlow System Use Case & Actor Matrix")

p_uc_desc = doc.add_paragraph()
p_uc_desc.paragraph_format.space_after = Pt(8)
r_uc_desc = p_uc_desc.add_run("Use case specification categorized by primary actor roles in the workspace:")
r_uc_desc.font.size = Pt(11.5)
r_uc_desc.font.color.rgb = COLOR_SECONDARY

add_section_subtitle(doc, "Actor 1: Unauthenticated Guest")
add_bullet_point(doc, "Register Account:", "Sign up with email, password, and full name.")
add_bullet_point(doc, "Authenticate:", "Log in using credentials to receive JWT bearer access token.")

add_section_subtitle(doc, "Actor 2: Workspace Member")
add_bullet_point(doc, "View Workspaces & Projects:", "Access assigned workspaces and browse active projects.")
add_bullet_point(doc, "Manage Tasks:", "Create tasks, drag tasks between status stages (Todo, In Progress, In Review, Done).")
add_bullet_point(doc, "Comment & Collaborate:", "Post comments on task cards and view live real-time teammate updates.")

add_section_subtitle(doc, "Actor 3: Workspace Admin & Owner")
add_bullet_point(doc, "Create & Manage Workspaces:", "Establish new workspaces and configure team settings.")
add_bullet_point(doc, "Invite Collaborators:", "Invite registered users by email and assign roles (Admin, Member, Viewer).")
add_bullet_point(doc, "Manage Roles & Membership:", "Update member roles or revoke workspace access.")
add_bullet_point(doc, "Project Administration:", "Create, update, or archive projects and milestones within the workspace.")
add_footer_label(doc, 11)
doc.add_page_break()

# ==================== SLIDE 12: FUTURE WORK ====================
add_slide_header(doc, "Future Work")

p_fw = doc.add_paragraph()
p_fw.paragraph_format.space_after = Pt(8)
r_fw = p_fw.add_run("Planned architectural and functional enhancements for subsequent iterations:")
r_fw.font.size = Pt(12)
r_fw.font.color.rgb = COLOR_SECONDARY

add_bullet_point(doc, "File Attachments & Cloud Storage:", "Support task asset uploads, design previews, and documents via Amazon S3 / Cloudflare R2.")
add_bullet_point(doc, "Advanced Sprint Analytics & Gantt Charts:", "Burndown charts, velocity tracking, cumulative flow diagrams, and interactive milestone Gantt views.")
add_bullet_point(doc, "Push Notifications & Webhooks:", "Integrate browser push notifications, email digests, and Slack/Discord webhook alerts for task assignments.")
add_bullet_point(doc, "Third-Party Developer Integrations:", "GitHub/GitLab PR linking to automatically transition tasks to 'Done' upon merge.")
add_bullet_point(doc, "Mobile Application:", "Develop a responsive Progressive Web App (PWA) or native React Native mobile application for on-the-go updates.")
add_bullet_point(doc, "Cloud Deployment & CI/CD Pipeline:", "Containerize via Docker, establish automated GitHub Actions CI/CD, and deploy on AWS / Render with managed PostgreSQL.")
add_footer_label(doc, 12)
doc.add_page_break()

# ==================== SLIDE 13: CONCLUSION ====================
add_slide_header(doc, "Conclusion")

add_bullet_point(doc, "TeamFlow", "successfully demonstrates a high-performance, asynchronous approach to modern collaborative project management using FastAPI and native WebSockets.")
add_bullet_point(doc, "Operational Friction Resolved:", "The system eliminates traditional communication latency by providing instant real-time synchronization across Kanban boards without requiring manual refreshes.")
add_bullet_point(doc, "Robust & Secure Multi-Tenancy:", "Enforces strict Role-Based Access Control (RBAC), cryptographic password hashing, and clean relational data isolation via PostgreSQL.")
add_bullet_point(doc, "Scalable Foundation:", "With planned future enhancements (cloud storage, CI/CD, sprint analytics), TeamFlow serves as an extensible foundation ready to evolve into a full-scale commercial productivity SaaS.")
add_footer_label(doc, 13)
doc.add_page_break()

# ==================== SLIDE 14: REFERENCES ====================
add_slide_header(doc, "References")

references = [
    ("FastAPI Documentation", "https://fastapi.tiangolo.com/"),
    ("SQLAlchemy 2.0 Async Documentation", "https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html"),
    ("PostgreSQL & asyncpg Driver", "https://magicstack.github.io/asyncpg/"),
    ("Alembic Database Migration Guide", "https://alembic.sqlalchemy.org/en/latest/"),
    ("MDN WebSockets API Reference", "https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API"),
    ("Pydantic Validation & Settings", "https://docs.pydantic.dev/latest/"),
    ("Passlib & Bcrypt Security Standards", "https://passlib.readthedocs.io/")
]

for title, url in references:
    p_ref = doc.add_paragraph(style='List Bullet')
    p_ref.paragraph_format.space_before = Pt(5)
    p_ref.paragraph_format.space_after = Pt(5)
    
    r_t = p_ref.add_run(f"{title} — ")
    r_t.font.name = "Calibri"
    r_t.font.size = Pt(11.5)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_SECONDARY
    
    r_u = p_ref.add_run(url)
    r_u.font.name = "Calibri"
    r_u.font.size = Pt(11.5)
    r_u.font.color.rgb = COLOR_PRIMARY
    r_u.font.underline = True

add_footer_label(doc, 14)

output_path = "TeamFlow_Project_Report_Slides.docx"
doc.save(output_path)
print(f"Successfully generated: {output_path}")
