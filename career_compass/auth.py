from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from career_compass.models import User, db
from career_compass.utils import validate_login_data, validate_registration_data

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    errors = validate_registration_data(full_name, email, password, confirm_password)
    if errors:
        return jsonify({"errors": errors}), 400

    user = User(full_name=full_name, email=email, role="student", created_at=datetime.utcnow())
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": {"email": "An account with this email already exists."}}), 400

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Registered successfully.", "token": token, "user": user.serialize()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    errors = validate_login_data(email, password)
    if errors:
        return jsonify({"errors": errors}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"errors": {"authentication": "Incorrect email or password."}}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Login successful.", "token": token, "user": user.serialize()}), 200


@auth_bp.route("/profile", methods=["GET"])
def profile():
    token = request.headers.get("Authorization", "")
    if not token:
        return jsonify({"user": None}), 401
    return jsonify({"message": "Token received."}), 200
