"""
NabhaHealth — Rural Telemedicine Platform
==========================================
Serves 173 villages around Nabha, Punjab.
Flask backend with SQLite. Serves frontend from /static.

Run:
    pip install flask flask-cors flask-sqlalchemy flask-jwt-extended bcrypt
    python app.py
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models.db import db
from routes.auth import auth_bp
from routes.doctors import doctors_bp
from routes.appointments import appointments_bp
from routes.medicines import medicines_bp
from routes.records import records_bp
from routes.symptoms import symptoms_bp
from routes.pharmacy import pharmacy_bp
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///nabhahealth.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "nabha-secret-change-in-prod")
    app.config["JSON_AS_ASCII"] = False

    CORS(app)
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(doctors_bp,      url_prefix="/api/doctors")
    app.register_blueprint(appointments_bp, url_prefix="/api/appointments")
    app.register_blueprint(medicines_bp,    url_prefix="/api/medicines")
    app.register_blueprint(records_bp,      url_prefix="/api/records")
    app.register_blueprint(symptoms_bp,     url_prefix="/api/symptom-check")
    app.register_blueprint(pharmacy_bp,     url_prefix="/api/pharmacy")

    with app.app_context():
        db.create_all()
        from services.seeder import seed_all
        seed_all()

    # Serve frontend
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        static_dir = os.path.join(BASE_DIR, "static")
        full = os.path.join(static_dir, path)
        if path and os.path.exists(full):
            return send_from_directory(static_dir, path)
        return send_from_directory(static_dir, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    print("\n" + "="*60)
    print("  🏥  NabhaHealth — Ready at http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
