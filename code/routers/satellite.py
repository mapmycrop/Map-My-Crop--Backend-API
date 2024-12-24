from sentinelhub import (
    SentinelHubRequest,
    SentinelHubCatalog,
    DataCollection,
    SentinelHubStatistical,
    MimeType,
    CRS,
    BBox,
    SHConfig,
)
from sentinelhub.constants import ResamplingType
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import JSONResponse
from typing import List
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import case
from PIL import Image, ImageColor
from starlette.background import BackgroundTasks
from rasterio import mask
from dateutil import parser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal
import requests
import rasterio
import numpy as np
import io
import os
import shutil
import json
import traceback
import base64
import json
from uuid import uuid4

from config import setting
from db import get_db
from models import Farm, Satellite, Indice, PlanetCollection
from schemas import SatelliteResponseModel
from utils.api import get_farm, check_indice, has_permission
from cache import get_redis
from constant import FARMER, COMPANY

upscale_factor = 0.01

route = APIRouter(prefix="/satellite", tags=["Satellite"])

SENTINEL_HUB_CLIENT_ID = setting.SENTINEL_HUB_CLIENT_ID
SENTINEL_HUB_CLIENT_SECRET = setting.SENTINEL_HUB_CLIENT_SECRET


def read_file(file):
    with rasterio.open(file) as src:
        return src.read()


def remove_file(path: str):
    os.unlink(path)


def remove_folder(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)


@route.get("/", response_model=List[SatelliteResponseModel])
@has_permission([FARMER, COMPANY])
def satellite_list(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    planet_collection = (
        db.query(PlanetCollection).filter(PlanetCollection.farm_id == farm_id).first()
    )

    if planet_collection is not None:
        satellites = (
            db.query(Satellite.name, Satellite.satellite, Indice.alias)
            .join(Indice, Satellite.name == Indice.satellite)
            .all()
        )
    else:
        satellites = (
            db.query(Satellite.name, Satellite.satellite, Indice.alias)
            .join(Indice, Satellite.name == Indice.satellite)
            .filter(Satellite.satellite != "S6")
            .all()
        )

    satellite_data = {}
    for name, satellite, alias in satellites:
        if name not in satellite_data:
            satellite_data[name] = {"name": name, "satellite": satellite, "indices": []}
        satellite_data[name]["indices"].append(alias)

    return list(satellite_data.values())


@route.get("/dates")
@has_permission([FARMER, COMPANY])
def satellite_available_date_list(
    api_key: str,
    farm_id: str,
    start_date: date = None,
    end_date: date = None,
    response: Response = None,
    cloud_cover: int = Query(ge=0, le=100, default=50),
    db: Session = Depends(get_db),
    cache=Depends(get_redis),
):

    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date can't be greater or equal to end date.",
        )

    if end_date is not None and end_date > datetime.today().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date can't be in future.",
        )

    if start_date is not None and start_date > datetime.today().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date can't be in future.",
        )

    if start_date is None and end_date is not None:
        start_date = end_date - timedelta(days=365)

    if start_date is not None and end_date is None:
        end_date = start_date + timedelta(days=365)

        if end_date > datetime.today().date():
            end_date = datetime.today().date()

    if start_date is None and end_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

    farm = json.loads(get_farm(db, api_key, farm_id)["geom"])

    redis_key = "catalogue"

    for value in [
        farm_id,
        cloud_cover,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    ]:
        redis_key = redis_key + "_" + str(value)

    try:
        cache_response = cache.get(redis_key)
        if cache_response:
            response.headers["x-cached"] = "True"

            return json.loads(cache_response)
    except Exception as e:
        pass

    # TODO This is script may only work with sentinelhub.__version__ >= '3.4.0'
    bbox = BBox(bbox=farm["properties"]["bbox"], crs=CRS.WGS84)

    satellites = db.query(Satellite).filter(Satellite.catalogue == True).all()

    catalogs = []
    for statellite in satellites:
        config = SHConfig()
        config.sh_client_id = SENTINEL_HUB_CLIENT_ID
        config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
        config.sh_base_url = statellite.region_url

        catalog = SentinelHubCatalog(config=config)

        args = {
            "collection": statellite.name,
            "bbox": bbox,
            "time": (start_date, end_date),
            "filter": (
                f"eo:cloud_cover < {cloud_cover}" if statellite.cloud_cover else None
            ),
        }
        catalogs.append(catalog.search(**args))

    planets = (
        db.query(PlanetCollection).filter(PlanetCollection.farm_id == farm_id).all()
    )

    for planet in planets:
        config = SHConfig()
        config.sh_client_id = SENTINEL_HUB_CLIENT_ID
        config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
        config.sh_base_url = "https://services.sentinel-hub.com"

        catalog = SentinelHubCatalog(config=config)

        args = {
            "collection": "byoc-" + planet.collection_id,
            "bbox": bbox,
            "time": (start_date, end_date),
        }
        catalogs.append(catalog.search(**args))
    executions = []
    with ThreadPoolExecutor() as executor:
        executions = [executor.submit(list, catalog) for catalog in catalogs]

    result = [execution.result() for execution in executions]

    response = []
    for products in result:
        for product in products:
            collection = product["collection"]

            if "byoc-" in collection:
                item = {
                    "satellite": "S6",
                    "datetime": product["properties"]["datetime"],
                    "cloud_cover": None,
                }
            else:
                satellite_name = next(
                    x.satellite for x in satellites if x.name == collection
                )

                item = {
                    "satellite": satellite_name,
                    "datetime": product["properties"]["datetime"],
                    "cloud_cover": None,
                }

            if "eo:cloud_cover" in product["properties"]:
                item["cloud_cover"] = product["properties"]["eo:cloud_cover"]

            response.append(item)

    response = sorted(response, key=lambda x: parser.parse(x["datetime"]), reverse=True)

    try:
        tomorrrow = datetime.now(tz=timezone.utc).replace(hour=23, minute=59, second=59)
        now = datetime.now(tz=timezone.utc)

        cache.set(redis_key, json.dumps(response), (tomorrrow - now).seconds)
    except Exception as e:
        pass

    return response


@route.get("/indices")
@has_permission([FARMER, COMPANY])
def available_indice_list(api_key: str, satellite: str, db: Session = Depends(get_db)):
    satellite_avaialble = (
        db.query(Satellite.name).filter(Satellite.satellite == satellite).count()
    )

    if not satellite_avaialble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Satellite is not available",
        )

    indice = (
        db.query(
            Indice.category,
            Indice.rank,
            Indice.description,
            Indice.created_at,
            Indice.updated_at,
            Indice.alias,
            case((Indice.evalscript.isnot(None), True), else_=False).label("process"),
            case((Indice.statistical_evalscript.isnot(None), True), else_=False).label(
                "statistics"
            ),
            Satellite.satellite,
        )
        .filter(Satellite.name == Indice.satellite)
        .filter(Satellite.satellite == satellite)
        .order_by(Indice.rank)
        .all()
    )

    response = {}
    for index in indice:
        if index["category"] in response:
            response[index["category"]].append(index)
        else:
            response[index["category"]] = [index]

    return response


@route.get("/field-imagery-stats", deprecated=True)
def indice_imagery(
    api_key: str,
    farm_id: str,
    index: str,
    satellite: str,
    satellite_date: date,
    background_tasks: BackgroundTasks,
    response: Response = None,
    db: Session = Depends(get_db),
    cache=Depends(get_redis),
):
    return


@route.get("/field-imagery")
@has_permission([FARMER, COMPANY])
def indice_imagery(
    api_key: str,
    farm_id: str,
    index: str,
    satellite: str,
    satellite_date: date,
    background_tasks: BackgroundTasks,
    response: Response = None,
    db: Session = Depends(get_db),
    cache=Depends(get_redis),
):
    [selected_index, selected_satellite] = check_indice(db, index, satellite, "imagery")

    farm = get_farm(db, api_key, farm_id)
    farm_geom = json.loads(farm["geom"])
    farm_area = farm_geom["properties"]["area"]
    config = SHConfig()
    config.sh_client_id = SENTINEL_HUB_CLIENT_ID
    config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
    config.sh_base_url = selected_satellite.region_url

    if satellite == "S6":
        temp_collection = (
            db.query(PlanetCollection.collection_id)
            .filter(PlanetCollection.farm_id == farm_id)
            .first()
        )

        collection = DataCollection.define_byoc(temp_collection[0])
    else:
        collection = next(
            x for x in list(DataCollection) if x.api_id == selected_index.satellite
        )

    bbox = BBox(bbox=farm_geom["properties"]["bbox"], crs=CRS.WGS84)

    # make folder
    today = satellite_date
    data_folder = f"static/field-imagery-stats-{uuid4()}"
    Path(data_folder).mkdir(parents=True, exist_ok=True)

    # remove folder as background task
    background_tasks.add_task(remove_folder, data_folder)

    redis_key = "field_imagery"

    for value in [farm_id, index, satellite, satellite_date.strftime("%Y-%m-%d")]:
        redis_key = redis_key + "_" + str(value.replace(" ", "_"))

    try:
        cache_response = cache.get(redis_key)
        if cache_response:
            response.headers["x-cached"] = "True"

            return json.loads(cache_response)
    except Exception as e:
        pass

    try:
        request = SentinelHubRequest(
            data_folder=data_folder,
            evalscript=selected_index.evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=collection,
                    time_interval=(today, today),
                    upsampling=ResamplingType.BICUBIC,
                    downsampling=ResamplingType.BICUBIC,
                ),
            ],
            responses=[
                SentinelHubRequest.output_response("default", MimeType.TIFF),
            ],
            bbox=bbox,
            config=config,
        )
        request.get_data(save_data=True)
        full_path = f"{data_folder}/{next(os.walk(data_folder))[1][0]}"

        with rasterio.open(f"{full_path}/response.tiff") as src:  # type: ignore
            # TODO: Remove if the `if` condition if possible
            # TODO: This if condition is copied twice, bad code
            if (
                selected_index.legend is None
                or selected_index.legend.get("dynamic", False) == False
            ):
                out_image, out_transform = mask.mask(
                    src, [farm_geom["geometry"]], crop=True, nodata=0
                )
                out_meta = src.meta.copy()
                out_meta.update(
                    {
                        "driver": "PNG",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform,
                        "nodata": 0,
                    }
                )
            else:
                out_image = mask.mask(
                    src,
                    [farm_geom["geometry"]],
                    crop=True,
                    filled=False,
                )
                band_value = out_image[0][0]

        # If no legends
        if (
            selected_index.legend is None
            or selected_index.legend.get("dynamic", False) == False
        ):
            # TODO: Fix this code. Don't need to write to filesystem if sending base64
            # But the code below was not working properly
            masked_img_path = f"{full_path}/masked.png"
            with rasterio.open(masked_img_path, "w", **out_meta) as dst:
                dst.write(out_image)
                dst.close()

            with open(masked_img_path, "rb") as masked_image:
                encoded_image_string = base64.b64encode(masked_image.read()).decode()

            legends = (
                selected_index.legend.get("values", []) if selected_index.legend else []
            )
            data = {"image": encoded_image_string, "dynamic": False, "legends": legends}

            cache.set(redis_key, json.dumps(data), 60 * 60 * 24)
            return data

        image_colors = np.zeros(band_value.shape + (4,))

        legends = selected_index.legend["values"].copy()

        counted_pixels = band_value.count()
        pixel_area = farm_area / counted_pixels

        for legend in legends:
            min_legend, max_legend, hex = legend["min"], legend["max"], legend["hex"]
            # !! Fixed value
            legend["unit"] = "acre"
            if min_legend is not None and max_legend is not None:
                pixel_positions = (band_value >= min_legend) & (band_value < max_legend)
                image_colors[pixel_positions] = ImageColor.getcolor(hex, "RGBA")
                legend_pixels = (pixel_positions).sum()
                legend["area"] = round(legend_pixels * pixel_area, 2)
                legend["area%"] = f"{round((legend_pixels / counted_pixels) * 100, 2)}%"
            elif min_legend is not None:
                pixel_positions = band_value >= min_legend
                image_colors[pixel_positions] = ImageColor.getcolor(hex, "RGBA")
                legend_pixels = (pixel_positions).sum()
                legend["area"] = round(legend_pixels * pixel_area, 2)
                legend["area%"] = f"{round((legend_pixels / counted_pixels) * 100, 2)}%"
            elif max_legend is not None:
                pixel_positions = band_value < max_legend
                image_colors[pixel_positions] = ImageColor.getcolor(hex, "RGBA")
                legend_pixels = (pixel_positions).sum()
                legend["area"] = round(legend_pixels * pixel_area, 2)
                legend["area%"] = f"{round((legend_pixels / counted_pixels) * 100, 2)}%"

        image_colors[np.ma.getmaskarray(band_value)] = (0, 0, 0, 0)
        masked_img = Image.fromarray(image_colors.astype(np.uint8), mode="RGBA")
        buffered = io.BytesIO()
        masked_img.save(buffered, format="PNG")
        encoded_image_string = base64.b64encode(buffered.getvalue()).decode()

        # masked_img.save(f"{full_path}/masked.png")
        # return FileResponse(f"{full_path}/masked.png")

        data = {"image": encoded_image_string, "dynamic": True, "legends": legends}
        cache.set(redis_key, json.dumps(data), 60 * 60 * 24)
        return data

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Check with admin",
        )


@route.get("/statistics")
@has_permission([FARMER, COMPANY])
def indice_statistic(
    api_key: str,
    farm_id: str,
    start_date: date,
    end_date: date,
    index: str,
    satellite: str,
    interval: str = "P1D",
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    [curr_indice, curr_satellite] = check_indice(db, index, satellite, "statistics")

    curr_farm_bbox = None

    if s_user.role == 1:
        curr_farm_bbox = (
            db.query(Farm.bbox)
            .filter(Farm.user_id == s_user.id, Farm.id == farm_id)
            .first()
        )

    elif s_user.role == 2:
        curr_farm_bbox = (
            db.query(Farm.bbox)
            .filter(Farm.company_id == s_user.id, Farm.id == farm_id)
            .first()
        )

    if not curr_farm_bbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm with given id not found for API key",
        )

    if not curr_farm_bbox:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Farm not found"
        )

    config = SHConfig()
    config.sh_client_id = SENTINEL_HUB_CLIENT_ID
    config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
    config.sh_base_url = curr_satellite.region_url

    if curr_indice.satellite == "S6":
        temp_collection = (
            db.query(PlanetCollection.collection_id)
            .filter(PlanetCollection.farm_id == farm_id)
            .first()
        )
        collection = DataCollection.define_byoc(temp_collection)
    else:
        collection = next(
            x for x in list(DataCollection) if x.api_id == curr_indice.satellite
        )

    calculations = {"default": {"histograms": {"default": {"nBins": 10}}}}

    request = SentinelHubStatistical(
        aggregation=SentinelHubStatistical.aggregation(
            evalscript=curr_indice.statistical_evalscript,
            time_interval=(start_date, end_date),
            aggregation_interval=interval,
        ),
        input_data=[
            SentinelHubStatistical.input_data(
                collection, other_args={"dataFilter": {"maxCloudCoverage": 20}}
            )
        ],
        bbox=BBox(curr_farm_bbox[0], "EPSG:4326"),  # type: ignore
        config=config,
        calculations=calculations,
    )

    result = request.get_data()[0]

    return result["data"]


@route.get("/historic-statistic", deprecated=True)
def historic_statistic(
    api_key: str,
    farm_id: str,
    start_date: date,
    end_date: date,
    index: str,
    satellite: str,
    soil: Literal["moisture", "temperature"],
    db: Session = Depends(get_db),
):
    return


@route.get("/statistic-historic")
@has_permission([FARMER, COMPANY])
def historic_statistic(
    api_key: str,
    farm_id: str,
    start_date: date,
    end_date: date,
    index: str,
    satellite: str,
    soil: Literal["moisture", "temperature"],
    db: Session = Depends(get_db),
):
    [current_index, current_satellite] = check_indice(
        db, index, satellite, "statistics"
    )

    farm = json.loads(get_farm(db, api_key, farm_id)[0])

    if not farm["properties"]["is_paid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This farm is not paid",
        )

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    config = SHConfig()
    config.sh_client_id = SENTINEL_HUB_CLIENT_ID
    config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
    config.sh_base_url = current_satellite.region_url

    if satellite == "S6":
        temp_collection = (
            db.query(PlanetCollection.collection_id)
            .filter(PlanetCollection.farm_id == farm_id)
            .first()
        )
        collection = DataCollection.define_byoc(temp_collection)
    else:
        collection = next(
            x for x in list(DataCollection) if x.api_id == current_index.satellite
        )

    calculations = {"default": {"histograms": {"default": {"nBins": 10}}}}

    request = SentinelHubStatistical(
        aggregation=SentinelHubStatistical.aggregation(
            evalscript=current_index.statistical_evalscript,
            time_interval=(start_date, end_date),
            aggregation_interval="P5D",
        ),
        input_data=[SentinelHubStatistical.input_data(collection)],
        bbox=BBox(farm["properties"]["bbox"], "EPSG:4326"),
        config=config,
        calculations=calculations,
    )

    result = request.get_data()[0]
    data = result["data"]

    indices = {"timestamp": [], "min": [], "max": [], "mean": []}
    for indice in data:
        date = datetime.strptime(
            indice["interval"]["from"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y-%m-%d")
        indices["timestamp"].append(date)
        indices["min"].append(indice["outputs"]["data"]["bands"]["B0"]["stats"]["min"])
        indices["max"].append(indice["outputs"]["data"]["bands"]["B0"]["stats"]["max"])
        indices["mean"].append(
            indice["outputs"]["data"]["bands"]["B0"]["stats"]["mean"]
        )

    # weather
    hourly_param_list = {
        "temperature": [
            "precipitation",
            "soil_temperature_0_to_7cm",
            "soil_temperature_7_to_28cm",
        ],
        "moisture": [
            "precipitation",
            "soil_moisture_0_to_7cm",
            "soil_moisture_7_to_28cm",
        ],
    }[soil]

    hourly_param = ",".join(hourly_param_list)

    api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly={hourly_param}"

    response = requests.request("GET", api_url)
    if response.status_code != 200:
        HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()

    weather = {"timestamp": []}
    for hourly_item in hourly_param_list:
        weather[hourly_item] = []

    nIndex = 0
    for i in range(len(data["hourly"]["time"])):
        date = datetime.strptime(data["hourly"]["time"][i], "%Y-%m-%dT%H:%M").strftime(
            "%Y-%m-%d"
        )

        if date in weather["timestamp"]:
            for hourly_item in hourly_param_list:
                if data["hourly"][hourly_item][i] is None:
                    data["hourly"][hourly_item][i] = 0

                weather[hourly_item][nIndex - 1] += data["hourly"][hourly_item][i]
        else:
            weather["timestamp"].append(date)

            for hourly_item in hourly_param_list:
                if data["hourly"][hourly_item][i] is None:
                    data["hourly"][hourly_item][i] = 0

                weather[hourly_item].append(data["hourly"][hourly_item][i])

            nIndex += 1

    for hourly_item in hourly_param_list:
        for i in range(len(weather[hourly_item])):
            weather[hourly_item][i] = round(weather[hourly_item][i] / 24, 3)

    response = {"weather": weather, "indices": indices}

    return response
