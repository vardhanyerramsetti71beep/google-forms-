"""
create_db.py
Creates the MySQL database and tables directly from the project folder.
Uses SQLAlchemy ORM and Python - NO manual SQL commands needed.
"""

import os
import sys
import getpass
import pymysql
from dotenv import load_dotenv, set_key

# Load environment configuration
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(ENV_FILE)

def get_config():
    return {
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "database": os.getenv("MYSQL_DB", "google_form_db"),
    }

def connect_mysql_server(config):
    """Connects to the MySQL server (without selecting a database)."""
    return pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        port=config["port"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def setup_mysql():
    print("=" * 65)
    print("  MySQL Database Setup (Run from Project Folder)  ")
    print("  Creates Database & Tables without Manual SQL Commands  ")
    print("=" * 65)

    config = get_config()
    conn = None

    # Step 1: Try connecting with current credentials from .env
    print(f"Connecting to MySQL server at {config['host']}:{config['port']} as '{config['user']}'...")
    try:
        conn = connect_mysql_server(config)
    except pymysql.err.OperationalError as e:
        # If access is denied (code 1045), prompt for password interactively if running in a terminal
        if e.args[0] == 1045:
            print("\n[!] Access denied. Your MySQL password in .env might be missing or incorrect.")
            if sys.stdin.isatty():
                entered_pwd = getpass.getpass(f"Enter MySQL password for user '{config['user']}': ")
                config["password"] = entered_pwd
                try:
                    conn = connect_mysql_server(config)
                    # Save working password into .env
                    set_key(ENV_FILE, "MYSQL_PASSWORD", entered_pwd)
                    print("✔ Password verified and saved to .env!")
                except Exception as ex:
                    print(f"\n❌ Connection failed: {ex}")
                    return False
            else:
                print(f"\nPlease open the '.env' file in this folder and update:")
                print(f"  MYSQL_PASSWORD=your_actual_mysql_password")
                print("Then run 'python create_db.py' again.")
                return False
        else:
            print(f"\n❌ Could not connect to MySQL server: {e}")
            print("Please ensure the MySQL service is running on your machine.")
            return False

    # Step 2: Create MySQL database if it doesn't exist
    try:
        db_name = config["database"]
        with conn.cursor() as cursor:
            # Check if database already exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        conn.close()
        print(f"✔ MySQL database '{db_name}' created / verified successfully!")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

    # Step 3: Use Flask-SQLAlchemy ORM to generate all tables (No SQL commands needed!)
    try:
        print("Creating tables using SQLAlchemy ORM (models.py)...")
        # Reload environment variables for Flask app
        os.environ["MYSQL_PASSWORD"] = config["password"]
        
        from app import app
        from models import db

        with app.app_context():
            # db.create_all() creates tables from Python model classes
            db.create_all()
            print("✔ Table 'form_responses' generated successfully from Python ORM!")

        print("\n🎉 SUCCESS: Database and tables are ready!")
        print("You can now start the application with: python app.py")
        print("=" * 65)
        return True

    except Exception as e:
        print(f"❌ Error creating tables via ORM: {e}")
        return False

if __name__ == "__main__":
    setup_mysql()
