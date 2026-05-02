"""
NabhaHealth — Database Seeder
Seeds realistic doctors, medicines, pharmacies and a demo patient.
Only runs if the DB is empty (idempotent).
"""

import bcrypt
from models.db import db
from models.models import User, DoctorProfile, Pharmacy, Medicine, MedicineStock


DOCTORS = [
    {"name": "Dr. Gurpreet Singh",     "spec": "General Physician",   "qual": "MBBS, MD",       "lang": "Punjabi,Hindi,English"},
    {"name": "Dr. Amrita Sharma",      "spec": "Gynaecologist",        "qual": "MBBS, MS (OBG)", "lang": "Hindi,Punjabi"},
    {"name": "Dr. Ravinder Kumar",     "spec": "Paediatrician",        "qual": "MBBS, DCH",      "lang": "Hindi,Punjabi,English"},
    {"name": "Dr. Sukhwinder Kaur",    "spec": "Dermatologist",        "qual": "MBBS, DVD",      "lang": "Punjabi,Hindi"},
    {"name": "Dr. Harjot Brar",        "spec": "Orthopaedist",         "qual": "MBBS, MS (Ortho)","lang": "Punjabi,Hindi"},
    {"name": "Dr. Mandeep Dhillon",    "spec": "Ophthalmologist",      "qual": "MBBS, DO",       "lang": "Punjabi,Hindi"},
    {"name": "Dr. Parveen Rani",       "spec": "ENT Specialist",       "qual": "MBBS, DLO",      "lang": "Hindi,Punjabi"},
    {"name": "Dr. Balwinder Sidhu",    "spec": "General Physician",    "qual": "MBBS",           "lang": "Punjabi,Hindi"},
    {"name": "Dr. Tejinder Gill",      "spec": "Psychiatrist",         "qual": "MBBS, MD (Psych)","lang": "Punjabi,Hindi,English"},
    {"name": "Dr. Kulwant Sandhu",     "spec": "Cardiologist",         "qual": "MBBS, DM (Cardio)","lang": "Punjabi,Hindi"},
    {"name": "Dr. Simran Toor",        "spec": "Pulmonologist",        "qual": "MBBS, MD (Chest)","lang": "Punjabi,Hindi"},
]

PHARMACIES = [
    {"name": "Nabha Civil Hospital Pharmacy", "address": "Civil Hospital, Nabha", "village": "Nabha",        "phone": "01765-220001", "lat": 30.3732, "lng": 76.1490},
    {"name": "Sharma Medical Store",          "address": "Main Bazar, Nabha",     "village": "Nabha",        "phone": "9876500001",   "lat": 30.3740, "lng": 76.1500},
    {"name": "Punjab Pharma",                 "address": "Bus Stand Road, Nabha", "village": "Nabha",        "phone": "9876500002",   "lat": 30.3720, "lng": 76.1480},
    {"name": "Patiala Road Medicos",          "address": "Patiala Road, Nabha",   "village": "Nabha",        "phone": "9876500003",   "lat": 30.3710, "lng": 76.1460},
    {"name": "Sehna Village Pharmacy",        "address": "Sehna Village",         "village": "Sehna",        "phone": "9876500004",   "lat": 30.3850, "lng": 76.1300},
    {"name": "Barnala Road Dispensary",       "address": "Barnala Road",          "village": "Barnala Road", "phone": "9876500005",   "lat": 30.3600, "lng": 76.1600},
]

MEDICINES = [
    # Generic life-saving / commonly needed in rural Punjab
    {"name": "Paracetamol 500mg",        "generic": "Paracetamol",           "cat": "Analgesic/Antipyretic", "form": "tablet",   "rx": False},
    {"name": "Amoxicillin 500mg",        "generic": "Amoxicillin",           "cat": "Antibiotic",            "form": "capsule",  "rx": True},
    {"name": "Metformin 500mg",          "generic": "Metformin",             "cat": "Antidiabetic",          "form": "tablet",   "rx": True},
    {"name": "Amlodipine 5mg",           "generic": "Amlodipine",            "cat": "Antihypertensive",      "form": "tablet",   "rx": True},
    {"name": "ORS Sachets",              "generic": "Oral Rehydration Salts","cat": "Rehydration",           "form": "sachet",   "rx": False},
    {"name": "Cetirizine 10mg",          "generic": "Cetirizine",            "cat": "Antihistamine",         "form": "tablet",   "rx": False},
    {"name": "Omeprazole 20mg",          "generic": "Omeprazole",            "cat": "Antacid/PPI",           "form": "capsule",  "rx": False},
    {"name": "Azithromycin 500mg",       "generic": "Azithromycin",          "cat": "Antibiotic",            "form": "tablet",   "rx": True},
    {"name": "Ibuprofen 400mg",          "generic": "Ibuprofen",             "cat": "NSAID",                 "form": "tablet",   "rx": False},
    {"name": "Ferrous Sulphate 200mg",   "generic": "Iron (Ferrous Sulphate)","cat": "Haematinic",           "form": "tablet",   "rx": False},
    {"name": "Folic Acid 5mg",           "generic": "Folic Acid",            "cat": "Vitamin",               "form": "tablet",   "rx": False},
    {"name": "Albendazole 400mg",        "generic": "Albendazole",           "cat": "Anthelmintic",          "form": "tablet",   "rx": False},
    {"name": "Chloroquine 250mg",        "generic": "Chloroquine",           "cat": "Antimalarial",          "form": "tablet",   "rx": True},
    {"name": "Insulin Regular 40IU/ml",  "generic": "Human Insulin",         "cat": "Antidiabetic",          "form": "injection","rx": True},
    {"name": "Salbutamol Inhaler 100mcg","generic": "Salbutamol",            "cat": "Bronchodilator",        "form": "inhaler",  "rx": True},
    {"name": "Betadine Solution 100ml",  "generic": "Povidone-Iodine",       "cat": "Antiseptic",            "form": "solution", "rx": False},
    {"name": "Metronidazole 400mg",      "generic": "Metronidazole",         "cat": "Antibiotic/Antiprotozoal","form": "tablet", "rx": True},
    {"name": "Losartan 50mg",            "generic": "Losartan",              "cat": "Antihypertensive",      "form": "tablet",   "rx": True},
    {"name": "Atorvastatin 10mg",        "generic": "Atorvastatin",          "cat": "Statin",                "form": "tablet",   "rx": True},
    {"name": "Vitamin D3 60000IU",       "generic": "Cholecalciferol",       "cat": "Vitamin",               "form": "capsule",  "rx": False},
]

# Stock quantities: [pharmacy_1_qty, pharmacy_2_qty, ..., pharmacy_6_qty]
STOCK_MAP = {
    "Paracetamol 500mg":        [500, 300, 200, 150, 80, 60],
    "Amoxicillin 500mg":        [200, 100, 50,  80,  20, 15],
    "Metformin 500mg":          [150, 80,  60,  40,  10, 8],
    "Amlodipine 5mg":           [100, 50,  40,  30,  5,  3],
    "ORS Sachets":              [300, 200, 100, 80,  50, 40],
    "Cetirizine 10mg":          [200, 120, 80,  60,  30, 20],
    "Omeprazole 20mg":          [180, 90,  60,  45,  15, 10],
    "Azithromycin 500mg":       [80,  40,  30,  25,  8,  5],
    "Ibuprofen 400mg":          [250, 150, 100, 80,  40, 30],
    "Ferrous Sulphate 200mg":   [200, 80,  60,  40,  20, 15],
    "Folic Acid 5mg":           [300, 100, 80,  60,  30, 20],
    "Albendazole 400mg":        [100, 50,  30,  20,  10, 8],
    "Chloroquine 250mg":        [50,  20,  15,  10,  5,  0],
    "Insulin Regular 40IU/ml":  [30,  10,  5,   8,   0,  0],
    "Salbutamol Inhaler 100mcg":[20,  8,   5,   4,   0,  0],
    "Betadine Solution 100ml":  [60,  30,  20,  15,  8,  5],
    "Metronidazole 400mg":      [150, 60,  40,  30,  10, 8],
    "Losartan 50mg":            [80,  40,  30,  20,  5,  3],
    "Atorvastatin 10mg":        [70,  35,  25,  15,  4,  2],
    "Vitamin D3 60000IU":       [100, 50,  40,  30,  15, 10],
}

DEMO_PW = bcrypt.hashpw(b"demo1234", bcrypt.gensalt()).decode()


def seed_all():
    if User.query.first():
        return  # already seeded

    # ── Demo patient
    patient = User(name="Harpreet Singh", phone="9876543210",
                   email="patient@nabha.health", password_hash=DEMO_PW,
                   role="patient", language="pa", village="Sehna")
    db.session.add(patient)

    # ── Admin
    admin = User(name="Admin NabhaHealth", phone="9999999999",
                 email="admin@nabha.health", password_hash=DEMO_PW,
                 role="admin", language="en")
    db.session.add(admin)

    # ── Doctors
    doctor_users = []
    for i, d in enumerate(DOCTORS):
        phone = f"98765{10000 + i}"
        u = User(name=d["name"], phone=phone,
                 password_hash=DEMO_PW, role="doctor", language="pa")
        db.session.add(u)
        db.session.flush()
        p = DoctorProfile(
            user_id        = u.id,
            specialisation = d["spec"],
            qualification  = d["qual"],
            languages      = d["lang"],
            is_available   = True,
        )
        db.session.add(p)
        doctor_users.append(u)

    # ── Pharmacies
    pharm_objs = []
    for ph in PHARMACIES:
        pharm = Pharmacy(**ph)
        db.session.add(pharm)
        pharm_objs.append(pharm)

    db.session.flush()

    # ── Medicines + Stock
    med_objs = {}
    for m in MEDICINES:
        med = Medicine(
            name       = m["name"],
            generic    = m["generic"],
            category   = m["cat"],
            form       = m["form"],
            requires_rx= m["rx"],
        )
        db.session.add(med)
        db.session.flush()
        med_objs[m["name"]] = med

    prices = {
        "tablet": 2.5, "capsule": 3.0, "sachet": 5.0,
        "injection": 25.0, "inhaler": 150.0, "solution": 40.0,
    }
    for med_name, qty_list in STOCK_MAP.items():
        med = med_objs.get(med_name)
        if not med:
            continue
        for idx, pharm in enumerate(pharm_objs):
            qty   = qty_list[idx] if idx < len(qty_list) else 0
            price = prices.get(med.form, 5.0)
            stock = MedicineStock(
                pharmacy_id = pharm.id,
                medicine_id = med.id,
                quantity    = qty,
                unit_price  = price,
            )
            db.session.add(stock)

    db.session.commit()
    print("✅  Database seeded — Nabha Civil Hospital data loaded.")
    print("   Demo credentials:")
    print("     Patient  → phone: 9876543210  password: demo1234")
    print("     Admin    → phone: 9999999999  password: demo1234")
    print(f"    Doctors  → phone: 9876510000 … 9876510010  password: demo1234")
