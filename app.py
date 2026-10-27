import csv
import io
import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, Response, send_from_directory

from config import (
    SQLALCHEMY_DATABASE_URI, SECRET_KEY,
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,
    IS_VERCEL, DB_TYPE
)
from models import db, FormResponse

# Initialize Flask App with absolute paths for serverless compatibility
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = SECRET_KEY

# Configure SQLAlchemy with target database URI
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Bind SQLAlchemy to Flask App
db.init_app(app)

def auto_init_database():
    """
    Creates the database and tables from Python without manual SQL commands.
    Automatically handles local MySQL, cloud databases, and serverless SQLite.
    """
    try:
        # Step 1: If MySQL is targeted and not in serverless localhost fallback, ensure database exists
        if SQLALCHEMY_DATABASE_URI.startswith("mysql") and not (IS_VERCEL and MYSQL_HOST in ("localhost", "127.0.0.1")):
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                port=int(MYSQL_PORT)
            )
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
            conn.commit()
            conn.close()

        # Step 2: Use Flask-SQLAlchemy ORM to generate all tables (no SQL needed!)
        with app.app_context():
            db.create_all()
            print(f"[OK] Database ({DB_TYPE}) & Tables are verified and ready.")
    except Exception as err:
        print(f"\n[Note] Database initialization notice: {err}")
        print("Please verify connection settings in '.env' or environment variables.\n")

# Run auto initialization at startup
auto_init_database()

@app.before_request
def ensure_tables_exist():
    """Ensures tables are present on fresh serverless worker invocations."""
    if not getattr(app, "_tables_created", False):
        try:
            db.create_all()
            app._tables_created = True
        except Exception:
            pass

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Fallback static asset router for serverless platforms."""
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)

@app.route("/")
def index():
    """Renders the Google Form submission page."""
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    """Handles form submission and saves data into database using SQLAlchemy ORM (no SQL commands)."""
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    gender = request.form.get("gender", "").strip()
    
    # Checkbox inputs: multiple selections are returned as a list
    topics_list = request.form.getlist("topics")
    topics = ", ".join(topics_list) if topics_list else "None"
    
    experience_level = request.form.get("experience_level", "").strip()
    rating_val = request.form.get("rating", "5")
    feedback = request.form.get("feedback", "").strip()

    # Basic server-side validation
    if not full_name or not email or not gender or not experience_level:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("index"))

    try:
        rating = int(rating_val)
    except ValueError:
        rating = 5

    try:
        # Create ORM object instance - No manual SQL INSERT statement!
        new_entry = FormResponse(
            full_name=full_name,
            email=email,
            gender=gender,
            topics=topics,
            experience_level=experience_level,
            rating=rating,
            feedback=feedback or "N/A"
        )
        
        # Persist to database via ORM session
        db.session.add(new_entry)
        db.session.commit()
        
        return redirect(url_for("success"))

    except Exception as err:
        db.session.rollback()
        flash(f"Database error: {str(err)}", "error")
        return redirect(url_for("index"))

@app.route("/success")
def success():
    """Renders the Google Forms submission confirmation page."""
    return render_template("success.html")

@app.route("/responses")
def view_responses():
    """Displays all responses stored in database using ORM query (no manual SQL SELECT query)."""
    try:
        # Query through ORM - No raw SQL SELECT query!
        responses = FormResponse.query.order_by(FormResponse.submitted_at.desc()).all()
        return render_template("responses.html", responses=responses, total=len(responses))
    except Exception as err:
        flash(f"Could not load responses: {str(err)}", "error")
        return render_template("responses.html", responses=[], total=0)

@app.route("/export-csv")
def export_csv():
    """Exports all stored responses into a downloadable CSV file."""
    try:
        responses = FormResponse.query.order_by(FormResponse.submitted_at.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "ID", "Full Name", "Email", "Gender", 
            "Interested Topics", "Experience Level", 
            "Rating (1-5)", "Feedback", "Submitted At"
        ])
        
        for r in responses:
            writer.writerow([
                r.id, r.full_name, r.email, r.gender,
                r.topics, r.experience_level, r.rating,
                r.feedback, r.submitted_at
            ])
            
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=form_responses.csv"}
        )
    except Exception as err:
        flash(f"Error exporting CSV: {str(err)}", "error")
        return redirect(url_for("view_responses"))

if __name__ == "__main__":
    print("Starting Flask Google Form server...")
    print("Google Form: http://127.0.0.1:5000")
    print("Responses: http://127.0.0.1:5000/responses")
    app.run(debug=True, port=5000)
