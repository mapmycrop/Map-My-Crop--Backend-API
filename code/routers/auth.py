from re import compile
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, Literal
import re
from db import get_db
from schemas import (
    UserSchema,
    UuidOfUser,
    UserTokenSchema,
    SendOTPPayload,
    VerifyOTPPayload,
    ResetPasswordSchema,
    ResetPasswordWithOTPPayload,
)
from utils.api import (
    send_otp_to_email,
    send_otp_to_phone,
    check_phone_otp,
    check_email_otp,
    get_user,
)
from utils.auth import get_user_by_ph, create_user, get_user_by_email, get_company_by_id
from utils.notification import send_email
from utils.outh2 import create_access_token
from utils.password import secure_pwd
from utils.password import verify_pwd
from cache import get_redis
from variables import SocialLoginProviderType
from models import User, LoginLogs, InvitedUsers, UserReferral

route = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_password(payload):
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters long"
        )

    if not re.search(r"[a-z]", payload.password):
        raise HTTPException(
            status_code=400, detail="Password must include lowercase letters"
        )

    if not re.search(r"[A-Z]", payload.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter",
        )

    if not re.search(r"\d", payload.password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one numeric digit"
        )

    if not re.search(r"[@#$!%*?&]", payload.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character (e.g., !, @, #, $, %)",
        )


@route.post("/register", response_model=UuidOfUser)
def register(payload: UserSchema, db: Session = Depends(get_db)):
    get_company_by_id(db, payload.company_id)

    if not payload.ph and not payload.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please input phone or email",
        )

    if payload.ph and payload.country_code:
        phone = payload.country_code + payload.ph
        phone_exists = get_user_by_ph(db, phone)

        if phone_exists:
            if hasattr(phone_exists, "is_deleted") and phone_exists.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This User is marked for Deletion.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User with same phone number already exists",
                )

        payload.ph = payload.country_code + payload.ph

    if payload.email:
        email_exists = get_user_by_email(db, payload.email)
        if email_exists:
            if hasattr(email_exists, "is_deleted") and email_exists.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account cannot be created with these credentials. Please use any other email or phone number.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User with same email already exists",
                )

    validate_password(payload)

    user = create_user(db, payload)
    user.source = user.source.value

    invited_user = (
        db.query(InvitedUsers)
        .filter(InvitedUsers.accepted_at == None)
        .filter(InvitedUsers.mobile_number == payload.ph)
        .first()
    )

    if invited_user:
        invited_user.accepted_at = func.now()
        user_referral = UserReferral(user_id=user.id, ref_code=invited_user.ref_code)

        db.add(user_referral)
        db.commit()
        db.refresh(invited_user)
        db.refresh(user_referral)

    return user


@route.post("/login", response_model=UserTokenSchema)
def login(
    source: Optional[Literal["web", "android", "ios", "api"]] = "web",
    payload: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_ph(db, payload.username) or get_user_by_email(
        db, payload.username
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with the phone/email does not exist",
        )

    if hasattr(user, "is_deleted") and user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This User is marked for Deletion.",
        )

    if not (verify_pwd(payload.password, user.password)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password incorrect"
        )

    # save client login history
    if not user.role == 2:
        loginLog = LoginLogs(
            ph=user.ph,
            email=user.email,
            source=source,
            apikey=user.apikey,
            role=user.role,
        )
    else:
        loginLog = LoginLogs(
            ph=None, email=user.email, source=source, apikey=user.apikey, role=user.role
        )

    db.add(loginLog)
    db.commit()

    if user.role == 2:
        company_id = user.id
    else:
        company_id = user.company_id

    token = create_access_token({"user_id": user.id, "company_id": company_id})

    if user.role == 2:
        return UserTokenSchema(
            token=token,
            apikey=user.apikey,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )
    else:
        return UserTokenSchema(
            token=token,
            apikey=user.apikey,
            phone=user.ph,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )


@route.post("/send_otp")
def send_otp(payload: SendOTPPayload, db: Session = Depends(get_db)):
    if payload.type == "phone":
        if not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input phone number",
            )

        return send_otp_to_phone(payload.phone)
    else:
        if not payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input email",
            )

        return send_otp_to_email(payload.email)


@route.post("/verify_otp", response_model=UserTokenSchema, deprecated=True)
def verify_otp(payload: VerifyOTPPayload, db: Session = Depends(get_db)):
    # phone otp
    if payload.type == "phone":
        if not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input phone number",
            )

        # checking if phone exists in database
        user = get_user_by_ph(db, payload.phone)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone number doesn't exist",
            )

        if check_phone_otp(payload.phone, payload.code):
            token = create_access_token(
                {"user_id": user.id, "company_id": user.company_id}
            )

            return UserTokenSchema(
                token=token,
                apikey=user.apikey,
                phone=user.ph,
                email=user.email,
                role=user.role,
            )
    # email otp
    else:
        if not payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input email",
            )

        user = get_user_by_email(db, payload.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email doesn't exist",
            )

        if check_email_otp(payload.email, payload.code):
            token = create_access_token(
                {"user_id": user.id, "company_id": user.company_id}
            )

            return UserTokenSchema(
                token=token,
                apikey=user.apikey,
                phone=user.ph,
                email=user.email,
                role=user.role,
            )


@route.put("/reset_password", deprecated=True)
def reset_password(
    api_key: str, payload: ResetPasswordSchema, db: Session = Depends(get_db)
):
    return


@route.put("/reset_pass_otp", deprecated=True)
def reset_pass_otp(payload: ResetPasswordWithOTPPayload, db: Session = Depends(get_db)):
    return


@route.put("/password-reset")
def reset_pass_otp(payload: ResetPasswordWithOTPPayload, db: Session = Depends(get_db)):

    # phone otp
    if payload.type == "phone":
        if not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input phone number",
            )

        user = get_user_by_ph(db, payload.phone)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone number doesn't exist",
            )

        if check_phone_otp(payload.phone, payload.code):
            validate_password(payload)
            user.password = secure_pwd(payload.password)
            db.commit()

            return True

    # email otp
    else:
        if not payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input email",
            )

        user = get_user_by_email(db, payload.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email doesn't exist",
            )

        if check_email_otp(payload.email, payload.code):
            validate_password(payload)
            user.password = secure_pwd(payload.password)
            db.commit()

            return True


@route.put("/activate")
def activate_user_with_otp(payload: VerifyOTPPayload, db: Session = Depends(get_db)):
    # phone otp
    if payload.type == "phone":
        if not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input phone number",
            )

        # checking if phone exists in database
        user = get_user_by_ph(db, payload.phone)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone number doesn't exist",
            )

        if check_phone_otp(payload.phone, payload.code):
            user.is_active = True
            db.commit()

            return True
    # email otp
    else:
        if not payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input email",
            )

        user = get_user_by_email(db, payload.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email doesn't exist",
            )

        if check_email_otp(payload.email, payload.code):
            user.is_active = True
            db.commit()

            return True


@route.put("/deactivate", deprecated=True)
def deactivate(api_key: str, db: Session = Depends(get_db)):
    return


@route.put("/delete_account")
def delete_user_with_otp(payload: VerifyOTPPayload, db: Session = Depends(get_db)):
    # phone otp
    if payload.type == "phone":
        if not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input phone number",
            )

        # checking if phone exists in database
        user = get_user_by_ph(db, payload.phone)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone number doesn't exist",
            )

        if check_phone_otp(payload.phone, payload.code):
            user.is_deleted = True
            db.commit()

            return True
    # email otp
    else:
        if not payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please input email",
            )

        user = get_user_by_email(db, payload.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email doesn't exist",
            )

        if check_email_otp(payload.email, payload.code):
            user.is_deleted = True
            db.commit()

            return True
