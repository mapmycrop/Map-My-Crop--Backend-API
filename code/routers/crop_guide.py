from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from models import CropGuide
from schemas import CropGuide as CropGuideSchema
from utils.api import has_permission


route = APIRouter(prefix="/crop-guide", tags=["Crop Guide"])


@route.get("/", response_model=List[CropGuideSchema])
@has_permission([])
def index(api_key: str, db: Session = Depends(get_db)):
    rows = db.query(CropGuide).all()

    return rows


@route.post("/", response_model=CropGuideSchema, deprecated=True)
def create(
    payload: CropGuideSchema = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "name": "Crop",
                    "link": "https://crop.com",
                    "image_url": "https://crop.com/guide.jpg",
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    crop_guide = CropGuide(**payload.dict())

    db.add(crop_guide)
    db.commit()

    return crop_guide
