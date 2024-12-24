from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2 import func
import re

from db import get_db
from utils.api import has_permission
from cache import get_redis
from models import Farm, User
from constant import ADMIN

route = APIRouter(prefix="/mis", tags=["MIS"])


@route.get("/statistic")
@has_permission([ADMIN])
def statistic(api_key: str, db: Session = Depends(get_db)):
    farmers = db.query(User).filter(User.role == 1).all()
    farms = db.query(
        *[c for c in Farm.__table__.c if c.name not in ["geometry", "bbox", "center"]]
    ).all()

    return {"farmers": farmers, "farms": farms}


@route.get("/global-farm")
@has_permission([ADMIN])
def global_farm(
    api_key: str, bbox: str = "-180,-90,180,90", db: Session = Depends(get_db)
):
    pattern = r"^(-?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?)),(-?(?:90(?:\.0+)?|[1-8]\d(?:\.\d+)?|\d(?:\.\d+)?)),(-?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?)),(-?(?:90(?:\.0+)?|[1-8]\d(?:\.\d+)?|\d(?:\.\d+)?))$"

    if not re.match(pattern, bbox):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="BBOX is not valid"
        )

    bbox = bbox.split(",")

    farms = (
        db.query(Farm.geometry.ST_AsGeoJSON().label("geometry"))
        .filter(Farm.geometry.ST_Intersects(func.ST_MakeEnvelope(*bbox)))
        .all()
    )

    return farms


@route.get("/filter-farm")
@has_permission([ADMIN])
def filter_farm(
    api_key: str,
    country: str = "",
    state: str = "",
    bbox: str = "-180,-90,180,90",
    db: Session = Depends(get_db),
):
    pattern = r"^(-?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?)),(-?(?:90(?:\.0+)?|[1-8]\d(?:\.\d+)?|\d(?:\.\d+)?)),(-?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?)),(-?(?:90(?:\.0+)?|[1-8]\d(?:\.\d+)?|\d(?:\.\d+)?))$"

    if not re.match(pattern, bbox):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="BBOX is not valid"
        )

    bbox = bbox.split(",")
    farms = db.query(Farm).filter(
        Farm.geometry.ST_Intersects(func.ST_MakeEnvelope(*bbox))
    )

    if country != "":
        farms = farms.filter(Farm.country == country)

    if state != "":
        farms = farms.filter(Farm.state == state)

    return farms.count()


@route.get("/cache/drop", include_in_schema=False)
@has_permission([ADMIN])
def cache_drop(
    api_key: str,
):
    """
    Remove All Cache from Redis
    """
    cache = get_redis()
    cache.flushall()
    return {"operation": "success"}
