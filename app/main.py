from fastapi import FastAPI
from app.api import auth, workspaces, projects, tasks
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="TeamFlow API", version="0.3.0")

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")