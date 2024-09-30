import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_VARS = {"_frontend_url": os.getenv("FRONTEND_URL")}
DB = {
    "provider": os.getenv("POSTGRES_PROVIDER"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DB_NAME"),
    "port": os.getenv("POSTGRES_PORT"),
}
DS = {
    "baserow": {"type": "http-connector", "url": os.getenv("BASEROW_CONNECTOR_URL")},
    "sendgrid": {"type": "http-connector", "url": os.getenv("SENDGRID_CONNECTOR_URL")},
    "pdf": {"type": "http-connector", "url": os.getenv("PDF_CONNECTOR_URL")},
}
BUGSNAG = {"api_key": os.getenv("BUGSNAG")}
