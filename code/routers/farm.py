from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from geoalchemy2 import func
from shapely.wkt import loads
from sqlalchemy import desc
import json
import requests
from datetime import datetime

from config import setting
from db import get_db
from models import (
    Farm,
    FarmCrop,
    Crop,
    Scouting,
    States,
    CalendarData,
    PlanetCollection,
)
from utils.api import get_farm, check_farm_bounds, has_permission, get_all_farms
from schemas import (
    CreateFarmCropPayload,
    CreateFarmPayload,
    UpdateFarmPayload,
)
from constant import FARMER, COMPANY

route = APIRouter(prefix="/farm", tags=["Farm"])

SENTINEL_HUB_CLIENT_ID = setting.SENTINEL_HUB_CLIENT_ID
SENTINEL_HUB_CLIENT_SECRET = setting.SENTINEL_HUB_CLIENT_SECRET
PLANET_API_KEY = setting.PLANET_API_KEY


@route.get("/")
@has_permission([FARMER, COMPANY])
def index(
    api_key: str = "",
    paid: bool = None,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Get farm list according to api key

    :param api_key: user's api key
    :param paid: True if it's paid, False it not
    :param db: database dependencies
    :return: return all farms belongs to farmer
    """

    query = db.query(
        *[c for c in Farm.__table__.c if c.name not in ["geometry", "bbox", "center"]]
    )

    if paid is not None:
        query = query.filter(Farm.is_paid == paid)

    # Farmer
    if s_user.role == 1:
        farms = (
            query.filter(Farm.user_id == s_user.id)
            .order_by(desc(Farm.created_at))
            .all()
        )

    # Company
    if s_user.role == 2:
        farms = (
            query.filter(Farm.company_id == s_user.id)
            .order_by(desc(Farm.created_at))
            .all()
        )

    return farms


@route.post("/create", status_code=status.HTTP_201_CREATED)
@has_permission([FARMER])
def create(
    api_key: str = "",
    payload: CreateFarmPayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "name": "My Farm",
                    "description": "My farm for apple",
                    "geometry": "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Create a farm with data

    :param api_key: user's api key
    :param payload: payload including name, description, and geometry
    :param db: database dependencies
    :return: return all farms belongs to farmer
    """

    if s_user:
        payload.user_id = s_user.id
        payload.company_id = s_user.company_id

    if len(payload.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Name cannot be longer than 50 characters",
        )

    if payload.description and len(payload.description) > 200:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Description cannot be longer than 200 characters",
        )

    try:
        polygon = loads(payload.geometry)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The geometry is incorret"
        )

    if polygon.type != "Polygon":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Geometry can only be a polygon",
        )

    if (
        polygon.bounds[0] < -180
        or polygon.bounds[1] < -90
        or polygon.bounds[2] > 180
        or polygon.bounds[3] > 90
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Something is wrong with the geometry.Check if it's 4326 projection",
        )

    check_farm_bounds(db, polygon.bounds)

    existed_farm = (
        db.query(Farm)
        .filter(
            Farm.name == payload.name
            and Farm.user_id == payload.user_id
            and Farm.company_id == payload.company_id
        )
        .first()
    )

    if existed_farm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farm name already exists. Please use another name.",
        )

    try:
        (state, country) = (
            db.query(States.name, States.admin)
            .filter(
                func.ST_Within(
                    func.ST_GeomFromText(str(polygon.centroid), 4326), States.geom
                )
            )
            .first()
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not locate farm in any state",
        )

    farm = Farm(
        **payload.dict(), bbox=list(polygon.bounds), state=state, country=country
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    my_farm = (
        db.query(func.ST_AsGeoJSON(Farm).label("geom")).filter(Farm.id == farm.id).one()
    )

    feature = json.loads(my_farm["geom"])

    # create planet collection

    response = {"type": "FeatureCollection", "features": [feature]}

    return response


@route.get("/all")
@has_permission([FARMER, COMPANY])
def get_all(
    api_key: str = "",
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    features = []

    farms = None

    if s_user.role == 1:
        farms = (
            db.query(
                func.ST_AsGeoJSON(Farm).label("geom"),
                func.json_agg(
                    func.json_build_object(
                        "sowing_date",
                        FarmCrop.sowing_date,
                        "harvesting_date",
                        FarmCrop.harvesting_date,
                        "season",
                        FarmCrop.season,
                        "id",
                        Crop.id,
                        "name",
                        Crop.name,
                    )
                ).label("crops"),
            )
            .outerjoin(FarmCrop, FarmCrop.farm_id == Farm.id)
            .outerjoin(Crop, FarmCrop.crop_id == Crop.id)
            .filter(Farm.user_id == s_user.id)
            .group_by(Farm.id)
            .order_by(desc(Farm.created_at))
            .all()
        )

    if s_user.role == 2:
        farms = (
            db.query(
                func.ST_AsGeoJSON(Farm).label("geom"),
                func.json_agg(
                    func.json_build_object(
                        "sowing_date",
                        FarmCrop.sowing_date,
                        "harvesting_date",
                        FarmCrop.harvesting_date,
                        "season",
                        FarmCrop.season,
                        "id",
                        Crop.id,
                        "name",
                        Crop.name,
                    )
                ).label("crops"),
            )
            .outerjoin(FarmCrop, FarmCrop.farm_id == Farm.id)
            .outerjoin(Crop, FarmCrop.crop_id == Crop.id)
            .filter(Farm.company_id == s_user.id)
            .group_by(Farm.id)
            .order_by(desc(Farm.created_at))
            .all()
        )

    if not farms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm with given id not found for the API key",
        )

    for item in farms:
        temp = json.loads(item["geom"])
        temp["properties"]["crops"] = item["crops"]
        features.append(temp)

    return features


@route.get("/{farm_id}")
@has_permission([FARMER, COMPANY])
def show(api_key: str = "", farm_id: str = "", db: Session = Depends(get_db)):
    """
    Get farm according to id

    :param api_key: user's api key
    :param farm_id: farm's primary key
    :param db: database dependencies
    :return: return farm as GEOJSON
    """

    farm = get_farm(db, api_key, farm_id)

    feature = json.loads(farm["geom"])

    crops = (
        db.query(FarmCrop, Crop.name)
        .filter(FarmCrop.farm_id == farm_id)
        .filter(Crop.id == FarmCrop.crop_id)
        .order_by(desc(FarmCrop.sowing_date))
        .all()
    )

    crops_list = []
    for crop in crops:
        crops_list.append(
            {
                "sowing_date": crop[0].sowing_date,
                "harvesting_date": crop[0].harvesting_date,
                "season": crop[0].season,
                "id": crop[0].crop_id,
                "name": crop[1],
            }
        )

    feature["properties"]["crops"] = crops_list
    response = {"type": "FeatureCollection", "features": [feature]}

    return response


@route.put("/{farm_id}")
@has_permission([FARMER, COMPANY])
def update(
    api_key: str,
    farm_id: str,
    payload: UpdateFarmPayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {"name": "My Farm"},
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Update farm's name according to id

    :param api_key: user's api key
    :param farm_id: farm's primary key
    :param payload: payload including name
    :param db: database dependencies
    :return: return True if success, False it not
    """

    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farm doesn't exists",
        )

    existed_farm = (
        db.query(Farm)
        .filter(Farm.name == payload.name)
        .filter(Farm.id != farm.id)
        .filter(Farm.user_id == farm.user_id)
        .filter(Farm.company_id == farm.company_id)
        .first()
    )

    if existed_farm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farm name already exists. Please use another name.",
        )

    farm.name = payload.name

    db.commit()

    return True


@route.delete("/{farm_id}")
@has_permission([FARMER])
def delete(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    """
    Delete farm

    :param api_key: user's api key
    :param farm_id: farm's primary key
    :param db: database dependencies
    :return: return farm as GEOJSON
    """
    get_farm(db, api_key, farm_id)

    db.query(FarmCrop).filter(FarmCrop.farm_id == farm_id).delete()
    db.query(Scouting).filter(Scouting.farm == farm_id).delete()
    db.query(CalendarData).filter(CalendarData.farm == farm_id).delete()
    db.query(Farm).filter(Farm.id == farm_id).delete()

    db.commit()

    return True


@route.post("/crop/{farm_id}", deprecated=True)
def create_crop(
    api_key: str,
    farm_id: str,
    payload: CreateFarmCropPayload,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    return


@route.put("/crop/{farm_id}", deprecated=True)
def update_crop(
    api_key: str,
    farm_id: str,
    crop_id: str,
    payload: CreateFarmCropPayload,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    return
