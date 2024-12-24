from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from models import Feedback
from schemas import GetFeedback, PostFeedback
from utils.api import has_permission
from constant import ADMIN

route = APIRouter(prefix="/feedback", tags=["Feedback"])


@route.get("/", response_model=List[GetFeedback])
@has_permission([ADMIN])
def index(api_key: str, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).all()

    return feedback


@route.post("/", response_model=GetFeedback)
@has_permission([])
def create(
    payload: PostFeedback = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "feedback": "I want to update the API",
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    feedback = Feedback(**payload.dict())

    db.add(feedback)
    db.commit()

    return feedback
