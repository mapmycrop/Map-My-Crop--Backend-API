from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from db import get_db
from models import ScheduleCall
from schemas import PostScheduleCall, GetScheduleCall
from utils.api import has_permission
from variables import HowToContact, Topic, TypeOfExpert
from constant import FARMER, COMPANY, ADMIN, AGRONOMISTS

route = APIRouter(prefix="/schedule_call", tags=["Schedule Call"])


@route.post("/", response_model=GetScheduleCall, status_code=status.HTTP_201_CREATED)
@has_permission([FARMER, COMPANY])
def create(
    payload: PostScheduleCall = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "how_to_contact": "whatsapp",
                    "date_time": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                    "topic": "general",
                    "message": "I hope talking with Support team",
                    "type_of_expert": "local",
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    if payload.how_to_contact.value not in [item.value for item in HowToContact]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The how to contact is not valid",
        )

    if payload.date_time == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The datetime is not valid"
        )

    if payload.topic.value not in [item.value for item in Topic]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The topic is not valid"
        )

    if payload.message == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The message is not valid"
        )

    if payload.type_of_expert.value not in [item.value for item in TypeOfExpert]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The type of expert is not valid",
        )

    schedule_call = ScheduleCall(**payload.dict())

    db.add(schedule_call)
    db.commit()
    db.refresh(schedule_call)

    schedule_call.how_to_contact = schedule_call.how_to_contact.value
    schedule_call.topic = schedule_call.topic.value
    schedule_call.type_of_expert = schedule_call.type_of_expert.value

    return schedule_call


@route.get("/", response_model=List[GetScheduleCall])
@has_permission([ADMIN, AGRONOMISTS])
def index(api_key: str, db: Session = Depends(get_db)):
    return db.query(ScheduleCall).all()
