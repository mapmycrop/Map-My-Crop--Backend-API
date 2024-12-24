from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
import requests
from typing import Union
from schemas import cropDiseaseDetection, water_req_record
from typing import List
from config import setting
import uuid
from datetime import datetime, date
import json
from utils.irrigation_data import crop_details
from utils.api import get_farm
from routers.weather import get_forecast_data
from utils.jobprocessor import create_job_run, get_job_status, get_job_xCom

from utils.api import has_permission, save_file_to_bucket
from constant import FARMER, COMPANY
from enum import Enum
from models import Company

route = APIRouter(prefix="/ai", tags=["AI"])

OBJECTS_CLASS_NAME = "Objects"


@route.post("/crop-disease", response_model=cropDiseaseDetection)
@has_permission([FARMER, COMPANY])
def crop_disease(
    api_key: str,
    image: UploadFile,
    crop: Union[str, None] = None,
    db: Session = Depends(get_db),
):
    if image.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file. Send an image in .png or .jpeg format",
        )

    if crop == None:
        crop = ""

    content = image.file.read()

    guid = uuid.uuid4()

    file_extension = ".png" if image.content_type == "image/png" else ".jpg"
    envFolder = setting.ENVIRONMENT

    save_file_to_bucket(
        bucket_name=setting.CROP_DISEASE_BUCKET_NAME,
        file_path=envFolder,
        file_name=f"{guid}{file_extension}",
        file_content=content,
    )

    # Save the metadata to the bucket
    metadata = {
        "api_key": api_key,
        "timestamp": datetime.now().isoformat(),
        "crop": crop,
        "env": setting.ENVIRONMENT,
    }

    save_file_to_bucket(
        bucket_name=setting.CROP_DISEASE_BUCKET_NAME,
        file_path=envFolder,
        file_name=f"{guid}.json",
        file_content=json.dumps(metadata),
    )

    # Prepare the files dictionary for the new request
    files = {"image": (image.filename, content, image.content_type)}
    URL_BASE = setting.AI_API_URL
    target_URL = "{0}/ai/crop-disease?crop={1}".format(URL_BASE, crop)
    # Send the file content to the target API
    response = requests.post(target_URL, files=files)
    if response.status_code == 200:
        output = response.json()

        return output
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not process the inputs",
        )


# ENUM Indicating the the Irrigation Type
class IrrigationType(str, Enum):
    DRIP = "DRIP"
    FLOOD = "FLOOD"


# Get the Water Requirement by Model 1
@route.post("/water-requirement-model1", response_model=List[water_req_record])
@has_permission([FARMER, COMPANY])
def water_requirement_model1(
    api_key: str,
    crop_name: str,
    farm_id: str,
    sowing_date: date,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Water Requirement Model 1

    :param api_key: user's api key
    :param crop_name: crop name
    :param farm_id: farm's primary key
    :param sowing_date: date of sowing
    :param db: database dependencies
    :return: return Water Requirement per day
    """
    if crop_name not in crop_details.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid crop. Please provide a valid crop name",
        )

    selected_crop_data = crop_details[crop_name]

    # get the Farm's area
    farmResponse = get_farm(db, api_key, farm_id)
    farm = json.loads(farmResponse[0])
    properties = farm["properties"]
    area = properties.get("area", 0)

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    # Fetch weather data for 7 days
    forecast_data = get_forecast_data(lat, lon, s_user, 7)
    if not forecast_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No weather data available.",
        )

    results = []
    for day in forecast_data:
        forecast_date = date.fromisoformat(day.get("date", str(date.today())))
        days_since_sowing = (forecast_date - sowing_date).days
        for stage_name, details in selected_crop_data.items():
            start_day, end_day = map(int, details["Days"].split("-"))
            if start_day <= days_since_sowing <= end_day:
                stage = stage_name
                coefficient = float(details["Coefficient"])
                break
        if stage is None:
            stage = "Unknown stage"
            coefficient = 0.0

        et = float(day.get("evapotranspiration", "0").replace(" mm", ""))
        water_requirement = et * area * coefficient * 4000
        results.append(
            {
                "date": day.get("date", "No date provided"),
                "crop_days": days_since_sowing,
                "stage": stage,
                "coefficient": coefficient,
                "area": area,
                "water_requirement": water_requirement,
            }
        )
    return results


# Get the Water Requirement by Model 2
@route.post("/water-requirement-model2", response_model=List[water_req_record])
@has_permission([FARMER, COMPANY])
def water_requirement_model2(
    api_key: str,
    crop_name: str,
    farm_id: str,
    sowing_date: date,
    irrigation: IrrigationType,
    db: Session = Depends(get_db),
    s_user=Depends(lambda: None),
):
    """
    Water Requirement Model 2

    :param api_key: user's api key
    :param crop_name: crop name
    :param farm_id: farm's primary key
    :param sowing_date: date of sowing
    :irrigation: type of irrigation
    :param db: database dependencies
    :return: return Water Requirement per day
    """
    if irrigation == IrrigationType.DRIP:
        irrigation_efficiency = 0.9
    elif irrigation == IrrigationType.FLOOD:
        irrigation_efficiency = 0.6

    if crop_name not in crop_details.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid crop. Please provide a valid crop name",
        )

    selected_crop_data = crop_details[crop_name]

    # get the Farm's area
    farmResponse = get_farm(db, api_key, farm_id)
    farm = json.loads(farmResponse[0])
    properties = farm["properties"]
    area = properties.get("area", 0)

    [lon, lat] = farm["properties"]["center"]["coordinates"]

    # Fetch weather data for 7 days
    forecast_data = get_forecast_data(lat, lon, s_user, 7)
    if not forecast_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No weather data available.",
        )

    # Constants
    ACRE_INCH_TO_GALLON = 27154
    GALLONS_TO_LITERS = 3.78541

    results = []
    for day in forecast_data:
        forecast_date = date.fromisoformat(day.get("date", str(date.today())))
        days_since_sowing = (forecast_date - sowing_date).days

        stage, coefficient = None, None
        for stage_name, details in selected_crop_data.items():
            start_day, end_day = map(int, details["Days"].split("-"))
            if start_day <= days_since_sowing <= end_day:
                stage = stage_name
                coefficient = float(details["Coefficient"])
                break

        if stage is None:
            stage = "Unknown stage"
            coefficient = 0.0

        et = float(day.get("evapotranspiration", "0").replace(" mm", ""))
        # Access irrigation_efficiency from crop_input
        water_requirement = (
            ((et * coefficient) / irrigation_efficiency)
            * ACRE_INCH_TO_GALLON
            * GALLONS_TO_LITERS
        )
        results.append(
            {
                "date": day.get("date", "No date provided"),
                "crop_days": days_since_sowing,
                "stage": stage,
                "coefficient": coefficient,
                "area": area,
                "water_requirement": water_requirement,
            }
        )
    return results


@route.post("/job_create")
@has_permission([COMPANY])
def job_create(
    api_key: str,
    model_id: str,
    inputs: dict,
    db: Session = Depends(get_db),
):

    # Check if the farms belong to the company
    company = db.query(Company).filter(Company.apikey == api_key).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid API KEY",
        )

    # Now check if the farms belong to the company
    farm_ids = inputs.get("farm_ids", [])
    for farm_id in farm_ids:
        farm = get_farm(db, api_key, farm_id)
        if farm == None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Farm ID",
            )
    # Check for the model_id
    if model_id != "Farms_Index":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Model ID",
        )

    # right now we have only one model to run. In the future we may to change this
    models = {"Farms_Index": "Farms_Indices_Values"}

    # Can't find a better way to get this
    URLS = {
        "dev": "https://api.mapmycrop.store",
        "preprod": "https://api.mapmycrop.live",
        "prod": "https://api.mapmycrop.com",
    }

    # Now we are ready to create the job
    inputs = {
        "enterprise_api_key": api_key,
        "farm_ids": farm_ids,
        "BaseURL": URLS[setting.ENVIRONMENT],
    }
    print(inputs)
    response = create_job_run(models[model_id], inputs)
    if response == None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating job",
        )
    return {"job_id": response["dag_run_id"]}


@route.get("/job_status")
@has_permission([COMPANY])
def job_create(
    api_key: str,
    model_id: str,
    job_id: str,
    db: Session = Depends(get_db),
):
    # Check for the model_id
    if model_id != "Farms_Index":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Model ID",
        )

    # right now we have only one model to run. In the future we may to change this
    models = {"Farms_Index": ["Farms_Indices_Values", "get_farm_indices_values"]}

    response = get_job_status(models[model_id][0], job_id)
    if response == None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting job status",
        )
    if response["state"] == "success":
        outValue = get_job_xCom(
            models[model_id][0], job_id, models[model_id][1], "return_value"
        )
        # TODO Figure out why the JSON has single inverted quotes
        outValue = json.loads(outValue.replace("'", '"'))
        output = {"status": response["state"], "output": outValue}
        return output
    elif response["state"] == "failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error running job",
        )
    elif response["state"] in ["running", "queued"]:
        return {"status": response["state"]}
    return response
