from __future__ import annotations

import base64
import json
import logging
from datetime import datetime
from typing import Any

log = logging.getLogger(__name__)


def _get_nested(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if isinstance(data, dict) and key in data:
            return data[key]
    return None


def _decode_eka_emr_value(b64_value: str) -> dict[str, Any] | None:
    if not b64_value or not isinstance(b64_value, str):
        return None
    try:
        raw = base64.b64decode(b64_value, validate=True)
        decoded = json.loads(raw.decode("utf-8"))
        if isinstance(decoded, dict):
            return decoded.get("prescription") or decoded
        return None
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _extract_eka_emr_payload(ekascribe_result: dict[str, Any]) -> dict[str, Any] | None:
    data = ekascribe_result.get("data") or ekascribe_result
    if not isinstance(data, dict):
        return None
    for key in ("output", "template_results"):
        items = data.get(key)
        if key == "template_results" and isinstance(items, dict):
            items = items.get("integration")
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            typ = item.get("type") or ""
            name = (item.get("name") or "") if isinstance(item.get("name"), str) else ""
            value = item.get("value")
            if (typ in ("eka_emr", "json") or "Eka EMR" in name) and value:
                payload = _decode_eka_emr_value(value)
                if payload:
                    return payload
    return None


def get_decoded_prescription(ekascribe_result: dict[str, Any]) -> dict[str, Any] | None:
    return _extract_eka_emr_payload(ekascribe_result)


def _extract_payload(ekascribe_result: dict[str, Any]) -> dict[str, Any]:
    eka = _extract_eka_emr_payload(ekascribe_result)
    if eka:
        return eka
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


def _eka_severity_from_properties(properties: dict[str, Any]) -> Severity | None:
    from scribe2fhir.core import Severity as _Severity
    if not isinstance(properties, dict):
        return None
    for v in properties.values():
        if isinstance(v, dict) and _safe_str(v.get("name")) == "Severity":
            sel = v.get("selection") or []
            if isinstance(sel, list) and sel and isinstance(sel[0], dict):
                val = _safe_str(sel[0].get("value"))
                if val and val.lower() in ("mild", "moderate", "severe"):
                    return _Severity(val.lower())
    return None


def _eka_details_from_properties(properties: dict[str, Any]) -> str | None:
    if not isinstance(properties, dict):
        return None
    for v in properties.values():
        if isinstance(v, dict) and _safe_str(v.get("name")) == "Details":
            sel = v.get("selection") or []
            if isinstance(sel, list) and sel and isinstance(sel[0], dict):
                return _safe_str(sel[0].get("value"))
    return None


def _eka_vital_value(item: dict[str, Any]) -> tuple[Any, str | None]:
    val = item.get("value")
    if isinstance(val, dict):
        qt = val.get("qt")
        unit = _safe_str(val.get("unit"))
        return (qt, unit)
    return (item.get("value"), _safe_str(item.get("unit")))


def ekascribe_result_to_fhir_bundle(ekascribe_result: dict[str, Any]) -> dict[str, Any]:
    from scribe2fhir.core import (
        FHIRDocumentBuilder,
        Severity,
        FindingStatus,
        ConditionClinicalStatus,
        Interpretation,
        AllergyCategory,
    )
    payload = _extract_payload(ekascribe_result)
    try:
        log.info("Eka EMR raw JSON (decoded prescription): %s", json.dumps(payload, indent=2, default=str))
    except Exception:
        log.info("Eka EMR raw payload keys: %s", list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__)
    builder = FHIRDocumentBuilder()

    patient = _get_nested(payload, "patientDemographics", "patient", "patient_info", "patientInfo") or payload
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
                props = item.get("properties") or {}
                sev = _eka_severity_from_properties(props)
                details = _eka_details_from_properties(props) if not sev else None
                builder.add_symptom(
                    code=code,
                    severity=sev,
                    notes=details or _safe_str(item.get("notes") or item.get("description")),
                    finding_status=FindingStatus.PRESENT if item.get("present", True) else FindingStatus.ABSENT,
                )
        elif isinstance(item, str) and item.strip():
            builder.add_symptom(code=item.strip())

    history = _get_nested(payload, "medicalHistory", "medical_history") or {}
    patient_history = (history.get("patientHistory") or history) if isinstance(history, dict) else {}
    if isinstance(patient_history, dict):
        for item in _safe_list(patient_history.get("patientMedicalConditions") or patient_history.get("patient_medical_conditions")):
            if isinstance(item, dict):
                code = _safe_str(item.get("name") or item.get("code"))
                if code:
                    builder.add_medical_condition_history(
                        code=code,
                        notes=_safe_str(item.get("notes")),
                        clinical_status=ConditionClinicalStatus.ACTIVE if _safe_str(item.get("status")) == "Active" else ConditionClinicalStatus.INACTIVE,
                    )
            elif isinstance(item, str) and item.strip():
                builder.add_medical_condition_history(code=item.strip())

        for item in _safe_list(patient_history.get("currentMedications") or patient_history.get("current_medications")):
            if isinstance(item, dict):
                med = _safe_str(item.get("name") or item.get("code"))
                if med:
                    builder.add_medication_history(
                        medication=med,
                        notes=_safe_str(item.get("notes")),
                        status=_safe_str(item.get("status")) or "active",
                    )
            elif isinstance(item, str) and item.strip():
                builder.add_medication_history(medication=item.strip())

        for item in _safe_list(patient_history.get("familyHistory") or patient_history.get("family_history")):
            if isinstance(item, dict):
                code = _safe_str(item.get("name") or item.get("code"))
                who = _safe_str(item.get("who"))
                if code:
                    builder.add_family_history(condition=code, relation=who)

        for item in _safe_list(patient_history.get("lifestyleHabits") or patient_history.get("lifestyle_habits")):
            if isinstance(item, dict):
                code = _safe_str(item.get("name") or item.get("code"))
                if code:
                    builder.add_lifestyle_history(
                        code=code,
                        status_value=_safe_str(item.get("status")),
                        notes=_safe_str(item.get("notes")),
                    )

        for item in _safe_list(patient_history.get("foodOtherAllergy") or patient_history.get("food_other_allergy")):
            if isinstance(item, dict):
                code = _safe_str(item.get("name") or item.get("code"))
                if code:
                    builder.add_allergy_history(
                        code=code,
                        category=AllergyCategory.FOOD,
                        clinical_status=_safe_str(item.get("status")) or "inactive",
                    )
            elif isinstance(item, str) and item.strip():
                builder.add_allergy_history(code=item.strip(), category=AllergyCategory.FOOD)

        for item in _safe_list(patient_history.get("drugAllergy") or patient_history.get("drug_allergy")):
            if isinstance(item, dict):
                code = _safe_str(item.get("name") or item.get("code"))
                if code:
                    builder.add_allergy_history(
                        code=code,
                        category=AllergyCategory.MEDICATION,
                        clinical_status=_safe_str(item.get("status")) or "inactive",
                    )
            elif isinstance(item, str) and item.strip():
                builder.add_allergy_history(code=item.strip(), category=AllergyCategory.MEDICATION)

    for item in _safe_list(_get_nested(payload, "examinations", "examination")):
        if isinstance(item, dict):
            code = _safe_str(item.get("name") or item.get("code"))
            notes = _safe_str(item.get("notes"))
            if code:
                builder.add_examination_finding(code=code, value=notes, notes=notes)

    for item in _safe_list(_get_nested(payload, "vitals", "vital_signs", "observations")):
        if isinstance(item, dict):
            code = _safe_str(item.get("dis_name") or item.get("name") or item.get("code"))
            val, unit = _eka_vital_value(item)
            if code and val is not None:
                builder.add_vital_finding(code=code, value=val, unit=unit)

    for item in _safe_list(_get_nested(payload, "diagnosis", "conditions", "diagnoses", "medical_conditions")):
        if isinstance(item, dict):
            code = _safe_str(item.get("code") or item.get("condition_name") or item.get("name") or item.get("icd_code"))
            if code:
                builder.add_medical_condition_encountered(
                    code=code,
                    severity=_eka_severity_from_properties(item.get("properties") or {}),
                    notes=_eka_details_from_properties(item.get("properties") or {}),
                )
        elif isinstance(item, str) and item.strip():
            builder.add_medical_condition_encountered(code=item.strip())

    for item in _safe_list(_get_nested(payload, "medications", "medication_prescriptions", "prescriptions")):
        if isinstance(item, dict):
            med = _safe_str(item.get("medication") or item.get("medication_name") or item.get("name"))
            if med:
                freq = item.get("frequency")
                dur = item.get("duration")
                dosage_str = None
                if isinstance(freq, dict):
                    dosage_str = _safe_str(freq.get("custom"))
                if isinstance(dur, dict):
                    d = _safe_str(dur.get("custom"))
                    if d:
                        dosage_str = f"{dosage_str or ''} {d}".strip() or dosage_str
                builder.add_medication_prescribed(
                    medication=med,
                    dosage=None,
                    notes=_safe_str(item.get("instruction")) or dosage_str,
                )
        elif isinstance(item, str) and item.strip():
            builder.add_medication_prescribed(medication=item.strip())

    for item in _safe_list(_get_nested(payload, "advices", "advice")):
        if isinstance(item, dict):
            text = _safe_str(item.get("text") or item.get("parsedText"))
            if text:
                builder.add_advice(note=text)
        elif isinstance(item, str) and item.strip():
            builder.add_advice(note=item.strip())

    followup = _get_nested(payload, "followup", "follow_up")
    if isinstance(followup, dict):
        date_val = followup.get("date")
        notes_val = _safe_str(followup.get("notes"))
        if date_val or notes_val:
            try:
                dt = datetime.fromisoformat(str(date_val).replace("Z", "+00:00")) if date_val else None
            except (ValueError, TypeError):
                dt = None
            builder.add_followup(date=dt, notes=notes_val)

    prescription_notes = _get_nested(payload, "prescriptionNotes", "prescription_notes")
    if isinstance(prescription_notes, dict):
        text = _safe_str(prescription_notes.get("text") or prescription_notes.get("parsedText"))
        if text:
            builder.add_notes(note=text, category="clinical-note")

    for item in _safe_list(_get_nested(payload, "labTests", "lab_tests", "lab_tests_prescribed")):
        if isinstance(item, dict):
            code = _safe_str(item.get("name") or item.get("common_name") or item.get("code"))
            remark = _safe_str(item.get("remark"))
            if code:
                builder.add_test_prescribed(code=code, notes=remark)

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
