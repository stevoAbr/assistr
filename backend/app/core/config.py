from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

# Any config variable that does not have a default MUST be provided a value in the backend/.env file or an error will be thrown

config = Config(".env")

# project + app

PROJECT_NAME = "APPAPI"
VERSION = "0.0.1"
API_PREFIX = "/api"


# JWT
SECRET_KEY = config("SECRET_KEY", cast=Secret)  # no default, must be set in .env
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=7 * 24 * 60  # one week
)

# JWT
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")

JWT_AUDIENCE = config(
    "JWT_AUDIENCE", cast=str, default="DEFAULTROUTE"
)  # TODO: add auth route

JWT_TOKEN_PREFIX = config("JWT_TOKEN_PREFIX", cast=str, default="Bearer")

# DB
POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)
DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}",
)


DB_MIN_CONNECTIONS = config("DB_MIN_CONNECTIONS", cast=int, default=2)
DB_MAX_CONNECTIONS = config("DB_MAX_CONNECTIONS", cast=int, default=10)
