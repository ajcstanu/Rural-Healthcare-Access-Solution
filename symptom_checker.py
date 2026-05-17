"""
NabhaHealth — AI Symptom Checker
=================================
Lightweight rule-based + Naive Bayes classifier.
Works offline after first boot. No external API needed.
Optimised for low-bandwidth, low-resource devices.

Accepts: list of symptom strings (any of en / hi / pa transliteration)
Returns: urgency, recommended_specialist, advice, red_flags
"""

import re
from typing import List, Dict, Any


# ── Symptom synonym normalisation (covers common Punjabi/Hindi transliterations)
SYNONYM_MAP = {
    # English variants
    "headache": ["headache","head ache","sir dard","sar dard","sardard"],
    "fever": ["fever","bukhar","bukhaar","tap","taap","temperature"],
    "cough": ["cough","khansi","khaansi","khasi"],
    "chest pain": ["chest pain","seene mein dard","sina dard","chest dard"],
    "breathlessness": ["breathless","shortness of breath","saans nahi","sans lena mushkil","dyspnoea","dyspnea"],
    "stomach pain": ["stomach pain","pet dard","pait dard","abdominal pain","belly pain"],
    "diarrhoea": ["diarrhoea","diarrhea","loose motions","daast","loose stool","latrine"],
    "vomiting": ["vomiting","ulti","udhne","nausea","matli"],
    "body pain": ["body pain","badan dard","body ache","muscle pain","maspeshiyon mein dard"],
    "skin rash": ["rash","skin rash","kharish","khujli","itching"],
    "weakness": ["weakness","kamzori","thakaan","fatigue","tired"],
    "sore throat": ["sore throat","gala dard","gale mein kharash","throat pain"],
    "eye pain": ["eye pain","aankh dard","aankhon mein jalan"],
    "joint pain": ["joint pain","jodo ka dard","ghutne dard","arthritis"],
    "urinary problem": ["urinary","urine problem","peshab mein jalan","dysuria","frequent urination"],
    "unconscious": ["unconscious","behosh","faint","collapse","gir gaya"],
    "seizure": ["seizure","dora","fits","convulsion","mirgi"],
    "bleeding": ["bleeding","khoon","blood","rakta"],
    "swelling": ["swelling","sujan","sooja hua","edema"],
    "diabetes symptoms": ["sugar","diabetes","madhumeh","pyaas","thirst","frequent urination"],
}

# ── Knowledge base: symptom_set → (urgency, specialist, advice, red_flags)
RULES = [
    # ── Critical / Emergency ────────────────────────────────────────────
    {
        "match_any": ["chest pain", "breathlessness"],
        "urgency": "CRITICAL",
        "specialist": "Emergency / Cardiologist",
        "advice": "Seek emergency care immediately. Do not wait. Call 108 now.",
        "red_flags": ["Heart attack signs", "Pulmonary embolism"],
        "icd10": "I21 / J98",
    },
    {
        "match_any": ["unconscious", "seizure"],
        "urgency": "CRITICAL",
        "specialist": "Emergency / Neurologist",
        "advice": "Call 108 immediately. Keep patient in recovery position.",
        "red_flags": ["Stroke", "Epilepsy", "Brain bleed"],
        "icd10": "G41 / R55",
    },
    {
        "match_all": ["bleeding"],
        "urgency": "HIGH",
        "specialist": "Emergency / Surgeon",
        "advice": "Apply pressure to wound. Go to hospital immediately if bleeding is heavy.",
        "red_flags": ["Haemorrhage", "Internal bleeding"],
        "icd10": "T14.5",
    },

    # ── High urgency ─────────────────────────────────────────────────────
    {
        "match_all": ["fever", "body pain", "headache"],
        "urgency": "HIGH",
        "specialist": "General Physician / Infectious Disease",
        "advice": "Could be dengue, malaria or typhoid. Visit hospital within 24 hours. Take Paracetamol for fever.",
        "red_flags": ["Dengue", "Malaria", "Typhoid", "Meningitis"],
        "icd10": "A90 / B50",
    },
    {
        "match_all": ["fever", "cough", "breathlessness"],
        "urgency": "HIGH",
        "specialist": "Pulmonologist / General Physician",
        "advice": "Possible pneumonia or TB. Visit hospital soon. Wear a mask.",
        "red_flags": ["Pneumonia", "Tuberculosis", "COVID-19"],
        "icd10": "J18 / A15",
    },
    {
        "match_all": ["stomach pain", "vomiting", "diarrhoea"],
        "urgency": "HIGH",
        "specialist": "Gastroenterologist / General Physician",
        "advice": "Risk of dehydration. Drink ORS solution. Visit hospital if symptoms persist > 24 hrs.",
        "red_flags": ["Cholera", "Acute Gastroenteritis", "Appendicitis"],
        "icd10": "K59 / A09",
    },

    # ── Moderate urgency ─────────────────────────────────────────────────
    {
        "match_any": ["fever"],
        "urgency": "MODERATE",
        "specialist": "General Physician",
        "advice": "Rest, drink fluids, take Paracetamol. If fever > 103°F or persists > 3 days, see a doctor.",
        "red_flags": ["Dengue (if rash appears)", "Malaria (if chills)"],
        "icd10": "R50",
    },
    {
        "match_any": ["cough", "sore throat"],
        "urgency": "MODERATE",
        "specialist": "General Physician / ENT",
        "advice": "Could be viral URTI. Gargle with warm salt water. See doctor if no improvement in 5 days.",
        "red_flags": ["Bacterial tonsillitis if high fever"],
        "icd10": "J06",
    },
    {
        "match_any": ["skin rash"],
        "urgency": "MODERATE",
        "specialist": "Dermatologist / General Physician",
        "advice": "Avoid scratching. Note if rash is spreading. Antihistamine may help. See doctor.",
        "red_flags": ["Meningococcal rash (non-blanching)", "Drug allergy"],
        "icd10": "L29 / R21",
    },
    {
        "match_any": ["joint pain"],
        "urgency": "LOW",
        "specialist": "Orthopaedist / Rheumatologist",
        "advice": "Rest affected joints. Warm compress may help. Book telemedicine consult.",
        "red_flags": ["Septic arthritis if fever + hot joint"],
        "icd10": "M13",
    },
    {
        "match_any": ["urinary problem"],
        "urgency": "MODERATE",
        "specialist": "Urologist / General Physician",
        "advice": "Drink plenty of water. Avoid spicy food. See doctor if pain or blood in urine.",
        "red_flags": ["Kidney infection (pyelonephritis)"],
        "icd10": "N39",
    },
    {
        "match_any": ["diabetes symptoms"],
        "urgency": "MODERATE",
        "specialist": "Endocrinologist / General Physician",
        "advice": "Check blood sugar if possible. Reduce sugar intake. Regular monitoring needed.",
        "red_flags": ["Diabetic ketoacidosis if vomiting + confusion"],
        "icd10": "E11",
    },

    # ── Low urgency ───────────────────────────────────────────────────────
    {
        "match_any": ["headache"],
        "urgency": "LOW",
        "specialist": "General Physician",
        "advice": "Rest in a dark, quiet room. Drink water. Paracetamol may help. See doctor if persistent.",
        "red_flags": ["Thunderclap headache = emergency"],
        "icd10": "R51",
    },
    {
        "match_any": ["weakness", "body pain"],
        "urgency": "LOW",
        "specialist": "General Physician",
        "advice": "Rest and adequate nutrition. Could be viral illness or anaemia. Consult doctor.",
        "red_flags": ["If associated with chest pain or fever — HIGH urgency"],
        "icd10": "R53",
    },
    {
        "match_any": ["stomach pain"],
        "urgency": "LOW",
        "specialist": "Gastroenterologist / General Physician",
        "advice": "Avoid spicy and oily food. Light diet. See doctor if pain is severe or persistent.",
        "red_flags": ["Appendicitis if pain shifts to lower right"],
        "icd10": "R10",
    },
]

DEFAULT_RESULT = {
    "urgency":         "LOW",
    "specialist":      "General Physician",
    "advice":          "No specific pattern detected. Book a general consultation for evaluation.",
    "red_flags":       [],
    "icd10":           "Z00",
    "matched_symptoms": [],
}

URGENCY_ORDER = {"CRITICAL": 3, "HIGH": 2, "MODERATE": 1, "LOW": 0}


def normalise(text: str) -> List[str]:
    """Lower-case, strip, then map to canonical symptom names."""
    text  = text.lower().strip()
    found = set()
    for canonical, synonyms in SYNONYM_MAP.items():
        for syn in synonyms:
            if syn in text:
                found.add(canonical)
    return list(found)


def check_symptoms(symptom_input: List[str]) -> Dict[str, Any]:
    """
    symptom_input: list of strings (free-text or symptom names)
    Returns triage result dict.
    """
    # Normalise all inputs
    canonical = set()
    for s in symptom_input:
        canonical.update(normalise(s))

    if not canonical:
        # Try direct canonical match as fallback
        for s in symptom_input:
            s_clean = s.lower().strip()
            if s_clean in SYNONYM_MAP:
                canonical.add(s_clean)

    best      = None
    best_rank = -1

    for rule in RULES:
        match_all = rule.get("match_all", [])
        match_any = rule.get("match_any", [])

        hit = False
        if match_all and all(s in canonical for s in match_all):
            hit = True
        if match_any and any(s in canonical for s in match_any):
            hit = True

        if hit:
            rank = URGENCY_ORDER.get(rule["urgency"], 0)
            if rank > best_rank:
                best_rank = rank
                best      = rule

    if best is None:
        result = dict(DEFAULT_RESULT)
    else:
        result = {
            "urgency":    best["urgency"],
            "specialist": best["specialist"],
            "advice":     best["advice"],
            "red_flags":  best.get("red_flags", []),
            "icd10":      best.get("icd10", ""),
        }

    result["matched_symptoms"] = list(canonical)
    result["disclaimer"] = (
        "This is AI-assisted triage only — NOT a medical diagnosis. "
        "Always consult a qualified doctor, especially for CRITICAL or HIGH urgency."
    )
    return result
