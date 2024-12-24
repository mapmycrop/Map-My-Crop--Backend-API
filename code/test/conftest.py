from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from main import app
from config import setting
from db import Base, get_db
from models import Role, User, Company, Farm, Fertilizer, Crop, FarmCrop
from utils.password import secure_pwd

SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.db_usr}:{setting.db_pwd}@{setting.db_host}:{setting.db_port}/{setting.db_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture()
def company(session):
    db = session

    role = {"id": 2, "name": "Company", "description": "Admin of Company"}

    new_role = Role(**role)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    company = {
        "email": "company@test.com",
        "password": secure_pwd("password"),
        "name": "company",
        "site": "company.com",
        "country": "India",
        "role": 2,
    }

    new_company = Company(**company)

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


@pytest.fixture
def superadmin(session, company):
    db = session

    role = {
        "id": 3,
        "name": "Super Admin",
        "description": "Role of super admin for MMC",
    }

    db.add(Role(**role))
    db.commit()

    user = {
        "email": "suerpadmin@test.com",
        "ph": "1234567890",
        "password": secure_pwd("password"),
        "is_active": True,
        "country_code": "91",
        "company_id": company.id,
        "role": 3,
    }

    admin = User(**user)

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


@pytest.fixture
def farmer(session, company):
    db = session

    role = {"id": 1, "name": "Farmer", "description": "User who can add farms"}

    db.add(Role(**role))
    db.commit()

    user = {
        "email": "farmer@test.com",
        "ph": "1234567890",
        "password": secure_pwd("password"),
        "country_code": "91",
        "company_id": company.id,
        "role": 1,
        "is_active": True,
    }

    new_user = User(**user)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@pytest.fixture()
def fertilizer(session, crop):
    payload = {
        "crop_id": crop.id,
        "urea": 109,
        "ssp": 312,
        "mop": 42,
        "dap": 0,
    }

    db = session

    fertilizer = Fertilizer(**payload)

    db.add(fertilizer)
    db.commit()
    db.refresh(fertilizer)

    return fertilizer


@pytest.fixture
def crop(session):
    payload = {
        "name": "Bean",
        "description": "Bean",
        "yield_value": 1,
        "yield_unit": 1,
        "yield_per": 1,
    }

    db = session

    crop = Crop(**payload)

    db.add(crop)
    db.commit()
    db.refresh(crop)

    return crop


@pytest.fixture
def farm(session, farmer):
    farm = {
        "user_id": farmer.id,
        "company_id": farmer.company_id,
        "name": "farm",
        "description": "farm description",
        "geometry": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
        "bbox": "",
        "country": "91",
        "state": "VA",
    }

    db = session

    new_farm = Farm(**farm)

    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    return new_farm


@pytest.fixture
def farm_crop(session, farm, crop):
    payload = {
        "farm_id": farm.id,
        "crop_id": crop.id,
        "sowing_date": date.today().strftime("%Y-%m-%d"),
        "harvesting_date": date.today().strftime("%Y-%m-%d"),
        "season": 1,
    }

    db = session

    farm_crop = FarmCrop(**payload)

    db.add(farm_crop)
    db.commit()
    db.refresh(farm_crop)

    return farm_crop
