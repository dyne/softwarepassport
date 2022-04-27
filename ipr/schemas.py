from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class ScanBase(BaseModel):
    identifier: str
    reuse_report: str
    sawroom_tag: Optional[str] = None
    fabric_tag: Optional[str] = None
    scancode_report: Optional[str] = None


class Scan(ScanBase):
    id: int
    date_created: Optional[datetime] = None
    date_last_updated: Optional[datetime] = None

    class Config:
        orm_mode = True


class ScanCreate(ScanBase):
    pass
