from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json

from db import get_db
from models import Fertilizer, FarmCrop, Crop
from schemas import ResForFertilizer, PostFertilizer, GetFertilizer
from utils.api import has_permission, get_farm


route = APIRouter(prefix="/fertilizer", tags=["Fertilizer"])


@route.post("/", response_model=GetFertilizer)
@has_permission([])
def create(
    api_key: str,
    payload: PostFertilizer = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "crop_id": "{{crop_id}}",
                    "urea": 2.3,
                    "ssp": 3.6,
                    "mop": 5.6,
                    "dap": 6.3,
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop doesn't exist"
        )

    fertilizer = Fertilizer(**payload.dict())

    db.add(fertilizer)
    db.commit()

    return fertilizer


@route.get("/", response_model=ResForFertilizer)
@has_permission([])
def index(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    """
    Get Fertilizer using api key and farm id

    :param api_key: user's api key
    :param farm_id: user's farm id
    :param db: database dependencies
    :return: return fertilizer data
    """

    farm = get_farm(db, api_key, farm_id)

    area = json.loads(farm.geom)["properties"]["area"]

    row = (
        db.query(FarmCrop, Crop)
        .filter(FarmCrop.farm_id == farm_id)
        .order_by(desc(FarmCrop.id))
        .join(Crop, Crop.id == FarmCrop.crop_id)
        .first()
    )

    crop = row.Crop

    fertilizer = db.query(Fertilizer).filter(Fertilizer.crop_id == crop.id).first()

    if not fertilizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="That Crop doesn't exist in fertilizer list",
        )

    if not area:
        area = 0

    response = ResForFertilizer(
        crop=crop.name,
        urea=round(fertilizer.urea * area, 2),
        ssp=round(fertilizer.ssp * area, 2),
        mop=round(fertilizer.mop * area, 2),
        dap=round(fertilizer.dap * area, 2),
    )

    return response
