from sqlalchemy.orm import Session

from . import models, schemas


def get_scans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Scans).offset(skip).limit(limit).all()


def get_scan_by_repo(db: Session, repo: str):
    return db.query(models.Scans).filter(models.Scans.identifier == repo).first()


def create_scan(db: Session, scan: schemas.ScanCreate):
    db_scan = models.Scans(**scan)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan
