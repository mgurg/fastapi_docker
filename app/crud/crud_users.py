from datetime import datetime

from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import User


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()


def create_user(db: Session):

    faker = Faker()

    new_user = User(
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        user_role_id=1,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
