# Definesc modelele SQLAlchemy: User, Task, SMTPSettings.
# / I define the SQLAlchemy models: User, Task, SMTPSettings.
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    notification_email = db.Column(db.String(120), nullable=True)  # adresa pentru memento-uri / reminder address
    role = db.Column(db.String(20), default="user", nullable=False)  # 'user' sau 'admin' / 'user' or 'admin'
    preferred_lang = db.Column(db.String(5), default='ro', nullable=False)  # 'ro' sau 'en' / preferred email language
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    tasks = db.relationship("Task", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return (self.role or "") == "admin"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    due_at = db.Column(db.DateTime, nullable=True)
    remind_at = db.Column(db.DateTime, nullable=True)
    remind_email = db.Column(db.Boolean, default=False, nullable=False)
    reminder_sent_at = db.Column(db.DateTime, nullable=True)
    brevo_message_id = db.Column(db.String(64), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)   # imagine unică (legacy) / single image legacy
    image_filenames = db.Column(db.Text, nullable=True)         # JSON list de imagini (max 5) / JSON list up to 5 images
    notes = db.Column(db.Text, nullable=True)  # note suplimentare ale sarcinii / extra notes for the task

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class SMTPSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_host = db.Column(db.String(255), nullable=True)  # ex: smtp-relay.brevo.com
    smtp_port = db.Column(db.Integer, nullable=True)  # ex: 587 (TLS)
    smtp_username = db.Column(db.String(255), nullable=True)  # email de autentificare / login email
    smtp_password = db.Column(db.String(255), nullable=True)  # cheie SMTP / SMTP key or password
    sender_email = db.Column(db.String(120), nullable=True)
    sender_name = db.Column(db.String(80), nullable=True)
    test_email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)