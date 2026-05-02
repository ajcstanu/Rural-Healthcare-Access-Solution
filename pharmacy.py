"""
NabhaHealth — Pharmacy Routes
GET /api/pharmacy            list all pharmacies
GET /api/pharmacy/<id>/stock stock levels at this pharmacy
"""

from flask import Blueprint, request, jsonify
from models.models import Pharmacy, MedicineStock

pharmacy_bp = Blueprint("pharmacy", __name__)


@pharmacy_bp.route("", methods=["GET"])
def list_pharmacies():
    village = request.args.get("village")
    q = Pharmacy.query.filter_by(is_active=True)
    if village:
        q = q.filter(Pharmacy.village.ilike(f"%{village}%"))
    return jsonify([p.to_dict() for p in q.all()]), 200


@pharmacy_bp.route("/<int:pharmacy_id>/stock", methods=["GET"])
def pharmacy_stock(pharmacy_id):
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    stocks   = MedicineStock.query.filter_by(pharmacy_id=pharmacy_id).all()
    return jsonify({
        "pharmacy": pharmacy.to_dict(),
        "stock": [s.to_dict() for s in stocks],
        "low_stock": [s.to_dict() for s in stocks if 0 < s.quantity <= 10],
        "out_of_stock": [s.to_dict() for s in stocks if s.quantity == 0],
    }), 200
