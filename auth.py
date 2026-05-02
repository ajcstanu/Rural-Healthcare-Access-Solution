"""
NabhaHealth — Authentication Routes
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt

from models.db import db
from models.models import User, DoctorProfile

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)

    required = ["name", "phone", "password"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(phone=data["phone"]).first():
        return jsonify({"error": "Phone number already registered"}), 409

    pw_hash = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()

    user = User(
        name          = data["name"].strip(),
        phone         = data["phone"].strip(),
        email         = data.get("email"),
        password_hash = pw_hash,
        role          = data.get("role", "patient"),
        language      = data.get("language", "hi"),
        village       = data.get("village"),
    )
    db.session.add(user)
    db.session.flush()   # get user.id before committing

    if user.role == "doctor":
        profile = DoctorProfile(
            user_id        = user.id,
            specialisation = data.get("specialisation", "General Physician"),
            qualification  = data.get("qualification", "MBBS"),
            languages      = data.get("languages", "Hindi,Punjabi"),
        )
        db.session.add(profile)

    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict(include_sensitive=True)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    user = User.query.filter_by(phone=data.get("phone")).first()

    if not user or not bcrypt.checkpw(data.get("password", "").encode(),
                                      user.password_hash.encode()):
        return jsonify({"error": "Invalid phone or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict(include_sensitive=True)}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    uid  = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    return jsonify(user.to_dict(include_sensitive=True)), 200
