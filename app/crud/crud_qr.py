from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.models import QrCodes


def get_entity_by_qr_code(db: Session, qr_code_id: str) -> QrCodes:
    return db.execute(select(QrCodes).where(QrCodes.qr_code_id == qr_code_id)).scalar_one_or_none()
