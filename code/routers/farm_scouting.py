from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from shapely.wkt import loads
from typing import List
from geoalchemy2 import func
from shapely.geometry import shape
from shapely import wkt
import re
import json

from utils.api import get_farm, has_permission
from db import get_db
from schemas import PostScouting, GetScouting, PutScouting
from models import Scouting
from constant import FARMER, COMPANY, ADMIN

route = APIRouter(prefix="/farm-scouting", tags=["Farm Scouting"])


def check_point_in_polygon(point, feature):
    """
    point:string Point(x, y)
    feature:geojson geometry json
    """
    feature = json.loads(feature)

    point = wkt.loads(point)
    polygon = shape(feature["geometry"])

    return polygon.contains(point)


@route.get("/{farm_id}", response_model=List[GetScouting])
@has_permission([FARMER, COMPANY])
def index_farm_scouting__farm_id__get(
    farm_id: str,
    api_key: str,
    bbox: str = "-180,-90,180,90",
    db: Session = Depends(get_db),
):
    get_farm(db, api_key, farm_id)

    pattern = r"^(-?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?)),(-?(?:90(?:\.0+)?|[1-8]\d(?:\.\d+)?|\d(?:\.\d+)?)),(-?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?)),(-?(?:90(?:\.0+)?|[1-8]\d(?:\.\d+)?|\d(?:\.\d+)?))$"

    if not re.match(pattern, bbox):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="BBOX is not valid"
        )

    bbox = bbox.split(",")

    scoutings = (
        db.query(
            Scouting.farm,
            Scouting.geometry.ST_AsGeoJSON().label("geometry"),
            Scouting.note_type,
            Scouting.id,
            Scouting.comments,
            Scouting.attachments,
            Scouting.status,
            Scouting.title,
            Scouting.due_date,
            Scouting.scouting_date,
            Scouting.created_at,
            Scouting.ground_notes,
            Scouting.amount,
        )
        .filter(
            Scouting.farm == farm_id,
            Scouting.geometry.ST_Intersects(func.ST_MakeEnvelope(*bbox)),
        )
        .all()
    )

    return scoutings


@route.post("/", response_model=GetScouting, status_code=status.HTTP_201_CREATED)
@has_permission([FARMER])
def create_farm_scouting__post(
    scouting: PostScouting = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "farm": "{{farm_id}}",
                    "title": "scouting title",
                    "geometry": "POINT(18.232 73.221)",
                    "note_type": "Disease",
                    "comments": "This is initial stage",
                    "attachments": ["https://bit.ly/krishna_youtube"],
                    "status": "open",
                    "due_date": "2024-03-01",
                    "scouting_date": "2024-03-01",
                    "ground_notes": "Ground notes",
                    "amount": 0,
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    farm = get_farm(db, api_key, scouting.farm)

    if not check_point_in_polygon(scouting.geometry, farm["geom"]):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Scouting point is outside farm",
        )

    try:
        loads(scouting.geometry)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The geometry is incorrect"
        )

    scouting = Scouting(**scouting.dict())

    db.add(scouting)
    db.commit()
    db.refresh(scouting)

    (scouting.geometry,) = (
        db.query(Scouting.geometry.ST_AsGeoJSON())
        .filter(Scouting.id == scouting.id)
        .one()
    )

    return scouting


@route.put("/{id}", response_model=GetScouting)
@has_permission([FARMER])
def update_farm_scouting__id__put(
    id: int,
    scouting: PutScouting = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "title": "scouting title",
                    "geometry": "POINT(18.232 73.221)",
                    "note_type": "Disease",
                    "comments": "This is initial stage",
                    "attachments": ["https://bit.ly/krishna_youtube"],
                    "status": "open",
                    "due_date": "2024-03-01",
                    "scouting_date": "2024-03-01",
                    "ground_notes": "Ground notes",
                    "amount": 0,
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):

    row = db.query(Scouting).filter(Scouting.id == id).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scouting not found"
        )

    farm = get_farm(db, api_key, row.farm)

    if scouting.geometry is not None:
        if not check_point_in_polygon(scouting.geometry, farm["geom"]):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Scouting point is outside farm",
            )
        else:
            try:
                loads(scouting.geometry)
                row.geometry = scouting.geometry
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The geometry is incorrect",
                )

    if scouting.title is not None:
        row.title = scouting.title

    if scouting.note_type is not None:
        row.note_type = scouting.note_type

    if scouting.comments is not None:
        row.comments = scouting.comments

    if scouting.attachments is not None:
        row.attachments = scouting.attachments

    if scouting.status is not None:
        row.status = scouting.status

    if scouting.due_date is not None:
        row.due_date = scouting.due_date

    if scouting.scouting_date is not None:
        row.scouting_date = scouting.scouting_date

    if scouting.ground_notes is not None:
        row.ground_notes = scouting.ground_notes

    if scouting.amount is not None:
        row.amount = scouting.amount

    db.commit()
    db.refresh(row)

    (row.geometry,) = (
        db.query(Scouting.geometry.ST_AsGeoJSON()).filter(Scouting.id == id).one()
    )

    return row


@route.delete("/{id}")
@has_permission([FARMER, COMPANY, ADMIN])
def ddelete_farm_scouting__id__deleteelete(
    id: int, api_key: str, db: Session = Depends(get_db)
):
    row = db.query(Scouting).filter(Scouting.id == id).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scouting not found"
        )

    db.delete(row)
    db.commit()

    return True
