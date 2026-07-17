from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="student")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    resume_analyses = db.relationship("ResumeAnalysis", backref="user", lazy=True)
    chat_messages = db.relationship("ChatMessage", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class ResumeAnalysis(db.Model):
    __tablename__ = "resume_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    strengths = db.Column(db.Text, nullable=False)
    weaknesses = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "score": self.score,
            "strengths": self.strengths.split("||"),
            "weaknesses": self.weaknesses.split("||"),
            "recommendations": self.recommendations.split("||"),
            "created_at": self.created_at.isoformat(),
        }


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_question = db.Column(db.Text, nullable=False)
    assistant_reply = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "user_question": self.user_question,
            "assistant_reply": self.assistant_reply,
            "created_at": self.created_at.isoformat(),
        }
