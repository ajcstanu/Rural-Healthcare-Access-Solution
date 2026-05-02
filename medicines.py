"""
NabhaHealth — Medicine Routes
GET  /api/medicines                   all medicines
GET  /api/medicines/search?q=<name>   search
GET  /api/medicines?pharmacy=<id>     stock at a pharmacy
POST /api/medicines/update-stock      pharmacy update stock
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models.db import db
from models.models import Medicine, MedicineStock, Pharmacy, User

medicines_bp = Blueprint("medicines", __name__)


@medicines_bp.route("", methods=["GET"])
def list_medicines():
    pharmacy_id = request.args.get("pharmacy", type=int)
    category    = request.args.get("category")

    if pharmacy_id:
        # stock for this pharmacy
        q = MedicineStock.query.filter_by(pharmacy_id=pharmacy_id)
        stocks = q.all()
        return jsonify([s.to_dict() for s in stocks]), 200

    # all medicines (with aggregate availability)
    q = Medicine.query
    if category:
        q = q.filter(Medicine.category.ilike(f"%{category}%"))

    medicines = q.all()

    result = []
    for m in medicines:
        total_qty = sum(s.quantity for s in m.stocks)
        pharmacies_with_stock = [
            {"id": s.pharmacy_id, "name": s.pharmacy.name, "qty": s.quantity}
            for s in m.stocks if s.quantity > 0
        ]
        d = m.to_dict()
        d["total_available"] = total_qty
        d["available_at"]    = pharmacies_with_stock
        result.append(d)

    return jsonify(result), 200


@medicines_bp.route("/search", methods=["GET"])
def search():
    q_str = request.args.get("q", "").strip()
    if len(q_str) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400

    medicines = Medicine.query.filter(
        db.or_(
            Medicine.name.ilike(f"%{q_str}%"),
            Medicine.generic.ilike(f"%{q_str}%"),
        )
    ).all()

    result = []
    for m in medicines:
        d = m.to_dict()
        d["available_at"] = [
            {"pharmacy": s.pharmacy.name, "village": s.pharmacy.village, "qty": s.quantity, "price": s.unit_price}
            for s in m.stocks if s.quantity > 0
        ]
        result.append(d)

    return jsonify(result), 200


@medicines_bp.route("/update-stock", methods=["POST"])
@jwt_required()
def update_stock():
    uid  = int(get_jwt_identity())
    user = User.query.get(uid)
    if user.role not in ("pharmacy", "admin"):
        return jsonify({"error": "Only pharmacy staff can update stock"}), 403

    data = request.get_json(force=True)
    required = ["pharmacy_id", "medicine_id", "quantity"]
    missing  = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400

    stock = MedicineStock.query.filter_by(
        pharmacy_id = data["pharmacy_id"],
        medicine_id = data["medicine_id"],
    ).first()

    if stock:
        stock.quantity     = data["quantity"]
        stock.unit_price   = data.get("unit_price", stock.unit_price)
        stock.last_updated = datetime.utcnow()
    else:
        stock = MedicineStock(
            pharmacy_id = data["pharmacy_id"],
            medicine_id = data["medicine_id"],
            quantity    = data["quantity"],
            unit_price  = data.get("unit_price", 0.0),
        )
        db.session.add(stock)

    db.session.commit()
    return jsonify(stock.to_dict()), 200


@medicines_bp.route("/categories", methods=["GET"])
def categories():
    rows = db.session.query(Medicine.category).distinct().all()
    return jsonify([r[0] for r in rows if r[0]]), 200
