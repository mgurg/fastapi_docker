from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import QrCodes


def get_entity_by_qr_code(db: Session, qr_code_id: str) -> QrCodes:
    return db.execute(select(QrCodes).where(QrCodes.qr_code_id == qr_code_id)).scalar_one_or_none()


def create_qr_code(db: Session, data: dict) -> QrCodes:
    new_qr_code = QrCodes(**data)
    db.add(new_qr_code)
    db.commit()
    db.refresh(new_qr_code)

    return new_qr_code
