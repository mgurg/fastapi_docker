import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import QrCode
from app.models.shared_models import PublicCompany


def get_entity_by_qr_code(db: Session, qr_code_id: str) -> QrCode:
    return db.execute(select(QrCode).where(QrCode.qr_code_id == qr_code_id)).scalar_one_or_none()


def get_qr_code_by_resource_uuid(db: Session, resource_uuid: UUID) -> QrCode:
    return db.execute(select(QrCode).where(QrCode.resource_uuid == resource_uuid)).scalar_one_or_none()


def create_qr_code(db: Session, data: dict) -> QrCode:
    new_qr_code = QrCode(**data)
    db.add(new_qr_code)
    db.commit()
    db.refresh(new_qr_code)

    return new_qr_code


def generate_custom_unique_id(allowed_chars: str, company_ids):
    proposed_id = "".join(random.choice(allowed_chars) for _x in range(3))
    while proposed_id in company_ids:
        proposed_id = "".join(random.choice(allowed_chars) for _x in range(3))
    return proposed_id


def add_noise_to_qr(qr_code: str) -> str:
    noise = ["2", "3", "4", "5", "6", "7", "8", "9"]
    return "".join(f"{x}{random.choice(noise) if random.randint(0, 1) else ''}" for x in qr_code)


def generate_company_qr_id(db: Session) -> str:
    company_ids = db.execute(select(PublicCompany.qr_id)).scalars().all()
    allowed_chars = "abcdefghijkmnopqrstuvwxyz"  # ABCDEFGHJKLMNPRSTUVWXYZ23456789
    return generate_custom_unique_id(allowed_chars, company_ids)


def generate_item_qr_id(db: Session) -> str:
    items_ids = db.execute(select(QrCode.qr_code_id)).scalars().all()
    allowed_chars = "abcdefghijkmnopqrstuvwxyz23456789"  # ABCDEFGHJKLMNPRSTUVWXYZ23456789
    return generate_custom_unique_id(allowed_chars, items_ids)
