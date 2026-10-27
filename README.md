# Google Form with Flask & MySQL (No Manual SQL Commands)

A Google Forms replica built with **Flask**, **MySQL**, and **Flask-SQLAlchemy ORM**.

This project creates the MySQL database and table schema **entirely from Python inside the project folder**—without running manual SQL commands (`CREATE DATABASE`, `CREATE TABLE`, `INSERT INTO`, `SELECT`).

---

## 📁 Project Structure

```text
flask-google-form/
│
├── .env                    # MySQL credentials (User, Password, Host, Port, DB)
├── config.py               # Database URI configuration with PyMySQL
├── models.py               # Python ORM model (FormResponse)
├── create_db.py            # Script to create MySQL database & tables from Python
├── app.py                  # Flask backend (Routes, ORM insert, ORM queries, CSV export)
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
│
├── static/
│   └── css/
│       └── style.css       # Google Forms Material Design styling
│
└── templates/
    ├── form.html           # Google Form interface
    ├── success.html        # "Response recorded" confirmation
    └── responses.html      # MySQL responses dashboard & CSV export
```

---

## ⚙️ 1. Configure MySQL Credentials (`.env`)

Open the `.env` file in the project folder and update your MySQL password:

```env
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=google_form_db
```

---

## 🛠️ 2. Create MySQL Database & Tables (Without SQL Commands)

Run this single command from your terminal inside the project folder:

```powershell
cd d:\PROJECTS\flask-google-form
python create_db.py
```

### What this code does automatically:
1. Connects to your local MySQL server.
2. Checks if `google_form_db` exists; if not, creates it programmatically.
3. Calls SQLAlchemy's `db.create_all()` to inspect `models.py` and build the `form_responses` table automatically.

---

## 🚀 3. Start the Flask App

```powershell
python app.py
```

Open your browser:
- **Google Form:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **View MySQL Responses:** [http://127.0.0.1:5000/responses](http://127.0.0.1:5000/responses)
- **Export CSV:** [http://127.0.0.1:5000/export-csv](http://127.0.0.1:5000/export-csv)

---

## 🔍 How It Works Without SQL Commands

### Table Definition (Python Class in `models.py`)
```python
class FormResponse(db.Model):
    __tablename__ = "form_responses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    topics = db.Column(db.String(255))
    experience_level = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Table Creation (Python Call)
```python
db.create_all()  # Generates tables from the Python class above
```

### Inserting Data (Python ORM Session)
```python
new_entry = FormResponse(
    full_name="John Doe",
    email="john@example.com",
    gender="Male",
    topics="Python & Flask, SQL & Databases",
    experience_level="Intermediate",
    rating=5,
    feedback="Great form!"
)
db.session.add(new_entry)
db.session.commit()
```

### Retrieving Data (Python Query)
```python
responses = FormResponse.query.order_by(FormResponse.submitted_at.desc()).all()
```
