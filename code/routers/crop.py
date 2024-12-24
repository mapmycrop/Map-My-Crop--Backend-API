from fastapi import APIRouter, Depends, HTTPException, status, Response
from schemas import PostCrop, GetCrop, CropCalendarResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import json

from db import get_db
from models import Crop, CropStage, FarmCrop, CropGrowthStageAdvisory
from utils.api import get_farm, has_permission
from schemas import GetCropGrowthStageAdvisory
from cache import get_redis
from constant import FARMER, COMPANY, ADMIN, AGRONOMISTS

route = APIRouter(prefix="/crop", tags=["Crop"])


@route.get("/", response_model=List[GetCrop])
@has_permission([FARMER, COMPANY])
def index(api_key: str, response: Response, db: Session = Depends(get_db)):
    """
    Get all crop data from databse. Response will be cached

    :param api_key: user's api key
    :param response: FastAPI Response object
    :param db: database
    :return: array of crop
    """
    cache = get_redis()
    cache_key = "crop"

    try:
        cache_response = cache.get(cache_key)
        if cache_response:
            response.headers["x-cached"] = "True"

            return json.loads(cache_response)
    except Exception as e:
        pass

    crops = db.query(Crop).all()
    crops_as_dict = [crop.__dict__ for crop in crops]

    for crop_dict in crops_as_dict:
        crop_dict.pop("_sa_instance_state", None)

    cache.set(cache_key, json.dumps(crops_as_dict), 60 * 60 * 24)

    return crops


@route.post(
    "/", response_model=GetCrop, status_code=status.HTTP_201_CREATED, deprecated=True
)
@has_permission([ADMIN, AGRONOMISTS])
def create(api_key: str, payload: PostCrop, db: Session = Depends(get_db)):
    duplicate = db.query(Crop).filter(Crop.name == payload.name).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Crop with the name already exists",
        )

    row = Crop(**payload.dict())

    db.add(row)
    db.commit()

    return row


@route.get("/crop_stage")
@has_permission([FARMER, COMPANY])
def get_crop_stage(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    get_farm(db, api_key, farm_id)

    latest_crop = (
        db.query(FarmCrop.crop_id)
        .filter(FarmCrop.farm_id == farm_id)
        .order_by(desc(FarmCrop.sowing_date))
        .order_by(desc(FarmCrop.created_at))
        .first()
    )

    if not latest_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Crops found to return crop stage information. Please add crops.",
        )

    crop = (
        db.query(
            Crop.harvesting_days,
            Crop.flowering,
            Crop.seedling,
            Crop.fruiting,
            Crop.maturity,
            Crop.harvesting,
            Crop.germination,
            Crop.vegetative_growth,
            Crop.color,
        )
        .filter(Crop.id == latest_crop.crop_id)
        .all()
    )

    if len(crop) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We are working on adding information, please check in few days",
        )

    return crop


@route.get("/growth_advisory", response_model=List[GetCropGrowthStageAdvisory])
@has_permission([FARMER, ADMIN])
def get_growth_advisory(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    get_farm(db, api_key, farm_id)

    latest_crop = (
        db.query(FarmCrop.crop_id)
        .filter(FarmCrop.farm_id == farm_id)
        .order_by(desc(FarmCrop.sowing_date))
        .order_by(desc(FarmCrop.created_at))
        .first()
    )

    if not latest_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Crops found to return crop stage information. Please add crops.",
        )

    response = (
        db.query(CropGrowthStageAdvisory.advisory, CropGrowthStageAdvisory.stage)
        .filter(CropGrowthStageAdvisory.crop_id == latest_crop.crop_id)
        .all()
    )

    return response


@route.get("/calendar", response_model=List[CropCalendarResponse])
@has_permission([])
def get_crop_calendar(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    get_farm(db, api_key, farm_id)

    latest_crop = (
        db.query(FarmCrop.crop_id)
        .filter(FarmCrop.farm_id == farm_id)
        .order_by(desc(FarmCrop.sowing_date))
        .order_by(desc(FarmCrop.created_at))
        .first()
    )

    if not latest_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Crops found to return crop stage information. Please add crops.",
        )

    crop_stages = (
        db.query(CropStage.stages, CropStage.days, CropStage.title, CropStage.tasks)
        .filter(CropStage.crop == latest_crop.crop_id)
        .all()
    )

    if len(crop_stages) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We are working on adding information, please check in few days",
        )

    return crop_stages


@route.get("/{name}", response_model=GetCrop)
@has_permission([FARMER, ADMIN])
def show(api_key: str, name: str, response: Response, db: Session = Depends(get_db)):
    """
    Get specific crop data according to the crop name. Response will be cached

    :param api_key: user's api key
    :param name: crop name which the user inputs
    :param response: FastAPI Response object
    :param db: database
    :return: crop data
    """
    cache = get_redis()
    cache_key = f"crop_{name}"

    try:
        cache_response = cache.get(cache_key)
        if cache_response:
            response.headers["x-cached"] = "True"

            return json.loads(cache_response)
    except Exception as e:
        pass

    crop = db.query(Crop).filter(Crop.name == name).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    crop_as_dict = crop.__dict__
    crop_as_dict.pop("_sa_instance_state", None)

    cache.set(cache_key, json.dumps(crop_as_dict), 60 * 60 * 24)

    return crop
