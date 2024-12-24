from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.sql import func

from db import get_db
from schemas import (
    ResellerLoginPayload,
    ResellerInput,
    ResellerResetPassword,
    ResellerUserInput,
    ResellerResponseModel,
    ResellerSummaryInfoModel,
    ResponseMessageModel,
)
from utils.password import verify_pwd, secure_pwd
from utils.api import check_phone_otp
from utils.auth import get_user_by_ph
from utils.notification import send_whatsapp
from models import Resellers, InvitedUsers, UserReferral, User, Farm
from datetime import datetime, timedelta

route = APIRouter(prefix="/reseller", tags=["Reseller"])


@route.post("/login", response_model=ResellerResponseModel)
def login(
    payload: ResellerLoginPayload = Body(
        examples={
            "normal": {
                "summary": "Used by a Reseller to Login",
                "description": "Login details of the Reseller",
                "value": {"phone_number": "919988776655", "password": "string"},
            }
        }
    ),
    db: Session = Depends(get_db),
):
    reseller = (
        db.query(Resellers)
        .filter(Resellers.phone_number == payload.phone_number)
        .first()
    )

    if not reseller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phone number is incorrect",
        )

    if not reseller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reseller needs to be activated",
        )

    if not (verify_pwd(payload.password, reseller.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect"
        )

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
        "created_at": reseller.created_at,
    }


@route.post("/register")
def register(
    payload: ResellerInput = Body(
        examples={
            "normal": {
                "summary": "Used by a new Reseller to create an Account",
                "description": "Login details of the Reseller",
                "value": {
                    "brand_name": "ABC Agro Enterprises",
                    "email": "info@example.com",
                    "name": "Ashok Kumar",
                    "address": " 123, Netaji Road, Pune-411037",
                    "phone_number": "919900776655",
                    "gst_number": "27AABCB1599F4ZP",
                    "password": "xxxxxxx",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    temp = (
        db.query(Resellers)
        .filter(
            or_(
                Resellers.email == payload.email,
                Resellers.phone_number == payload.phone_number,
            )
        )
        .first()
    )

    if temp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email or phone number alrady existed",
        )

    reseller = Resellers(
        brand_name=payload.brand_name,
        email=payload.email,
        name=payload.name,
        address=payload.address,
        phone_number=payload.phone_number,
        password=secure_pwd(payload.password),
        gst_number=payload.gst_number,
        ref_code=None,
        revenue=None,
        is_active=False,
        activated_at=None,
    )

    db.add(reseller)
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


@route.post("/password-reset")
def password_reset(
    payload: ResellerResetPassword = Body(
        examples={
            "normal": {
                "summary": "Used by a new Reseller to create an Account",
                "description": "Login details of the Reseller",
                "value": {
                    "phone": "91123456778",
                    "otp": "543678",
                    "password": "xxxxxxx",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    reseller = (
        db.query(Resellers).filter(Resellers.phone_number == payload.phone).first()
    )

    if not reseller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseller does not exist",
        )

    if not reseller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reseller needs to be activated",
        )

    check_phone_otp(payload.phone, payload.otp)

    reseller.password = secure_pwd(payload.password)
    db.commit()
    db.refresh(reseller)

    return "Password has been Reset"


@route.post(
    "/add-user",
    responses={
        201: {"model": ResponseMessageModel, "description": "User has been connected"},
        202: {
            "model": ResponseMessageModel,
            "description": "User does not exist and has been invited",
        },
        403: {
            "model": ResponseMessageModel,
            "description": "Reseller needs to be activated",
        },
        404: {"model": ResponseMessageModel, "description": "Reseller does not exist"},
        409: {
            "model": ResponseMessageModel,
            "description": "User is already connected to another reseller",
        },
        412: {
            "model": ResponseMessageModel,
            "description": "User has already been invited by you",
        },
    },
    status_code=201,
)
def add_user(
    apikey: str = "",
    payload: ResellerUserInput = Body(
        examples={
            "normal": {
                "summary": "Allow a Reseller to add a User",
                "description": "Details of the User that has to be connected with the Reseller",
                "value": {
                    "name": "Ashok Kumar",
                    "mobile_number": "919988776655",
                    "paid_status": True,
                    "farm_size": 378.90,
                    "crop_type": "flower",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    reseller = db.query(Resellers).filter(Resellers.apikey == apikey).first()

    if not reseller:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "Failure", "message": "Reseller does not exist"},
        )

    if not reseller.is_active:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": "Failure", "message": "Reseller needs to be activated"},
        )

    invited_user = (
        db.query(InvitedUsers)
        .filter(InvitedUsers.mobile_number == payload.mobile_number)
        .first()
    )

    if not invited_user:
        user = get_user_by_ph(db, payload.mobile_number)
        if not user:
            new_invited_user = InvitedUsers(
                ref_code=reseller.ref_code,
                name=payload.name,
                mobile_number=payload.mobile_number,
                paid_status=payload.paid_status,
                farm_size=payload.farm_size,
                crop_type=payload.crop_type,
            )

            db.add(new_invited_user)
            db.commit()
            db.refresh(new_invited_user)

            send_whatsapp(
                body="You have been invited by "
                + reseller.name
                + " to use the Map My Crop Application. You can download it from here: https://play.google.com/store/apps/details?id=com.mapmycrop.mmc",
                contact=payload.mobile_number,
                name="Map My Crop",
                title="Invite message",
            )

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "status": "Success",
                    "message": "User does not exist and has been invited",
                },
            )

        else:
            new_invited_user = InvitedUsers(
                ref_code=reseller.ref_code,
                name=payload.name,
                mobile_number=payload.mobile_number,
                paid_status=payload.paid_status,
                farm_size=payload.farm_size,
                crop_type=payload.crop_type,
            )

            new_user_referral = UserReferral(
                user_id=user.id, ref_code=reseller.ref_code
            )

            db.add(new_invited_user)
            db.add(new_user_referral)
            db.commit()
            db.refresh(new_invited_user)
            db.refresh(new_user_referral)

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "status": "Success",
                    "message": "User has been connected to the Reseller",
                },
            )

    else:
        if invited_user.ref_code == reseller.ref_code:
            return JSONResponse(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                content={
                    "status": "Failure",
                    "message": "User has already been invited by you",
                },
            )

        else:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "status": "Failure",
                    "message": "User is already connected to another reseller",
                },
            )


@route.get(
    "/summaryInfo",
    responses={
        200: {"model": ResellerSummaryInfoModel, "description": "Successful operation"},
        403: {
            "model": ResponseMessageModel,
            "description": "Reseller is marked as inactive",
        },
        404: {"model": ResponseMessageModel, "description": "Reseller does not exist"},
    },
)
def summaryInfo(
    apikey: str = "",
    db: Session = Depends(get_db),
):
    reseller = db.query(Resellers).filter(Resellers.apikey == apikey).first()

    if not reseller:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "Failure", "message": "Reseller does not exist"},
        )

    if not reseller.is_active:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": "Failure", "message": "Reseller needs to be activated"},
        )

    today = datetime.now()
    onboarded_today_count = (
        db.query(User)
        .join(UserReferral)
        .join(Resellers)
        .outerjoin(Farm)
        .filter(
            UserReferral.registered_at >= today - timedelta(days=1),
            Resellers.apikey == apikey,
            Farm.user_id != None,
        )
        .count()
    )

    target_month = today.month
    target_year = today.year

    onboarded_month_count = (
        db.query(User)
        .join(UserReferral)
        .join(Resellers)
        .outerjoin(Farm)
        .filter(
            func.extract("month", UserReferral.registered_at) == target_month,
            func.extract("year", UserReferral.registered_at) == target_year,
            Resellers.apikey == apikey,
            Farm.user_id != None,
        )
        .count()
    )

    farm_size = (
        db.query(func.sum(Farm.area))
        .join(User)
        .join(UserReferral)
        .join(Resellers)
        .filter(Resellers.apikey == apikey)
    ).scalar()

    if not farm_size:
        total_farm_size = 0
    else:
        total_farm_size = farm_size

    if not reseller.revenue:
        total_profit = 0
    else:
        total_profit = reseller.revenue

    summary_info = {
        "onboarded_today": onboarded_today_count,
        "onboarded_month": onboarded_month_count,
        "total_farm_size": total_farm_size,
        "total_profit": total_profit,
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=summary_info)
