from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from sqlalchemy.sql import func
from sqlalchemy import or_

from models import (
    Statistic,
    User,
    Farm,
    FarmCrop,
    Scouting,
    EnterpriseStas,
    Company,
    Crop,
)
from listeners.events import Events
from db import SessionLocal


def get_statistic(db):
    statistic = db.query(Statistic).first()

    is_new = statistic is None

    if not statistic:
        farmers_count = db.query(User).filter(User.role == 1).count()
        active_user_count = db.query(User).filter(User.is_active == True).count()
        total_farm_count = db.query(Farm).count()
        total_scouting_count = db.query(Scouting).count()

        statistic = Statistic(
            farmers_count=farmers_count,
            active_users=active_user_count,
            total_farms_mapped=total_farm_count,
            scouting_total=total_scouting_count,
        )

        db.add(statistic)
        db.commit()

    return statistic, is_new


def get_enterprise_statistic(db, enterprise_id):
    statistic = (
        db.query(EnterpriseStas)
        .filter(EnterpriseStas.enterprise_id == enterprise_id)
        .first()
    )

    is_new = statistic is None

    if not statistic:
        company = db.query(Company).filter(Company.id == enterprise_id).first()
        if company:
            total_farmers = (
                db.query(User)
                .filter(User.is_active == True, User.company_id == enterprise_id)
                .count()
            )
            total_farms = (
                db.query(Farm).filter(Farm.company_id == enterprise_id).count()
            )
            total_paid_farms = (
                db.query(Farm)
                .filter(Farm.company_id == enterprise_id, Farm.is_paid == True)
                .count()
            )
            total_unpaid_farms = total_farms - total_paid_farms
            total_area = (
                db.query(func.sum(Farm.area).label("total_area"))
                .filter(Farm.company_id == enterprise_id)
                .scalar()
            )

            statistic = EnterpriseStas(
                enterprise_id=enterprise_id,
                total_farmers=total_farmers,
                total_farms=total_farms,
                total_paid_farms=total_paid_farms,
                total_unpaid_farms=total_unpaid_farms,
                total_area=total_area,
            )

            db.add(statistic)
            db.commit()

    return statistic, is_new


@local_handler.register(event_name=f"{Events.NEW_FARMER_ADDED.value}")
async def handle_new_farmer_event(event: Event):
    event_name, payload = event
    db = SessionLocal()

    statistic, is_new = get_statistic(db)

    if statistic and not is_new:
        statistic.farmers_count += 1
        db.commit()

    enterprise_statistic, is_new = get_enterprise_statistic(db, payload["company_id"])

    if enterprise_statistic and not is_new:
        enterprise_statistic.total_farmers += 1
        db.commit()


@local_handler.register(event_name=f"{Events.NEW_FARM_ADDED.value}")
async def handle_new_farm_event(event: Event):
    event_name, payload = event
    db = SessionLocal()

    statistic, is_new = get_statistic(db)

    if statistic and not is_new:
        statistic.total_farms_mapped += 1
        db.commit()

    enterprise_statistic, is_new = get_enterprise_statistic(db, payload["company_id"])

    if enterprise_statistic and not is_new:
        enterprise_statistic.total_farms += 1
        enterprise_statistic.total_area += payload["area"]

        if payload["is_paid"]:
            enterprise_statistic.total_paid_farms += 1
        else:
            enterprise_statistic.total_unpaid_farms += 1

        db.commit()


@local_handler.register(event_name=f"{Events.NEW_SCOUTING_ADDED.value}")
async def handle_new_scouting_event(event: Event):
    event_name, payload = event
    db = SessionLocal()

    statistic, is_new = get_statistic(db)

    if statistic and not is_new:
        statistic.scouting_total += 1
        db.commit()


@local_handler.register(event_name=f"{Events.NEW_COMPANY_ADDED.value}")
async def handle_new_company_event(event: Event):
    event_name, payload = event
    db = SessionLocal()

    enterprise_statistic = EnterpriseStas(**payload)

    db.add(enterprise_statistic)
    db.commit()


@local_handler.register(event_name=f"{Events.FARM_PAYMENT_UPDATED.value}")
async def handle_farm_payment_updated_event(event: Event):
    event_name, payload = event
    api_keys = payload["api_keys"]
    payment_status = payload["payment_status"]

    db = SessionLocal()

    rows = (
        db.query(Farm.company_id, func.count(Farm.company_id).label("count"))
        .filter(
            or_(
                Farm.id.in_(api_keys),
                Farm.user_id.in_(db.query(User.id).filter(User.apikey.in_(api_keys))),
                Farm.company_id.in_(
                    db.query(Company.id).filter(Company.apikey.in_(api_keys))
                ),
            )
        )
        .group_by(Farm.company_id)
        .all()
    )

    for row in rows:
        enterprise_statistic, is_new = get_enterprise_statistic(db, row.company_id)

        if enterprise_statistic and not is_new:
            if payment_status:
                enterprise_statistic.total_paid_farms += row.count
                enterprise_statistic.total_unpaid_farms -= row.count
            else:
                enterprise_statistic.total_paid_farms -= row.count
                enterprise_statistic.total_unpaid_farms += row.count

    db.commit()


@local_handler.register(event_name=f"{Events.FARM_CROP_ADDED.value}")
async def handle_farm_crop_saved(event: Event):
    """
    Set enterprise statistic table for crop_wise column with updated farm crop
    :param event: Event including event_name and payload
    """

    event_name, payload = event
    db = SessionLocal()

    farm = db.query(Farm.company_id).filter(Farm.id == payload["farm_id"]).first()
    enterprise_statistic, is_new = get_enterprise_statistic(db, farm.company_id)

    if enterprise_statistic and not is_new:
        subquery = (
            db.query(Farm.id).filter(Farm.company_id == farm.company_id).subquery()
        )
        crops = (
            db.query(Crop.name, func.count(Crop.id).label("count"))
            .join(FarmCrop, FarmCrop.crop_id == Crop.id)
            .filter(FarmCrop.farm_id.in_(subquery))
            .group_by(Crop.id)
            .all()
        )

        crop_wise = {}
        for crop in crops:
            crop_wise[crop["name"]] = crop["count"]

        enterprise_statistic.crop_wise = crop_wise
        db.commit()
