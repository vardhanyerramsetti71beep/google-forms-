import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file inside project folder
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "google_form_db")

# Safely URL-encode password in case it contains special characters (@, #, :, etc.)
encoded_password = urllib.parse.quote_plus(MYSQL_PASSWORD)

if encoded_password:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
else:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

SECRET_KEY = os.getenv("SECRET_KEY", "google-forms-flask-secret-key-12345")
