from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from db import get_db
from utils.api import has_permission
import requests
from config import setting
from cache import get_redis
import json
from datetime import datetime

GOV_API_KEY = setting.GOV_API_KEY

route = APIRouter(prefix="/market", tags=["Market"])


@route.post("/live")
@has_permission([])
def get_market_data(
    api_key: str,
    response: Response,
    cache=Depends(get_redis),
):
    api_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": "579b464db66ec23bdd00000186821f6334354c27682ec3227e0a4526",
        "format": "json",
        "limit": 10000,
    }

    redis_key: str = "market_live"
    try:
        # TODO: can be wrapped inside a function
        cached_response = cache.get(redis_key)
        if cached_response:
            response.headers["x-cached"] = "True"

            return json.loads(cached_response)
    except Exception as e:
        pass

    gov_response = requests.get(api_url, params)

    if gov_response.status_code != 200:
        HTTPException(status_code=gov_response.status_code, detail=gov_response.json())

    data = gov_response.json()

    response = data["records"]

    try:
        # TODO: Even empty response is stored because data doesn't get updated that often
        # So we can save the amount of API requests we do
        # in turn improving our API response time
        # Cache till next 10AM
        morning_10AM = datetime.now().replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        now = datetime.now()
        cache_till_next_10AM = None

        if morning_10AM > now:
            cache_till_next_10AM = (morning_10AM - now).seconds
        else:
            cache_till_next_10AM = 60 * 60 * 24 - (now - morning_10AM).seconds

        cache.set(redis_key, json.dumps(response), cache_till_next_10AM)
    except Exception as e:
        pass

    return response
