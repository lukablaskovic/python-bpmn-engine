import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_VARS = {"_frontend_url": os.getenv("FRONTEND_URL")}
DB = {
    "provider": os.getenv("PROVIDER"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "host": os.getenv("HOST"),
    "database": os.getenv("DATABASE"),
}
DS = {
    "baserow": {"type": "http-connector", "url": os.getenv("BASEROW")},
    "sendgrid": {"type": "http-connector", "url": os.getenv("SENDGRID")},
    "pdf": {"type": "http-connector", "url": os.getenv("PDF")},
}
BUGSNAG = {"api_key": os.getenv("BUGSNAG")}
