from pydantic import BaseModel, EmailStr, constr, validator, Json, Field
from datetime import datetime, date
from typing import Optional, Literal, List, Dict
import re

from variables import HowToContact, Topic, TypeOfExpert


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    api_key: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None


class SocialGoogleToken(BaseModel):
    token: str


class PostCompany(BaseModel):
    email: str
    password: str
    name: str
    site: str
    country: str
    ph: Optional[str]
    unit: Literal["metric", "imperial"]

    class Config:
        orm_mode = True


class UpdateUser(BaseModel):
    api_key: str
    email: str
    password: str
    is_active: bool
    company_id: int
    name: str

    class Config:
        orm_mode = True


class GetCompany(PostCompany):
    id: int
    apikey: str


class GetUser(BaseModel):
    email: Optional[EmailStr] = None
    ph: Optional[str] = None
    country_code: Optional[constr(min_length=1, max_length=4, regex=r"^\d{1,4}$")]
    name: str
    company_id: int
    source: Optional[Literal["Web", "Mobile"]]
    unit: Optional[Literal["metric", "imperial"]]

    @validator("ph")
    def validate_phone_number(cls, v):
        if v and not re.match(r"^[0-9]{8,13}$", v):
            raise ValueError("Phone number must be between 8 and 13 digits")
        return v

    class Config:
        orm_mode = True
        use_enum_values = True


class UserSchema(GetUser):
    password: str

    class Config:
        orm_mode = True


class NormalUserForCompany(BaseModel):
    email: Optional[EmailStr] = None
    ph: Optional[str] = None
    is_active: Optional[bool] = False
    country_code: Optional[int] = 91
    created_at: Optional[datetime] = None
    apikey: str


class NormalUserForAdmin(BaseModel):
    email: Optional[EmailStr] = None
    ph: Optional[str] = None
    apikey: Optional[str] = None
    country_code: Optional[str] = None
    role: Optional[str] = None
    created_at: Optional[datetime] = None


class UuidOfUser(GetUser):
    apikey: str
    role: Optional[str] = None
    is_active: bool = True


class UserTokenSchema(BaseModel):
    token: str
    token_type: str = "Bearer"
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    apikey: str
    is_active: bool = False


class UserProfile(BaseModel):
    token: str
    token_type: str = "Bearer"
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    id: str
    name: Optional[str] = None
    api_key: str
    is_active: bool = False
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    unit: str
    timezone: str = "Asia/Kolkata"
    notification_active: bool = False


class UpdateProfile(BaseModel):
    phone: constr(regex="^[0-9]{7,13}$")  # type: ignore
    company_id: int


class CreateFarmPayload(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    name: str
    description: Optional[str] = ""
    geometry: str

    class Config:
        orm_mode = True


class GetFarm(BaseModel):
    id: str
    user_id: int
    company_id: int
    name: str
    description: Optional[str] = ""
    area: float
    country: str
    state: str
    is_paid: bool


class UpdateFarmPayload(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Crop(BaseModel):
    name: str
    description: Optional[str]
    yield_value: Optional[float] = None
    color: Optional[str]
    germination: Optional[int]
    vegetative_growth: Optional[int]
    flowering: Optional[int]
    seedling: Optional[int]
    fruiting: Optional[int]
    maturity: Optional[int]
    harvesting: Optional[int]
    crop_from: Optional[str]
    harvesting_days: Optional[int]
    yield_unit: Optional[str] = None
    yield_per: Optional[str] = None


class PostCrop(Crop):
    class Config:
        orm_mode = True


class GetCrop(Crop):
    id: str

    class Config:
        orm_mode = True


class cropDiseaseResult(BaseModel):
    primary_disease: str
    secondary_disease: list[str]
    potential_disease: str


class cropDiseaseDetection(BaseModel):
    crop_name: str
    result: cropDiseaseResult


class water_req_record(BaseModel):
    date: date
    crop_days: int
    stage: str
    coefficient: float
    area: float
    water_requirement: float


class DiseaseSchema(BaseModel):
    name: str
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    organic_control: Optional[str] = None
    chemical_control: Optional[str] = None
    preventive_measures: Optional[str] = None
    pre: Optional[str] = None
    folder_name: Optional[str] = None
    file_format: Optional[str] = None
    image1: Optional[str] = None
    image2: Optional[str] = None
    image3: Optional[str] = None
    image4: Optional[str] = None
    image5: Optional[str] = None
    image6: Optional[str] = None
    image7: Optional[str] = None
    image8: Optional[str] = None
    image9: Optional[str] = None
    image10: Optional[str] = None
    image11: Optional[str] = None
    image12: Optional[str] = None
    image13: Optional[str] = None
    image14: Optional[str] = None
    image15: Optional[str] = None
    image16: Optional[str] = None
    image17: Optional[str] = None
    image18: Optional[str] = None
    image19: Optional[str] = None
    image20: Optional[str] = None
    image21: Optional[str] = None
    image22: Optional[str] = None
    image23: Optional[str] = None
    image24: Optional[str] = None
    image25: Optional[str] = None
    image26: Optional[str] = None
    image27: Optional[str] = None
    image28: Optional[str] = None
    image29: Optional[str] = None
    image30: Optional[str] = None
    image31: Optional[str] = None
    image32: Optional[str] = None
    image33: Optional[str] = None
    image34: Optional[str] = None
    image35: Optional[str] = None
    image36: Optional[str] = None
    image37: Optional[str] = None
    image38: Optional[str] = None
    image39: Optional[str] = None
    image40: Optional[str] = None
    image41: Optional[str] = None
    image42: Optional[str] = None
    image43: Optional[str] = None
    image44: Optional[str] = None
    image45: Optional[str] = None
    image46: Optional[str] = None
    image47: Optional[str] = None
    image48: Optional[str] = None
    image49: Optional[str] = None
    image50: Optional[str] = None
    image51: Optional[str] = None
    image52: Optional[str] = None
    image53: Optional[str] = None
    image54: Optional[str] = None
    image55: Optional[str] = None
    image56: Optional[str] = None
    image57: Optional[str] = None
    image58: Optional[str] = None
    image59: Optional[str] = None

    class Config:
        orm_mode = True


class GetDisease(DiseaseSchema):
    id: int


class PostAdvisory(BaseModel):
    crop: str
    type: Optional[str] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_uv: Optional[float] = None
    max_uv: Optional[float] = None
    min_wind: Optional[float] = None
    max_wind: Optional[float] = None
    min_rainfall: Optional[float] = None
    max_rainfall: Optional[float] = None
    min_soilmoisture: Optional[float] = None
    max_soilmoisture: Optional[float] = None
    flag: Optional[str] = None
    stage_growth: Optional[str] = None
    advisory_title: Optional[str] = None
    advisory_desc: Optional[str] = None

    class Config:
        orm_mode = True


class GetAdvisory(PostAdvisory):
    id: str


class AdvisoryShowResponse(BaseModel):
    class AdvisoryItem(BaseModel):
        advisory_title: str
        advisory_desc: str
        flag: str

    humidity: Optional[List[AdvisoryItem]]
    temperature: Optional[List[AdvisoryItem]]
    wind: Optional[List[AdvisoryItem]]
    rainfall: Optional[List[AdvisoryItem]]
    soilmoisture: Optional[List[AdvisoryItem]]
    uv: Optional[List[AdvisoryItem]]


class NotificationPayload(BaseModel):
    farmers_api_key: List[str]
    message_title: str
    message_content: str
    message_type: Literal["SMS", "WHATSAPP", "EMAIL"]


class CreateFarmCropPayload(BaseModel):
    crop: str
    sowing_date: date
    harvesting_date: Optional[date] = None
    maturity: Optional[Literal["early", "mid", "late"]]
    irrigation_type: Optional[
        Literal[
            "center pivot",
            "drip",
            "horse end",
            "sprinkler",
            "micro",
            "canal",
            "borewell",
            "other",
        ]
    ]
    tillage_type: Optional[Literal["no till", "intense", "conservation"]]
    target_yield: Optional[float]
    actual_yield: Optional[float]
    season: int

    class Config:
        orm_mode = True


class StoreFarmCrop(CreateFarmCropPayload):
    farm_id: str
    crop_id: str


class CropStageSchema(BaseModel):
    crop: str
    stages: Optional[str]
    days: float
    image: Optional[str]
    title: str
    tasks: Optional[str]

    class Config:
        orm_mode = True


class CalendarData(BaseModel):
    farm: str
    title: Literal[
        "Tilage",
        "Planting",
        "Fertilization",
        "Spraying",
        "Harvesting",
        "Planned Cost",
        "Other",
    ]
    description: Optional[str]
    start_date: datetime
    end_date: datetime


class GetCalendarData(CalendarData):
    id: int

    class Config:
        orm_mode = True


class PostCalendarData(CalendarData):
    class Config:
        orm_mode = True


class Scouting(BaseModel):
    farm: str
    geometry: str
    title: str
    note_type: Literal[
        "Disease",
        "Pests",
        "Water logging",
        "Weeds",
        "Lodging",
        "Others",
        "Ground Visit",
        "Soil Moisture Readings",
        "Soil Temperature Readings",
        "Soil Sample Collection",
        "Physical Infections Inspections",
        "Fungal Attack",
        "Irrigation Issues",
    ]
    comments: Optional[str]
    attachments: Optional[List[str]]
    status: Literal["open", "in progress", "closed"]
    due_date: date
    scouting_date: date
    created_at: Optional[datetime]
    ground_notes: Optional[str]
    amount: int


class PostScouting(Scouting):
    class Config:
        orm_mode = True


class GetScouting(Scouting):
    id: int

    class Config:
        orm_mode = True


class PutScouting(BaseModel):
    title: Optional[str]
    geometry: Optional[str]
    note_type: Optional[
        Literal[
            "Disease",
            "Pests",
            "Water logging",
            "Weeds",
            "Lodging",
            "Others",
            "Ground Visit",
            "Soil Moisture Readings",
            "Soil Temperature Readings",
            "Soil Sample Collection",
            "Physical Infections Inspections",
            "Fungal Attack",
            "Irrigation Issues",
        ]
    ]
    comments: Optional[str]
    attachments: Optional[List[str]]
    status: Literal["open", "in progress", "closed"]
    due_date: Optional[date]
    scouting_date: Optional[date]
    ground_notes: Optional[str]
    amount: Optional[int]


class PostNotification(BaseModel):
    title: str
    description: str
    polygon: str

    @validator("*", pre=True)
    def blank_string(value, field):
        if value == "":
            return None

        return value


class PostContact(BaseModel):
    title: str
    message: str
    source: Literal["Web", "Mobile"]

    class Config:
        orm_mode = True

    @validator("*", pre=True)
    def blank_string(value, field):
        if value == "":
            return None

        return value


class GetContact(PostContact):
    id: int
    phone: Optional[str] = ""
    email: Optional[str] = ""
    created_at: datetime


class PostScheduleCall(BaseModel):
    how_to_contact: HowToContact
    date_time: datetime
    topic: Topic
    message: str
    type_of_expert: TypeOfExpert


class GetScheduleCall(PostScheduleCall):
    class Config:
        orm_mode = True


class SendOTPForUpdateProfilePayload(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex="^[0-9]{7,15}$")] = None
    api_key: Optional[bool] = None


class UpdateProfilePayload(BaseModel):
    name: Optional[str]
    country: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postcode: Optional[str]
    unit: Optional[Literal["metric", "imperial"]]
    timezone: Optional[str]
    is_notification_enabled: bool = False


class UpdateProfileEmailPayload(BaseModel):
    email: EmailStr


class UpdateProfilePhonePayload(BaseModel):
    phone: constr(regex="^[0-9]{7,15}$")


class UpdateProfilePasswordPayload(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str


class ResetPasswordSchema(BaseModel):
    new_password: str
    confirm_new_password: str


class PostFeedback(BaseModel):
    feedback: str

    @validator("*", pre=True)
    def blank_string(value, field):
        if value == "":
            return None

        return value


class GetFeedback(PostFeedback):
    id: int

    class Config:
        orm_mode = True


class PostFertilizer(BaseModel):
    crop_id: str
    urea: float
    ssp: float
    mop: float
    dap: float

    class Config:
        orm_mode = True


class GetFertilizer(PostFertilizer):
    id: int


class ResForFertilizer(BaseModel):
    crop: str
    urea: float
    ssp: float
    mop: float
    dap: float

    class Config:
        orm_mode = True


class CropGuide(BaseModel):
    name: str
    link: str
    image_url: str

    @validator("*", pre=True)
    def blank_string(value, field):
        if value == "":
            return None

        return value

    class Config:
        orm_mode = True


class SendOTPPayload(BaseModel):
    type: Literal["email", "phone"]
    phone: Optional[constr(regex="^[0-9]{7,15}$")]
    email: Optional[EmailStr]


class VerifyOTPPayload(SendOTPPayload):
    code: str


class UpdatePaymentStatus(BaseModel):
    api_keys: Optional[str] = ""
    payment_status: bool
    expiry_date: Optional[date]


class UpdatePaymentStatusResponse(BaseModel):
    updated_farms_count: int


class ResetPasswordWithOTPPayload(VerifyOTPPayload):
    password: str


class WeatherDayForecastResponse(BaseModel):
    temp: float
    pressure: float
    humidity: float
    wind_speed: float
    rain: float
    datetime: datetime


class GetCropGrowthStageAdvisory(BaseModel):
    stage: str
    advisory: str


class AddCashPayment(BaseModel):
    user_id: int
    farm_ids: List[str]
    status: Literal["Paid"]
    service: Literal["Cash"]
    payment_request: Dict

    class Config:
        orm_mode = True


class CropCalendarResponse(BaseModel):
    stages: Optional[str]
    days: int
    title: str
    tasks: Optional[str]


class AdminPaidFarmsResponse(BaseModel):
    farm_id: str
    apikey: str
    phone: Optional[constr(regex="^[0-9]{7,15}$")] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class AdminExpertRequestsResponse(BaseModel):
    how_to_contact: HowToContact
    date_time: datetime
    topic: Topic
    message: str
    type_of_expert: TypeOfExpert


class EnterpriseGetFarmersResponse(BaseModel):
    id: str
    apikey: str
    name: Optional[str]


class EnterpriseGetFarmersCountResponse(BaseModel):
    farmers_count: int


class EnterpriseGetFarmsCountResponse(BaseModel):
    farms_count: int


class EnterpriseGetTotalAreaResponse(BaseModel):
    total_area: float


class EnterpriseGetCropWiseResponse(BaseModel):
    crop_wise: dict


class ResellerLoginPayload(BaseModel):
    phone_number: constr(regex="^[0-9]{7,15}$")
    password: str


class ResellerStatusModifyInput(BaseModel):
    id: int
    active_status: bool


class ReferralInput(BaseModel):
    apikey: str
    ref_code: str


class ResellerInput(BaseModel):
    brand_name: str
    email: EmailStr
    name: str
    address: str
    phone_number: str
    gst_number: str
    password: str


class ResellerResetPassword(BaseModel):
    phone: constr(regex="^[0-9]{7,15}$")
    otp: str
    password: str


class ResellerUserInput(BaseModel):
    name: str
    mobile_number: constr(regex="^[0-9]{7,15}$")
    paid_status: bool
    farm_size: Optional[float]
    crop_type: str


class ResellerResponseModel(BaseModel):
    id: int
    brand_name: str
    email: str
    name: str
    address: str
    phone_number: str
    gst_number: str
    created_at: datetime
    is_active: bool
    apikey: str
    ref_code: str


class ResellerSummaryInfoModel(BaseModel):
    onboarded_today: int
    onboarded_month: int
    total_farm_size: float
    total_profit: float


class SatelliteResponseModel(BaseModel):
    name: str
    satellite: str
    indices: List[str]


class ResponseMessageModel(BaseModel):
    status: str
    message: str


class RequestUserInfo(BaseModel):
    type: Literal["email", "phone"]
    email: Optional[str]
    phone: Optional[str]
