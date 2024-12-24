from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from sqlalchemy.orm import Session
from re import compile
from uuid import uuid4
import zoneinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from db import get_db
from models import User, Resellers, UserReferral, DisplayPhoto
from schemas import (
    UserProfile,
    SendOTPForUpdateProfilePayload,
    UpdateProfilePasswordPayload,
    UpdateProfilePayload,
    UpdateProfileEmailPayload,
    UpdateProfilePhonePayload,
    ReferralInput,
)
from utils.outh2 import create_access_token
from utils.api import (
    has_permission,
    check_phone_otp,
    check_email_otp,
    get_user,
    save_file_to_bucket,
    get_file_public_url,
)
from utils.password import verify_pwd, secure_pwd
from constant import FARMER
from config import setting

route = APIRouter(prefix="/profile", tags=["Profile"])


def validate_timezone(time_zone: str):
    try:

        timezone = zoneinfo.ZoneInfo(time_zone)
        return timezone
    except ZoneInfoNotFoundError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timezone"
        )


@route.get("/", response_model=UserProfile)
@has_permission([])
def show(api_key: str = "", s_user=Depends(lambda: None)):
    """
    Get user's profile from api key

    :param api_key: user's api key
    :param db: database session
    :return: user's profile
    """
    if s_user.role == 2:
        token = create_access_token({"user_id": s_user.id, "company_id": s_user.id})

        return UserProfile(
            token=token,
            id=s_user.id,
            name=s_user.name,
            api_key=s_user.apikey,
            email=s_user.email,
            role=s_user.role,
            is_active=s_user.is_active,
            country=s_user.country,
            city=s_user.city,
            state=s_user.state,
            postcode=s_user.postcode,
            unit=s_user.unit,
        )
    else:
        token = create_access_token(
            {"user_id": s_user.id, "company_id": s_user.company_id}
        )

        return UserProfile(
            token=token,
            id=s_user.id,
            name=s_user.name,
            api_key=s_user.apikey,
            phone=s_user.ph,
            email=s_user.email,
            role=s_user.role,
            is_active=s_user.is_active,
            country=s_user.country,
            city=s_user.city,
            state=s_user.state,
            postcode=s_user.postcode,
            unit=s_user.unit,
            timezone=s_user.timezone,
            notification_active=s_user.is_notification_enabled,
        )


@route.post("/send-otp", deprecated=True)
def send_otp_for_update(
    api_key: str = "",
    payload: SendOTPForUpdateProfilePayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "User can update the email or phone. There will be OTP verification.",
                "value": {
                    "email": "user@mapmycrop.com",
                    "phone": "9123456789256",
                    "api_key": True,
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    return


@route.put("/update")
def update(
    api_key: str = "",
    payload: UpdateProfilePayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "User can update the name, country, city, state.",
                "value": {
                    "name": "Mahendra",
                    "country": "India",
                    "city": "Pune",
                    "state": "Pune",
                    "postcode": "12345",
                    "timezone": "Asia/Kolkata",
                    "unit": "metric",
                    "is_notification_enabled": "true",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    user = get_user(db, api_key)

    if (
        not payload.name
        and not payload.country
        and not payload.city
        and not payload.state
        and not payload.is_notification_enabled
        and not payload.timezone
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Input update value here"
        )

    if payload.name:
        user.name = payload.name

    if payload.country:
        user.country = payload.country

    if payload.city:
        user.city = payload.city

    if payload.state:
        user.state = payload.state

    if payload.postcode:
        user.postcode = payload.postcode

    if payload.unit:
        user.unit = payload.unit

    if payload.timezone:
        validate_timezone(payload.timezone)
        user.timezone = payload.timezone

    if payload.is_notification_enabled:
        user.is_notification_enabled = payload.is_notification_enabled

    db.commit()
    return True


@route.put("/email")
def update_email(
    api_key: str = "",
    otp_code: str = "",
    payload: UpdateProfileEmailPayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "User can update the email. There will be OTP verification.",
                "value": {"email": "user@mapmycrop.com"},
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Verify OTP and update email in profile.

    :param api_key: user's api key
    :param otp_code: user's otp code
    :param payload: request's payload including email
    :param db: database session
    :return: True if it's successful
    """
    user = get_user(db, api_key)

    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email should be here."
        )

    if payload.email:
        customer = (
            db.query(User)
            .filter(User.email == payload.email, User.id != user.id)
            .first()
        )
        if customer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email already exists.",
            )

        if check_email_otp(payload.email, otp_code):
            user.email = payload.email
            db.commit()

            return True


@route.put("/phone")
def update_phone(
    api_key: str = "",
    otp_code: str = "",
    payload: UpdateProfilePhonePayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "User can update the phone. There will be OTP verification.",
                "value": {"phone": "9123456789256"},
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Verify OTP and update phone in profile.

    :param api_key: user's api key
    :param otp_code: user's otp code
    :param payload: request's payload including phone
    :param db: database session
    :return: True if it's successful
    """

    user = get_user(db, api_key)

    if not payload.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Phone should be here."
        )

    if user.role == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number cannot be updated for Enterprise User",
        )

    if payload.phone:
        customer = (
            db.query(User).filter(User.ph == payload.phone, User.id != user.id).first()
        )
        if customer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone number already exists.",
            )

        if check_phone_otp(payload.phone, otp_code):
            user.ph = payload.phone
            db.commit()

            return True


@route.put("/password")
def update_password(
    api_key: str = "",
    payload: UpdateProfilePasswordPayload = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "User can change the password.",
                "value": {
                    "old_password": "v3S-2>T?;1L/",
                    "new_password": "fe482=Ka0&Sl",
                    "confirm_new_password": "fe482=Ka0&Sl",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Change the password.

    :param api_key: user's api key
    :param payload: request's payload including old, new, and confirmation password
    :param db: database session
    :return: True if it's successful
    """

    user = get_user(db, api_key)

    if not (verify_pwd(payload.old_password, user.password)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Old password is incorrect",
        )

    pattern = compile(r"[^\s]{8,24}$")
    if not pattern.match(payload.new_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password should between 8 and 24 characters and contain no space",
        )

    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password and confirm password does not match",
        )

    user.password = secure_pwd(payload.new_password)
    db.commit()

    return True


@route.post("/set-referral")
@has_permission([FARMER])
def set_referral(
    api_key: str = "",
    payload: ReferralInput = Body(
        examples={
            "normal": {
                "summary": "Details of user and reseller",
                "description": "",
                "value": {
                    "apikey": "1233-qwe1-qwsadsd",
                    "ref_code": "4564-asd3-xcvxcgv",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    """
    Called on behalf of user to set the referral for the user

    :param api_key: API Key of the User which is used to authenticate
    :param payload: Details of user and reseller
    """

    reseller = (
        db.query(Resellers).filter(Resellers.ref_code == payload.ref_code).first()
    )
    user = db.query(User).filter(User.apikey == payload.apikey).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    if not reseller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseller does not exist",
        )

    if not reseller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reseller is marked as inactive",
        )

    referral = db.query(UserReferral).filter(UserReferral.user_id == user.id).first()

    if not referral:
        user_referral = UserReferral(user_id=user.id, ref_code=reseller.ref_code)

        db.add(user_referral)
    else:
        referral.ref_code = payload.ref_code

    db.commit()

    return "success"


@route.get("/display_photo")
@has_permission([])
def get_profile_photo(
    api_key: str = "", db=Depends(get_db), s_user=Depends(lambda: None)
):
    """
    Get the user's display photo if it exists.
    """
    try:
        # Search for the active display photo in the database
        active_photo = (
            db.query(DisplayPhoto)
            .filter(DisplayPhoto.user_id == s_user.id, DisplayPhoto.is_active == True)
            .first()
        )
        if active_photo:
            path = get_file_public_url(
                bucket_name=setting.DISPLAY_PHOTO_BUCKET_NAME,
                file_path=active_photo.path,
            )
            return path
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active display photo found.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@route.post("/display_photo")
@has_permission([])
def upload_profile_photo(
    api_key: str = "",
    file: UploadFile = File(...),
    db=Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Upload a new display photo for the user.
    """
    try:
        # Check if there's an existing active display photo
        active_photo = (
            db.query(DisplayPhoto)
            .filter(DisplayPhoto.user_id == s_user.id, DisplayPhoto.is_active == True)
            .first()
        )
        if active_photo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active display photo already exists.",
            )

        # Upload the new photo to S3 and save the path in the database
        file_name = f"{str(uuid4())}.{file.filename.split('.')[-1]}"

        save_file_to_bucket(
            setting.DISPLAY_PHOTO_BUCKET_NAME,
            "profile_photos",
            file_name,
            file.file.read(),
        )
        payload = {
            "user_id": s_user.id,
            "path": f"profile_photos/{file_name}",
            "is_active": True,
        }

        photo = DisplayPhoto(**payload)
        db.add(photo)
        db.commit()

        return {"message": "Display photo uploaded successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@route.post("/display_photo/update")
@has_permission([])
def update_profile_photo(
    api_key: str = "",
    file: UploadFile = File(...),
    db=Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Update the user's display photo.
    """
    try:
        # Check if there's an existing active display photo
        active_photo = (
            db.query(DisplayPhoto)
            .filter(DisplayPhoto.user_id == s_user.id, DisplayPhoto.is_active == True)
            .first()
        )
        if not active_photo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No active display photo found.",
            )

        # Upload the new photo to S3 and save the path in the database
        file_name = f"{str(uuid4())}.{file.filename.split('.')[-1]}"
        save_file_to_bucket(
            setting.DISPLAY_PHOTO_BUCKET_NAME,
            "profile_photos",
            file_name,
            file.file.read(),
        )

        new_photo = DisplayPhoto(
            user_id=s_user.id, path=f"profile_photos/{file_name}", is_active=True
        )
        db.add(new_photo)

        return {"message": "Display photo updated successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@route.delete("/display_photo")
@has_permission([])
def delete_profile_photo(
    api_key: str = "", db=Depends(get_db), s_user=Depends(lambda: None)
):
    """
    Delete the user's display photo.
    """
    try:
        # Check if there's an existing active display photo
        active_photo = (
            db.query(DisplayPhoto)
            .filter(DisplayPhoto.user_id == s_user.id, DisplayPhoto.is_active == True)
            .first()
        )
        if not active_photo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No active display photo found.",
            )

        # Mark the active photo as inactive
        active_photo.is_active = False
        db.commit()
        return {"message": "Display photo deleted successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
