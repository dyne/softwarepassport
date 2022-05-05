import enum
import logging
import tempfile
from datetime import datetime
from io import StringIO

import git
import requests
from reuse import lint
from reuse.project import Project as ReuseProject
from scancode.cli import run_scan
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import Session

from .config import settings
from .database import Base
from .lib import AttrDict

L = logging.getLogger("uvicorn.error")


class State(enum.Enum):
    PROJECT_CREATED = 0
    CLONE_START = 1
    CLONE_END = 2
    REUSE_START = 3
    REUSE_END = 4
    SCANCODE_START = 5
    SCANCODE_END = 6
    BLOCKCHAIN_START = 7
    BLOCKCHAIN_END = 8


class Project(Base):
    __tablename__ = "projects"

    url = Column(String, index=True, primary_key=True)
    hash = Column(String)
    reuse_compliant = Column(Boolean, default=False)
    reuse_report = Column(String, default=None)
    scancode_report = Column(String, default=None)
    sawroom_tag = Column(String, index=True, default=None)
    fabric_tag = Column(String, index=True, default=None)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_last_updated = Column(DateTime, default=datetime.utcnow)
    description = Column(String, index=True, default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = tempfile.mkdtemp()

    def clone(self, db: Session):
        if not getattr(self, "path", False):
            self.path = tempfile.mkdtemp()
        L.info("Cloning project %s", self.url)
        self.__log(db, State.CLONE_START)
        repo = git.Repo.clone_from(self.url, self.path, depth=1)
        self.__log(db, State.CLONE_END)
        self.hash = repo.head.object.hexsha
        self.save(db=db)

    def reuse(self, db: Session):
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
        self.__log(db, State.REUSE_START)
        self.reuse_compliant = not lint.run(
            args, project=ReuseProject(self.path), out=result
        )
        self.__log(db, State.REUSE_END)
        self.reuse_report = result.getvalue().replace(self.path, "")
        self.save(db=db)

    def scancode(self, db: Session):
        L.info("Running scancode for %s", self.url)
        self.__log(db, State.SCANCODE_START)
        self.scancode_report = str(
            run_scan(
                self.path,
                license=True,
                copyright=True,
                consolidate=True,
                strip_root=True,
                n=8,
            )[1]
        )
        self.__log(db, State.SCANCODE_END)
        self.save(db=db)

    def blockchain(self, db: Session):
        blockchains = [
            (settings.SAWROOM, "mySawroomTag", "sawroom_tag"),
            (settings.FABRIC, "myFabricTag", "fabric_tag"),
        ]
        data = dict(
            data=dict(
                input=dict(
                    url=self.url,
                    hash=self.hash,
                    reuse_compliant=self.reuse_compliant,
                    reuse_report=self.reuse_report,
                    scancode_report=self.scancode_report,
                )
            )
        )
        self.__log(db, State.BLOCKCHAIN_START)
        for (url, param, tag) in blockchains:
            r = requests.post(url, json=data)
            setattr(self, tag, r.json()[param])
            L.info("Blockchain response to %s: %s", url, r.json())
        self.__log(db, State.BLOCKCHAIN_END)

    def scan(self, db: Session):
        L.info("Scanning project %s", self.url)
        self.clone(db)
        self.reuse(db)
        self.scancode(db)
        self.blockchain(db)
        self.save(db)

    def save(self, db: Session):
        self.date_last_updated = datetime.utcnow()
        db.merge(self)
        db.commit()

    @classmethod
    def by_url(cls, url: str, db: Session):
        return db.query(cls).get(url)

    @classmethod
    def all(cls, db: Session):
        return db.query(cls).all()

    @classmethod
    def all_by(
        cls, db: Session, skip: int = 0, limit: int = settings.PAGINATION_WINDOW
    ):
        return db.query(cls).offset(skip).limit(limit).all()

    def __log(self, db: Session, state: State, output: str = None):
        al = AuditLog(url=self.url, state=state, output=output)
        db.add(al)
        db.commit()
        db.flush()

    def logs(self, db: Session):
        return AuditLog.by_url(self.url, db)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    state = Column(Enum(State))
    output = Column(String, default=None)
    date_created = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def by_url(cls, url, db: Session):
        return db.query(cls).filter(url == url).all()
