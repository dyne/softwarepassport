from io import StringIO
import json
import requests
from sqlalchemy.exc import DBAPIError, OperationalError as SAOperationalError
import logging
import shutil
from sqlite3 import OperationalError
from pygit2 import RemoteCallbacks, clone_repository, GitError
from tempfile import TemporaryDirectory
from reuse import lint
from reuse.project import Project
from scancode.cli import run_scan
from ipr import crud

from ipr.lib import AttrDict

L = logging.getLogger("uvicorn.error")


class Repo:
    def __init__(self, url):
        self.url = url
        self.path = None
        self.report = ""
        self.scancode_report = None
        self.saved = None
        self.mySawroomTag = None
        self.myFabricTag = None

    def __clone(self):
        class Progress(RemoteCallbacks):
            def transfer_progress(self, stats):
                L.debug(f"{stats.indexed_objects}/{stats.total_objects}")

        clone_repository(self.url, self.path, callbacks=Progress())

    def __run_reuse(self):
        L.info("Running reuse for %s", self.url)
        args = AttrDict(
            {
                "no_multiprocessing": False,
                "quiet": False,
                "verbose": True,
                "debug": True,
            }
        )
        result = StringIO()
        lint.run(args, project=Project(self.path), out=result)
        self.report = result.getvalue().replace(self.path, "")
        return self.report

    def __run_scancode(self):
        L.info("Running scancode for %s", self.url)
        self.scancode_report = ""
        c = run_scan(
            self.path,
            license=True,
            copyright=True,
            consolidate=True,
            strip_root=True,
            n=8,
        )[1]
        print(json.dumps(c))
        return self.scancode_report

    def __save_scan(self, db):
        L.info("Saving scan for %s", self.url)
        reuse_report = self.__run_reuse()
        scancode_report = str(self.__run_scancode())
        self.__blockchain()
        self.saved = crud.create_scan(
            db=db,
            scan=dict(
                identifier=self.url,
                reuse_report=reuse_report,
                scancode_report=scancode_report,
                sawroom_tag=self.mySawroomTag,
                fabric_tag=self.myFabricTag,
            ),
        )

    def __cleanup(self):
        shutil.rmtree(self.path)

    def __blockchain(self):
        blockchains = [
            ("https://apiroom.net/api/zenbridge/sawroom-write", "mySawroomTag"),
            ("https://apiroom.net/api/zenbridge/fabric-write", "myFabricTag"),
        ]
        data = dict(
            data=dict(
                input=dict(
                    url=self.url,
                    reuse_report=self.report,
                    scancode_report=str(self.scancode_report),
                )
            )
        )
        for (url, tag) in blockchains:
            r = requests.post(url, json=data)
            setattr(self, tag, r.json()[tag])
            L.info("Blockchain response to %s: %s", url, r.json())

    def scan(self, db):
        with TemporaryDirectory() as path:
            try:
                self.path = path
                self.__clone()
                self.__save_scan(db)
                self.__cleanup()
            except GitError as eg:
                L.exception("Failed to clone %s, %s", self.url, eg)
                raise
            except (DBAPIError, OperationalError, SAOperationalError) as e:
                L.exception("Failed to save scan for %s, %s", self.url, ed)
                raise

    def __repr__(self):
        return f"<Repo {self.url}>"
