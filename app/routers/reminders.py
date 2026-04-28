from flask import Blueprint, request, jsonify
from app.services.gemini_service import gemini_service

reminders_bp = Blueprint("reminders", __name__)


@reminders_bp.post("/reminder")
def generate_reminder():
    data = request.get_json(silent=True) or {}
    patient_context = data.get("patient_context")
    phase = data.get("treatment_phase", "initial")

    if not patient_context:
        return jsonify({"error": "patient_context is required"}), 400

    result = gemini_service.generate_reminder(patient_context, phase)
    return jsonify(result)
