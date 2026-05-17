"""
NabhaHealth — Symptom Checker Route
POST /api/symptom-check
Body: { "symptoms": ["fever", "headache", "body pain"] }
      OR  { "symptoms": ["bukhar", "sardard"] }  (Hindi / Punjabi OK)
"""

from flask import Blueprint, request, jsonify
from ai.symptom_checker import check_symptoms

symptoms_bp = Blueprint("symptoms", __name__)


@symptoms_bp.route("", methods=["POST"])
def symptom_check():
    data = request.get_json(force=True)
    symptoms = data.get("symptoms", [])

    if not symptoms or not isinstance(symptoms, list):
        return jsonify({"error": "Provide 'symptoms' as a non-empty list"}), 400

    if len(symptoms) > 20:
        return jsonify({"error": "Too many symptoms (max 20)"}), 400

    result = check_symptoms(symptoms)
    return jsonify(result), 200
