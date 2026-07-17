from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from career_compass.models import ChatMessage, ResumeAnalysis, User, db
from career_compass.utils import analyze_resume_text, generate_chat_response

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/resume/analyze", methods=["POST"])
@jwt_required()
def analyze_resume():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    resume_text = payload.get("resume_text", "").strip()
    if not resume_text:
        return jsonify({"errors": {"resume_text": "Resume content is required."}}), 400

    result = analyze_resume_text(resume_text)
    analysis = ResumeAnalysis(
        user_id=user_id,
        text=resume_text,
        score=result["score"],
        strengths="||".join(result["strengths"]),
        weaknesses="||".join(result["weaknesses"]),
        recommendations="||".join(result["recommendations"]),
    )
    db.session.add(analysis)
    db.session.commit()

    return jsonify({"analysis": analysis.serialize()}), 200


@api_bp.route("/chat/ask", methods=["POST"])
@jwt_required()
def chat_ask():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    question = payload.get("question", "").strip()
    if not question:
        return jsonify({"errors": {"question": "Please ask a career question."}}), 400

    reply = generate_chat_response(question)
    chat_message = ChatMessage(user_id=user_id, user_question=question, assistant_reply=reply)
    db.session.add(chat_message)
    db.session.commit()

    return jsonify({"answer": reply}), 200


@api_bp.route("/admin/users", methods=["GET"])
@jwt_required()
def list_users():
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    if not current_user or current_user.role != "admin":
        return jsonify({"errors": {"authorization": "Admin access required."}}), 403

    users = [user.serialize() for user in User.query.order_by(User.created_at.desc()).all()]
    return jsonify({"users": users}), 200
