from sqlalchemy import create_engine
from sqlalchemy import URL

# TODO fill data from .env
url_object = URL.create(
    "postgresql+psycopg2",
    username="",
    password="",
    host="",
    database="",
    port=5432
)
engine = create_engine(url_object, echo=True)