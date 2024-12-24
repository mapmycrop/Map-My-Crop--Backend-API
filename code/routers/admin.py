from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from fastapi_events.dispatcher import dispatch
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from re import compile
from datetime import datetime, timedelta, date
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from cache import get_redis
import requests
from geoalchemy2 import func
import json

from db import get_db
from models import (
    Company,
    Farm,
    User,
    Payment,
    ScheduleCall,
    PlanetCollection,
    Resellers,
)
import uuid

from schemas import (
    GetCompany,
    PostCompany,
    UpdatePaymentStatus,
    AddCashPayment,
    UpdatePaymentStatusResponse,
    AdminPaidFarmsResponse,
    AdminExpertRequestsResponse,
    UpdateUser,
    ResellerStatusModifyInput,
    RequestUserInfo,
)
from utils.auth import get_user_by_email
from utils.api import has_permission, get_user
from utils.password import secure_pwd
from listeners.events import Events
from config import setting
from constant import ADMIN

route = APIRouter(prefix="/admin", tags=["Admin"])
Page = Page.with_custom_options(size=Query(1000, ge=1, le=1000))

SENTINEL_HUB_CLIENT_ID = setting.SENTINEL_HUB_CLIENT_ID
SENTINEL_HUB_CLIENT_SECRET = setting.SENTINEL_HUB_CLIENT_SECRET
PLANET_API_KEY = setting.PLANET_API_KEY


@route.post("/company", response_model=GetCompany)
@has_permission([ADMIN])
def register(
    payload: PostCompany = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "email": "info@mapmycrop.com",
                    "password": "IS4Z?OTR4FN6K+IKNB",
                    "name": "Map My Crop",
                    "site": "mapmycrop.com",
                    "country": "India",
                    "ph": "911122334455",
                    "unit": "imperial",
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    if payload.email:
        email_exist = get_user_by_email(db, payload.email)
        if email_exist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company with this email already exists",
            )

    name_exist = db.query(Company).filter(Company.name == payload.name).first()

    if name_exist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company with this name already exists",
        )

    pattern = compile(r"[^\s]{8,24}$")
    if not pattern.match(payload.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password should between 8 and 24 characters and contain no space",
        )

    payload.password = secure_pwd(payload.password)

    company = Company(**payload.dict())

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@route.put("/update-user")
@has_permission([ADMIN])
def register(
    payload: UpdateUser = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "api_key": "1234567890123456789",
                    "email": "info@mapmycrop.com",
                    "password": "IS4Z?OTR4FN6K+IKNB",
                    "is_active": True,
                    "company_id": 123,
                    "name": "name",
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    user = get_user(db, payload.api_key, [], False)

    if hasattr(payload, "company_id"):
        if hasattr(user, "company_id"):
            company = db.query(Company).filter(Company.id == payload.company_id).first()
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Company doesn't exist",
                )
            user.company_id = payload.company_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This user doesn't have company ID",
            )

    if hasattr(payload, "email"):
        email_exist = get_user_by_email(db, payload.email)
        if email_exist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email already exists",
            )
        user.email = payload.email

    if hasattr(payload, "password"):
        pattern = compile(r"[^\s]{8,24}$")
        if not pattern.match(payload.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Password should between 8 and 24 characters and contain no space",
            )
        user.password = secure_pwd(payload.password)

    if hasattr(payload, "is_active"):
        user.is_active = payload.is_active

    if hasattr(payload, "name"):
        user.name = payload.name

    db.commit()

    return True


@route.put("/payment_status", response_model=UpdatePaymentStatusResponse)
@has_permission([ADMIN])
def update_payment_status(
    payload: UpdatePaymentStatus = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "api_keys": "a16c5315491847238065347a3de3049b,bf9790f6593e4070a31d313d860c246c",
                    "payment_status": True,
                    "expiry_date": "2024-01-31",
                },
            }
        }
    ),
    api_key: str = "",
    db: Session = Depends(get_db),
):
    api_keys = payload.api_keys.replace(" ", "").split(",")

    if payload.expiry_date:
        if payload.expiry_date < date.today():
            payment_status = False
            expiry_date = payload.expiry_date
        else:
            payment_status = payload.payment_status
            expiry_date = payload.expiry_date

    else:
        payment_status = payload.payment_status
        expiry_date = "2099-12-31"

    updated_farms_count = (
        db.query(Farm)
        .filter(
            or_(
                Farm.id.in_(api_keys),
                Farm.user_id.in_(db.query(User.id).filter(User.apikey.in_(api_keys))),
                Farm.company_id.in_(
                    db.query(Company.id).filter(Company.apikey.in_(api_keys))
                ),
            )
        )
        .update(
            {"is_paid": payment_status, "expiry_date": expiry_date},
            synchronize_session=False,
        )
    )

    db.commit()

    if setting.ENVIRONMENT != "dev":
        dispatch(
            Events.FARM_PAYMENT_UPDATED.value,
            {"api_keys": api_keys, "payment_status": payload.payment_status},
        )

    response = {"updated_farms_count": updated_farms_count}

    return response


@route.post("/payment/cash")
@has_permission([ADMIN])
def update_payment_status(
    api_key: str,
    payload: AddCashPayment = Body(
        examples={
            "normal": {
                "summary": "Accept cash payment",
                "description": "",
                "value": {
                    "user_id": 10010101010,
                    "farm_ids": ["farm_id_1", "farm_id_2"],
                    "status": "Paid",
                    "service": "Cash",
                    "payment_request": {
                        "amount": "100",
                        "recived_by": {
                            "name": "Name",
                            "contact": "contact",
                        },
                        "transaction_id": "str",
                        "description": "description",
                    },
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    # check the user_id
    user = db.query(User).filter(User.id == payload.user_id).one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with the given id doest not exist",
        )

    farm_query = (
        db.query(Farm)
        .filter(Farm.id.in_(payload.farm_ids))
        .filter(Farm.user_id == payload.user_id)
    )

    farms = farm_query.all()

    if not farms or len(farms) < len(payload.farm_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm ids are not valid",
        )

    new_payment = Payment(**payload.dict())

    db.add(new_payment)
    farm_query.update({Farm.is_paid: True, Farm.expiry_date: "2099-12-31"})
    db.commit()

    return "Payment added and farm updated"


@route.get("/users-count")
@has_permission([ADMIN])
def users_count(api_key: str = "", days: int = 90, db: Session = Depends(get_db)):
    today = datetime.today()
    target_date = today + timedelta(days=-days)

    response = db.query(User).filter(User.created_at >= target_date).count()

    return response


@route.get("/paid-farms", response_model=Page[AdminPaidFarmsResponse])
@has_permission([ADMIN])
def paid_farms(api_key: str = "", db: Session = Depends(get_db)):
    response = paginate(
        db,
        select(
            Farm.id.label("farm_id"),
            User.ph.label("phone"),
            User.email,
            User.apikey,
            User.name,
        )
        .join(User, User.id == Farm.user_id)
        .where(Farm.is_paid == True),
    )

    return response


@route.get("/expert-requests", response_model=Page[AdminExpertRequestsResponse])
@has_permission([ADMIN])
def expert_requests(api_key: str = "", db: Session = Depends(get_db)):
    response = paginate(
        db,
        select(
            ScheduleCall.date_time,
            ScheduleCall.message,
            ScheduleCall.type_of_expert,
            ScheduleCall.how_to_contact,
            ScheduleCall.topic,
        ),
    )

    return response


@route.get("/deactivate-user")
@has_permission([ADMIN])
def deactivate_user(api_key: str = "", user_id: int = 0, db: Session = Depends(get_db)):
    """
    Deactivate user function

    :param api_key: admin's api key
    :param user_id: user's id
    :param db: database
    :return : "success"
    """
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .update({"is_active": False}, synchronize_session=False)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesn't exist!",
        )

    db.commit()

    return "success"


@route.get("/activate-user")
@has_permission([ADMIN])
def activate_user(api_key: str = "", user_id: int = 0, db: Session = Depends(get_db)):
    """
    Activate user function

    :param api_key: admin's api key
    :param user_id: user's id
    :param db: database
    :return : "success"
    """
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .update({"is_active": True}, synchronize_session=False)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesn't exist!",
        )

    db.commit()

    return "success"


@route.put("/activate-reseller")
@has_permission([ADMIN])
def activate_reseller(
    api_key: str = "",
    payload: ResellerStatusModifyInput = Body(
        examples={
            "normal": {
                "summary": "Input detailing out which Reseller to update",
                "description": "",
                "value": {"id": 10, "active_status": True},
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Used By admin to activate a particular reseller in the system

    :param api_key: API Key of the Admin which is used to authenticate
    :param payload: Input detailing out which Reseller to update
    """
    reseller = db.query(Resellers).filter(Resellers.id == payload.id).first()
    if not reseller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseller doesn't existed",
        )

    reseller.is_active = payload.active_status
    if not reseller.ref_code:
        reseller.ref_code = uuid.uuid4()

    reseller.activated_at = datetime.now()

    db.commit()
    db.refresh(reseller)

    return {
        "id": reseller.id,
        "brand_name": reseller.brand_name,
        "email": reseller.email,
        "name": reseller.name,
        "address": reseller.address,
        "phone_number": reseller.phone_number,
        "gst_number": reseller.gst_number,
        "ref_code": reseller.ref_code,
        "revenue": reseller.revenue,
        "is_active": reseller.is_active,
        "apikey": reseller.apikey,
    }


@route.put("/deactivate-reseller")
@has_permission([ADMIN])
def deactivate_reseller(
    api_key: str = "",
    payload: ResellerStatusModifyInput = Body(
        examples={
            "normal": {
                "summary": "Input detailing out which Reseller to update",
                "description": "",
                "value": {"id": 10, "active_status": True},
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Used By admin to deactivate a particular reseller in the system

    :param api_key: API Key of the Admin which is used to authenticate
    :param payload: Input detailing out which Reseller to update
    """
    reseller = db.query(Resellers).filter(Resellers.id == payload.id).first()
    if not reseller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseller doesn't existed",
        )

    reseller.is_active = payload.active_status

    db.commit()
    db.refresh(reseller)

    return {
        "id": reseller.id,
        "brand_name": reseller.brand_name,
        "email": reseller.email,
        "name": reseller.name,
        "address": reseller.address,
        "phone_number": reseller.phone_number,
        "gst_number": reseller.gst_number,
        "ref_code": reseller.ref_code,
        "revenue": reseller.revenue,
        "is_active": reseller.is_active,
        "apikey": reseller.apikey,
    }


@route.get("/resellers")
@has_permission([ADMIN])
def activate_reseller(
    api_key: str = "",
    db: Session = Depends(get_db),
):
    """
    Used by Admin to get a List of Resellers in the system

    :param api_key: API Key of the Admin which is used to authenticate
    """
    reseller = db.query(
        Resellers.id,
        Resellers.brand_name,
        Resellers.email,
        Resellers.name,
        Resellers.address,
        Resellers.phone_number,
        Resellers.gst_number,
        Resellers.ref_code,
        Resellers.revenue,
        Resellers.is_active,
        Resellers.apikey,
    ).all()

    return reseller


@route.get("/planetscope_subscription")
@has_permission([ADMIN])
def update_planetscope(
    api_key: str,
    farm_id: str,
    db: Session = Depends(get_db),
):
    temp = (
        db.query(PlanetCollection).filter(PlanetCollection.farm_id == farm_id).first()
    )

    if not temp:
        my_farm = (
            db.query(func.ST_AsGeoJSON(Farm).label("geom"))
            .filter(Farm.id == farm_id)
            .one()
        )

        feature = json.loads(my_farm["geom"])

        # create planet collection

        api_token_url = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload_data = (
            "grant_type=client_credentials&client_id="
            + SENTINEL_HUB_CLIENT_ID
            + "&client_secret="
            + SENTINEL_HUB_CLIENT_SECRET
        )
        token_response = requests.post(
            api_token_url, headers=headers, data=payload_data
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=token_response.status_code, detail=token_response.json()
            )

        data = token_response.json()

        access_token = "Bearer " + data["access_token"]

        api_subscription_url = (
            "https://services.sentinel-hub.com/api/v1/dataimport/subscriptions"
        )
        headers = {"Content-Type": "application/json", "Authorization": access_token}

        json_data = {
            "name": feature["properties"]["name"],
            "input": {
                "provider": "PLANET",
                "planetApiKey": PLANET_API_KEY,
                "bounds": {"geometry": feature["geometry"]},
                "data": [
                    {
                        "itemType": "PSScene",
                        "harmonizeTo": "NONE",
                        "productBundle": "analytic_8b_sr_udm2",
                        "dataFilter": {
                            "timeRange": {"from": "2017-01-01T00:00:00.000Z"}
                        },
                    }
                ],
            },
        }

        subscription_response = requests.post(
            api_subscription_url, headers=headers, json=json_data
        )
        if subscription_response.status_code != 200:
            raise HTTPException(
                status_code=subscription_response.status_code,
                detail=subscription_response.json(),
            )

        subscription_data = subscription_response.json()

        api_subscription_confirm_url = (
            "https://services.sentinel-hub.com/api/v1/dataimport/subscriptions/"
            + subscription_data["id"]
            + "/confirm"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": access_token,
        }

        subscription_confirm_response = requests.post(
            api_subscription_confirm_url, headers=headers
        )

        if subscription_confirm_response.status_code != 200:
            raise HTTPException(
                status_code=subscription_confirm_response.status_code,
                detail=subscription_confirm_response.json(),
            )

        api_subscription_detail_url = (
            "https://services.sentinel-hub.com/api/v1/dataimport/subscriptions/"
            + subscription_data["id"]
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": access_token,
        }

        subscription_detail_response = requests.get(
            api_subscription_detail_url, headers=headers
        )

        if subscription_detail_response.status_code != 200:
            raise HTTPException(
                status_code=subscription_detail_response.status_code,
                detail=subscription_detail_response.json(),
            )

        detaildata = subscription_detail_response.json()

        planet_data = {
            "farm_id": feature["properties"]["id"],
            "collection_id": detaildata["collectionId"],
            "service_id": subscription_data["id"],
        }
        planet_collection = PlanetCollection(**planet_data)

        db.add(planet_collection)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription already exists for this",
        )

    return "Subscription created successfully!"


@route.post("/search/company")
@has_permission([ADMIN])
def search_company(
    api_key: str = "",
    payload: RequestUserInfo = Body(
        example={
            "get_by_email": {"type": "email", "email": "test@test.com"},
            "get_by_phone": {"type": "phone", "phone": "9112345678"},
        }
    ),
    db: Session = Depends(get_db),
):
    if payload.type == "email" and payload.email:
        company = (
            db.query(Company)
            .filter(func.lower(Company.email) == payload.email.lower())
            .first()
        )
        if company:
            return company
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Match found",
            )

    if payload.type == "phone" and payload.phone:
        company = db.query(Company).filter(Company.ph == payload.phone).first()
        if company:
            return company
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Match found",
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No Match found",
    )


@route.post("/search/user")
@has_permission([ADMIN])
def search_user(
    api_key: str = "",
    payload: RequestUserInfo = Body(
        example={
            "get_by_email": {"type": "email", "email": "test@test.com"},
            "get_by_phone": {"type": "phone", "phone": "9112345678"},
        }
    ),
    db: Session = Depends(get_db),
):
    if payload.type == "email" and payload.email:
        user = (
            db.query(User)
            .filter(func.lower(User.email) == payload.email.lower())
            .first()
        )
        if user:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Match found",
            )

    if payload.type == "phone" and payload.phone:
        user = db.query(User).filter(User.ph == payload.phone).first()
        if user:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Match found",
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No Match found",
    )


@route.post("/cache/clear")
@has_permission([ADMIN])
def cache_cler(api_key: str = "", db: Session = Depends(get_db)):
    try:
        # Get the redis cache
        cache = get_redis()
        cache.flushall()
        # Send the response
        return {"status": "Cache cleared"}
    except Exception as e:
        print("Cache not connceted", e)
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Not connected. Check logs",
        )
