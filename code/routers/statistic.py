from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import Statistic, Contact, User, Farm
from utils.api import has_permission
from db import get_db
from constant import ADMIN, AGRONOMISTS

route = APIRouter(prefix="/statistic", tags=["Statistic"], include_in_schema=False)


@route.get("/")
@has_permission([ADMIN])
def index(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(
        *[
            column
            for column in Statistic.__table__.c
            if column.name not in ["id", "updated_at"]
        ]
    ).first()

    return statistic


@route.get("/farmers_count")
@has_permission([ADMIN])
def farmers_count(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.farmers_count
    else:
        return 0


@route.get("/farmer_details")
@has_permission([ADMIN])
def farmer_details(api_key: str, user_id: int, db: Session = Depends(get_db)):
    farmer = db.query(User).filter(User.id == user_id).first()

    return farmer


@route.get("/total_farms_mapped")
@has_permission([ADMIN])
def total_farms_mapped(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.total_farms_mapped
    else:
        return 0


@route.get("/active_users")
@has_permission([ADMIN])
def active_users(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.active_users
    else:
        return 0


@route.get("/non_active_users")
@has_permission([ADMIN])
def non_active_users(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.non_active_users
    else:
        return 0


@route.get("/paid_farms")
@has_permission([ADMIN])
def paid_farms(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.paid_farms
    else:
        return 0


@route.get("/non_paid_farms")
@has_permission([ADMIN])
def non_paid_farms(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.non_paid_farms
    else:
        return 0


@route.get("/enterprise_users")
@has_permission([ADMIN])
def enterprise_users(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.enterprise_users
    else:
        return 0


@route.get("/countrywise_farms")
@has_permission([ADMIN])
def countrywise_farms(api_key: str, country_name: str, db: Session = Depends(get_db)):
    countrywise_farms = db.query(Farm).filter(Farm.country == country_name).count()

    return countrywise_farms


@route.get("/api_keys")
@has_permission([ADMIN])
def api_keys(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.api_keys
    else:
        return 0


@route.get("/scouting_total")
@has_permission([ADMIN])
def scouting_total(api_key: str, db: Session = Depends(get_db)):
    statistic = db.query(Statistic).first()

    if statistic:
        return statistic.scouting_total
    else:
        return 0


@route.get("/speak_to_expert")
@has_permission([ADMIN, AGRONOMISTS])
def speak_to_expert(api_key: str, db: Session = Depends(get_db)):
    return (
        db.query(
            Contact.title,
            Contact.message,
            Contact.created_at,
            User.name,
            Contact.id,
            User.ph,
            User.email,
        )
        .join(User)
        .filter(User.id == Contact.user_id)
        .all()
    )


@route.get("/speak_to_expert/{id}")
@has_permission([ADMIN, AGRONOMISTS])
def speak_to_expert_detail(api_key: str, id: int, db: Session = Depends(get_db)):
    return (
        db.query(
            Contact.title,
            Contact.message,
            Contact.created_at,
            Contact.name,
            Contact.id,
            User.ph,
            User.email,
        )
        .join(User)
        .filter(User.id == Contact.user_id, Contact.id == id)
        .first()
    )
