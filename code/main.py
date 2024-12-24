from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from functools import lru_cache
from starlette.middleware.sessions import SessionMiddleware
from fastapi_pagination import add_pagination
from listeners import handlers
from apscheduler.schedulers.background import BackgroundScheduler

from config import setting
from routers import (
    admin,
    advisory,
    ai,
    auth,
    company,
    contact,
    crop,
    crop_disease,
    crop_guide,
    enterprise,
    farm,
    farm_scouting,
    farm_calendar,
    farm_crop,
    farm_delineation,
    feedback,
    fertilizer,
    file_upload,
    market,
    mis,
    notification,
    other,
    profile,
    schedule_call,
    satellite,
    statistic,
    status,
    reseller,
    weather,
)
from utils.api import check_and_update_paid_status

origins = ["http://localhost", "http://localhost:3000/", ""]


@lru_cache()
def get_settings():
    return Settings()


description = """
Map My Store API helps you do awesome stuff. 🌾
"""
app = FastAPI(
    title="Map My Crop",
    docs_url="/",
    description=description,
    version="0.0.1",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

add_pagination(app)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Map My Crop",
        version="0.1.0",
        description="Map My Crop's API",
        routes=app.routes,
        servers=[{"url": setting.SERVER}] if setting.SERVER != "" else [],
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://mapmycrop.store/images/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


scheduler = BackgroundScheduler()
scheduler.add_job(check_and_update_paid_status, "cron", hour=12, minute=0)
scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()


app.openapi = custom_openapi

# System middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=setting.secret_key)
app.add_middleware(EventHandlerASGIMiddleware, handlers=[local_handler])
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(admin.route)
app.include_router(advisory.route)
app.include_router(ai.route)
app.include_router(auth.route)
app.include_router(company.route)
app.include_router(contact.route)
app.include_router(crop.route)
app.include_router(crop_disease.route)
app.include_router(crop_guide.route)
app.include_router(enterprise.route)
app.include_router(farm.route)
app.include_router(farm_calendar.route)
app.include_router(farm_crop.route)
app.include_router(farm_delineation.route)
app.include_router(farm_scouting.route)
app.include_router(feedback.route)
app.include_router(fertilizer.route)
app.include_router(file_upload.route)
app.include_router(market.route)
app.include_router(mis.route)
app.include_router(notification.route)
app.include_router(other.route)
app.include_router(profile.route)
app.include_router(satellite.route)
app.include_router(schedule_call.route)
app.include_router(statistic.route)
app.include_router(status.route)
app.include_router(reseller.route)
app.include_router(weather.route)


@app.get("/")
def home():
    return {"data": "at home"}
