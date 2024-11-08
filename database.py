from sqlalchemy import create_engine
from sqlalchemy import URL
import os

# TODO fill data from .env
url_object = URL.create(
    "postgresql",
    username=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    port=5432,
)
DB_ENGINE = create_engine(url_object)