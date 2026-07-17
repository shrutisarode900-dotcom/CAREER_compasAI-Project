import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from career_compass.config import Config
from career_compass.models import db


def _find_project_root():
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.isdir(os.path.join(current, "frontend")) and os.path.isdir(os.path.join(current, "backend")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(os.path.join(current, ".."))
        current = parent


def create_app(test_config=None):
    project_root = _find_project_root()
    app = Flask(
        __name__,
        root_path=project_root,
        static_folder="frontend/static",
        template_folder="frontend/templates",
    )
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "production"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=4)

    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from career_compass.auth import auth_bp
    from career_compass.api import api_bp
    from career_compass.views import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "interest-cohort=()"
        return response

    with app.app_context():
        db.create_all()

    return app
