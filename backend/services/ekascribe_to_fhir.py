from datetime import datetime
from typing import Any

from scribe2fhir.core import (
    FHIRDocumentBuilder,
    Severity,
    FindingStatus,
    ConditionClinicalStatus,
    Interpretation,
    AllergyCategory,
)


def _get_nested(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if isinstance(data, dict) and key in data:
            return data[key]
    return None


def _extract_payload(ekascribe_result: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        ekascribe_result.get("result"),
        ekascribe_result.get("output"),
        ekascribe_result.get("data"),
        ekascribe_result.get("transcription"),
        ekascribe_result.get("emr"),
        ekascribe_result,
    ]
    for c in candidates:
        if isinstance(c, dict):
            return c
    return ekascribe_result


def _safe_str(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip() or None
    return str(v)


def _safe_list(v: Any) -> list:
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def _normalize_identifiers(v: Any) -> list[tuple[str, str]] | None:
    if v is None:
        return None
    if not isinstance(v, (list, tuple)):
        return None
    out = []
    for item in v:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append((str(item[0]), _safe_str(item[1]) or "unknown"))
        elif isinstance(item, dict):
            val = item.get("value") or item.get("id") or item.get("identifier")
            typ = item.get("type") or item.get("system")
            if val is not None:
                out.append((str(val), _safe_str(typ) or "unknown"))
    return out if out else None


def ekascribe_result_to_fhir_bundle(ekascribe_result: dict[str, Any]) -> dict[str, Any]:
    payload = _extract_payload(ekascribe_result)
    builder = FHIRDocumentBuilder()

    patient = _get_nested(payload, "patient", "patient_info", "patientInfo") or payload
    if isinstance(patient, dict):
        name = _safe_str(
            patient.get("name") or patient.get("patient_name")
            or (" ".join(filter(None, [patient.get("first_name"), patient.get("last_name")])).strip() or None)
        )
        if name:
            age_val = patient.get("age")
            age = (int(age_val), "years") if isinstance(age_val, (int, float)) else None
            if age is None and isinstance(patient.get("age"), dict):
                a = patient["age"]
                age = (int(a.get("value", 0)), _safe_str(a.get("unit")) or "years")
            builder.add_patient(
                name=name,
                age=age,
                gender=_safe_str(patient.get("gender") or patient.get("sex")),
                identifiers=_normalize_identifiers(patient.get("identifiers")),
                address=_safe_str(patient.get("address")),
                phone=_safe_str(patient.get("phone") or patient.get("mobile") or patient.get("contact")),
                email=_safe_str(patient.get("email")),
            )

    encounter = _get_nested(payload, "encounter", "encounter_info", "encounterInfo") or payload
    if isinstance(encounter, dict) and (encounter.get("encounter_type") or encounter.get("facility_name") or encounter.get("period_start")):
        period_start = encounter.get("period_start") or encounter.get("encounter_date") or encounter.get("start")
        if isinstance(period_start, str):
            try:
                period_start = datetime.fromisoformat(period_start.replace("Z", "+00:00"))
            except ValueError:
                period_start = None
        builder.add_encounter(
            encounter_class=_safe_str(encounter.get("encounter_class")) or "ambulatory",
            encounter_type=_safe_str(encounter.get("encounter_type") or encounter.get("type")),
            facility_name=_safe_str(encounter.get("facility_name") or encounter.get("facility") or encounter.get("location")),
            department=_safe_str(encounter.get("department")),
            period_start=period_start,
        )
    elif builder.patient:
        builder.add_encounter(
            encounter_class="ambulatory",
            encounter_type="Consultation",
            period_start=datetime.utcnow(),
        )

    for item in _safe_list(_get_nested(payload, "symptoms", "chief_complaints", "complaints")):
        if isinstance(item, dict):
            code = _safe_str(item.get("code") or item.get("name") or item.get("text"))
            if code:
                builder.add_symptom(
                    code=code,
                    severity=Severity(item.get("severity", "moderate").lower()) if isinstance(item.get("severity"), str) and item.get("severity").lower() in ("mild", "moderate", "severe") else None,
                    notes=_safe_str(item.get("notes") or item.get("description")),
                    finding_status=FindingStatus.PRESENT if item.get("present", True) else FindingStatus.ABSENT,
                )
        elif isinstance(item, str) and item.strip():
            builder.add_symptom(code=item.strip())

    for item in _safe_list(_get_nested(payload, "conditions", "diagnosis", "diagnoses", "medical_conditions")):
        if isinstance(item, dict):
            code = _safe_str(item.get("code") or item.get("condition_name") or item.get("name") or item.get("icd_code"))
            if code:
                builder.add_medical_condition_encountered(
                    code=code,
                    severity=Severity(item.get("severity", "mild").lower()) if isinstance(item.get("severity"), str) and item.get("severity").lower() in ("mild", "moderate", "severe") else None,
                    notes=_safe_str(item.get("notes")),
                )
        elif isinstance(item, str) and item.strip():
            builder.add_medical_condition_encountered(code=item.strip())

    for item in _safe_list(_get_nested(payload, "vitals", "vital_signs", "observations")):
        if isinstance(item, dict):
            code = _safe_str(item.get("code") or item.get("measurement_type") or item.get("name"))
            value = item.get("value") or item.get("systolic_value") or (f"{item.get('systolic_value')}/{item.get('diastolic_value')}" if item.get("diastolic_value") is not None else None)
            if code:
                builder.add_vital_finding(
                    code=code,
                    value=value,
                    unit=_safe_str(item.get("unit")),
                    interpretation=Interpretation(item.get("interpretation", "normal").lower()) if isinstance(item.get("interpretation"), str) and item.get("interpretation").lower() in ("normal", "high", "low", "abnormal") else None,
                )

    for item in _safe_list(_get_nested(payload, "medications", "medication_prescriptions", "prescriptions")):
        if isinstance(item, dict):
            med = _safe_str(item.get("medication") or item.get("medication_name") or item.get("name"))
            if med:
                builder.add_medication_prescribed(
                    medication=med,
                    dosage=None,
                    notes=_safe_str(item.get("dosage") or item.get("notes")),
                )
        elif isinstance(item, str) and item.strip():
            builder.add_medication_prescribed(medication=item.strip())

    for item in _safe_list(_get_nested(payload, "notes", "clinical_notes", "transcription_text")):
        if isinstance(item, dict):
            note = _safe_str(item.get("text") or item.get("note") or item.get("content"))
            if note:
                builder.add_notes(note=note, category=_safe_str(item.get("category")) or "clinical-note")
        elif isinstance(item, str) and item.strip():
            builder.add_notes(note=item.strip(), category="clinical-note")

    if not builder.patient:
        builder.add_patient(name="Unknown Patient")
        builder.add_encounter(encounter_class="ambulatory", encounter_type="Consultation", period_start=datetime.utcnow())

    raw_note = _safe_str(payload.get("raw") or payload.get("transcription")) or (str(ekascribe_result)[:2000] if not any((builder.observations, builder.conditions, builder.medication_requests)) else None)
    if raw_note:
        builder.add_notes(note=f"[EkaScribe raw]\n{raw_note}", category="source")

    return builder.convert_to_fhir()
