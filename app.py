import csv
import io
import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, Response

from config import (
    SQLALCHEMY_DATABASE_URI, SECRET_KEY,
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
)
from models import db, FormResponse

# Initialize Flask App
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configure SQLAlchemy with MySQL URI
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Bind SQLAlchemy to Flask App
db.init_app(app)

def auto_init_mysql():
    """
    Creates the MySQL database and tables from Python without typing SQL commands.
    Runs automatically when starting the Flask app.
    """
    try:
        # Step 1: Connect to MySQL server and ensure database exists
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
            print("✔ MySQL Database & Tables are verified and ready.")
    except Exception as err:
        print(f"\n[Note] Could not automatically initialize MySQL: {err}")
        print("Please set your MySQL password in '.env' or run: python create_db.py\n")

# Run auto initialization
auto_init_mysql()

@app.route("/")
def index():
    """Renders the Google Form submission page."""
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    """Handles form submission and saves data into MySQL using SQLAlchemy ORM (no SQL commands)."""
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
        
        # Persist to MySQL via ORM session
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
    """Displays all responses stored in MySQL using ORM query (no manual SQL SELECT query)."""
    try:
        # Query through ORM - No raw SQL SELECT query!
        responses = FormResponse.query.order_by(FormResponse.submitted_at.desc()).all()
        return render_template("responses.html", responses=responses, total=len(responses))
    except Exception as err:
        flash(f"Could not load responses from MySQL: {str(err)}", "error")
        return render_template("responses.html", responses=[], total=0)

@app.route("/export-csv")
def export_csv():
    """Exports all stored MySQL responses into a downloadable CSV file."""
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
    print("MySQL Responses: http://127.0.0.1:5000/responses")
    app.run(debug=True, port=5000)
