"""
NabhaHealth — SQLAlchemy ORM Models
"""

from datetime import datetime
from models.db import db


# ══════════════════════════════════════════════════════════════════
# User  (patients, doctors, pharmacy staff, admins)
# ══════════════════════════════════════════════════════════════════

class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(15),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20),  default="patient")   # patient | doctor | pharmacy | admin
    language      = db.Column(db.String(5),   default="hi")        # en | hi | pa
    village       = db.Column(db.String(120), nullable=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    # relationships
    patient_records    = db.relationship("HealthRecord",  foreign_keys="HealthRecord.patient_id",  back_populates="patient",  lazy="dynamic")
    doctor_records     = db.relationship("HealthRecord",  foreign_keys="HealthRecord.doctor_id",   back_populates="doctor",   lazy="dynamic")
    patient_appts      = db.relationship("Appointment",   foreign_keys="Appointment.patient_id",   back_populates="patient",  lazy="dynamic")
    doctor_appts       = db.relationship("Appointment",   foreign_keys="Appointment.doctor_id",    back_populates="doctor",   lazy="dynamic")
    doctor_profile     = db.relationship("DoctorProfile", back_populates="user", uselist=False)

    def to_dict(self, include_sensitive=False):
        d = {
            "id":       self.id,
            "name":     self.name,
            "phone":    self.phone,
            "role":     self.role,
            "language": self.language,
            "village":  self.village,
        }
        if include_sensitive:
            d["email"] = self.email
        return d


# ══════════════════════════════════════════════════════════════════
# DoctorProfile
# ══════════════════════════════════════════════════════════════════

class DoctorProfile(db.Model):
    __tablename__ = "doctor_profiles"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    specialisation  = db.Column(db.String(100), default="General Physician")
    qualification   = db.Column(db.String(200))
    languages       = db.Column(db.String(100), default="Hindi,Punjabi")   # comma-sep
    is_available    = db.Column(db.Boolean,  default=True)
    available_days  = db.Column(db.String(100), default="Mon,Tue,Wed,Thu,Fri")
    slot_duration   = db.Column(db.Integer, default=15)   # minutes
    max_daily_appts = db.Column(db.Integer, default=30)
    photo_url       = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", back_populates="doctor_profile")

    def to_dict(self):
        u = self.user
        return {
            "id":              self.user_id,
            "name":            u.name,
            "specialisation":  self.specialisation,
            "qualification":   self.qualification,
            "languages":       self.languages.split(","),
            "is_available":    self.is_available,
            "available_days":  self.available_days.split(","),
            "slot_duration":   self.slot_duration,
            "max_daily_appts": self.max_daily_appts,
            "photo_url":       self.photo_url,
        }


# ══════════════════════════════════════════════════════════════════
# Appointment
# ══════════════════════════════════════════════════════════════════

class Appointment(db.Model):
    __tablename__ = "appointments"

    id           = db.Column(db.Integer, primary_key=True)
    patient_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    mode         = db.Column(db.String(20), default="video")  # video | in_person
    status       = db.Column(db.String(20), default="booked") # booked | completed | cancelled | no_show
    notes        = db.Column(db.Text, nullable=True)          # patient notes pre-visit
    prescription = db.Column(db.Text, nullable=True)          # doctor fills after visit
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", foreign_keys=[patient_id], back_populates="patient_appts")
    doctor  = db.relationship("User", foreign_keys=[doctor_id],  back_populates="doctor_appts")

    def to_dict(self):
        return {
            "id":           self.id,
            "patient":      {"id": self.patient_id, "name": self.patient.name},
            "doctor":       {"id": self.doctor_id,  "name": self.doctor.name,
                             "specialisation": self.doctor.doctor_profile.specialisation
                             if self.doctor.doctor_profile else ""},
            "scheduled_at": self.scheduled_at.isoformat(),
            "mode":         self.mode,
            "status":       self.status,
            "notes":        self.notes,
            "prescription": self.prescription,
        }


# ══════════════════════════════════════════════════════════════════
# HealthRecord
# ══════════════════════════════════════════════════════════════════

class HealthRecord(db.Model):
    __tablename__ = "health_records"

    id            = db.Column(db.Integer, primary_key=True)
    patient_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    record_type   = db.Column(db.String(50), default="consultation")  # consultation|lab|vaccination|prescription
    title         = db.Column(db.String(200))
    description   = db.Column(db.Text)
    diagnosis     = db.Column(db.String(300), nullable=True)
    medications   = db.Column(db.Text, nullable=True)   # JSON string
    attachments   = db.Column(db.Text, nullable=True)   # JSON list of file URLs
    is_synced     = db.Column(db.Boolean, default=True)  # False = created offline, not yet synced
    recorded_at   = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", foreign_keys=[patient_id], back_populates="patient_records")
    doctor  = db.relationship("User", foreign_keys=[doctor_id],  back_populates="doctor_records")

    def to_dict(self):
        return {
            "id":           self.id,
            "patient_id":   self.patient_id,
            "doctor_id":    self.doctor_id,
            "doctor_name":  self.doctor.name if self.doctor else None,
            "record_type":  self.record_type,
            "title":        self.title,
            "description":  self.description,
            "diagnosis":    self.diagnosis,
            "medications":  self.medications,
            "attachments":  self.attachments,
            "is_synced":    self.is_synced,
            "recorded_at":  self.recorded_at.isoformat(),
        }


# ══════════════════════════════════════════════════════════════════
# Pharmacy + Medicine
# ══════════════════════════════════════════════════════════════════

class Pharmacy(db.Model):
    __tablename__ = "pharmacies"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(150), nullable=False)
    address    = db.Column(db.String(300))
    village    = db.Column(db.String(120))
    phone      = db.Column(db.String(15))
    lat        = db.Column(db.Float, nullable=True)
    lng        = db.Column(db.Float, nullable=True)
    is_active  = db.Column(db.Boolean, default=True)

    stocks = db.relationship("MedicineStock", back_populates="pharmacy", lazy="dynamic")

    def to_dict(self):
        return {
            "id":       self.id,
            "name":     self.name,
            "address":  self.address,
            "village":  self.village,
            "phone":    self.phone,
            "lat":      self.lat,
            "lng":      self.lng,
        }


class Medicine(db.Model):
    __tablename__ = "medicines"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    generic     = db.Column(db.String(200))          # generic / salt name
    category    = db.Column(db.String(100))           # antibiotic / analgesic / …
    form        = db.Column(db.String(50))            # tablet / syrup / injection
    requires_rx = db.Column(db.Boolean, default=False)

    stocks = db.relationship("MedicineStock", back_populates="medicine", lazy="dynamic")

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "generic":     self.generic,
            "category":    self.category,
            "form":        self.form,
            "requires_rx": self.requires_rx,
        }


class MedicineStock(db.Model):
    __tablename__ = "medicine_stocks"

    id           = db.Column(db.Integer, primary_key=True)
    pharmacy_id  = db.Column(db.Integer, db.ForeignKey("pharmacies.id"), nullable=False)
    medicine_id  = db.Column(db.Integer, db.ForeignKey("medicines.id"),  nullable=False)
    quantity     = db.Column(db.Integer, default=0)
    unit_price   = db.Column(db.Float,   default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pharmacy = db.relationship("Pharmacy", back_populates="stocks")
    medicine = db.relationship("Medicine", back_populates="stocks")

    def to_dict(self):
        return {
            "pharmacy_id":   self.pharmacy_id,
            "pharmacy_name": self.pharmacy.name,
            "medicine_id":   self.medicine_id,
            "medicine_name": self.medicine.name,
            "generic":       self.medicine.generic,
            "quantity":      self.quantity,
            "unit_price":    self.unit_price,
            "in_stock":      self.quantity > 0,
            "last_updated":  self.last_updated.isoformat(),
        }
