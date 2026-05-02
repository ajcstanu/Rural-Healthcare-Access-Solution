"""
NabhaHealth — Health Records Routes
GET  /api/records/<patient_id>        fetch all records (JWT)
POST /api/records/<patient_id>        add record (doctor or self)
PUT  /api/records/<patient_id>/sync   sync offline records (batch)
DELETE /api/records/<record_id>/delete
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models.db import db
from models.models import HealthRecord, User

records_bp = Blueprint("records", __name__)


def _can_access(uid: int, patient_id: int) -> bool:
    """Patient can read their own. Doctors/admins can read all."""
    if uid == patient_id:
        return True
    user = User.query.get(uid)
    return user and user.role in ("doctor", "admin")


@records_bp.route("/<int:patient_id>", methods=["GET"])
@jwt_required()
def get_records(patient_id):
    uid = int(get_jwt_identity())
    if not _can_access(uid, patient_id):
        return jsonify({"error": "Forbidden"}), 403

    rtype = request.args.get("type")
    q     = HealthRecord.query.filter_by(patient_id=patient_id)
    if rtype:
        q = q.filter_by(record_type=rtype)

    records = q.order_by(HealthRecord.recorded_at.desc()).all()
    return jsonify([r.to_dict() for r in records]), 200


@records_bp.route("/<int:patient_id>", methods=["POST"])
@jwt_required()
def add_record(patient_id):
    uid  = int(get_jwt_identity())
    user = User.query.get(uid)

    # Only doctor or the patient themselves can add
    if uid != patient_id and user.role not in ("doctor", "admin"):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(force=True)
    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    rec = HealthRecord(
        patient_id  = patient_id,
        doctor_id   = uid if user.role == "doctor" else None,
        record_type = data.get("record_type", "consultation"),
        title       = data["title"],
        description = data.get("description"),
        diagnosis   = data.get("diagnosis"),
        medications = json.dumps(data.get("medications", [])),
        attachments = json.dumps(data.get("attachments", [])),
        is_synced   = True,
    )
    db.session.add(rec)
    db.session.commit()
    return jsonify(rec.to_dict()), 201


@records_bp.route("/<int:patient_id>/sync", methods=["PUT"])
@jwt_required()
def sync_offline(patient_id):
    """
    Bulk-sync records created offline on the mobile app.
    Body: { "records": [ {...}, {...} ] }
    """
    uid = int(get_jwt_identity())
    if not _can_access(uid, patient_id):
        return jsonify({"error": "Forbidden"}), 403

    data    = request.get_json(force=True)
    records = data.get("records", [])
    created = []

    for r in records:
        rec = HealthRecord(
            patient_id  = patient_id,
            doctor_id   = r.get("doctor_id"),
            record_type = r.get("record_type", "consultation"),
            title       = r.get("title", "Offline record"),
            description = r.get("description"),
            diagnosis   = r.get("diagnosis"),
            medications = json.dumps(r.get("medications", [])),
            attachments = json.dumps(r.get("attachments", [])),
            is_synced   = True,
            recorded_at = datetime.fromisoformat(r["recorded_at"])
                          if r.get("recorded_at") else datetime.utcnow(),
        )
        db.session.add(rec)
        created.append(rec)

    db.session.commit()
    return jsonify({"synced": len(created), "records": [r.to_dict() for r in created]}), 201


@records_bp.route("/<int:record_id>/delete", methods=["DELETE"])
@jwt_required()
def delete_record(record_id):
    uid = int(get_jwt_identity())
    rec = HealthRecord.query.get_or_404(record_id)
    if rec.patient_id != uid:
        user = User.query.get(uid)
        if not user or user.role != "admin":
            return jsonify({"error": "Forbidden"}), 403
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"message": "Record deleted"}), 200
