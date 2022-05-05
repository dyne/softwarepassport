from typing import Optional
from datetime import datetime

from pydantic import AnyUrl, BaseModel


class ProjectBase(BaseModel):
    url: AnyUrl


class Project(ProjectBase):
    date_created: Optional[datetime] = None
    date_last_updated: Optional[datetime] = None

    # class Config:
    #     orm_mode = True
