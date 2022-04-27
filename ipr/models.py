from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .database import Base


class Scans(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, index=True, unique=True)
    reuse_report = Column(String, index=True)
    scancode_report = Column(String, index=True)
    sawroom_tag = Column(String, index=True)
    fabric_tag = Column(String, index=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_last_updated = Column(DateTime, default=datetime.utcnow)
    description = Column(String, index=True)
