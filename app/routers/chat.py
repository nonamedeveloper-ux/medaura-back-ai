from flask import Blueprint, request, jsonify
from app.services.gemini_service import gemini_service

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    patient_context = data.get("patient_context")
    message = data.get("message")

    if not patient_context or not message:
        return jsonify({"error": "patient_context and message are required"}), 400

    result = gemini_service.chat(patient_context, message)
    return jsonify(result)
