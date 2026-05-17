# 🏥 NabhaHealth — Rural Telemedicine Platform

A lightweight telemedicine platform built for 173 villages around Nabha, Punjab.  
Python/Flask backend · Plain HTML/CSS/JS frontend · SQLite database · Works on low-bandwidth connections.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server (auto-creates & seeds the database on first run)
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> The database (`nabhahealth.db`) is created automatically on first run with seed doctors, pharmacies, medicines, and a test patient account.

---

## 🔑 Demo Credentials

| Role    | Phone        | Password   |
|---------|--------------|------------|
| Patient | 9999999999   | patient123 |
| Doctor  | 9000000001   | doctor123  |
| Admin   | 9000000000   | admin123   |

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌐 **Multi-language UI** | English, Hindi (हिंदी), Punjabi (ਪੰਜਾਬੀ) — switches live without page reload |
| 🩺 **AI Symptom Checker** | Rule-based triage engine with ICD-10 codes, urgency levels (CRITICAL / HIGH / MEDIUM / LOW), red flags, and specialist recommendations. Accepts Hindi/Punjabi transliterations. |
| 👨‍⚕️ **Doctor Directory** | Browse doctors, filter by specialisation or availability, view languages spoken and schedule |
| 📅 **Appointment Booking** | Date picker → available slot grid → confirm in-person or video consult. Duplicate-slot prevention built in. |
| 💊 **Medicine Finder** | Search by brand or generic name. See which pharmacies have stock and at what price. |
| 🏪 **Pharmacy Stock** | View live stock levels per pharmacy. Low-stock and out-of-stock alerts shown. |
| 📋 **Health Records** | Patients view their own consultation history, lab reports, diagnoses, and prescriptions (JWT-protected). |
| 🔐 **Auth** | JWT login/register, bcrypt password hashing, 48-hour token expiry. Language preference saved per user. |

---

## 🗂️ Project Structure

```
nabhahealth/
├── app.py                  # Flask entry point — DB schema, seed data, all routes
├── requirements.txt
│
├── models/
│   ├── db.py               # SQLAlchemy instance
│   └── models.py           # ORM models (users, doctors, appointments, …)
│
├── routes/                 # API blueprints (modular version)
│   ├── auth.py
│   ├── doctors.py
│   ├── appointments.py
│   ├── medicines.py
│   ├── pharmacy.py
│   ├── records.py
│   └── symptoms.py
│
├── ai/
│   └── symptom_checker.py  # Rule-based triage + synonym normalisation (en/hi/pa)
│
├── services/
│   └── seeder.py           # DB seed data helper
│
└── static/
    ├── index.html          # Single-page frontend shell
    ├── css/
    │   └── style.css
    ├── js/
    │   └── app.js          # Frontend logic + i18n engine
    └── locales/            # Translation files (add to enable multi-language)
        ├── en.json
        ├── hi.json
        └── pa.json
```

---

## 🌐 i18n (Multi-language Support)

The frontend includes a lightweight i18n engine in `static/js/app.js`.

- Language is auto-detected from the user's saved preference → browser locale → defaults to `en`
- Switching language reloads all UI strings instantly (no page refresh)
- User's language preference is saved to `localStorage` and to their account on login
- Fonts switch automatically: Noto Sans Devanagari for Hindi, Noto Sans Gurmukhi for Punjabi

**To add or edit translations**, edit the files in `static/locales/`:

```
static/locales/en.json   ← English (default)
static/locales/hi.json   ← Hindi
static/locales/pa.json   ← Punjabi
```

Each file uses dot-path keys:
```json
{
  "nav": { "doctors": "Doctors" },
  "appointments": { "booked_success": "Appointment booked!" }
}
```

---

## 🔌 API Reference

All JSON. Auth-required endpoints need `Authorization: Bearer <token>` header.

### Auth
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | — | Register new patient |
| POST | `/api/auth/login` | — | Login, returns JWT token |
| GET  | `/api/auth/me` | ✅ | Get current user profile |

**Register payload:**
```json
{ "name": "Gurpreet", "phone": "9876500000", "password": "secret", "village": "Nabha", "language": "pa" }
```

### Doctors
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/doctors` | — | List doctors. Query: `?available=true`, `?specialisation=Cardiologist` |
| GET | `/api/doctors/specialisations` | — | List all unique specialisations |
| GET | `/api/doctors/<id>` | — | Get single doctor |

### Appointments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/api/appointments/slots` | ✅ | Available slots. Query: `?doctor_id=1&date=2025-06-01` |
| POST | `/api/appointments` | ✅ | Book an appointment |
| GET  | `/api/appointments` | ✅ | List my appointments. Query: `?status=booked` |
| PUT  | `/api/appointments/<id>/cancel` | ✅ | Cancel an appointment |

**Book payload:**
```json
{ "doctor_id": 1, "scheduled_at": "2025-06-01T10:00:00", "mode": "in_person", "notes": "Fever since 2 days" }
```

### Medicines
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/medicines` | — | List medicines. Query: `?category=Antibiotic` |
| GET | `/api/medicines/search?q=para` | — | Search by name or generic (min 2 chars) |

### Pharmacy
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/pharmacy` | — | List pharmacies. Query: `?village=Nabha` |
| GET | `/api/pharmacy/<id>/stock` | — | Stock for a pharmacy (includes low/out-of-stock alerts) |

### Symptom Checker
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/symptom-check` | — | Triage symptoms |

**Payload:**
```json
{ "symptoms": ["chest pain", "sweating"] }
```
**Response:**
```json
{
  "urgency": "CRITICAL",
  "specialist": "Cardiologist",
  "advice": "Call emergency services immediately.",
  "icd10": "I20-I25",
  "red_flags": ["Breathlessness", "Pain radiating to arm"],
  "matched_symptoms": ["chest pain", "sweating"]
}
```

### Health Records
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/api/records/<patient_id>` | ✅ | Get patient records. Query: `?type=lab_report` |
| POST | `/api/records` | ✅ | Create a new health record |

---

## 🗄️ Database Schema

SQLite · 7 tables · WAL mode · Foreign keys ON

| Table | Purpose |
|---|---|
| `users` | Patients, doctors, admins |
| `doctors` | Doctor profiles linked to users |
| `appointments` | Bookings with status tracking |
| `medicines` | Medicine catalogue |
| `pharmacies` | Pharmacy locations with GPS coords |
| `pharmacy_stock` | Stock levels and prices per pharmacy |
| `health_records` | Consultation notes, lab reports, diagnoses |
| `symptom_rules` | Triage rules with keywords, urgency, ICD-10 |

---

## 🩺 Symptom Checker — How It Works

1. Input symptoms are lowercased and matched against a **synonym map** covering English, Hindi, and Punjabi transliterations (e.g. `"bukhar"` → `fever`, `"seene mein dard"` → `chest pain`)
2. Normalised symptoms are matched against `symptom_rules` in the database (keyword list per rule)
3. The **highest-urgency** matching rule wins
4. Returns: urgency level · recommended specialist · plain-language advice · ICD-10 code · red flag warnings

Urgency levels: `CRITICAL` → `HIGH` → `MEDIUM` → `LOW`

---

## ⚙️ Configuration

All config is at the top of `app.py`:

```python
SECRET_KEY = secrets.token_hex(32)   # Rotates on restart — set via env var in production
DB_PATH    = "nabhahealth.db"        # SQLite file path
JWT_EXP_H  = 48                      # Token validity in hours
```

**For production**, replace `SECRET_KEY` with a stable environment variable:
```python
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
```

---

## 📦 Dependencies

```
flask>=3.0
flask-cors>=4.0
flask-sqlalchemy>=3.1
flask-jwt-extended>=4.6
bcrypt>=4.1
PyJWT
werkzeug
```

Install: `pip install -r requirements.txt`

---

## 🛠️ Development Notes

- **No build step** — plain HTML/CSS/JS, no bundler needed
- **Offline-capable** — symptom checker works with no internet after first boot
- **Low-bandwidth optimised** — minimal dependencies, small payloads
- **Single-file backend** — entire Flask app runs from `app.py` for easy deployment
- **SQLite** — no database server needed; suitable for village-level deployments

---

## 📄 License

Built for rural healthcare access in Punjab, India.  
Contact: admin@nabha.health

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](docs/contributing.md) and open a PR.
