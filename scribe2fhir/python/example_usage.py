"""
Complete Example - Demonstrates all FHIR SDK features.

This example mimics a real prescription pad scenario with all fields.
"""

import json
from datetime import datetime, timedelta

from scribe2fhir.core import (
    FHIRDocumentBuilder,
    DosageBuilder,
    Severity,
    Laterality,
    FindingStatus,
    ConditionClinicalStatus,
    MedicationStatementStatus,
    RouteOfAdministration,
    EventTiming,
    Interpretation,
    AllergyCategory,
    AllergyCriticality,
)


def main():
    # Create a new document builder
    builder = FHIRDocumentBuilder()
    
    # =========================================================================
    # PATIENT INFORMATION
    # =========================================================================
    builder.add_patient(
        name="Rahul Sharma",
        age=(30, "years"),
        gender="male",
        identifiers=[
            ("ABHA-1234567890", "ABHA"),
            ("MRN-001234", "MRN"),
            ("9876543210", "mobile")
        ],
        address="123 Main Street, Koramangala, Bangalore, Karnataka 560034",
        phone="9876543210",
        email="rahul.sharma@email.com"
    )
    
    # =========================================================================
    # ENCOUNTER INFORMATION
    # =========================================================================
    builder.add_encounter(
        encounter_class="ambulatory",
        encounter_type="Consultation",
        facility_name="Apollo Hospital",
        department="General Medicine",
        period_start=datetime.now()
    )
    
    # =========================================================================
    # SYMPTOMS (Chief Complaints)
    # =========================================================================
    builder.add_symptom(
        code="Headache",
        severity=Severity.MODERATE,
        laterality=Laterality.RIGHT,
        onset=datetime.now() - timedelta(days=1),
        notes="Higher in the morning and decreases towards the evening",
        finding_status=FindingStatus.PRESENT
    )
    
    builder.add_symptom(
        code="Leg pain",
        finding_status=FindingStatus.ABSENT  # Negative finding
    )
    
    # =========================================================================
    # DIAGNOSIS (Encounter Diagnoses)
    # =========================================================================
    builder.add_medical_condition_encountered(
        code="Type 2 diabetes",
        severity=Severity.MILD,
        onset=datetime.now() - timedelta(days=3)
    )
    
    builder.add_medical_condition_encountered(
        code="Cardiac condition",
        severity=Severity.MILD,
        laterality=Laterality.LEFT,
        notes="On the left portion"
    )
    
    # =========================================================================
    # VITALS
    # =========================================================================
    builder.add_vital_finding(
        code="Blood Pressure",
        value="120/80",
        unit="mmHg",
        interpretation=Interpretation.NORMAL
    )
    
    # =========================================================================
    # LAB FINDINGS (Lab Vitals)
    # =========================================================================
    builder.add_lab_finding(
        code="Hemoglobin",
        value=12,
        unit="percent",
        interpretation=Interpretation.NORMAL
    )
    
    builder.add_lab_finding(
        code="PCM test",
        interpretation=Interpretation.NORMAL
    )
    
    # =========================================================================
    # MEDICAL HISTORY
    # =========================================================================
    
    # Past Medical Conditions
    builder.add_medical_condition_history(
        code="Hypertension",
        clinical_status=ConditionClinicalStatus.ACTIVE,
        onset="2020-01-01",
        notes="Very severe"
    )
    
    # Current Medications (History)
    builder.add_medication_history(
        medication="Crocin 600",
        status=MedicationStatementStatus.ACTIVE,
        effective_start=datetime.now() - timedelta(days=90),
        notes="Every week once"
    )
    
    # Family History
    builder.add_family_history(
        condition="Hypertension",
        relation="Father",
        onset="1997",
        status="completed"
    )
    
    builder.add_family_history(
        condition="Type 2 diabetes",
        relation="Mother",
        status="completed",
        deceased=True,
        notes="Mother is dead now"
    )
    
    # Lifestyle Habits
    builder.add_lifestyle_history(
        code="Smoking",
        status_value="Active"
    )
    
    builder.add_lifestyle_history(
        code="Drinking",
        status_value="Active",
        notes="Occasional drinker"
    )
    
    # Recent Travel History
    builder.add_lifestyle_history(
        code="Traveled to Singapore",
        status_value="Active",
        notes="Came back a couple of weeks ago"
    )
    
    # Allergies
    builder.add_allergy_history(
        code="Pollen allergy",
        category=AllergyCategory.ENVIRONMENT
    )
    
    builder.add_allergy_history(
        code="Paracetamol",
        category=AllergyCategory.MEDICATION
    )
    
    # Past Procedures
    builder.add_procedure_history(
        code="Vasectomy",
        status="completed"
    )
    
    # Vaccination History
    builder.add_immunisation_history(
        vaccine="COVID vaccine",
        notes="Done during the second wave of COVID"
    )
    
    # Examinations
    builder.add_examination_finding(
        code="Hand examination",
        value="Swollen"
    )
    
    # =========================================================================
    # LAB TESTS ORDERED
    # =========================================================================
    builder.add_test_prescribed(
        code="CBC test"
    )
    
    builder.add_test_prescribed(
        code="Fasting blood sugar test",
        notes="Should be done on empty stomach"
    )
    
    # =========================================================================
    # MEDICATIONS PRESCRIBED
    # =========================================================================
    builder.add_medication_prescribed(
        medication="Dolo 650 Tablet",
        dosage=DosageBuilder.build(
            dose_value=1,
            dose_unit="tablet",
            frequency=3,
            period=1,
            period_unit="d",
            route=RouteOfAdministration.ORAL,
            timing_code=EventTiming.AFTER_MEAL,
            text="Take 1 tablet three times daily after meals"
        ),
        duration_value=7,
        duration_unit="d",
        notes="Dose: 1 tablet"
    )
    
    # =========================================================================
    # FOLLOW-UP
    # =========================================================================
    builder.add_followup(
        date="2025-05-21",
        notes="Come with empty stomach"
    )
    
    # =========================================================================
    # ADVICE
    # =========================================================================
    builder.add_advice(note="Drink plenty of water")
    builder.add_advice(note="Do not go out in sun")
    builder.add_advice(note="Do not eat oily food")
    
    # =========================================================================
    # PRESCRIPTION NOTES
    # =========================================================================
    builder.add_notes(
        note="Patient is a 30 year old living in Bangalore",
        category="prescription-note"
    )
    
    # =========================================================================
    # CONVERT TO FHIR
    # =========================================================================
    fhir_bundle = builder.convert_to_fhir()
    
    print("=" * 80)
    print("COMPLETE FHIR BUNDLE OUTPUT")
    print("=" * 80)
    print(json.dumps(fhir_bundle, indent=2))
    
    # Summary
    bundle_obj = builder.get_bundle()
    print(f"\n{'=' * 80}")
    print("BUNDLE SUMMARY")
    print("=" * 80)
    print(f"Total entries: {len(bundle_obj.entry or [])}")
    print("\nResources by type:")
    
    resource_counts = {}
    for entry in bundle_obj.entry or []:
        resource_type = entry.resource.get_resource_type()
        resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
    
    for resource_type, count in sorted(resource_counts.items()):
        print(f"  - {resource_type}: {count}")


if __name__ == "__main__":
    main()


