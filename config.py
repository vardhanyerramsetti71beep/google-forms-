import os
import tempfile
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file inside project folder if present
load_dotenv()

# Detect if running in Vercel serverless environment
IS_VERCEL = os.getenv("VERCEL") == "1"

# 1. First Priority: Generic Cloud Database URL (Postgres, TiDB, Cloud MySQL, Supabase, Neon)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. MySQL Configuration
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "google_form_db")

if DATABASE_URL:
    # Standardize legacy postgres:// scheme to postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    DB_TYPE = "cloud"
elif IS_VERCEL and (not MYSQL_HOST or MYSQL_HOST in ("localhost", "127.0.0.1")):
    # In AWS Lambda / Vercel serverless, localhost MySQL is not running.
    # Seamlessly fallback to SQLite in the writable temp directory (/tmp in Linux Lambda).
    temp_db_path = os.path.join(tempfile.gettempdir(), "google_form.db").replace("\\", "/")
    # If the path starts with a slash (Linux/Unix), prepend sqlite:////, else sqlite:///
    if temp_db_path.startswith("/"):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{temp_db_path}"
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{temp_db_path}"
    DB_TYPE = "sqlite"
else:
    # MySQL connection string
    encoded_password = urllib.parse.quote_plus(MYSQL_PASSWORD)
    if encoded_password:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    DB_TYPE = "mysql"

SECRET_KEY = os.getenv("SECRET_KEY", "google-forms-flask-secret-key-12345")
