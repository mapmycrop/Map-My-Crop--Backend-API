from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from typing import List, Optional

from db import get_db
from utils.api import has_permission
from models import User, Farm
from schemas import NormalUserForCompany, GetFarm
from constant import COMPANY

route = APIRouter(prefix="/company", tags=["Company"], deprecated=True)


@route.get("/users", response_model=Page[NormalUserForCompany])
@has_permission([COMPANY])
def users(
    api_key: str = "", db: Session = Depends(get_db), s_user=Depends(lambda: None)
):
    return paginate(
        db,
        select(
            User.ph,
            User.email,
            User.apikey,
            User.created_at,
            User.is_active,
            User.country_code,
        ).where(User.company_id == s_user.id),
    )


@route.get("/farms", response_model=List[GetFarm])
@has_permission([COMPANY])
def farms(
    api_key: str = "",
    user_api_key: str = "",
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    user = (
        db.query(User)
        .filter(User.company_id == s_user.id, User.apikey == user_api_key)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User API Key is not valid"
        )

    farms = (
        db.query(
            *[
                c
                for c in Farm.__table__.c
                if c.name not in ["geometry", "bbox", "center"]
            ]
        )
        .filter(Farm.user_id == user.id)
        .all()
    )

    return farms
