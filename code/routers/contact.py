from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from utils.api import has_permission
from models import Contact, User
from schemas import PostContact, GetContact
from constant import ADMIN

route = APIRouter(prefix="/contact", tags=["Contact"])


@route.post("/", status_code=status.HTTP_201_CREATED)
@has_permission([])
def create(
    payload: PostContact,
    api_key: str,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    data = payload.dict()
    data["user_id"] = s_user.id

    contact = Contact(**data)

    db.add(contact)
    db.commit()

    return True


@route.get("/", response_model=List[GetContact])
@has_permission([ADMIN])
def index(api_key: str, db: Session = Depends(get_db)):
    contacts = (
        db.query(
            Contact.title,
            Contact.message,
            Contact.created_at,
            Contact.source,
            Contact.id,
            User.ph.label("phone"),
            User.email,
        )
        .join(User)
        .filter(User.id == Contact.user_id)
        .all()
    )

    response = []
    for contact in contacts:
        response.append(
            {
                "id": contact.id,
                "title": contact.title,
                "message": contact.message,
                "source": contact.source.value,
                "email": contact.email,
                "phone": contact.phone,
                "created_at": contact.created_at,
            }
        )

    return response
