from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from models import Advisory
from schemas import PostAdvisory, GetAdvisory, AdvisoryShowResponse
from constant import FARMER, COMPANY, ADMIN, AGRONOMISTS
from utils.api import get_crop, has_permission

route = APIRouter(prefix="/advisory", tags=["Advisory"])


@route.get("/all", response_model=List[GetAdvisory])
@has_permission([FARMER, COMPANY])
def index(api_key: str, type: Optional[str] = None, db: Session = Depends(get_db)):
    results = db.query(Advisory)

    if type:
        results = results.filter(Advisory.type == type)

    response = list()

    for row in results:
        if not row.crop:
            row.crop = "All Crops"

        response.append(row)

    return response


@route.post("/create", response_model=GetAdvisory)
@has_permission([ADMIN, AGRONOMISTS])
def create(api_key: str, payload: PostAdvisory, db: Session = Depends(get_db)):
    selected_crop = get_crop(db, payload.crop)

    advisory = Advisory(**payload.dict())
    advisory.crop = selected_crop.id

    db.add(advisory)
    db.commit()
    db.refresh(advisory)

    advisory.crop = selected_crop.name

    return advisory


@route.get("/", response_model=AdvisoryShowResponse)
@has_permission([FARMER, COMPANY])
def show(
    api_key: str,
    humidity: Optional[float] = None,
    temperature: Optional[float] = None,
    wind: Optional[float] = None,
    rainfall: Optional[float] = None,
    uv: Optional[float] = None,
    soilmoisture: Optional[float] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Advisory.advisory_title, Advisory.advisory_desc, Advisory.flag)
    result = {}

    if humidity:
        result["humidity"] = query.filter(
            Advisory.humidity_min <= humidity, Advisory.humidity_max >= humidity
        ).all()

    if temperature:
        result["temperature"] = query.filter(
            Advisory.min_temp <= temperature, Advisory.max_temp >= temperature
        ).all()

    if wind:
        result["wind"] = query.filter(
            Advisory.min_wind <= wind, Advisory.max_wind >= wind
        ).all()

    if rainfall:
        result["rainfall"] = query.filter(
            Advisory.min_rainfall <= rainfall, Advisory.max_rainfall >= rainfall
        ).all()

    if soilmoisture:
        result["soilmoisture"] = query.filter(
            Advisory.min_soilmoisture <= soilmoisture,
            Advisory.max_soilmoisture >= soilmoisture,
        ).all()

    if uv:
        result["uv"] = query.filter(Advisory.min_uv <= uv, Advisory.max_uv >= uv).all()

    return result
