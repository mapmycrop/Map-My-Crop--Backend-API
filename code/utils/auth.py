from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from utils.password import secure_pwd
import re

from models import User, Company
from schemas import UserSchema
from fastapi import HTTPException, status


def get_company_by_id(db: Session, id: int):
    company = db.query(Company).filter(Company.id == id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company with company_id does not exist",
        )

    return company


def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    company = db.query(Company).filter(Company.id == user_id).first()

    return user or company


def get_user_by_ph(db: Session, ph: str):
    phone = re.compile(r"^\d{8,}$")

    if phone.match(ph):
        return db.query(User).filter(User.ph == ph).first()
    else:
        return None


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
    company = (
        db.query(Company).filter(func.lower(Company.email) == email.lower()).first()
    )

    return user or company


def create_user(db: Session, user: UserSchema):
    user.password = secure_pwd(user.password)

    new_user = User(**user.dict())
    new_user.is_active = False
    new_user.is_deleted = False

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
