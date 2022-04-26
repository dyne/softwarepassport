import uvicorn
from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import pygit2
import tempfile
from markupsafe import Markup
import markdown
from reuse import lint
from reuse.project import Project
from io import StringIO
from scancode import cli
import shutil
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
templates = Jinja2Templates(directory="templates/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", context={"request": request, "result": ""}
    )


@app.post("/")
def form_post(request: Request, repo: str = Form(...), db: Session = Depends(get_db)):
    previous_scan = crud.get_scan_by_repo(db, repo)
    if previous_scan:
        return templates.TemplateResponse(
            "index.html", context={"request": request, "result": "Repo already scanned"}
        )

    class Progress(pygit2.RemoteCallbacks):
        def transfer_progress(self, stats):
            print(f"{stats.indexed_objects}/{stats.total_objects}")

    print("Cloning project")

    with tempfile.TemporaryDirectory() as tmpdir:
        pygit2.clone_repository(repo, tmpdir, callbacks=Progress())
        print("Cloned")
        args = AttrDict(
            {
                "no_multiprocessing": False,
                "quiet": False,
                "verbose": True,
                "debug": True,
            }
        )
        result = StringIO()
        lint.run(args, project=Project(tmpdir), out=result)
        scancode_report = cli.run_scan(tmpdir)
        reuse_report = result.getvalue().replace(tmpdir, "")
        crud.create_scan(
            db=db,
            scan=dict(
                reuse_report=reuse_report,
                identifier=repo,
                scancode_report=str(scancode_report),
            ),
        )
        shutil.rmtree(tmpdir)
        return templates.TemplateResponse(
            "index.html",
            context={
                "request": request,
                "result": Markup(markdown.markdown(reuse_report)),
            },
        )


@app.get("/scans/", response_model=list[schemas.Scan])
def read_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scans = crud.get_scans(db, skip=skip, limit=limit)
    return scans


def start():
    uvicorn.run("ipr.app:app", host="0.0.0.0", port=8000, reload=True, workers=2)
