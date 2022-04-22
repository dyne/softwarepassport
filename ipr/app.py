import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import pygit2
import tempfile
from markupsafe import Markup
import markdown
from reuse import lint
from reuse.project import Project
from io import StringIO

app = FastAPI()
templates = Jinja2Templates(directory="templates/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request, 'result': ''})

@app.post("/")
def form_post(request: Request, repo: str = Form(...)):
    class Progress(pygit2.RemoteCallbacks):
        def transfer_progress(self, stats):
            print(f'{stats.indexed_objects}/{stats.total_objects}')

    print("Cloning project")
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = pygit2.clone_repository(repo, tmpdir, callbacks=Progress())
        print("Cloned")
        args = AttrDict({
            'no_multiprocessing': False,
            'quiet': False,
            'verbose': True,
            'debug': True})
        result = StringIO()
        lint.run(args, project=Project(tmpdir), out=result)
        result = result.getvalue().replace(tmpdir, "")
        return templates.TemplateResponse('index.html', context={'request': request, 'result': Markup(markdown.markdown(result))})

def start():
    uvicorn.run("ipr.app:app", host="0.0.0.0", port=8000, reload=True, workers=2)
