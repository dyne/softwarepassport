import logging

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_202_ACCEPTED

from .config import settings
from .database import SessionLocal, engine
from .models import Base, Project
from .schemas import ProjectBase

Base.metadata.create_all(bind=engine)


app = FastAPI()
L = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        L.exception(e)
        return JSONResponse(
            status_code=500,
            content={"message": f"🛑 Oops Something went wrong! \n\n {e}"},
        )


app.middleware("http")(catch_exceptions_middleware)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root(request: Request):
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list


@app.get("/projects")
def list_all_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@app.post("/project", status_code=HTTP_201_CREATED)
def create_or_update_a_new_project(project: ProjectBase, db: Session = Depends(get_db)):
    """
    ## Creates a new project
    If the project is already existing, it will be updated.
    """
    p = Project(url=project.url)
    p.save(db)
    return p


@app.post("/scan", status_code=HTTP_202_ACCEPTED)
async def scan(
    project: ProjectBase,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    ## Queue a scan of the project into a background task.
    """
    p = Project.by_url(project.url, db)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    # p.scan(db)
    background_tasks.add_task(p.scan, db)
    return {"message": "Scan queued visti the status on /status"}


@app.post("/status")
def status(project: ProjectBase, db: Session = Depends(get_db)):
    """
    ## Returns the status of the project.
    """
    p = Project.by_url(project.url, db)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    return p.logs(db)


def start():
    uvicorn.run(
        "ipr.app:app",
        host=str(settings.HOST),
        port=settings.PORT,
        reload=True,
        workers=settings.WORKERS,
    )
