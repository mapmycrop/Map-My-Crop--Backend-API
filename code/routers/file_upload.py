from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
import boto3
import os
import uuid

from config import setting
from utils.api import has_permission
from db import get_db
from pathlib import Path

route = APIRouter(prefix="/upload", tags=["Upload"])


@route.post("/")
@has_permission([])
def upload(api_key: str, file: UploadFile = File(...)):
    try:
        contents = file.file.read()

        # create rootDir if not exists
        rootDir = "./static/uploads"
        Path(rootDir).mkdir(parents=True, exist_ok=True)

        filepath = f"{rootDir}/{file.filename}"

        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There was an error uploading the file",
        )
    finally:
        file.file.close()

    filename, extension = os.path.splitext(file.filename)
    s3_filename = f"scouting-attachments/{str(uuid.uuid4()) + extension}"

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=setting.AWS_ACCESS_KEY,
        aws_secret_access_key=setting.AWS_SECRET_KEY,
    )
    try:
        s3_client.upload_file(filepath, setting.BUCKET_NAME, s3_filename)
        # TODO: Rather than the entire bucket public, we should use the ACL per object
        # s3_client.put_object_acl(ACL='public-read', Bucket=setting.BUCKET_NAME, Key=s3_filename)
        os.remove(filepath)
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="File Uploading was failed"
        )
    # We should use the the virtual-hosted style URL as per
    # https://aws.amazon.com/fr/blogs/aws/amazon-s3-path-deprecation-plan-the-rest-of-the-story/
    url = f"https://{setting.BUCKET_NAME}.s3.amazonaws.com/{s3_filename}"

    return url
