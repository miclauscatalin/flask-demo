from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    notification_email = db.Column(db.String(120), nullable=True)  # ex: user@example.com
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    tasks = db.relationship("Task", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    due_at = db.Column(db.DateTime, nullable=True)
    remind_at = db.Column(db.DateTime, nullable=True)
    remind_email = db.Column(db.Boolean, default=False, nullable=False)
    reminder_sent_at = db.Column(db.DateTime, nullable=True)
    brevo_message_id = db.Column(db.String(64), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class SMTPSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_host = db.Column(db.String(255), nullable=True)  # smtp-relay.brevo.com
    smtp_port = db.Column(db.Integer, nullable=True)  # 587
    smtp_username = db.Column(db.String(255), nullable=True)  # email
    smtp_password = db.Column(db.String(255), nullable=True)  # SMTP key
    sender_email = db.Column(db.String(120), nullable=True)
    sender_name = db.Column(db.String(80), nullable=True)
    test_email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)