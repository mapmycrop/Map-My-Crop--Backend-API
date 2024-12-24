from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import requests
import re

from db import get_db
from config import setting
from utils.api import has_permission
from constant import FARMER, COMPANY

route = APIRouter(prefix="/other", tags=["Other"])


def validate_latitude(latitude):
    if -90 <= latitude <= 90:
        return True
    else:
        return False


def validate_longitude(longitude):
    if -180 <= longitude <= 180:
        return True
    else:
        return False


@route.get("/historical")
@has_permission([FARMER, COMPANY])
def weather_monthly_historical(
    api_key: str, lat: float, lon: float, start: str, end: str
):
    if not validate_latitude(lat) or not validate_longitude(lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude and/or longitude values.",
        )

    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, start) or not re.match(pattern, end):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start and End date formate should be YYYY-MM-DD.",
        )

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date should be before the End date.",
        )

    params = {
        "max_temp": "temperature_2m_max",
        "min_temp": "temperature_2m_min",
        "relative humidity": "relativehumidity_2m",
        "rain": "rain",
    }

    api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    open_meteo_response = requests.request("GET", api_url)
    if open_meteo_response.status_code != 200:
        raise HTTPException(
            status_code=open_meteo_response.status_code,
            detail=open_meteo_response.json(),
        )

    data = open_meteo_response.json()

    units = data["daily_units"]

    response = {}
    for i in range(len(data["daily"]["time"])):
        year_month = datetime.fromisoformat(data["daily"]["time"][i]).strftime("%Y-%m")

        min_temp = (
            data["daily"]["temperature_2m_min"][i]
            if data["daily"]["temperature_2m_min"][i]
            else 0
        )
        max_temp = (
            data["daily"]["temperature_2m_max"][i]
            if data["daily"]["temperature_2m_max"][i]
            else 0
        )

        if year_month in response:
            response[year_month]["min_temp"].append(min_temp)
            response[year_month]["max_temp"].append(max_temp)
        else:
            response[year_month] = {
                "min_temp": [min_temp],
                "max_temp": [max_temp],
            }

    api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&hourly=relativehumidity_2m,rain&timezone=auto"
    open_meteo_response = requests.request("GET", api_url)
    if open_meteo_response.status_code != 200:
        raise HTTPException(
            status_code=open_meteo_response.status_code,
            detail=open_meteo_response.json(),
        )

    data = open_meteo_response.json()
    units.update(data["hourly_units"])

    for i in range(len(data["hourly"]["time"])):
        year_month = datetime.fromisoformat(data["hourly"]["time"][i]).strftime("%Y-%m")

        relative_humidity = (
            data["hourly"]["relativehumidity_2m"][i]
            if data["hourly"]["relativehumidity_2m"][i]
            else 0
        )
        rain = data["hourly"]["rain"][i] if data["hourly"]["rain"][i] else 0

        if "relative humidity" in response[year_month]:
            response[year_month]["relative humidity"].append(relative_humidity)
        else:
            response[year_month].update({"relative humidity": [relative_humidity]})

        if "rain" in response[year_month]:
            response[year_month]["rain"].append(rain)
        else:
            response[year_month].update({"rain": [rain]})

    for key in list(response.keys()):
        for param in list(response[key]):
            unit = units[params[param]]
            response[key][
                param
            ] = f"{ round(sum(response[key][param]), 2) if param == 'rain' else round(sum(response[key][param]) / len(response[key][param]), 2)} {unit}"

    return response


@route.get("/current")
@has_permission([FARMER, COMPANY])
def weather_current(api_key: str, lat: float, lon: float):
    if not validate_latitude(lat) or not validate_longitude(lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude and/or longitude values.",
        )

    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={setting.OPEN_WEATHER_MAP_API_KEY}&units=metric"

    open_weather_response = requests.request("GET", api_url)
    if open_weather_response.status_code != 200:
        raise HTTPException(
            status_code=open_weather_response.status_code,
            detail=open_weather_response.json(),
        )

    data = open_weather_response.json()

    rain = 0
    if "rain" in data:
        rain = data["rain"]["1h"]

    response = {
        "temperature": f"{data['main']['temp']} °C",
        "relative humidity": f"{data['main']['humidity']} %",
        "rain": f"{rain} mm",
    }

    return response


@route.get("/forecast-hours")
@has_permission([FARMER, COMPANY])
def weather_forecast_hours(api_key: str, lat: float, lon: float):
    if not validate_latitude(lat) or not validate_longitude(lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude and/or longitude values.",
        )

    response = []

    api_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={setting.OPEN_WEATHER_MAP_API_KEY}&units=metric"
    open_weather_map_response = requests.request("GET", api_url)
    if open_weather_map_response.status_code != 200:
        raise HTTPException(
            status_code=open_weather_map_response.status_code,
            detail=open_weather_map_response.json(),
        )

    open_weather_map_data = open_weather_map_response.json()

    for i in range(5):
        item = open_weather_map_data["list"][i]
        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d %H:%M:%S")

        rain = None
        if "rain" in item:
            rain = f"{float(item['rain']['3h'])} mm"

        response.append(
            {
                "date": date,
                "min_temp": f"{float(item['main']['temp_min'])} °C",
                "max_temp": f"{float(item['main']['temp_max'])} °C",
                "relative humidity": f"{float(item['main']['humidity'])} %",
                "rain": rain,
            }
        )

    return response


@route.get("/forecast-days")
@has_permission([FARMER, COMPANY])
def weather_forecast_days(api_key: str, lat: float, lon: float):
    if not validate_latitude(lat) or not validate_longitude(lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude and/or longitude values.",
        )

    response = []

    api_url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt=14&appid={setting.OPEN_WEATHER_MAP_API_KEY}&units=metric"
    open_weather_map_response = requests.request("GET", api_url)
    if open_weather_map_response.status_code != 200:
        raise HTTPException(
            status_code=open_weather_map_response.status_code,
            detail=open_weather_map_response.json(),
        )

    open_weather_map_data = open_weather_map_response.json()

    api_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={setting.OPEN_WEATHER_MAP_API_KEY}"
    moon_phase_response = requests.request("GET", api_url)

    moon_phase_res = moon_phase_response.json()

    for item in open_weather_map_data["list"]:
        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")

        moon_phase = [
            el["moon_phase"]
            for el in moon_phase_res["daily"]
            if datetime.fromtimestamp(el["dt"]).strftime("%Y-%m-%d") == date
        ]

        if len(moon_phase):
            moon_phase_data = moon_phase[0]
        else:
            moon_phase_data = None

        rain = None
        if "rain" in item:
            rain = f"{float(item['rain'])} mm"

        response.append(
            {
                "date": date,
                "min_temp": f"{float(item['temp']['min'])} °C",
                "max_temp": f"{float(item['temp']['max'])} °C",
                "relative humidity": f"{float(item['humidity'])} %",
                "rain": rain,
                "moon_phase": moon_phase_data,
            }
        )

    return response


@route.get("/isochrone")
@has_permission([FARMER, COMPANY])
def isochrone(api_key: str, lat: float, lon: float):
    if not validate_latitude(lat) or not validate_longitude(lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude and/or longitude values.",
        )

    api_url = f"https://api.mapbox.com/isochrone/v1/mapbox/driving-traffic/{lon},{lat}?contours_minutes=15,30,45,60&contours_colors=99D9EA,9fbf40,bf8f40,bf4040&polygons=false&denoise=1&access_token={setting.ISOCHRONE_ACCESS_TOKEN}"

    response = requests.request("GET", api_url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
        )

    return response.json()
