from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from geoalchemy2 import func
from shapely.wkt import loads
from sqlalchemy import or_
from typing import List
from geoalchemy2 import Geography
from sqlalchemy.sql.expression import cast
import json
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Params
from sqlalchemy import select, func

from db import get_db
from models import FarmDelineation
from utils.api import has_permission

route = APIRouter(prefix="/farm-delineation", tags=["Farm Delineation"])


def convertToGeojson(obj):
    geojson_response = {
        "type": "FeatureCollection",
        "features": [],
        "total": obj.total,
        "page": obj.page,
        "size": obj.size,
        "pages": obj.pages,
    }
    for geom in obj.items:
        geojson_response["features"].append(json.loads(geom))

    return geojson_response


@route.get("/")
@has_permission([])
def get_all(api_key: str, param: Params = Depends(), db: Session = Depends(get_db)):
    """
    Get all Farm Delineations

    :param api_key: user's api key
    :param param: pagination data
    :param db: database
    :return: return all farm delineations
    """
    farm_delination = paginate(
        db, select(func.ST_AsGeoJSON(FarmDelineation).label("geojson")), params=param
    )

    if len(farm_delination.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Outside test area"
        )

    return convertToGeojson(farm_delination)


@route.get("/polygon")
@has_permission([])
def get_with_polygon(
    api_key: str,
    polygon: str = Query(
        example="POLYGON((-76.74394087668612 40.0798897683467,-76.74392862739128 40.07943051346837,-76.74322306797794 40.07920744569597,-76.74291928545304 40.07983353322183,-76.74394087668612 40.0798897683467))",
        description="All values within and intersecting with polygon, WKT format with SRID 4326",
    ),
    param: Params = Depends(),
    db: Session = Depends(get_db),
):
    """
    Get farm delineations with Polygon

    :param api_key: user's api key
    :param polygon: Polygon data
    :param param: pagination data
    :param db: database
    :return: farm delineation
    """
    err_message = "Please provide a valid polygon in WKT format"

    try:
        shapely_polygon = loads(polygon)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    if not shapely_polygon.is_valid or shapely_polygon.geom_type != "Polygon":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    farm_delination = paginate(
        db,
        select(func.ST_AsGeoJSON(FarmDelineation).label("geojson")).filter(
            or_(
                FarmDelineation.geometry.ST_Within(func.ST_GeomFromText(polygon, 4326)),
                FarmDelineation.geometry.ST_Intersects(
                    func.ST_GeomFromText(polygon, 4326)
                ),
            )
        ),
        params=param,
    )

    if len(farm_delination.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Outside test area"
        )

    return convertToGeojson(farm_delination)


@route.get("/bbox")
@has_permission([])
def get_with_bbox(
    api_key: str,
    bbox: str = Query(
        example="POLYGON((-76.7442740811436 40.0788681563385,-76.7442740811436 40.0804389956234,-76.7428923133823 40.0804389956234,-76.7428923133823 40.0788681563385,-76.7442740811436 40.0788681563385))",
        description="All values within and intersecting with bbox, WKT format with SRID 4326",
    ),
    param: Params = Depends(),
    db: Session = Depends(get_db),
):
    """
    Get farm delineation with bbox

    :param api_key: user's api key
    :param bbox: boundary of area
    :param param: pagination data
    :param db: database
    :return: farm delineation
    """
    err_message = "Please provide a valid BBOX in WKT format e.g. POLYGON((long lat, long lat, long lat, long lat))"

    try:
        shapely_bbox = loads(bbox)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    if not shapely_bbox.is_valid or shapely_bbox.geom_type != "Polygon":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    shapely_bounds: List[float] = shapely_bbox.bounds

    if shapely_bbox.area != (shapely_bounds[2] - shapely_bounds[0]) * (
        shapely_bounds[3] - shapely_bounds[1]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    farm_delination = paginate(
        db,
        select(func.ST_AsGeoJSON(FarmDelineation).label("geojson")).filter(
            or_(
                FarmDelineation.geometry.ST_Within(func.ST_GeomFromText(bbox, 4326)),
                FarmDelineation.geometry.ST_Intersects(
                    func.ST_GeomFromText(bbox, 4326)
                ),
            )
        ),
        params=param,
    )

    if len(farm_delination.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Outside test area"
        )

    return convertToGeojson(farm_delination)


@route.get("/point")
@has_permission([])
def get_with_point(
    api_key: str,
    point: str = Query(
        example="POINT(-76.74354697730406 40.07958037192528)",
        description="WKT format with SRID 4326",
    ),
    param: Params = Depends(),
    db: Session = Depends(get_db),
):
    """
    Get farm delineation wiht point

    :param api_key: user's api key
    :param point: point data
    :param param: pagination data
    :param db: database
    :return: farm delineation
    """
    err_message = "Please provide a valid Point in WKT format e.g. POINT(long lat)"
    try:
        shapely_point = loads(point)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )
    if not shapely_point.is_valid or shapely_point.geom_type != "Point":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    farm_delination = paginate(
        db,
        select(func.ST_AsGeoJSON(FarmDelineation).label("geojson")).filter(
            FarmDelineation.geometry.ST_Contains(func.ST_GeomFromText(point, 4326))
        ),
        params=param,
    )

    if len(farm_delination.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Outside test area"
        )

    return convertToGeojson(farm_delination)


@route.get("/point-buffer")
@has_permission([])
def get_with_point_buffer(
    api_key: str,
    point: str = Query(
        example="POINT(-76.74354697730406 40.07958037192528)",
        description="WKT format with SRID 4326",
    ),
    buffer: int = Query(example=1, ge=0, le=1000, description="Distance in KMs"),
    param: Params = Depends(),
    db: Session = Depends(get_db),
):
    """
    Get farm delineation with point and range

    :param api_key: user's api key
    :param point: point data
    :param buffer: range data
    :param param: pagination data
    :param db: database
    :return: farm delineation
    """
    err_message = "Please provide a valid Point in WKT format e.g. POINT(long lat)"
    try:
        shapely_point = loads(point)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )
    if not shapely_point.is_valid or shapely_point.geom_type != "Point":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_message,
        )

    distance_m = buffer * 1000

    farm_delination = paginate(
        db,
        select(func.ST_AsGeoJSON(FarmDelineation).label("geojson")).filter(
            func.ST_Distance(
                cast(func.ST_centroid(FarmDelineation.geometry), Geography),
                cast(func.ST_GeomFromText(point, 4326), Geography),
                True,
            )
            <= distance_m
        ),
        params=param,
    )

    if len(farm_delination.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Outside test area"
        )

    return convertToGeojson(farm_delination)
