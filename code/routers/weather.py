from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List
import requests
import calendar
import json

from utils.api import has_permission, get_farm
from db import get_db
from config import setting
from schemas import WeatherDayForecastResponse


route = APIRouter(prefix="/weather", tags=["Weather"])

hourly_current_params_unpaid = {
    "uv_index": "uv index",
    "soil_temperature_0cm": "soil temperature 0 cm",
    "soil_moisture_0_1cm": "soil moisture 0 cm",
}

hourly_current_params_paid = {
    "uv_index": "uv index",
    "soil_temperature_0cm": "soil temperature 0 cm",
    "soil_temperature_6cm": "soil temperature 6 cm",
    "soil_temperature_54cm": "soil temperature 54 cm",
    "soil_moisture_0_1cm": "soil moisture 0 cm",
    "soil_moisture_1_3cm": "soil moisture 2 cm",
    "soil_moisture_3_9cm": "soil moisture 6 cm",
    "soil_moisture_9_27cm": "soil moisture 18 cm",
    "soil_moisture_27_81cm": "soil moisture 48 cm",
}

hourly_forecast_params_paid = {
    "soil_temperature_0cm": "soil temperature 0cm",
    "soil_temperature_6cm": "soil temperature 6cm",
    "soil_temperature_54cm": "soil temperature 54cm",
    "soil_moisture_0_1cm": "soil moisture 0cm",
    "soil_moisture_1_3cm": "soil moisture 2cm",
    "soil_moisture_3_9cm": "soil moisture 6cm",
    "soil_moisture_9_27cm": "soil moisture 18cm",
    "soil_moisture_27_81cm": "soil moisture 48cm",
}

hourly_forecast_params_unpaid = {
    "soil_temperature_0cm": "soil temperature 0cm",
    "soil_moisture_0_1cm": "soil moisture 0cm",
}

hourly_historical_params_paid = {
    "temperature_2m": "temperature 2m",
    "windspeed_10m": "windspeed 10m",
    "winddirection_10m": "winddirection 10m",
    "windgusts_10m": "windgusts 10m",
    "soil_temperature_0_to_7cm": "soil temperature 4cm",
    "soil_temperature_7_to_28cm": "soil temperature 14cm",
    "soil_temperature_28_to_100cm": "soil temperature 70cm",
    "soil_moisture_0_to_7cm": "soil moisture 4cm",
    "soil_moisture_7_to_28cm": "soil moisture 14cm",
    "soil_moisture_28_to_100cm": "soil moisture 70cm",
}

hourly_historical_params_unpaid = {
    "soil_temperature_0_to_7cm": "soil temperature 4cm",
    "soil_moisture_0_to_7cm": "soil moisture 4cm",
}

monthly_params = {
    "temperature_2m": "temperature 2m",
    "relativehumidity_2m": "humidity",
    "rain": "rain",
}


@route.get("/")
@has_permission([])
def current(
    api_key: str,
    farm_id: str,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={s_user.unit}&appid={setting.OPEN_WEATHER_MAP_API_KEY}"

    open_weather_map_response = requests.request("GET", api_url)

    if open_weather_map_response.status_code != 200:
        HTTPException(
            status_code=open_weather_map_response.status_code,
            detail=open_weather_map_response.json(),
        )

    data = open_weather_map_response.json()

    response = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "type": data["weather"][0]["main"],
        "wind": data["wind"]["speed"],
        "deg": data["wind"]["deg"],
        "clouds": data["clouds"]["all"],
    }

    if "rain" in data:
        response["rain"] = data["rain"]["1h"]
    else:
        response["rain"] = 0

    if farm["properties"]["is_paid"]:
        hourly_current_params = hourly_current_params_paid
    else:
        hourly_current_params = hourly_current_params_unpaid

    hourly_params = ",".join(list(hourly_current_params))

    if s_user.unit == "metric":
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={hourly_params}&timezone=auto"
    else:
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={hourly_params}&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph"

    open_meteo_response = requests.request("GET", api_url)

    if open_meteo_response.status_code != 200:
        HTTPException(
            status_code=open_meteo_response.status_code,
            detail=open_meteo_response.json(),
        )

    data = open_meteo_response.json()

    current_datetime = (
        datetime.today().replace(second=0, microsecond=0, minute=0).isoformat()
    )

    for i in range(len(data["hourly"]["time"])):
        hourly_datetime = datetime.fromisoformat(data["hourly"]["time"][i]).isoformat()

        if current_datetime == hourly_datetime:
            for param in list(hourly_current_params):
                response[hourly_current_params[param]] = float(
                    data["hourly"][param][i] or 0
                )

    return response


@route.get("/et-forecast")
@has_permission([])
def et_forecast(
    api_key: str,
    farm_id: str,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    hourly_params = "evapotranspiration,et0_fao_evapotranspiration"

    if s_user.unit == "metric":
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={hourly_params}&timezone=auto&forecast_days=16"
    else:
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={hourly_params}&timezone=auto&forecast_days=16&temperature_unit=fahrenheit&wind_speed_unit=mph"

    response = requests.request("GET", api_url)

    if response.status_code != 200:
        HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()

    return data["hourly"]


@route.get("/soil-forecast")
@has_permission([])
def soil_forecast(
    api_key: str,
    farm_id: str,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    if farm["properties"]["is_paid"]:
        hourly_forecast_params = hourly_forecast_params_paid
    else:
        hourly_forecast_params = hourly_forecast_params_unpaid

    hourly_params = ",".join(list(hourly_forecast_params))

    if s_user.unit == "metric":
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={hourly_params}&forecast_days=7&timezone=Asia%2FKolkata"
    else:
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={hourly_params}&forecast_days=7&timezone=Asia%2FKolkata&temperature_unit=fahrenheit&wind_speed_unit=mph"

    open_weather_map_response = requests.request("GET", api_url)
    if open_weather_map_response.status_code != 200:
        HTTPException(
            status_code=open_weather_map_response.status_code,
            detail=open_weather_map_response.json(),
        )

    response = []
    data = open_weather_map_response.json()

    for i in range(0, len(data["hourly"]["time"]), 24):
        item = {
            "datetime": datetime.strptime(
                data["hourly"]["time"][i], "%Y-%m-%dT%H:%M"
            ).strftime("%Y-%m-%d")
        }
        for key in list(data["hourly"]):
            if key in hourly_forecast_params:
                item[hourly_forecast_params[key]] = 0

        for j in range(0, 24):
            for key in list(data["hourly"]):
                if key in hourly_forecast_params:
                    if data["hourly"][key][i + j]:
                        item[hourly_forecast_params[key]] += data["hourly"][key][i + j]

        for key in list(data["hourly"]):
            if key in hourly_forecast_params:
                item[hourly_forecast_params[key]] = round(
                    item[hourly_forecast_params[key]] / 24, 3
                )

        response.append(item)

    return response


@route.get("/day-forecast", response_model=List[WeatherDayForecastResponse])
@has_permission([])
def day_forecast(
    api_key: str,
    farm_id: str,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    api_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={setting.OPEN_WEATHER_MAP_API_KEY}&units={s_user.unit}"

    open_weather_map_response = requests.request("GET", api_url)
    if open_weather_map_response.status_code != 200:
        HTTPException(
            status_code=open_weather_map_response.status_code,
            detail=open_weather_map_response.json(),
        )

    response = []

    data = open_weather_map_response.json()
    for item in data["list"]:

        response.append(
            {
                "temp": float(item["main"]["temp"]),
                "pressure": float(item["main"]["pressure"]),
                "humidity": float(item["main"]["humidity"]),
                "wind_speed": float(item["wind"]["speed"]),
                "rain": item["rain"]["3h"] if "rain" in item else 0,
                "datetime": item["dt_txt"],
            }
        )
    return response


def get_forecast_data(lat, lon, s_user, days):
    response = []

    api_url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt={days}&appid={setting.OPEN_WEATHER_MAP_API_KEY}&units={s_user.unit}"
    open_weather_map_response = requests.request("GET", api_url)
    if open_weather_map_response.status_code != 200:
        HTTPException(
            status_code=open_weather_map_response.status_code,
            detail=open_weather_map_response.json(),
        )

    if s_user.unit == "metric":
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=direct_radiation&daily=et0_fao_evapotranspiration&timezone=auto"
    else:
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=direct_radiation&daily=et0_fao_evapotranspiration&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph"

    open_meteo_response = requests.request("GET", api_url)
    if open_meteo_response.status_code != 200:
        HTTPException(
            status_code=open_meteo_response.status_code,
            detail=open_meteo_response.json(),
        )

    open_weather_map_data = open_weather_map_response.json()
    open_meteo_data = open_meteo_response.json()

    for item in open_weather_map_data["list"]:
        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")

        precipitation = None
        if "rain" in item:
            precipitation = f"{float(item['rain'])} mm"

        et0_fao_evapotranspiration = None
        if date in open_meteo_data["daily"]["time"]:
            et0_fao_evapotranspiration = f"{open_meteo_data['daily']['et0_fao_evapotranspiration'][open_meteo_data['daily']['time'].index(date)]} mm"

        direct_radiation = None
        for datetime_item in open_meteo_data["hourly"]["time"]:
            if date in datetime_item:
                if direct_radiation is None:
                    direct_radiation = []

                direct_radiation.append(
                    float(
                        open_meteo_data["hourly"]["direct_radiation"][
                            open_meteo_data["hourly"]["time"].index(datetime_item)
                        ]
                    )
                )

        if direct_radiation is not None:
            direct_radiation = (
                f"{round(sum(direct_radiation) / len(direct_radiation), 2)} W/m^2"
            )

        if s_user.unit == "metric":
            response.append(
                {
                    "date": date,
                    "weather": f"http://openweathermap.org/img/w/{item['weather'][0]['icon']}.png",
                    "mintemp": f"{float(item['temp']['min'])} °C",
                    "maxtemp": f"{float(item['temp']['max'])} °C",
                    "relative humidity": f"{float(item['humidity'])} %",
                    "clouds": f"{float(item['clouds'])} %",
                    "wind": f"{float(item['speed'])} m/s",
                    "precipitation": precipitation,
                    "evapotranspiration": et0_fao_evapotranspiration,
                    "direct solar radiation": direct_radiation,
                }
            )
        else:
            response.append(
                {
                    "date": date,
                    "weather": f"http://openweathermap.org/img/w/{item['weather'][0]['icon']}.png",
                    "mintemp": f"{float(item['temp']['min'])} °F",
                    "maxtemp": f"{float(item['temp']['max'])} °F",
                    "relative humidity": f"{float(item['humidity'])} %",
                    "clouds": f"{float(item['clouds'])} %",
                    "wind": f"{float(item['speed'])} mph",
                    "precipitation": precipitation,
                    "evapotranspiration": et0_fao_evapotranspiration,
                    "direct solar radiation": direct_radiation,
                }
            )

    return response


@route.get("/weather-forecast")
@has_permission([])
def forecast(
    api_key: str,
    farm_id: str,
    days: int = 14,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])
    [lon, lat] = farm["properties"]["center"]["coordinates"]
    return get_forecast_data(lat, lon, s_user, days)


@route.get("/historical")
@has_permission([])
def historical(
    api_key: str,
    farm_id: str,
    start: date,
    end: date,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    # all params are available for only paid farm
    if farm["properties"]["is_paid"]:
        hourly_historical_params = hourly_historical_params_paid
    else:
        hourly_historical_params = hourly_historical_params_unpaid

    hourly = ",".join(list(hourly_historical_params))

    if s_user.unit == "metric":
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&hourly={hourly}&timezone=auto"
    else:
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&hourly={hourly}&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph"

    response = requests.request("GET", api_url)

    if response.status_code != 200:
        HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()

    for key in list(data["hourly"]):
        if key in hourly_historical_params:
            data["hourly"][hourly_historical_params[key]] = data["hourly"].pop(key)

    return data["hourly"]


@route.get("/et-historical")
@has_permission([])
def et_historical(
    api_key: str,
    farm_id: str,
    start: date,
    end: date,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    if s_user.unit == "metric":
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=et0_fao_evapotranspiration&timezone=auto"
    else:
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=et0_fao_evapotranspiration&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph"

    response = requests.request("GET", api_url)

    if response.status_code != 200:
        HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()
    return data["daily"]


@route.get("/monthly")
@has_permission([])
def monthly_data(api_key: str, lat: str, lon: str, s_user=Depends(lambda: None)):
    year = datetime.now().year
    month = datetime.now().month
    last_day = calendar.monthrange(year, month)[1]

    start_date = date(year, month, 1).strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d")
    end_date = date(year, month, last_day).strftime("%Y-%m-%d")

    hourly = ",".join(list(monthly_params))

    if s_user.unit == "metric":
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={now}&hourly={hourly}&timezone=auto"
    else:
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={now}&hourly={hourly}&timezone=auto&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph"

    response = requests.request("GET", api_url)

    if response.status_code != 200:
        HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()

    response = {}
    for key in list(data["hourly"]):
        if key in monthly_params:
            # remove null value from the list
            key_data = list(filter(None, data["hourly"].pop(key)))

            response[monthly_params[key]] = {"min": min(key_data), "max": max(key_data)}

    return response
