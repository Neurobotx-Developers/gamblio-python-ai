from sqlalchemy import create_engine
from sqlalchemy import URL
from config import CONFIG

# TODO fill data from .env
url_object = URL.create(
    "postgresql",
    username=CONFIG["DB_USERNAME"],
    password=CONFIG["DB_PASSWORD"],
    host=CONFIG["DB_HOST"],
    database=CONFIG["DB_NAME"],
    port=5432,
)
DB_ENGINE = create_engine(url_object)
