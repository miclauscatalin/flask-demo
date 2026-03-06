import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Cheie secretă — OBLIGATORIU setată în .env în producție
    # / Secret key — MUST be set in .env in production
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY nu este setat în .env! Generează unul cu: python -c \"import secrets; print(secrets.token_hex(32))\"")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASEDIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB limită upload / 8 MB upload size limit

    # Cookie-uri securizate / Secure session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Activez SECURE doar în producție (HTTPS) / I enable SECURE only in production (HTTPS)
    SESSION_COOKIE_SECURE   = os.getenv("FLASK_ENV") == "production"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE   = os.getenv("FLASK_ENV") == "production"