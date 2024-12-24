from fastapi import status, HTTPException, Request, Depends
from sqlalchemy import String, text
from sqlalchemy.orm import Session
from geoalchemy2 import func
from datetime import datetime
from typing import List, Literal
from twilio.rest import Client
import json
import math
import random
from functools import wraps
import boto3
from botocore.exceptions import ClientError

from db import get_db
from db import SessionLocal
from models import User, Company, Farm, Crop, Indice, Role, Satellite
from utils.notification import send_email
from config import setting
from cache import get_redis
from constant import COMPANY


def get_user(db: Session, api: str, roles: list = [], is_active: bool = True):
    if not len(roles):
        roles = [role.id for role in db.query(Role).all()]

    user = db.query(User).filter(User.apikey == api, User.role.in_(roles)).first()

    company = (
        db.query(Company).filter(Company.apikey == api, Company.role.in_(roles)).first()
    )

    if not user and not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with given key and role does not exist",
        )

    user = user or company

    if not COMPANY in roles and user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="This User is marked for Deletion.",
        )

    if not user.is_active and is_active:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Your account is not active. Please contact administrator",
        )

    return user


def get_company(db: Session, api_key: str):
    user = db.query(Company).filter(Company.apikey == api_key).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company with given key does not exist",
        )

    return user


def get_farm(db: Session, api_key: str, farm_id: str):
    user = get_user(db, api_key)

    farm = None

    if user.role == 1:
        farm = (
            db.query(func.ST_AsGeoJSON(Farm).label("geom"))
            .filter(Farm.user_id == user.id, Farm.id == farm_id)
            .first()
        )

    if user.role == 2:
        farm = (
            db.query(func.ST_AsGeoJSON(Farm).label("geom"))
            .filter(Farm.company_id == user.id, Farm.id == farm_id)
            .first()
        )

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm with given id not found for the API key",
        )

    return farm


def get_all_farms(db: Session, role: int, id: int):
    farms = None

    if role == 1:
        farms = (
            db.query((func.ST_AsGeoJSON(Farm)).label("geom"))
            .filter(Farm.user_id == id)
            .all()
        )

    if role == 2:
        farms = db.query(func.ST_AsGeoJSON(Farm).label("geom")).filter(
            Farm.company_id == id
        )

    if not farms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm with given id not found for the API key",
        )

    return farms


def get_crop(db: Session, crop_name: str):
    crop = db.query(Crop).filter(Crop.name == crop_name).first()

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Crop with the given name does not exist",
        )

    return crop


def check_farm_bounds(db: Session, bounds: List[int]):
    check_farm = (
        db.query(Farm).filter(Farm.bbox.cast(String) == json.dumps(bounds)).first()
    )

    if check_farm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farm with the given bounds already exists",
        )

    return None


def check_crop_params(sowing_date, harvesting_date, season):

    if harvesting_date and harvesting_date <= sowing_date:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Harvesting date cannot be earlier to the sowing date",
        )

    if season < 2015 or season > (datetime.today().year + 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Season should be between 2015 and {datetime.today().year}",
        )

    return None


def check_indice(
    db: Session, name: str, satellite: str, type: Literal["imagery", "statistics"]
):
    columns = {"imagery": "evalscript", "statistics": "statistical_evalscript"}

    selected_indice = (
        db.query(Indice, Satellite)
        .filter(Indice.alias == name)
        .filter(getattr(Indice, columns[type]).isnot(None))
        .filter(Satellite.satellite == satellite)
        .filter(Satellite.name == Indice.satellite)
        .first()
    )

    if not selected_indice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Index not found for given satellite",
        )

    return selected_indice


def send_otp_to_phone(phone):
    """
    Sending OTP code to specific phone.

    :param phone: phone for OTP
    :return: True if it's successful, raise Exception if it's failed
    """

    twilio_client = Client(setting.TWILIO_SID, setting.TWILIO_AUTH_TOKEN)

    try:
        twilio_client.verify.v2.services(
            setting.TWILIO_SERVICE_SID
        ).verifications.create(f"+{phone}", "sms")

        return True
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This phone number is not valid",
        )


def send_otp_to_email(email):
    """
    Sending OTP code to specific email.

    :param email: email for OTP
    :return: True if it's successful, raise Exception if it's failed
    """

    otp_code = generate_otp()

    cache = get_redis()
    cache.set(f"{email}_otp", otp_code, 10 * 60)

    sender = {"name": "Map My Crop", "email": "alerts@mapmycrop.com"}
    to = {"email": email, "name": "Customer"}
    subject = "Map My Crop OTP"
    html_content = f"<html><body><h3>Your Map My Crop OTP verification code is {otp_code}</h3></body></html>"

    send_email(sender=sender, to=to, subject=subject, html_content=html_content)

    return True


def send_otp_to_api_key(email):
    """
    Sending OTP code to specific email.

    :param email: email for OTP
    :return: True if it's successful, raise Exception if it's failed
    """

    otp_code = generate_otp()

    cache = get_redis()
    cache.set(f"{email}_otp", otp_code, 10 * 60)

    sender = {"name": "Map My Crop", "email": "alerts@mapmycrop.com"}
    to = {"email": email, "name": "Customer"}
    subject = "Map My Crop OTP"
    html_content = f"<html><body><h3>Your Map My Crop OTP verification code is {otp_code}</h3></body></html>"

    send_email(sender=sender, to=to, subject=subject, html_content=html_content)

    return True


def check_phone_otp(phone, code):
    """
    Check phone verification with OTP code

    :param phone: phone number for OTP verification
    :param code: OTP code
    :return: True if it's successful, raise Exception if not
    """

    twilio_client = Client(setting.TWILIO_SID, setting.TWILIO_AUTH_TOKEN)

    try:
        verification_check = twilio_client.verify.v2.services(
            setting.TWILIO_SERVICE_SID
        ).verification_checks.create(code=code, to=f"+{phone}")

        if verification_check.status == "approved":
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="OTP is not valid"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This phone number or code is not valid",
        )


def check_email_otp(email, code):
    """
    Check email verification with OTP code

    :param email: email number for OTP verification
    :param code: OTP code
    :return: True if it's successful, raise Exception if not
    """

    cache = get_redis()

    if code == cache.get(f"{email}_otp"):
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="OTP is not valid"
        )


def check_api_key_otp(api_key, code):
    """
    Check email verification with OTP code

    :param email: email number for OTP verification
    :param code: OTP code
    :return: True if it's successful, raise Exception if not
    """

    cache = get_redis()

    if code == cache.get(f"{api_key}_otp"):
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="OTP is not valid"
        )


def generate_otp():
    """
    Generate OTP code for email verification

    :return: OTP code
    """

    digits = "0123456789"
    otp = ""

    for i in range(6):
        otp += digits[math.floor(random.random() * 10)]

    return otp


def get_middleware_user(request: Request):
    return request.state.user


def check_user_role(db: Session, user, roleList=[]):
    if not len(roleList):
        roleList = [role.id for role in db.query(Role).all()]
    print(roleList)
    if not user.role in roleList:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role does not exist",
        )


def has_permission(permission: List[int] = []):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = kwargs.get("api_key")
            db = SessionLocal()
            user = get_user(db, api_key, permission)

            if "s_user" in kwargs:
                kwargs["s_user"] = user
            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_and_update_paid_status():
    current_date = datetime.now()

    farms = Farm.query.all()
    db = SessionLocal()
    for farm in farms:
        if farm.expiry_date < current_date:
            farm.paid_status = False
            db.session.commit()


def save_file_to_bucket(bucket_name, file_path, file_name, file_content):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=setting.AWS_ACCESS_KEY,
        aws_secret_access_key=setting.AWS_SECRET_KEY,
    )

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"{file_path}/{file_name}",
            Body=file_content,
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            raise Exception(f"Bucket '{bucket_name}' does not exist.")
        else:
            raise Exception(f"Error uploading file to S3 bucket: {e}")


def get_file_public_url(bucket_name, file_path):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=setting.AWS_ACCESS_KEY,
        aws_secret_access_key=setting.AWS_SECRET_KEY,
    )

    try:
        # Generate the presigned URL
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": file_path},
            ExpiresIn=3600,  # The URL will be valid for 1 hour (3600 seconds)
        )
        return url
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            raise Exception(
                f"Bucket '{bucket_name}' or file '{file_path}' does not exist."
            )
        else:
            raise Exception(f"Error generating public URL for the file: {e}")
