"""
NabhaHealth — Rural Telemedicine Platform
==========================================
Serves 173 villages around Nabha, Punjab.
Full Python/Flask backend with SQLite (dev) / PostgreSQL (prod).

Run:
    pip install flask flask-cors flask-sqlalchemy flask-jwt-extended bcrypt scikit-learn numpy pandas
    python app.py

API docs printed to console on startup.
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from models.db import db
from routes.auth     import auth_bp
from routes.doctors  import doctors_bp
from routes.appointments import appointments_bp
from routes.medicines    import medicines_bp
from routes.records      import records_bp
from routes.symptoms     import symptoms_bp
from routes.pharmacy     import pharmacy_bp

import os

def create_app():
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────────────────
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///nabhahealth.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "nabha-secret-change-in-prod")
    app.config["JSON_AS_ASCII"] = False   # allow Punjabi / Hindi in JSON

    # ── Extensions ────────────────────────────────────────────────────────────
    CORS(app)
    db.init_app(app)
    JWTManager(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(doctors_bp,      url_prefix="/api/doctors")
    app.register_blueprint(appointments_bp, url_prefix="/api/appointments")
    app.register_blueprint(medicines_bp,    url_prefix="/api/medicines")
    app.register_blueprint(records_bp,      url_prefix="/api/records")
    app.register_blueprint(symptoms_bp,     url_prefix="/api/symptom-check")
    app.register_blueprint(pharmacy_bp,     url_prefix="/api/pharmacy")

    # ── DB init + seed ────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        from services.seeder import seed_all
        seed_all()

    return app


def print_routes(app):
    print("\n" + "=" * 60)
    print("  🏥  NabhaHealth API — Ready")
    print("=" * 60)
    routes = [
        ("POST", "/api/auth/register",               "Register patient or doctor"),
        ("POST", "/api/auth/login",                  "Login → JWT token"),
        ("GET",  "/api/doctors",                     "List available doctors"),
        ("GET",  "/api/doctors/<id>",                "Doctor detail"),
        ("POST", "/api/appointments",                "Book appointment"),
        ("GET",  "/api/appointments",                "My appointments (JWT)"),
        ("PUT",  "/api/appointments/<id>/cancel",    "Cancel appointment"),
        ("GET",  "/api/medicines",                   "All medicines"),
        ("GET",  "/api/medicines?pharmacy=<id>",     "Stock by pharmacy"),
        ("GET",  "/api/medicines/search?q=<name>",   "Search medicine"),
        ("POST", "/api/medicines/update-stock",      "Update stock (pharmacy JWT)"),
        ("GET",  "/api/records/<patient_id>",        "Patient health records (JWT)"),
        ("POST", "/api/records/<patient_id>",        "Add record (doctor JWT)"),
        ("PUT",  "/api/records/<patient_id>/sync",   "Sync offline records"),
        ("POST", "/api/symptom-check",               "AI symptom triage"),
        ("GET",  "/api/pharmacy",                    "List pharmacies"),
        ("GET",  "/api/pharmacy/<id>/stock",         "Pharmacy stock levels"),
    ]
    for method, path, desc in routes:
        print(f"  {method:6s}  {path:45s}  {desc}")
    print("=" * 60)
    print("  Base URL : http://127.0.0.1:5000")
    print("  DB       : nabhahealth.db  (SQLite — switch to PostgreSQL in prod)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    app = create_app()
    print_routes(app)
    app.run(debug=True, port=5000)
