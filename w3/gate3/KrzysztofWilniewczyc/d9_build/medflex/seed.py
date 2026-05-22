"""Seed data: hospitals, nurses, past acceptance history.

Crafted to make the spec's worked example (§6) discriminating:
- Nurse N: 3 prior shifts at Hospital A + paediatric-allergy profile note
- Nurse M: stronger credentials, no Hospital A history
- Plus extra nurses to test eligibility filtering, DNR, expiry.
"""
from datetime import datetime, timedelta

from .entities import HospitalAcceptanceRecord, Nurse


NOW = datetime(2026, 5, 13, 10, 0, 0)  # fixed clock for deterministic demo


HOSPITALS = {
    "hosp_A": {"name": "St. Jude Memorial (Hospital A)", "city": "Boston"},
    "hosp_B": {"name": "Riverside General (Hospital B)", "city": "Cambridge"},
}


NURSES: list[Nurse] = [
    Nurse(
        id="n_NICOLE",   # "Nurse N" in the worked example
        name="Nicole Park, RN",
        specialties=["ICU", "PICU"],
        credentials=["RN", "ICU", "BLS", "ACLS"],
        credential_expiry=NOW + timedelta(days=180),
        available=True,
        location="Boston",
        distance_km=3.2,
        profile_notes=(
            "Six years ICU experience. Two prior shifts involving paediatric "
            "patients with medication allergy protocols. Calm under pressure, "
            "preferred night-shift availability."
        ),
    ),
    Nurse(
        id="n_MARK",     # "Nurse M" in the worked example
        name="Mark Hollis, RN",
        specialties=["ICU"],
        credentials=["RN", "ICU", "BLS", "ACLS", "CCRN"],  # stronger credentials
        credential_expiry=NOW + timedelta(days=400),
        available=True,
        location="Boston",
        distance_km=4.0,
        profile_notes=(
            "Eight years ICU experience. Strong adult cardiac background. "
            "No paediatric notes on file."
        ),
    ),
    Nurse(
        id="n_PAULA",
        name="Paula Reyes, RN",
        specialties=["ICU"],
        credentials=["RN", "ICU", "BLS"],
        credential_expiry=NOW - timedelta(days=1),     # already expired (compliance flag)
        available=True,
        location="Boston",
        distance_km=6.0,
        profile_notes="Recently completed ICU rotation. Credentials renewal in progress.",
    ),
    Nurse(
        id="n_QUINN",
        name="Quinn O'Hara, RN",
        specialties=["ICU"],
        credentials=["RN", "ICU", "BLS", "ACLS"],
        credential_expiry=NOW + timedelta(days=200),
        available=False,                                # not available
        location="Boston",
        distance_km=2.5,
        profile_notes="Out on PTO this week.",
    ),
    Nurse(
        id="n_RAY",
        name="Ray Chen, RN",
        specialties=["ICU"],
        credentials=["RN", "ICU", "BLS", "ACLS"],
        credential_expiry=NOW + timedelta(days=90),
        available=True,
        location="Boston",
        distance_km=5.5,
        dnr_hospitals=["hosp_A"],                       # do-not-rotate at A
        profile_notes="Prior conflict noted; DNR with Hospital A.",
    ),
]


# Hospital acceptance history (D#4a step 4 input). The signal: Hospital A has
# previously accepted Nicole for similar requests.
ACCEPTANCE_HISTORY: list[HospitalAcceptanceRecord] = [
    HospitalAcceptanceRecord("hosp_A", "n_NICOLE", True, NOW - timedelta(days=60),
                              "ICU night, paediatric admit"),
    HospitalAcceptanceRecord("hosp_A", "n_NICOLE", True, NOW - timedelta(days=130),
                              "ICU night"),
    HospitalAcceptanceRecord("hosp_A", "n_NICOLE", True, NOW - timedelta(days=220),
                              "ICU day"),
    HospitalAcceptanceRecord("hosp_B", "n_MARK",   True, NOW - timedelta(days=30),
                              "ICU cardiac"),
]


def hospital_history(hospital_id: str, nurse_id: str) -> list[HospitalAcceptanceRecord]:
    return [
        r for r in ACCEPTANCE_HISTORY
        if r.hospital_id == hospital_id and r.nurse_id == nurse_id and r.accepted
    ]
