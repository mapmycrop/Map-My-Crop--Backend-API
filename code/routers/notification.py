from fastapi import APIRouter, status, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from shapely.wkt import loads
from geoalchemy2 import func

from models import Farm, User
from schemas import PostNotification, NotificationPayload
from db import get_db
from utils.api import has_permission
from constant import ADMIN, AGRONOMISTS, COMPANY
from utils.notification import send_notification

route = APIRouter(prefix="/notification", tags=["Notification"])


@route.post("/", status_code=status.HTTP_200_OK, deprecated=True)
@has_permission([ADMIN, AGRONOMISTS])
def create(
    api_key: str,
    payload: PostNotification,
    db: Session = Depends(get_db),
):
    try:
        loads(payload.polygon)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The polygon is incorrect"
        )

    farms = (
        db.query(
            func.ST_AsGeoJSON(Farm).label("geom"),
            User.email,
            User.ph.label("phone"),
            User.name,
        )
        .filter(Farm.geometry.ST_Intersects(payload.polygon))
        .join(User)
        .filter(Farm.user_id == User.id)
        .all()
    )

    response = {"farms": farms, "count": len(farms)}

    return response


@route.post("/send_msg")
@has_permission([COMPANY])
def send_message(
    api_key: str,
    payload: NotificationPayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "User can send message via SMS, WHATSAPP and EMAIL",
                "value": {
                    "farmers_api_key": ["123456789", "987654321"],
                    "message_title": "MMC Notification",
                    "message_content": "Please write description here",
                    "message_type": "EMAIL, SMS or WHATSAPP",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    if payload.message_type == "EMAIL":
        users = (
            db.query(User.email.label("contact"), User.name.label("name"))
            .filter(User.apikey.in_(payload.farmers_api_key))
            .filter(User.email != "")
            .all()
        )

    else:
        users = (
            db.query(User.ph.label("contact"), User.name.label("name"))
            .filter(User.apikey.in_(payload.farmers_api_key))
            .filter(User.ph != "")
            .all()
        )

    for user in users:
        send_notification(
            payload.message_type,
            user.contact,
            user.name,
            payload.message_title,
            payload.message_content,
        )

    return True
