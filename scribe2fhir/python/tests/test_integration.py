"""
Comprehensive integration tests for the entire FHIR SDK.

This test file validates the complete workflow from the example_usage.py
and ensures all components work together correctly.
"""

import pytest
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


class TestCompleteWorkflow:
    """Test complete FHIR document creation workflow."""
    
    def test_example_usage_recreation(self):
        """Recreate the complete example from example_usage.py."""
        # Create a new document builder
        builder = FHIRDocumentBuilder()
        
        # =========================================================================
        # PATIENT INFORMATION
        # =========================================================================
        patient = builder.add_patient(
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
        encounter = builder.add_encounter(
            encounter_class="ambulatory",
            encounter_type="Consultation",
            facility_name="Apollo Hospital",
            department="General Medicine",
            period_start=datetime.now()
        )
        
        # =========================================================================
        # SYMPTOMS (Chief Complaints)
        # =========================================================================
        symptom1 = builder.add_symptom(
            code="Headache",
            severity=Severity.MODERATE,
            laterality=Laterality.RIGHT,
            onset=datetime.now() - timedelta(days=1),
            notes="Higher in the morning and decreases towards the evening",
            finding_status=FindingStatus.PRESENT
        )
        
        symptom2 = builder.add_symptom(
            code="Leg pain",
            finding_status=FindingStatus.ABSENT  # Negative finding
        )
        
        # =========================================================================
        # DIAGNOSIS (Encounter Diagnoses)
        # =========================================================================
        condition1 = builder.add_medical_condition_encountered(
            code="Type 2 diabetes",
            severity=Severity.MILD,
            onset=datetime.now() - timedelta(days=3)
        )
        
        condition2 = builder.add_medical_condition_encountered(
            code="Cardiac condition",
            severity=Severity.MILD,
            laterality=Laterality.LEFT,
            notes="On the left portion"
        )
        
        # =========================================================================
        # VITALS
        # =========================================================================
        vital = builder.add_vital_finding(
            code="Blood Pressure",
            value="120/80",
            unit="mmHg",
            interpretation=Interpretation.NORMAL
        )
        
        # =========================================================================
        # LAB FINDINGS (Lab Vitals)
        # =========================================================================
        lab1 = builder.add_lab_finding(
            code="Hemoglobin",
            value=12,
            unit="percent",
            interpretation=Interpretation.NORMAL
        )
        
        lab2 = builder.add_lab_finding(
            code="PCM test",
            interpretation=Interpretation.NORMAL
        )
        
        # =========================================================================
        # MEDICAL HISTORY
        # =========================================================================
        
        # Past Medical Conditions
        history_condition = builder.add_medical_condition_history(
            code="Hypertension",
            clinical_status=ConditionClinicalStatus.ACTIVE,
            onset="2020-01-01",
            notes="Very severe"
        )
        
        # Current Medications (History)
        med_history = builder.add_medication_history(
            medication="Crocin 600",
            status=MedicationStatementStatus.ACTIVE,
            effective_start=datetime.now() - timedelta(days=90),
            notes="Every week once"
        )
        
        # Family History
        family1 = builder.add_family_history(
            condition="Hypertension",
            relation="Father",
            onset="1997",
            status="completed"
        )
        
        family2 = builder.add_family_history(
            condition="Type 2 diabetes",
            relation="Mother",
            status="completed",
            deceased=True,
            notes="Mother is dead now"
        )
        
        # Lifestyle Habits
        lifestyle1 = builder.add_lifestyle_history(
            code="Smoking",
            status_value="Active"
        )
        
        lifestyle2 = builder.add_lifestyle_history(
            code="Drinking",
            status_value="Active",
            notes="Occasional drinker"
        )
        
        # Recent Travel History
        travel = builder.add_lifestyle_history(
            code="Traveled to Singapore",
            status_value="Active",
            notes="Came back a couple of weeks ago"
        )
        
        # Allergies
        allergy1 = builder.add_allergy_history(
            code="Pollen allergy",
            category=AllergyCategory.ENVIRONMENT
        )
        
        allergy2 = builder.add_allergy_history(
            code="Paracetamol",
            category=AllergyCategory.MEDICATION
        )
        
        # Past Procedures
        procedure = builder.add_procedure_history(
            code="Vasectomy",
            status="completed"
        )
        
        # Vaccination History
        immunization = builder.add_immunisation_history(
            vaccine="COVID vaccine",
            notes="Done during the second wave of COVID"
        )
        
        # Examinations
        exam = builder.add_examination_finding(
            code="Hand examination",
            value="Swollen"
        )
        
        # =========================================================================
        # LAB TESTS ORDERED
        # =========================================================================
        test1 = builder.add_test_prescribed(
            code="CBC test"
        )
        
        test2 = builder.add_test_prescribed(
            code="Fasting blood sugar test",
            notes="Should be done on empty stomach"
        )
        
        # =========================================================================
        # MEDICATIONS PRESCRIBED
        # =========================================================================
        dosage = DosageBuilder.build(
            dose_value=1,
            dose_unit="tablet",
            frequency=3,
            period=1,
            period_unit="d",
            route=RouteOfAdministration.ORAL,
            timing_code=EventTiming.AFTER_MEAL,
            text="Take 1 tablet three times daily after meals"
        )
        
        medication = builder.add_medication_prescribed(
            medication="Dolo 650 Tablet",
            dosage=dosage,
            duration_value=7,
            duration_unit="d",
            notes="Dose: 1 tablet"
        )
        
        # =========================================================================
        # FOLLOW-UP
        # =========================================================================
        followup = builder.add_followup(
            date="2025-05-21",
            notes="Come with empty stomach"
        )
        
        # =========================================================================
        # ADVICE
        # =========================================================================
        advice1 = builder.add_advice(note="Drink plenty of water")
        advice2 = builder.add_advice(note="Do not go out in sun")
        advice3 = builder.add_advice(note="Do not eat oily food")
        
        # =========================================================================
        # PRESCRIPTION NOTES
        # =========================================================================
        note = builder.add_notes(
            note="Patient is a 30 year old living in Bangalore",
            category="prescription-note"
        )
        
        # =========================================================================
        # CONVERT TO FHIR AND VALIDATE
        # =========================================================================
        fhir_bundle = builder.convert_to_fhir()
        
        # Validate bundle structure
        assert "resourceType" in fhir_bundle
        assert fhir_bundle["resourceType"] == "Bundle"
        assert "type" in fhir_bundle
        assert "entry" in fhir_bundle
        assert len(fhir_bundle["entry"]) > 0
        
        # Count resources by type
        resource_counts = {}
        for entry in fhir_bundle["entry"]:
            resource_type = entry["resource"]["resourceType"]
            resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
        
        # Verify expected resource counts
        assert resource_counts["Patient"] == 1
        assert resource_counts["Encounter"] == 1
        assert resource_counts["Observation"] >= 5  # symptoms, vitals, labs, lifestyle, exams
        assert resource_counts["Condition"] >= 3   # encounter diagnoses + history
        assert resource_counts["MedicationRequest"] >= 1
        assert resource_counts["MedicationStatement"] >= 1
        assert resource_counts["ServiceRequest"] >= 2  # lab tests
        assert resource_counts["FamilyMemberHistory"] >= 2
        assert resource_counts["AllergyIntolerance"] >= 2
        assert resource_counts["Procedure"] >= 1
        assert resource_counts["Immunization"] >= 1
        assert resource_counts["Appointment"] >= 1
        assert resource_counts["CarePlan"] >= 3  # advice
        assert resource_counts["Communication"] >= 1  # notes
        
        # Verify all resources have IDs
        for entry in fhir_bundle["entry"]:
            assert "id" in entry["resource"]
            assert entry["resource"]["id"] is not None
        
        # Verify patient references in other resources
        patient_id = None
        encounter_id = None
        
        for entry in fhir_bundle["entry"]:
            resource = entry["resource"]
            if resource["resourceType"] == "Patient":
                patient_id = resource["id"]
            elif resource["resourceType"] == "Encounter":
                encounter_id = resource["id"]
        
        assert patient_id is not None
        assert encounter_id is not None
        
        # Check references in other resources
        for entry in fhir_bundle["entry"]:
            resource = entry["resource"]
            if resource["resourceType"] not in ["Patient", "Encounter"]:
                # Most resources should reference the patient
                if "subject" in resource:
                    assert resource["subject"]["reference"] == f"Patient/{patient_id}"
                elif "patient" in resource:
                    assert resource["patient"]["reference"] == f"Patient/{patient_id}"
                
                # Resources created in encounter context should reference encounter
                if resource["resourceType"] in ["Observation", "Condition", "MedicationRequest", 
                                              "ServiceRequest", "AllergyIntolerance", "CarePlan", "Communication"]:
                    if "encounter" in resource:
                        assert resource["encounter"]["reference"] == f"Encounter/{encounter_id}"
        
        return fhir_bundle
    
    def test_bundle_serialization(self):
        """Test that the bundle can be serialized to valid JSON."""
        builder = FHIRDocumentBuilder()
        
        # Add minimal required data
        builder.add_patient(name="Test Patient", age=(25, "years"))
        builder.add_encounter()
        builder.add_symptom(code="Test Symptom")
        
        # Test JSON serialization
        fhir_bundle = builder.convert_to_fhir()
        json_string = json.dumps(fhir_bundle, indent=2)
        
        # Should be able to parse back
        parsed_bundle = json.loads(json_string)
        assert parsed_bundle["resourceType"] == "Bundle"
        
        # Test builder's to_json method
        builder_json = builder.to_json()
        parsed_builder_json = json.loads(builder_json)
        assert parsed_builder_json["resourceType"] == "Bundle"
    
    def test_empty_bundle(self):
        """Test creating a bundle with no resources."""
        builder = FHIRDocumentBuilder()
        fhir_bundle = builder.convert_to_fhir()
        
        assert fhir_bundle["resourceType"] == "Bundle"
        assert fhir_bundle["type"] == "collection"
        # Entry should be None or empty list
        assert fhir_bundle.get("entry") is None or len(fhir_bundle["entry"]) == 0
    
    def test_minimal_patient_only_bundle(self):
        """Test bundle with only patient."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Minimal Patient")
        
        fhir_bundle = builder.convert_to_fhir()
        
        assert len(fhir_bundle["entry"]) == 1
        assert fhir_bundle["entry"][0]["resource"]["resourceType"] == "Patient"
    
    def test_get_bundle_object(self):
        """Test getting the Bundle object directly."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Bundle Object Test", age=(30, "years"))
        
        bundle_obj = builder.get_bundle()
        
        assert bundle_obj.get_resource_type() == "Bundle"
        assert bundle_obj.type == "collection"
        assert len(bundle_obj.entry) == 1
        assert bundle_obj.entry[0].resource.get_resource_type() == "Patient"
    
    def test_resource_references_consistency(self):
        """Test that all resource references are consistent."""
        builder = FHIRDocumentBuilder()
        
        # Add resources that create references
        patient = builder.add_patient(name="Reference Test", age=(30, "years"))
        encounter = builder.add_encounter()
        symptom = builder.add_symptom(code="Test Symptom")
        condition = builder.add_medical_condition_history(code="Test Condition")
        
        fhir_bundle = builder.convert_to_fhir()
        
        # Verify all references point to existing resources in bundle
        resource_ids = {f"{entry['resource']['resourceType']}/{entry['resource']['id']}" 
                       for entry in fhir_bundle["entry"]}
        
        for entry in fhir_bundle["entry"]:
            resource = entry["resource"]
            
            # Check subject/patient references
            if "subject" in resource:
                assert resource["subject"]["reference"] in resource_ids
            if "patient" in resource:
                assert resource["patient"]["reference"] in resource_ids
            
            # Check encounter references
            if "encounter" in resource:
                assert resource["encounter"]["reference"] in resource_ids
    
    def test_large_bundle_performance(self):
        """Test performance with a large number of resources."""
        builder = FHIRDocumentBuilder()
        
        # Add patient and encounter
        builder.add_patient(name="Performance Test Patient", age=(40, "years"))
        builder.add_encounter()
        
        # Add many resources
        start_time = datetime.now()
        
        # Add 50 symptoms
        for i in range(50):
            builder.add_symptom(code=f"Symptom {i+1}")
        
        # Add 20 conditions
        for i in range(20):
            builder.add_medical_condition_history(code=f"Condition {i+1}")
        
        # Add 10 medications
        for i in range(10):
            builder.add_medication_prescribed(medication=f"Medication {i+1}")
        
        end_time = datetime.now()
        build_time = (end_time - start_time).total_seconds()
        
        # Convert to FHIR
        fhir_start = datetime.now()
        fhir_bundle = builder.convert_to_fhir()
        fhir_end = datetime.now()
        fhir_time = (fhir_end - fhir_start).total_seconds()
        
        # Verify bundle
        assert len(fhir_bundle["entry"]) == 82  # 1 patient + 1 encounter + 50 + 20 + 10
        
        # Performance should be reasonable (less than 5 seconds each)
        assert build_time < 5.0
        assert fhir_time < 5.0
        
        print(f"Build time: {build_time:.2f}s, FHIR conversion time: {fhir_time:.2f}s")
