import logging
import uvicorn
from fastapi import FastAPI, Request, Response, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from markupsafe import Markup
import markdown
from sqlalchemy.orm import Session

from ipr.repo import Repo

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
templates = Jinja2Templates(directory="templates/")
L = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        L.exception(e)
        error = f"""
# Opps! Something went wrong!

```
{e}
```
        """

        return templates.TemplateResponse(
            "index.html",
            context={"request": request, "result": Markup(markdown.markdown(error))},
            status_code=500,
        )


app.middleware("http")(catch_exceptions_middleware)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", context={"request": request, "result": ""}
    )


@app.post("/")
def form_post(request: Request, repo: str = Form(...), db: Session = Depends(get_db)):
    previous_scan = crud.get_scan_by_repo(db, repo)
    if previous_scan:
        L.warning("Scan for %s already exists", repo)
        return templates.TemplateResponse(
            "index.html",
            context={
                "request": request,
                "result": Markup(markdown.markdown("## Repo already scanned")),
            },
        )
    project = Repo(repo)
    project.scan(db)
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "result": Markup(markdown.markdown(project.report)),
        },
    )


@app.get("/scans/", response_model=list[schemas.Scan])
def read_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scans = crud.get_scans(db, skip=skip, limit=limit)
    return scans


def start():
    uvicorn.run("ipr.app:app", host="0.0.0.0", port=8000, reload=True, workers=2)
