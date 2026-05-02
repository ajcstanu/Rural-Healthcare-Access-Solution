# 🏥 NabhaHealth — Rural Telemedicine Platform

> Connecting 173 villages around Nabha to qualified doctors, real-time medicine availability, and offline health records — even on 2G networks.

![NabhaHealth Banner](https://img.shields.io/badge/NabhaHealth-Rural%20Telemedicine-00c896?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Prototype-ffb547?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

---

## 🚨 Problem Statement

Nabha Civil Hospital serves **173 surrounding villages** but operates at less than 50% capacity — only **11 doctors for 23 sanctioned posts**. Rural patients:

- Travel long distances, often missing daily wages
- Arrive only to find specialists unavailable
- Cannot check medicine stock before visiting
- Have no digital health records → repeated tests, lost history
- Are restricted by poor roads, language barriers, and low connectivity

---

## 💡 Solution

**NabhaHealth** is a multilingual, offline-capable telemedicine web + mobile app that:

| Feature | Description |
|---|---|
| 📹 Video Consultations | WebRTC-based video calls with doctors, adaptive to 2G |
| 🤖 AI Symptom Checker | On-device (<500KB) model, works offline |
| 💊 Medicine Availability | Real-time pharmacy stock API, 30-min refresh |
| 📋 Digital Health Records | Encrypted, offline-ready via IndexedDB + PWA |
| 🌐 Multilingual | Punjabi, Hindi, English support throughout |
| 👨‍⚕️ Doctor Portal | Staff dashboard for queue, history, prescriptions |

---

## 📁 Project Structure

```
nabha-health/
├── index.html               # Main frontend (single-file prototype)
├── README.md
│
├── frontend/                # React Native mobile app (future)
│   ├── src/
│   │   ├── screens/
│   │   │   ├── HomeScreen.jsx
│   │   │   ├── ConsultScreen.jsx
│   │   │   ├── SymptomChecker.jsx
│   │   │   ├── MedicineTracker.jsx
│   │   │   └── HealthRecords.jsx
│   │   ├── components/
│   │   │   ├── VideoCall.jsx
│   │   │   ├── DoctorCard.jsx
│   │   │   ├── ChatBot.jsx
│   │   │   └── OfflineBadge.jsx
│   │   ├── i18n/
│   │   │   ├── en.json
│   │   │   ├── pa.json       # Punjabi
│   │   │   └── hi.json       # Hindi
│   │   └── utils/
│   │       ├── offlineSync.js
│   │       └── lowBandwidth.js
│   └── package.json
│
├── backend/                 # Node.js / Express API
│   ├── src/
│   │   ├── routes/
│   │   │   ├── doctors.js
│   │   │   ├── appointments.js
│   │   │   ├── medicines.js
│   │   │   ├── records.js
│   │   │   └── symptomAI.js
│   │   ├── models/
│   │   │   ├── Patient.js
│   │   │   ├── Doctor.js
│   │   │   ├── Medicine.js
│   │   │   └── Appointment.js
│   │   ├── services/
│   │   │   ├── webrtcService.js
│   │   │   ├── smsService.js    # Twilio for SMS alerts
│   │   │   └── aiService.js
│   │   └── app.js
│   ├── .env.example
│   └── package.json
│
├── ai-model/                # Lightweight symptom checker
│   ├── train.py
│   ├── model.onnx            # <500KB ONNX model
│   ├── symptoms_dataset.csv
│   └── inference.js          # Browser-side inference
│
└── docs/
    ├── architecture.md
    ├── api-reference.md
    └── deployment.md
```

---

## 🛠 Tech Stack

### Frontend / Mobile
- **React Native** — Cross-platform mobile app (iOS + Android)
- **PWA** — Offline-capable web version
- **WebRTC** — Real-time video consultations
- **IndexedDB** — Client-side offline health record storage
- **i18next** — Multilingual support (Punjabi, Hindi, English)

### Backend
- **Node.js + Express** — REST API
- **PostgreSQL** — Relational data (doctors, appointments, records)
- **Redis** — Session caching and real-time queue
- **Twilio** — SMS notifications for appointments
- **Firebase** — Push notifications

### AI / ML
- **TensorFlow Lite / ONNX** — On-device symptom triage (<500KB)
- **Python (scikit-learn)** — Model training pipeline

### DevOps
- **Docker + Docker Compose** — Containerized deployment
- **GitHub Actions** — CI/CD
- **Nginx** — Reverse proxy
- **Let's Encrypt** — HTTPS

---

## 🚀 Quick Start

### Prerequisites
- Node.js v18+
- PostgreSQL 14+
- Redis

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/nabha-health.git
cd nabha-health
```

### 2. Backend Setup
```bash
cd backend
cp .env.example .env        # Fill in DB credentials, API keys
npm install
npm run migrate             # Run DB migrations
npm run seed                # Seed test doctors/medicines data
npm start
```

### 3. Frontend (Web Prototype)
```bash
# Open directly in browser
open index.html

# Or serve locally
npx serve .
```

### 4. Run with Docker
```bash
docker-compose up --build
# App available at http://localhost:3000
```

---

## 🌐 API Endpoints (Key)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/doctors` | List available doctors with status |
| POST | `/api/appointments` | Book a consultation slot |
| GET | `/api/medicines?pharmacy=1` | Get medicine stock by pharmacy |
| POST | `/api/symptom-check` | AI triage (text → urgency + advice) |
| GET | `/api/records/:patientId` | Fetch encrypted health records |
| PUT | `/api/records/:patientId/sync` | Sync offline records to server |

---

## 📱 Key Features — Technical Details

### 📶 Offline-First Architecture
```javascript
// Service Worker caches all critical assets
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});

// IndexedDB for health records
const db = await openDB('nabha-health', 1, {
  upgrade(db) {
    db.createObjectStore('records', { keyPath: 'patientId' });
    db.createObjectStore('pendingSync', { autoIncrement: true });
  }
});
```

### 🤖 On-Device Symptom Checker
```javascript
// Load ONNX model (<500KB) once, run inference locally
import * as ort from 'onnxruntime-web';
const session = await ort.InferenceSession.create('./model.onnx');
const output = await session.run({ symptoms: encodedInput });
// Returns: { urgency: 'HIGH'|'MODERATE'|'LOW', recommended_specialist: '...' }
```

### 📹 Low-Bandwidth Video
```javascript
// Adaptive bitrate for 2G/3G connections
const constraints = {
  video: { width: { ideal: 320 }, height: { ideal: 240 }, frameRate: { max: 15 } },
  audio: { echoCancellation: true, noiseSuppression: true }
};
```

---

## 👥 Target Stakeholders

| Stakeholder | How they use NabhaHealth |
|---|---|
| 🧑‍🌾 Rural Patients | Book consultations, check medicines, view records |
| 👨‍⚕️ Hospital Staff | Manage queue, write prescriptions, access patient history |
| 🏥 Punjab Health Dept | Analytics dashboard, coverage reports |
| 💊 Local Pharmacies | Update stock, receive low-stock alerts |
| 👨‍👩‍👧 Daily-wage Workers | Skip travel for minor issues, consult from village |

---

## 📊 Impact Numbers

- 🏘️ **173 villages** to be served in Phase 1
- 👨‍⚕️ **11 active doctors** currently onboarded
- 📶 **31% of rural Punjab** has internet → offline mode critical
- 📈 Telemedicine in India growing at **31% CAGR (2020–2025)**

---

## 🌍 Scalability Plan

- **Phase 1**: Nabha block (173 villages) — Pilot
- **Phase 2**: All of Patiala district
- **Phase 3**: Pan-Punjab rollout via Punjab Health Dept
- **Phase 4**: Open-source model for other rural districts in India

---

## 🔐 Privacy & Security

- All health records encrypted with AES-256
- HIPAA/DISHA-compliant data handling
- Doctor verification via Punjab Medical Council registry
- No health data shared with third parties

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](docs/contributing.md) and open a PR.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

