from flask import Blueprint, request, jsonify
from app.services.gemini_service import gemini_service

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.post("/risk-assessment")
def risk_assessment():
    data = request.get_json(silent=True) or {}
    patient_id = data.get("patient_id", "")
    adherence_data = data.get("adherence_data", {})
    chat_history = data.get("chat_history", [])

    result = gemini_service.assess_risk(patient_id, adherence_data, chat_history)
    return jsonify(result)


@analytics_bp.post("/sentiment")
def sentiment():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "message is required"}), 400

    return jsonify(gemini_service.analyze_sentiment(message))
