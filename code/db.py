from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import setting


SQLALCHEMY_DATABASE_URL = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
    setting.db_usr, setting.db_pwd, setting.db_host, setting.db_port, setting.db_name
)


is_prod = setting.ENVIRONMENT == "prod"

pool_size = 75 if is_prod else 50
max_overflow = 25 if is_prod else 0

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=pool_size, max_overflow=max_overflow
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db.close()
        print("Database error", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Please try again later",
        )

    try:
        yield db
    finally:
        db.close()
