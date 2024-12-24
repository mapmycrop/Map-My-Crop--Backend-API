from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from models import FarmCrop
from utils.api import (
    has_permission,
    get_farm,
    get_crop,
    check_crop_params,
)
from schemas import CreateFarmCropPayload, StoreFarmCrop
from constant import FARMER

route = APIRouter(prefix="/farm-crop", tags=["Farm Crop"])


@route.post("/")
@has_permission([FARMER])
def create_crop(
    api_key: str,
    farm_id: str,
    payload: CreateFarmCropPayload,
    db: Session = Depends(get_db),
):
    """
    Create farm crop

    :param api_key: user's api key
    :param farm_id: farm's primary key
    :param payload: payload for creatation
    :param db: database dependencies
    :return: return farm as GEOJSON
    """
    get_farm(db, api_key, farm_id)
    crop = get_crop(db, payload.crop)

    stored_crop = StoreFarmCrop(farm_id=farm_id, crop_id=crop.id, **payload.dict())

    check_crop_params(payload.sowing_date, payload.harvesting_date, payload.season)

    stored_crop_dic = stored_crop.dict()
    stored_crop_dic.pop("crop", None)

    stored_crop_dic = FarmCrop(**stored_crop_dic)

    db.add(stored_crop_dic)
    db.commit()

    return True


@route.put("/")
@has_permission([FARMER])
def update_crop(
    api_key: str,
    farm_id: str,
    crop_id: str,
    payload: CreateFarmCropPayload,
    db: Session = Depends(get_db),
):
    """
    Update farm crop

    :param api_key: user's api key
    :param farm_id: farm's primary key
    :param crop_id: crop's primary key
    :param payload: payload for creatation
    :param db: database dependencies
    :return: return farm as GEOJSON
    """
    get_farm(db, api_key, farm_id)

    selected_crop = (
        db.query(FarmCrop)
        .filter(FarmCrop.crop_id == crop_id, farm_id == FarmCrop.farm_id)
        .first()
    )

    if not selected_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm crop not found"
        )

    check_crop_params(payload.sowing_date, payload.harvesting_date, payload.season)

    selected_crop.sowing_date = payload.sowing_date
    selected_crop.harvesting_date = payload.harvesting_date
    selected_crop.season = payload.season
    selected_crop.irrigation_type = payload.irrigation_type
    selected_crop.tillage_type = payload.tillage_type
    selected_crop.maturity = payload.maturity
    selected_crop.target_yield = payload.target_yield
    selected_crop.actual_yield = payload.actual_yield

    crop = get_crop(db, payload.crop)
    selected_crop.crop_id = crop.id

    db.commit()

    return True
