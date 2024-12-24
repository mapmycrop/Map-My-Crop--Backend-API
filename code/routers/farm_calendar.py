from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import date
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from utils.api import get_farm, has_permission
from schemas import GetCalendarData, PostCalendarData
from models import CalendarData
from db import get_db
from constant import FARMER, COMPANY

route = APIRouter(prefix="/farm-calendar", tags=["Farm Calendar"])


@route.get("/{farm_id}", response_model=List[GetCalendarData])
@has_permission([FARMER, COMPANY])
def index(farm_id: str, api_key: str, db: Session = Depends(get_db)):
    get_farm(db, api_key, farm_id)

    calendar_data = db.query(CalendarData).filter(CalendarData.farm == farm_id).all()

    return calendar_data


@route.post("/", response_model=GetCalendarData, status_code=status.HTTP_201_CREATED)
@has_permission([FARMER])
def create(
    calendar_data: PostCalendarData = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "farm": "{{farm_id}}",
                    "title": "Tilage",
                    "description": "description",
                    "start_date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    get_farm(db, api_key, calendar_data.farm)

    if calendar_data.title not in [
        "Tilage",
        "Planting",
        "Fertilization",
        "Spraying",
        "Harvesting",
        "Planned Cost",
        "Other",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The title is not valid"
        )

    if calendar_data.end_date < calendar_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The End Date is not valid"
        )

    row = CalendarData(**calendar_data.dict())

    db.add(row)
    db.commit()
    db.refresh(row)

    new_calendar_data = db.query(CalendarData).filter(CalendarData.id == row.id).one()

    return new_calendar_data


@route.put("/{id}", response_model=GetCalendarData)
@has_permission([FARMER])
def update(
    id: int,
    calendar_data: PostCalendarData = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "farm": "{{farm_id}}",
                    "title": "Tilage",
                    "description": "description",
                    "start_date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    row = db.query(CalendarData).filter(CalendarData.id == id).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar data not found"
        )

    get_farm(db, api_key, row.farm)

    get_farm(db, api_key, calendar_data.farm)

    if calendar_data.end_date < calendar_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The End Date is not valid"
        )

    if calendar_data.title is not None:
        row.title = calendar_data.title

    if calendar_data.description is not None:
        row.description = calendar_data.description

    row.start_date = calendar_data.start_date
    row.end_date = calendar_data.end_date

    db.commit()

    return row


@route.delete("/{id}")
@has_permission([FARMER])
def delete(id: int, api_key: str, db: Session = Depends(get_db)):
    calendar_data = db.query(CalendarData).filter(CalendarData.id == id).one()

    if not calendar_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There is not calendar data for this id",
        )

    get_farm(db, api_key, calendar_data.farm)

    db.delete(calendar_data)
    db.commit()

    return True
