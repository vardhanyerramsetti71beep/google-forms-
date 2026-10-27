from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy ORM instance
db = SQLAlchemy()

class FormResponse(db.Model):
    """
    Python ORM Model representing the Google Form response table.
    SQLAlchemy translates this class into a MySQL table without writing any SQL commands.
    """
    __tablename__ = "form_responses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    topics = db.Column(db.String(255), nullable=True)
    experience_level = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Helper to convert model instance to dictionary."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "gender": self.gender,
            "topics": self.topics,
            "experience_level": self.experience_level,
            "rating": self.rating,
            "feedback": self.feedback,
            "submitted_at": self.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if self.submitted_at else ""
        }
