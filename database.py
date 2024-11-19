from sqlalchemy import create_engine
from sqlalchemy import URL
from config import CONFIG

url_object = URL.create(
    "postgresql",
    username=CONFIG["DB_USERNAME"],
    password=CONFIG["DB_PASSWORD"],
    host=CONFIG["DB_HOST"],
    database=CONFIG["DB_NAME"],
    port=5432,
)
DB_ENGINE = create_engine(url_object)

# New database connection for chat database
chat_url_object = URL.create(
    "postgresql",
    username=CONFIG["DB_USERNAME"],
    password=CONFIG["CHAT_DATABASE_PASSWORD"],
    host=CONFIG["DB_HOST"],
    database=CONFIG["CHAT_DATABASE_NAME"],
    port=5432,
)
CHAT_DB_ENGINE = create_engine(chat_url_object)


