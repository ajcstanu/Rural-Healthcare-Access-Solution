# 🏥 NabhaHealth — Rural Telemedicine Platform

> Connecting 173 villages around Nabha, Punjab to quality healthcare.  
> Flask backend · SQLite · Plain HTML/CSS/JS frontend · Works on low-bandwidth connections.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Demo Credentials](#demo-credentials)
- [API Reference](#api-reference)
- [Symptom Checker](#symptom-checker)
- [Database Models](#database-models)
- [Configuration](#configuration)
- [Known Issues & Fixes](#known-issues--fixes)
- [Tech Stack](#tech-stack)

---

## Overview

NabhaHealth is a telemedicine web application built for rural communities in Punjab, India. It allows patients from remote villages to find doctors, book appointments (video or in-person), check medicine availability at nearby pharmacies, and get an AI-assisted symptom triage — all in Hindi, Punjabi, or English.

The backend is a modular Flask application. The frontend is a single-page app (`static/index.html`) served directly by Flask, requiring no separate build step or Node.js.

---

## Features

| Feature | Description |
|---|---|
| 🔐 Auth | JWT-based login & registration with bcrypt password hashing |
| 👨‍⚕️ Doctor Directory | Browse doctors by specialisation, language, availability |
| 📅 Appointment Booking | 15-minute slot grid (09:00–17:00), video or in-person mode |
| 💊 Medicine Finder | Search by brand or generic name, see stock across all pharmacies |
| 🏪 Pharmacy Stock | Per-pharmacy inventory with low-stock and out-of-stock alerts |
| 🤒 AI Symptom Checker | Rule-based triage engine; supports Hindi/Punjabi transliterations |
| 📋 Health Records | Patient medical history — JWT protected, role-aware access |
| 🌐 Multilingual | Accepts symptoms in English, Hindi (`bukhar`, `sardard`) and Punjabi |

---

## Project Structure

```
nabhahealth/
│
├── app.py                   # App factory, blueprint registration, frontend serving
├── requirements.txt
├── README.md
│
├── models/
│   ├── db.py                # SQLAlchemy instance (db = SQLAlchemy())
│   └── models.py            # ORM models: User, DoctorProfile, Appointment,
│                            #   HealthRecord, Pharmacy, Medicine, MedicineStock
│
├── routes/                  # Flask blueprints (one file per domain)
│   ├── auth.py              # POST /api/auth/register, /login, GET /me
│   ├── doctors.py           # GET /api/doctors, /specialisations, /<id>/availability
│   ├── appointments.py      # POST/GET /api/appointments, /slots, /cancel, /complete
│   ├── medicines.py         # GET /api/medicines, /search, /categories; POST /update-stock
│   ├── pharmacy.py          # GET /api/pharmacy, /<id>/stock
│   ├── records.py           # GET/POST /api/records/<patient_id>, /sync, /delete
│   └── symptoms.py          # POST /api/symptom-check
│
├── ai/
│   └── symptom_checker.py   # Offline rule-based triage engine + synonym normaliser
│
├── services/
│   └── seeder.py            # Seeds 11 doctors, 6 pharmacies, 20 medicines on first run
│
└── static/                  # Frontend (served by Flask at /)
    ├── index.html           # Single-page app
    ├── css/style.css
    └── js/app.js
```

---

## Getting Started

### 1. Clone / unzip the project

```bash
cd nabhahealth
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**.  
The database (`nabhahealth.db`) is created and seeded automatically on first run.

### 5. Open the app

Navigate to **http://127.0.0.1:5000** in your browser.

---

## Demo Credentials

| Role    | Phone        | Password  | Notes |
|---------|--------------|-----------|-------|
| Patient | `9876543210` | `demo1234`| Village: Sehna |
| Admin   | `9999999999` | `demo1234`| Full access |
| Doctor  | `9876510000` | `demo1234`| Dr. Gurpreet Singh — General Physician |
| Doctor  | `9876510001` | `demo1234`| Dr. Amrita Sharma — Gynaecologist |
| Doctor  | `9876510002` | `demo1234`| Dr. Ravinder Kumar — Paediatrician |

> All 11 seeded doctors use the same password `demo1234`. Phones run from `9876510000` to `9876510010`.

---

## API Reference

All API routes are prefixed with `/api`. Endpoints marked 🔒 require a `Bearer` JWT token in the `Authorization` header.

### Auth

| Method | Endpoint | Auth | Body / Params | Description |
|--------|----------|------|--------------|-------------|
| `POST` | `/api/auth/register` | — | `name, phone, password, [email, village, language, role]` | Register new user |
| `POST` | `/api/auth/login` | — | `phone, password` | Login, returns JWT token |
| `GET`  | `/api/auth/me` | 🔒 | — | Get current user's profile |

**Register / Login response:**
```json
{
  "token": "<jwt>",
  "user": { "id": 1, "name": "Harpreet Singh", "phone": "9876543210", "role": "patient", "village": "Sehna" }
}
```

---

### Doctors

| Method | Endpoint | Auth | Params | Description |
|--------|----------|------|--------|-------------|
| `GET`  | `/api/doctors` | — | `?available=true`, `?specialisation=`, `?language=` | List all doctors |
| `GET`  | `/api/doctors/specialisations` | — | — | List of distinct specialisations |
| `GET`  | `/api/doctors/<id>` | — | — | Doctor detail + today's slot count |
| `PUT`  | `/api/doctors/<id>/availability` | 🔒 | `{ "is_available": true }` | Toggle availability (doctor only) |

---

### Appointments

| Method | Endpoint | Auth | Params / Body | Description |
|--------|----------|------|--------------|-------------|
| `GET`  | `/api/appointments/slots` | 🔒 | `?doctor_id=&date=YYYY-MM-DD` | Available time slots |
| `POST` | `/api/appointments` | 🔒 | `doctor_id, scheduled_at, [mode, notes]` | Book appointment |
| `GET`  | `/api/appointments` | 🔒 | `?status=booked\|completed\|cancelled` | My appointments |
| `GET`  | `/api/appointments/<id>` | 🔒 | — | Single appointment detail |
| `PUT`  | `/api/appointments/<id>/cancel` | 🔒 | — | Cancel an appointment |
| `PUT`  | `/api/appointments/<id>/complete` | 🔒 | `{ "prescription": "..." }` | Mark complete (doctor only) |

**Slots response:**
```json
{
  "date": "2025-06-15",
  "doctor_id": 1,
  "slots": [
    { "time": "09:00", "available": true },
    { "time": "09:15", "available": false }
  ]
}
```

---

### Medicines

| Method | Endpoint | Auth | Params / Body | Description |
|--------|----------|------|--------------|-------------|
| `GET`  | `/api/medicines` | — | `?category=`, `?pharmacy=<id>` | List medicines with stock info |
| `GET`  | `/api/medicines/search` | — | `?q=<name>` (min 2 chars) | Search by brand or generic name |
| `GET`  | `/api/medicines/categories` | — | — | List distinct categories |
| `POST` | `/api/medicines/update-stock` | 🔒 | `pharmacy_id, medicine_id, quantity, [unit_price]` | Update stock (pharmacy/admin only) |

---

### Pharmacy

| Method | Endpoint | Auth | Params | Description |
|--------|----------|------|--------|-------------|
| `GET`  | `/api/pharmacy` | — | `?village=` | List pharmacies |
| `GET`  | `/api/pharmacy/<id>/stock` | — | — | Full stock list with low/out-of-stock alerts |

**Stock response:**
```json
{
  "pharmacy": { "id": 1, "name": "Nabha Civil Hospital Pharmacy", ... },
  "stock": [ { "medicine_name": "Paracetamol 500mg", "quantity": 500, "unit_price": 2.5 } ],
  "low_stock": [],
  "out_of_stock": []
}
```

---

### Health Records

| Method | Endpoint | Auth | Params / Body | Description |
|--------|----------|------|--------------|-------------|
| `GET`  | `/api/records/<patient_id>` | 🔒 | `?type=consultation\|lab\|vaccination` | Get patient records |
| `POST` | `/api/records/<patient_id>` | 🔒 | `title, [record_type, description, diagnosis, medications]` | Add a record |
| `PUT`  | `/api/records/<patient_id>/sync` | 🔒 | `{ "records": [...] }` | Batch sync offline records |
| `DELETE` | `/api/records/<record_id>/delete` | 🔒 | — | Delete a record (patient or admin) |

---

### Symptom Checker

| Method | Endpoint | Auth | Body | Description |
|--------|----------|------|------|-------------|
| `POST` | `/api/symptom-check` | — | `{ "symptoms": ["fever", "bukhar", "sardard"] }` | AI triage |

**Response:**
```json
{
  "urgency": "HIGH",
  "specialist": "General Physician / Infectious Disease",
  "advice": "Could be dengue, malaria or typhoid. Visit hospital within 24 hours.",
  "red_flags": ["Dengue", "Malaria", "Typhoid"],
  "icd10": "A90 / B50",
  "matched_symptoms": ["fever", "body pain", "headache"],
  "disclaimer": "This is AI-assisted triage only — NOT a medical diagnosis."
}
```

---

## Symptom Checker

The triage engine (`ai/symptom_checker.py`) works **fully offline** — no external API calls.

**How it works:**

1. Each input symptom string is normalised through a **synonym map** that covers common Hindi and Punjabi transliterations (`bukhar` → `fever`, `sardard` → `headache`, `seene mein dard` → `chest pain`, etc.)
2. Normalised symptoms are matched against a **rule set** using `match_all` (all must match) or `match_any` (any one matches) logic
3. The **highest-urgency** matching rule wins
4. Returns urgency level, recommended specialist, advice, ICD-10 code, and red flag warnings

**Urgency levels:** `CRITICAL` → `HIGH` → `MODERATE` → `LOW`

**Example inputs that work:**
```
"bukhar", "sardard", "khansi"          # Hindi/Punjabi
"fever", "headache", "body pain"       # English
"seene mein dard", "saans nahi"        # Hindi phrases
```

---

## Database Models

```
User ──────────────┬── DoctorProfile (one-to-one)
                   ├── Appointment (as patient, many)
                   ├── Appointment (as doctor, many)
                   ├── HealthRecord (as patient, many)
                   └── HealthRecord (as doctor, many)

Pharmacy ──────────── MedicineStock (many)
Medicine ──────────── MedicineStock (many)
```

User roles: `patient` · `doctor` · `pharmacy` · `admin`

---

## Configuration

All config lives in `app.py` inside `create_app()`. Override with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///nabhahealth.db` | SQLAlchemy DB URI |
| `JWT_SECRET` | `nabha-secret-change-in-prod` | JWT signing key — **change in production** |

**Example for production:**
```bash
export DATABASE_URL="postgresql://user:pass@localhost/nabhahealth"
export JWT_SECRET="your-very-long-random-secret"
python app.py
```

---

## Known Issues & Fixes

### 1. `/api/doctors/specialisations` returns 404
The `/specialisations` route must be defined **before** `/<int:doctor_id>` in `doctors.py`, otherwise Flask matches the word `specialisations` as a doctor ID integer and raises a 404.

**Fix:** Move the `list_specialisations` function above `get_doctor` in `routes/doctors.py`.

### 2. Slot date filtering (SQLAlchemy 2.x)
`db.func.date(Appointment.scheduled_at) == target_date` may behave unexpectedly outside SQLite. Replace with:

```python
from datetime import datetime, date as date_type
Appointment.scheduled_at >= datetime.combine(target_date, datetime.min.time()),
Appointment.scheduled_at <  datetime.combine(target_date, datetime.max.time()),
```

### 3. SQLAlchemy 2.x deprecation warning
`User.query.get(uid)` is deprecated. Replace with:
```python
db.session.get(User, uid)
```

### 4. Email unique constraint with NULL values
`email` has `unique=True` but most seeded users have no email. SQLite allows multiple NULLs in unique columns, but PostgreSQL does not. If migrating to PostgreSQL, remove `unique=True` from the `email` column or use a partial index.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ · Flask 3.x |
| ORM | Flask-SQLAlchemy 3.x |
| Auth | Flask-JWT-Extended · bcrypt |
| Database | SQLite (dev) · PostgreSQL-compatible |
| Frontend | Vanilla HTML · CSS · JavaScript (no build step) |
| AI/ML | Rule-based engine (no external API, works offline) |
| CORS | Flask-CORS |

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](docs/contributing.md) and open a PR.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

