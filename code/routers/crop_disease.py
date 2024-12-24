from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from sqlalchemy.orm import Session
from typing import List
import json

from db import get_db
from models import Disease
from schemas import DiseaseSchema, GetDisease
from utils.api import has_permission
from cache import get_redis


route = APIRouter(prefix="/crop-disease", tags=["Crop Disease"])


@route.get(
    "/all",
    response_model=List[GetDisease],
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    response_model_exclude_defaults=True,
)
@has_permission([])
def index(api_key: str, response: Response, db: Session = Depends(get_db)):
    """
    Get all disease data from databse. Response will be cached

    :param api_key: user's api key
    :param response: FastAPI Response object
    :param db: database
    :return: array of disease
    """
    cache = get_redis()
    cache_key = "disease"

    try:
        cache_response = cache.get(cache_key)
        if cache_response:
            response.headers["x-cached"] = "True"

            return json.loads(cache_response)
    except Exception as e:
        pass

    diseases = db.query(Disease).all()
    diseases_as_dict = [crop.__dict__ for crop in diseases]

    for disease_dict in diseases_as_dict:
        disease_dict.pop("_sa_instance_state", None)

    cache.set(cache_key, json.dumps(diseases_as_dict), 60 * 60 * 24)

    return diseases


@route.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=GetDisease,
    deprecated=True,
)
def create(
    api_key: str = "",
    payload: DiseaseSchema = Body(
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "",
                "value": {
                    "name": "Anthracnose Leaf Blight and Stalk Rot",
                    "symptoms": "Cankers that emerge on twigs and branches are the",
                    "cause": "kg",
                    "organic_control": "Grasshoppers, parasitic wasps, flies, and other predators are just a few of the dangers that cutworms face. Bio-insecticides provide effective population control based on Beauveria bassiana, Nucleopolyhedrosis virus, and Bacillus thuringiensis. Avoiding needless treatment will promote natural predators.",
                    "chemical_control": "Always consider an integrated strategy that includes natural alternatives and preventative actions, where possible. Cutworm populations can be controlled by the use of products containing chlorpyrifos, beta-cypermethrin, deltamethrin, and lambda-cyhalothrin. Insecticide applications before planting can also be beneficial, although they should only be advised if substantial populations are anticipated.",
                    "preventive_measures": "Anthracnose_of_Almond_1",
                    "pre": "https://crop-disease-images.s3.ap-south-1.amazonaws.com",
                    "folder_name": "Anthracnose_of_Almond/",
                    "file_format": "jpg",
                    "image1": "",
                    "image2": "",
                    "image3": "",
                    "image4": "",
                    "image5": "",
                    "image6": "",
                    "image7": "",
                    "image8": "",
                    "image9": "",
                    "image10": "",
                    "image11": "",
                    "image12": "",
                    "image13": "",
                    "image14": "",
                    "image15": "",
                    "image16": "",
                    "image17": "",
                    "image18": "",
                    "image19": "",
                    "image20": "",
                    "image21": "",
                    "image22": "",
                    "image23": "",
                    "image24": "",
                    "image25": "",
                    "image26": "",
                    "image27": "",
                    "image28": "",
                    "image29": "",
                    "image30": "",
                    "image31": "",
                    "image32": "",
                    "image33": "",
                    "image34": "",
                    "image35": "",
                    "image36": "",
                    "image37": "",
                    "image38": "",
                    "image39": "",
                    "image40": "",
                    "image41": "",
                    "image42": "",
                    "image43": "",
                    "image44": "",
                    "image45": "",
                    "image46": "",
                    "image47": "",
                    "image48": "",
                    "image49": "",
                    "image50": "",
                    "image51": "",
                    "image52": "",
                    "image53": "",
                    "image54": "",
                    "image55": "",
                    "image56": "",
                    "image57": "",
                    "image58": "",
                    "image59": "",
                },
            }
        }
    ),
    db: Session = Depends(get_db),
):
    disease = Disease(**payload.dict())

    db.add(disease)
    db.commit()

    return disease


@route.get("/{id}", response_model=GetDisease)
@has_permission([])
def show(api_key: str, id: str, db: Session = Depends(get_db)):
    disease = db.query(Disease).filter(Disease.id == id).first()

    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease with given ID does not exist",
        )

    return disease
