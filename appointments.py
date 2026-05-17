"""
NabhaHealth — Appointments Routes
POST /api/appointments               book appointment
GET  /api/appointments               my appointments (JWT)
GET  /api/appointments/<id>          detail
PUT  /api/appointments/<id>/cancel   cancel
PUT  /api/appointments/<id>/complete complete + add prescription (doctor JWT)
GET  /api/appointments/slots         available slots for a doctor on a date
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from models.db import db
from models.models import User, Appointment, DoctorProfile

appointments_bp = Blueprint("appointments", __name__)


@appointments_bp.route("", methods=["POST"])
@jwt_required()
def book():
    uid  = int(get_jwt_identity())
    data = request.get_json(force=True)

    required = ["doctor_id", "scheduled_at"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400

    try:
        sched = datetime.fromisoformat(data["scheduled_at"])
    except ValueError:
        return jsonify({"error": "scheduled_at must be ISO-8601 e.g. 2025-06-15T10:00:00"}), 400

    if sched < datetime.utcnow():
        return jsonify({"error": "Cannot book in the past"}), 400

    doctor = User.query.filter_by(id=data["doctor_id"], role="doctor").first()
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    # check slot clash
    profile = doctor.doctor_profile
    if profile:
        slot_end = sched + timedelta(minutes=profile.slot_duration)
        clash = Appointment.query.filter(
            Appointment.doctor_id  == doctor.id,
            Appointment.status     == "booked",
            Appointment.scheduled_at >= sched,
            Appointment.scheduled_at <  slot_end,
        ).first()
        if clash:
            return jsonify({"error": "That slot is already booked. Please choose another time."}), 409

    appt = Appointment(
        patient_id   = uid,
        doctor_id    = doctor.id,
        scheduled_at = sched,
        mode         = data.get("mode", "video"),
        notes        = data.get("notes"),
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify(appt.to_dict()), 201


@appointments_bp.route("", methods=["GET"])
@jwt_required()
def my_appointments():
    uid  = int(get_jwt_identity())
    user = User.query.get(uid)
    status_filter = request.args.get("status")

    if user.role == "doctor":
        q = Appointment.query.filter_by(doctor_id=uid)
    else:
        q = Appointment.query.filter_by(patient_id=uid)

    if status_filter:
        q = q.filter_by(status=status_filter)

    appts = q.order_by(Appointment.scheduled_at.desc()).all()
    return jsonify([a.to_dict() for a in appts]), 200


@appointments_bp.route("/<int:appt_id>", methods=["GET"])
@jwt_required()
def get_appointment(appt_id):
    uid  = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != uid and appt.doctor_id != uid:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(appt.to_dict()), 200


@appointments_bp.route("/<int:appt_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel(appt_id):
    uid  = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != uid and appt.doctor_id != uid:
        return jsonify({"error": "Forbidden"}), 403
    appt.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Appointment cancelled", "id": appt_id}), 200


@appointments_bp.route("/<int:appt_id>/complete", methods=["PUT"])
@jwt_required()
def complete(appt_id):
    uid  = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != uid:
        return jsonify({"error": "Only the attending doctor can complete the appointment"}), 403

    data = request.get_json(force=True)
    appt.status       = "completed"
    appt.prescription = data.get("prescription")
    db.session.commit()
    return jsonify(appt.to_dict()), 200


@appointments_bp.route("/slots", methods=["GET"])
def available_slots():
    """Return free 15-min slots for a doctor on a given date."""
    doctor_id = request.args.get("doctor_id", type=int)
    date_str  = request.args.get("date")   # YYYY-MM-DD

    if not doctor_id or not date_str:
        return jsonify({"error": "doctor_id and date required"}), 400

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "date must be YYYY-MM-DD"}), 400

    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
    if not profile or not profile.is_available:
        return jsonify({"slots": [], "message": "Doctor unavailable"}), 200

    # generate slots 09:00–17:00
    slot_minutes = profile.slot_duration
    booked = {
        a.scheduled_at.strftime("%H:%M")
        for a in Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status    == "booked",
            db.func.date(Appointment.scheduled_at) == target_date,
        ).all()
    }

    slots = []
    current = datetime(target_date.year, target_date.month, target_date.day, 9, 0)
    end     = datetime(target_date.year, target_date.month, target_date.day, 17, 0)
    while current < end:
        slot_str = current.strftime("%H:%M")
        slots.append({"time": slot_str, "available": slot_str not in booked})
        current += timedelta(minutes=slot_minutes)

    return jsonify({"date": date_str, "doctor_id": doctor_id, "slots": slots}), 200
