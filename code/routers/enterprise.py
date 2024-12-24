from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from db import get_db
from utils.api import has_permission
from schemas import (
    EnterpriseGetFarmersResponse,
    EnterpriseGetFarmersCountResponse,
    EnterpriseGetFarmsCountResponse,
    EnterpriseGetTotalAreaResponse,
    EnterpriseGetCropWiseResponse,
)
from models import User, EnterpriseStas
from constant import COMPANY


route = APIRouter(prefix="/enterprise", tags=["Enterprise"])


@route.get("/farmers-list", deprecated=True)
def farmers_list(
    api_key: str = "", search_word: str = "", db: Session = Depends(get_db)
):
    return


@route.get("/farmers", response_model=Page[EnterpriseGetFarmersResponse])
@has_permission([COMPANY])
def farmers_list(
    api_key: str = "",
    search_word: str = "",
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Get farmers list belongs to certain enterprise

    :param api_key: enterprise api key
    :param search_word: keyword to search user name, email and phone
    :param db: database
    :return: Farmers list including id, apikey, name
    """
    response = paginate(
        db,
        select(User.id, User.name, User.ph, User.email, User.apikey).filter(
            User.company_id == s_user.id,
            or_(
                User.ph.like(f"%{search_word}%"),
                User.name.like(f"%{search_word}%"),
                User.email.like(f"%{search_word}%"),
            ),
        ),
    )

    return response


@route.get("/farmers-count", response_model=EnterpriseGetFarmersCountResponse | None)
@has_permission([COMPANY])
def farmers_count(
    api_key: str, db: Session = Depends(get_db), s_user=Depends(lambda: None)
):
    """
    Get enterprise farmer's count according to enterprise id

    :param api_key: user's api key
    :param enterprise_id: enterprise's primary key
    :return: enterprise farmer's count
    """
    response = (
        db.query(EnterpriseStas.total_farmers.label("farmers_count"))
        .filter(EnterpriseStas.enterprise_id == s_user.id)
        .first()
    )

    return response


@route.get("/farms-count", response_model=EnterpriseGetFarmsCountResponse | None)
@has_permission([COMPANY])
def farms_count(
    api_key: str, db: Session = Depends(get_db), s_user=Depends(lambda: None)
):
    """
    Get enterprise farm's count according to enterprise id

    :param api_key: user's api key
    :param enterprise_id: enterprise's primary key
    :return: enterprise farm's count
    """
    response = (
        db.query(EnterpriseStas.total_farms.label("farms_count"))
        .filter(EnterpriseStas.enterprise_id == s_user.id)
        .first()
    )

    return response


@route.get("/total-area", response_model=EnterpriseGetTotalAreaResponse | None)
@has_permission([COMPANY])
def total_area(
    api_key: str, db: Session = Depends(get_db), s_user=Depends(lambda: None)
):
    """
    Get enterprise area according to enterprise id

    :param api_key: user's api key
    :param enterprise_id: enterprise's primary key
    :return: enterprise area
    """
    response = (
        db.query(EnterpriseStas.total_area)
        .filter(EnterpriseStas.enterprise_id == s_user.id)
        .first()
    )

    return response


@route.get("/crop-wise", response_model=EnterpriseGetCropWiseResponse | None)
@has_permission([COMPANY])
def crop_wise(
    api_key: str, db: Session = Depends(get_db), s_user=Depends(lambda: None)
):
    """
    Get enterprise crop_wise according to enterprise id

    :param api_key: user's api key
    :param enterprise_id: enterprise's primary key
    :return: enterprise crop_wise
    """
    response = (
        db.query(EnterpriseStas.crop_wise)
        .filter(EnterpriseStas.enterprise_id == s_user.id)
        .first()
    )

    return response
