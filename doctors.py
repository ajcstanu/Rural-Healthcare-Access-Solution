"""
NabhaHealth — Doctors Routes
GET  /api/doctors           list all doctors with availability
GET  /api/doctors/<id>      doctor detail
PUT  /api/doctors/<id>/availability   toggle availability (doctor JWT)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.db import db
from models.models import User, DoctorProfile, Appointment
from datetime import datetime, date

doctors_bp = Blueprint("doctors", __name__)


@doctors_bp.route("", methods=["GET"])
def list_doctors():
    specialisation = request.args.get("specialisation")
    language       = request.args.get("language")
    available_only = request.args.get("available", "false").lower() == "true"

    query = DoctorProfile.query.join(User)
    if specialisation:
        query = query.filter(DoctorProfile.specialisation.ilike(f"%{specialisation}%"))
    if language:
        query = query.filter(DoctorProfile.languages.ilike(f"%{language}%"))
    if available_only:
        query = query.filter(DoctorProfile.is_available == True)

    doctors = query.all()
    return jsonify([d.to_dict() for d in doctors]), 200


@doctors_bp.route("/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first_or_404()
    data    = profile.to_dict()

    # today's appointment count
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end   = datetime.combine(date.today(), datetime.max.time())
    booked_today = Appointment.query.filter(
        Appointment.doctor_id  == doctor_id,
        Appointment.status     == "booked",
        Appointment.scheduled_at.between(today_start, today_end)
    ).count()

    data["booked_today"]      = booked_today
    data["slots_remaining"]   = max(0, profile.max_daily_appts - booked_today)
    return jsonify(data), 200


@doctors_bp.route("/<int:doctor_id>/availability", methods=["PUT"])
@jwt_required()
def toggle_availability(doctor_id):
    uid     = int(get_jwt_identity())
    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first_or_404()

    if uid != doctor_id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(force=True)
    profile.is_available = data.get("is_available", not profile.is_available)
    db.session.commit()
    return jsonify({"is_available": profile.is_available}), 200


@doctors_bp.route("/specialisations", methods=["GET"])
def list_specialisations():
    rows = db.session.query(DoctorProfile.specialisation).distinct().all()
    return jsonify([r[0] for r in rows]), 200
