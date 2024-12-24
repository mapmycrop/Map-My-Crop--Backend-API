from pydantic import BaseSettings
import sys
from pathlib import Path


class Settings(BaseSettings):
    SERVER: str
    db_host: str
    db_port: int
    db_name: str
    db_pwd: str
    db_usr: str
    secret_key: str
    algorithm: str
    timeout: int
    SENTINEL_HUB_CLIENT_ID: str
    SENTINEL_HUB_CLIENT_SECRET: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    BUCKET_NAME: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    FACEBOOK_CLIENT_ID: str
    FACEBOOK_CLIENT_SECRET: str
    # Notification
    SENDINBLUE_KEY: str
    TWILIO_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_SERVICE_SID: str
    # Gov API-key
    GOV_API_KEY: str
    # redis
    REDIS_HOST: str
    REDIS_PORT: int
    # open weather
    OPEN_WEATHER_MAP_API_KEY: str
    # environment
    ENVIRONMENT: str
    # isochrone access token
    ISOCHRONE_ACCESS_TOKEN: str
    # API endpoint for AI Models
    AI_API_URL: str
    # aisendy api key
    AISENSY_APIKEY: str
    # planetscope api subscription key
    PLANET_API_KEY: str
    # crop-disease bucket name in S3
    CROP_DISEASE_BUCKET_NAME: str
    # display-photo bucket name in S3
    DISPLAY_PHOTO_BUCKET_NAME: str
    # API endpoint for Job Processor
    JOB_PROCESSOR_API_URL: str
    # Username for Job Processor
    JOB_PROCESSOR_USER: str
    # Password for Job Processor
    JOB_PROCESSOR_PASSWORD: str

    class Config:
        env_file = Path(Path(__file__).resolve().parent) / ".env"


setting = Settings()
