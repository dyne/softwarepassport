import logging

import uvicorn
from celery import Celery
from celery.utils.log import get_task_logger
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_202_ACCEPTED

from .config import settings
from .database import SessionLocal, engine
from .models import AuditLog, Base, Project
from .schemas import RepoBase

# Base.metadata.create_all(bind=engine, checkfirst=True)

celery = Celery(
    __name__, broker=settings.CELERY_BROKER, backend=settings.CELERY_BACKEND
)
celery_log = get_task_logger(__name__)

app = FastAPI(title="IPR")
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


@app.get("/repositories")
def list_all_repositories(db: Session = Depends(get_db)):
    repos = Project.all(db)
    for r in repos:
        r.status = AuditLog.last_status(r.url, db)
    return repos


@app.post("/repository", status_code=HTTP_201_CREATED)
def create_or_update_a_new_repository(
    repository: RepoBase, db: Session = Depends(get_db)
):
    """
    ## Creates a new repository
    If the repo is already existing, it will be updated.
    """
    repo = Project.by_url(url=repository.url, db=db)
    if not repo:
        repo = Project(url=repository.url)
        repo.save(db)
    return repo


@celery.task
def scan_task(url):
    db = next(get_db())
    repo = Project.by_url(url, db)
    repo.scan(db)


@app.post("/scan", status_code=HTTP_202_ACCEPTED)
async def scan(
    repository: RepoBase,
    db: Session = Depends(get_db),
):
    """
    ## Queue a scan of the project into a background task.
    """
    repo = Project.by_url(repository.url, db)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    scan_task.delay(repository.url)
    return {"message": "Scan queued visit the status on /status"}


@app.post("/status")
def status(repository: RepoBase, db: Session = Depends(get_db)):
    """
    ## Returns the status of the project.
    """
    repo = Project.by_url(repository.url, db)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return repo.logs(db)


def start():
    uvicorn.run(
        "ipr.app:app",
        host=str(settings.HOST),
        port=settings.PORT,
        reload=True,
        workers=settings.WORKERS,
    )
