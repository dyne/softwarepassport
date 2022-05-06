from typing import Optional
from datetime import datetime

from pydantic import AnyUrl, BaseModel


class RepoBase(BaseModel):
    url: AnyUrl


class Repo(RepoBase):
    date_created: Optional[datetime] = None
    date_last_updated: Optional[datetime] = None

    # class Config:
    #     orm_mode = True
