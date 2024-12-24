from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    JSON,
    String,
    BigInteger,
    DATE,
    Float,
    Computed,
    DateTime,
    Enum,
    ARRAY,
    event,
)
from sqlalchemy.sql import func
from fastapi_events.dispatcher import dispatch
from geoalchemy2 import Geometry
import uuid

from db import Base
from variables import (
    ScoutingStatus,
    SocialLoginProviderType,
    ContactSource,
    HowToContact,
    Topic,
    TypeOfExpert,
    RegisterSource,
    IrrigationType,
    Maturity,
    TillageType,
    LogSource,
)
from listeners.events import Events
from config import setting


def generate_uuid():
    return str(uuid.uuid4().hex)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True, default="")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    name = Column(String, unique=True, index=True)
    site = Column(String, nullable=True, default="")
    country = Column(String, nullable=True, default="India")
    role = Column(Integer, ForeignKey("roles.id"), default=2)
    apikey = Column(String, default=generate_uuid)
    is_active = Column(Boolean, nullable=False, default=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    unit = Column(String, nullable=False, default="metric")
    ph = Column(String, nullable=True)


@event.listens_for(Company, "after_insert")
def company_after_insert(mapper, connection, target):
    if setting.ENVIRONMENT != "dev":
        dispatch(Events.NEW_COMPANY_ADDED.value, {"enterprise_id": target.id})


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    ph = Column(String, unique=True, index=True, nullable=True)
    country_code = Column(Integer, nullable=False, default=91)  # Corrected to integer
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False, default="")
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_active = Column(Boolean, nullable=False, default=False)
    role = Column(Integer, ForeignKey("roles.id"), default=1)
    apikey = Column(String, default=generate_uuid)
    is_deleted = Column(Boolean, nullable=False, default=False)
    source = Column(Enum(RegisterSource), default=RegisterSource.Web, nullable=False)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    unit = Column(String, nullable=False, default="metric")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    timezone = Column(
        String, nullable=False, default="Asia/Kolkata"
    )  # Fixed parentheses
    is_notification_enabled = Column(Boolean, default=False)  # Fixed parentheses


@event.listens_for(User, "after_insert")
def user_after_insert(mapper, connection, target):
    if setting.ENVIRONMENT != "dev" and target.role == 1:
        dispatch(Events.NEW_FARMER_ADDED.value, {"company_id": target.company_id})


class Farm(Base):
    __tablename__ = "farm"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    geometry = Column(Geometry("POLYGON"))
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    bbox = Column(JSON, nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)
    area = Column(
        Float,
        Computed(
            "((ST_Area(ST_setSRID(geometry, 4326)::geography)) * 0.0002471054)", True
        ),
    )
    center = Column(Geometry("POINT"), Computed("(ST_Centroid(geometry))", True))
    region = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    expiry_date = Column(DateTime, nullable=True)


@event.listens_for(Farm, "after_insert")
def farm_after_insert(mapper, connection, target):
    if setting.ENVIRONMENT != "dev":
        dispatch(
            Events.NEW_FARM_ADDED.value,
            {
                "company_id": target.company_id,
                "area": target.area,
                "is_paid": target.is_paid,
            },
        )


class Crop(Base):
    __tablename__ = "crop"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    harvesting_days = Column(Integer, nullable=True)
    yield_value = Column(Float)
    yield_unit = Column(String)
    yield_per = Column(String)
    crop_from = Column(String)
    germination = Column(Integer)
    vegetative_growth = Column(Integer)
    flowering = Column(Integer)
    seedling = Column(Integer)
    fruiting = Column(Integer)
    maturity = Column(Integer)
    harvesting = Column(Integer)
    color = Column(String, default="#000000")


class Disease(Base):
    __tablename__ = "disease"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    symptoms = Column(String, nullable=False)
    causes = Column(String, nullable=True)
    organic_control = Column(String, nullable=True)
    chemical_control = Column(String, nullable=True)
    preventive_measures = Column(String, nullable=True)
    pre = Column(String, nullable=True)
    folder_name = Column(String, nullable=True)
    file_format = Column(String, nullable=True)
    class_name = Column(String, nullable=True)
    crop_id = Column(String, ForeignKey("crop.id"), nullable=True)
    image1 = Column(String, nullable=True)
    image2 = Column(String, nullable=True)
    image3 = Column(String, nullable=True)
    image4 = Column(String, nullable=True)
    image5 = Column(String, nullable=True)
    image6 = Column(String, nullable=True)
    image7 = Column(String, nullable=True)
    image8 = Column(String, nullable=True)
    image9 = Column(String, nullable=True)
    image10 = Column(String, nullable=True)
    image11 = Column(String, nullable=True)
    image12 = Column(String, nullable=True)
    image13 = Column(String, nullable=True)
    image14 = Column(String, nullable=True)
    image15 = Column(String, nullable=True)
    image16 = Column(String, nullable=True)
    image17 = Column(String, nullable=True)
    image18 = Column(String, nullable=True)
    image19 = Column(String, nullable=True)
    image20 = Column(String, nullable=True)
    image21 = Column(String, nullable=True)
    image22 = Column(String, nullable=True)
    image23 = Column(String, nullable=True)
    image24 = Column(String, nullable=True)
    image25 = Column(String, nullable=True)
    image26 = Column(String, nullable=True)
    image27 = Column(String, nullable=True)
    image28 = Column(String, nullable=True)
    image29 = Column(String, nullable=True)
    image30 = Column(String, nullable=True)
    image31 = Column(String, nullable=True)
    image32 = Column(String, nullable=True)
    image33 = Column(String, nullable=True)
    image34 = Column(String, nullable=True)
    image35 = Column(String, nullable=True)
    image36 = Column(String, nullable=True)
    image37 = Column(String, nullable=True)
    image38 = Column(String, nullable=True)
    image39 = Column(String, nullable=True)
    image40 = Column(String, nullable=True)
    image41 = Column(String, nullable=True)
    image42 = Column(String, nullable=True)
    image43 = Column(String, nullable=True)
    image44 = Column(String, nullable=True)
    image45 = Column(String, nullable=True)
    image46 = Column(String, nullable=True)
    image47 = Column(String, nullable=True)
    image48 = Column(String, nullable=True)
    image49 = Column(String, nullable=True)
    image50 = Column(String, nullable=True)
    image51 = Column(String, nullable=True)
    image52 = Column(String, nullable=True)
    image53 = Column(String, nullable=True)
    image54 = Column(String, nullable=True)
    image55 = Column(String, nullable=True)
    image56 = Column(String, nullable=True)
    image57 = Column(String, nullable=True)
    image58 = Column(String, nullable=True)
    image59 = Column(String, nullable=True)


class Satellite(Base):
    __tablename__ = "satellite"

    name = Column(String, primary_key=True)
    region_url = Column(String, nullable=False)
    satellite = Column(String, nullable=False)
    catalogue = Column(Boolean, default=True)
    cloud_cover = Column(Boolean, default=False, nullable=False)


class Indice(Base):
    __tablename__ = "indice"

    name = Column(String, primary_key=True, nullable=False)
    evalscript = Column(String, nullable=False)
    satellite = Column(
        String, ForeignKey("satellite.name"), primary_key=True, nullable=False
    )
    statistical_evalscript = Column(String, nullable=True)
    category = Column(String, nullable=True, default="all")
    rank = Column(Integer, nullable=True)
    description = Column(String())
    source = Column(String())
    alias = Column(String)
    legend = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class Advisory(Base):
    __tablename__ = "advisory"

    id = Column(String, primary_key=True, default=generate_uuid)
    crop = Column(String, ForeignKey("crop.id"), nullable=False)
    type = Column(String)
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_uv = Column(Float)
    max_uv = Column(Float)
    min_wind = Column(Float)
    max_wind = Column(Float)
    min_rainfall = Column(Float)
    max_rainfall = Column(Float)
    min_soilmoisture = Column(Float)
    max_soilmoisture = Column(Float)
    humidity_min = Column(Float)
    humidity_max = Column(Float)
    flag = Column(String)
    advisory_title = Column(String)
    advisory_desc = Column(String)
    stage_growth = Column(String)


class FarmCrop(Base):
    __tablename__ = "farm_crop"

    id = Column(String, primary_key=True, default=generate_uuid)
    farm_id = Column(String, ForeignKey("farm.id"), nullable=False)
    crop_id = Column(String, ForeignKey("crop.id"), nullable=False)
    sowing_date = Column(DATE, nullable=False)
    harvesting_date = Column(DATE)
    maturity = Column(String, nullable=True)
    irrigation_type = Column(String, nullable=True)
    tillage_type = Column(String, nullable=True)
    target_yield = Column(Float, default=0)
    actual_yield = Column(Float, default=0)
    season = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)


@event.listens_for(FarmCrop, "after_insert")
def farm_crop_after_insert(mapper, connection, target):
    if setting.ENVIRONMENT != "dev":
        dispatch(
            Events.FARM_CROP_ADDED.value,
            {"farm_id": target.farm_id},
        )


@event.listens_for(FarmCrop, "after_update")
def farm_crop_after_update(mapper, connection, target):
    if setting.ENVIRONMENT != "dev":
        dispatch(
            Events.FARM_CROP_ADDED.value,
            {"farm_id": target.farm_id},
        )


class CropStage(Base):
    __tablename__ = "crop_stages"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String, ForeignKey("crop.id"), nullable=False)
    stages = Column(String, nullable=True)
    days = Column(Float, nullable=False)
    image = Column(String, nullable=True)
    title = Column(String, nullable=False)
    tasks = Column(String, nullable=True)


class CalendarData(Base):
    __tablename__ = "calendar_data"

    id = Column(Integer, primary_key=True, index=True)
    farm = Column(String, ForeignKey("farm.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)


class Scouting(Base):
    __tablename__ = "scoutings"

    id = Column(Integer, primary_key=True, index=True)
    farm = Column(String, ForeignKey("farm.id"), nullable=False)
    geometry = Column(Geometry("POINT"), nullable=False)
    note_type = Column(String, nullable=False)
    comments = Column(String, nullable=True)
    attachments = Column(ARRAY(String), nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    scouting_date = Column(DateTime, nullable=True)
    status = Column(String, default=ScoutingStatus.open, nullable=False)
    ground_notes = Column(String, nullable=True)
    amount = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=True)


@event.listens_for(Scouting, "after_insert")
def scouting_after_insert(mapper, connection, target):
    if setting.ENVIRONMENT != "dev":
        dispatch(Events.NEW_SCOUTING_ADDED.value)


class States(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    geom = Column(Geometry("MULTIPOLYGON"), nullable=False)
    name = Column(String, nullable=True)
    admin = Column(String, nullable=True)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    source = Column(Enum(ContactSource), default=ContactSource.Web, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    feedback = Column(String, nullable=False)


class Fertilizer(Base):
    __tablename__ = "fertilizers"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String, ForeignKey("crop.id"), nullable=False)
    urea = Column(Float, nullable=False)
    ssp = Column(Float, nullable=False)
    mop = Column(Float, nullable=False)
    dap = Column(Float, nullable=False)


class CropGuide(Base):
    __tablename__ = "crop_guide"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    link = Column(String, nullable=False)
    image_url = Column(String, nullable=False)


class Market(Base):
    __tablename__ = "market"

    state = Column(String, primary_key=True)
    district = Column(String, primary_key=True)
    market = Column(String, primary_key=True)
    commodity = Column(String, primary_key=True)
    variety = Column(String, primary_key=True)
    grade = Column(String, primary_key=True)
    arrival_date = Column(DATE, nullable=False, primary_key=True)
    min_price = Column(Float, primary_key=True)
    max_price = Column(Float, primary_key=True)
    modal_price = Column(Float, primary_key=True)
    updated_date = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)


class FarmDelineation(Base):
    __tablename__ = "farm_delineation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    old_id = Column(String)
    seeded_area = Column(Float)
    area = Column(Float)
    stileid = Column(String)
    dates = Column(ARRAY(DATE))
    country = Column(String)
    version = Column(String)
    cluids = Column(ARRAY(String))
    flatness = Column(Float)
    perimeter = Column(Float)
    confidence = Column(Float)
    state = Column(String)
    json = Column(JSON)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Statistic(Base):
    __tablename__ = "statistic"

    id = Column(Integer, primary_key=True, index=True)
    farmers_count = Column(Integer, nullable=False, default=0)
    total_farms_mapped = Column(Integer, nullable=False, default=0)
    active_users = Column(Integer, nullable=False, default=0)
    non_active_users = Column(Integer, nullable=False, default=0)
    paid_farms = Column(Integer, nullable=False, default=0)
    non_paid_farms = Column(Integer, nullable=False, default=0)
    enterprise_users = Column(Integer, nullable=False, default=0)
    api_keys = Column(Integer, nullable=False, default=0)
    scouting_total = Column(Integer, nullable=False, default=0)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )


class EnterpriseStas(Base):
    __tablename__ = "enterprise_stats"

    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("companies.id"))
    total_farmers = Column(Integer, nullable=False, default=0)
    total_farms = Column(Integer, nullable=False, default=0)
    total_area = Column(Float, nullable=False, default=0)
    total_paid_farms = Column(Integer, nullable=False, default=0)
    total_unpaid_farms = Column(Integer, nullable=False, default=0)
    crop_wise = Column(JSON, nullable=True)


class CropGrowthStageAdvisory(Base):
    __tablename__ = "crop_growth_stage_advisories"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String, ForeignKey("crop.id"))
    stage = Column(String, nullable=True, default="")
    advisory = Column(String, nullable=True, default="")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, default=generate_uuid, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    farm_ids = Column(ARRAY(String))
    status = Column(String)
    service = Column(String)
    payment_request = Column(JSON)
    payment_response = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class ScheduleCall(Base):
    __tablename__ = "schedule_calls"

    id = Column(Integer, primary_key=True, index=True)
    how_to_contact = Column(
        Enum(HowToContact), default=HowToContact.whatsapp, nullable=False
    )
    date_time = Column(DateTime)
    topic = Column(Enum(Topic), default=Topic.harvesting, nullable=False)
    message = Column(String)
    type_of_expert = Column(
        Enum(TypeOfExpert), default=TypeOfExpert.local, nullable=False
    )


class PlanetCollection(Base):
    __tablename__ = "planet_collections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(String, nullable=False, default="")
    collection_id = Column(String, nullable=False, default="")
    service_id = Column(String, nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __init__(self, farm_id, collection_id, service_id):
        self.farm_id = farm_id
        self.collection_id = collection_id
        self.service_id = service_id


class Resellers(Base):
    __tablename__ = "resellers"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    password = Column(String, nullable=False)
    gst_number = Column(String, nullable=True)
    ref_code = Column(String, nullable=True)
    revenue = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    activated_at = Column(DateTime, nullable=True)
    apikey = Column(String, nullable=False, default=uuid.uuid4())


class UserReferral(Base):
    __tablename__ = "user_referral"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ref_code = Column(String, ForeignKey("resellers.ref_code"))
    registered_at = Column(DateTime, server_default=func.now(), nullable=False)


class LoginLogs(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, index=True)
    ph = Column(Integer, nullable=True)
    email = Column(String, nullable=True)
    apikey = Column(String, nullable=False)
    role = Column(Integer, nullable=False)
    source = Column(Enum(LogSource), default=LogSource.web, nullable=False)
    datetime = Column(DateTime, server_default=func.now(), nullable=False)


class InvitedUsers(Base):
    __tablename__ = "invited_users"
    id = Column(Integer, primary_key=True, index=True)
    ref_code = Column(String, ForeignKey("resellers.ref_code"))
    name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    paid_status = Column(Boolean, nullable=False, default=False)
    farm_size = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True, default=func.now())
    accepted_at = Column(DateTime, nullable=True)


class DisplayPhoto(Base):
    __tablename__ = "display_photo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())
