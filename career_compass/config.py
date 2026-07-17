import os


def _find_project_root():
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.isdir(os.path.join(current, "frontend")) and os.path.isdir(os.path.join(current, "backend")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(os.path.join(current, ".."))
        current = parent


PROJECT_ROOT = _find_project_root()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-default-please-change-123456")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        os.getenv("SECRET_KEY", SECRET_KEY)
    )
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(PROJECT_ROOT, 'career_compass.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = False
    CORS_HEADERS = "Content-Type"
