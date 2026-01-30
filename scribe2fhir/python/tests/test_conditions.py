"""
Test cases for Condition resource functionality (medical conditions and diagnoses).
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import (
    FHIRDocumentBuilder,
    ConditionClinicalStatus,
    ConditionVerificationStatus,
    Severity,
    Laterality
)


class TestConditionResource:
    """Test condition resource creation and validation."""
    
    def test_basic_medical_history_condition(self, encounter_builder):
        """Test creating a medical history condition with minimal information."""
        condition = encounter_builder.add_medical_condition_history(
            code="Hypertension"
        )
        
        # Verify condition was created
        assert condition is not None
        assert condition.get_resource_type() == "Condition"
        assert condition.id is not None
        
        # Verify code
        assert condition.code.text == "Hypertension"
        
        # Verify default clinical status
        assert condition.clinicalStatus.coding[0].code == "active"
        
        # Verify category (problem-list-item for history)
        assert len(condition.category) == 1
        assert condition.category[0].coding[0].code == "problem-list-item"
        
        # Verify references
        assert condition.subject is not None
        assert "Patient/" in condition.subject.reference
        assert condition.encounter is not None
        assert "Encounter/" in condition.encounter.reference
    
    def test_medical_history_condition_with_all_properties(self, encounter_builder, test_dates):
        """Test creating a comprehensive medical history condition."""
        condition = encounter_builder.add_medical_condition_history(
            code="Hypertension",
            onset=test_dates['year_ago'],
            clinical_status=ConditionClinicalStatus.ACTIVE,
            verification_status=ConditionVerificationStatus.CONFIRMED,
            severity=Severity.MILD,
            laterality=Laterality.LEFT,
            notes="Well controlled with medication"
        )
        
        # Verify code and status
        assert condition.code.text == "Hypertension"
        assert condition.clinicalStatus.coding[0].code == "active"
        assert condition.verificationStatus.coding[0].code == "confirmed"
        
        # Verify onset
        assert condition.onsetDateTime.replace(tzinfo=None, microsecond=0) == test_dates['year_ago'].replace(microsecond=0)
        
        # Verify severity (directly in severity field, not extension)
        assert condition.severity is not None
        assert condition.severity.text == "Mild"
        
        # Verify laterality (body site)
        assert len(condition.bodySite) == 1
        assert condition.bodySite[0].text == "Left"
        
        # Verify notes
        assert len(condition.note) == 1
        assert condition.note[0].text == "Well controlled with medication"
    
    def test_encounter_diagnosis_condition(self, encounter_builder):
        """Test creating an encounter diagnosis."""
        condition = encounter_builder.add_medical_condition_encountered(
            code="Type 2 diabetes",
            severity=Severity.MILD,
            onset=datetime.now() - timedelta(days=3)
        )
        
        # Verify category (encounter-diagnosis)
        assert len(condition.category) == 1
        assert condition.category[0].coding[0].code == "encounter-diagnosis"
        
        # Verify default verification status for encounter diagnosis
        assert condition.verificationStatus.coding[0].code == "confirmed"
    
    def test_condition_clinical_status_values(self, encounter_builder):
        """Test different clinical status values."""
        status_tests = [
            (ConditionClinicalStatus.ACTIVE, "active"),
            (ConditionClinicalStatus.INACTIVE, "inactive"),
            (ConditionClinicalStatus.RESOLVED, "resolved"),
            (ConditionClinicalStatus.RECURRENCE, "recurrence"),
            ("active", "active"),  # String input
            ("resolved", "resolved")
        ]
        
        for status_input, expected_code in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            condition = builder.add_medical_condition_history(
                code="Test Condition",
                clinical_status=status_input
            )
            
            assert condition.clinicalStatus.coding[0].code == expected_code
    
    def test_condition_verification_status_values(self, encounter_builder):
        """Test different verification status values."""
        status_tests = [
            (ConditionVerificationStatus.UNCONFIRMED, "unconfirmed"),
            (ConditionVerificationStatus.PROVISIONAL, "provisional"),
            (ConditionVerificationStatus.DIFFERENTIAL, "differential"),
            (ConditionVerificationStatus.CONFIRMED, "confirmed"),
            (ConditionVerificationStatus.REFUTED, "refuted"),
            ("confirmed", "confirmed"),  # String input
            ("provisional", "provisional")
        ]
        
        for status_input, expected_code in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            condition = builder.add_medical_condition_history(
                code="Test Condition",
                verification_status=status_input
            )
            
            assert condition.verificationStatus.coding[0].code == expected_code
    
    def test_condition_severity_values(self, encounter_builder):
        """Test different severity values."""
        severity_tests = [
            (Severity.MILD, "Mild"),
            (Severity.MODERATE, "Moderate"),
            (Severity.SEVERE, "Severe"),
            ("mild", "Mild"),  # String input
            ("severe", "Severe")
        ]
        
        for severity_input, expected_text in severity_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            condition = builder.add_medical_condition_history(
                code="Test Condition",
                severity=severity_input
            )
            
            assert condition.severity is not None
            assert condition.severity.text == expected_text
    
    def test_condition_laterality_values(self, encounter_builder):
        """Test different laterality values."""
        laterality_tests = [
            (Laterality.LEFT, "Left"),
            (Laterality.RIGHT, "Right"),
            (Laterality.BILATERAL, "Bilateral"),
            ("left", "Left"),  # String input
            ("right", "Right")
        ]
        
        for laterality_input, expected_text in laterality_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            condition = builder.add_medical_condition_history(
                code="Test Condition",
                laterality=laterality_input
            )
            
            assert len(condition.bodySite) == 1
            assert condition.bodySite[0].text == expected_text
    
    def test_condition_with_onset_and_offset(self, encounter_builder, test_dates):
        """Test condition with both onset and offset (resolved condition)."""
        condition = encounter_builder.add_medical_condition_history(
            code="Acute condition",
            onset=test_dates['month_ago'],
            offset=test_dates['week_ago'],
            clinical_status=ConditionClinicalStatus.RESOLVED
        )
        
        # Should have onset period (not datetime) and abatement
        assert condition.onsetPeriod is not None
        assert condition.onsetPeriod.start.replace(tzinfo=None, microsecond=0) == test_dates['month_ago'].replace(microsecond=0)
        assert condition.onsetPeriod.end.replace(tzinfo=None, microsecond=0) == test_dates['week_ago'].replace(microsecond=0)
        assert condition.clinicalStatus.coding[0].code == "resolved"
    
    def test_condition_with_coded_input(self, encounter_builder):
        """Test condition with coded vs text input."""
        # Test with simple text
        condition1 = encounter_builder.add_medical_condition_history(
            code="Diabetes mellitus"
        )
        assert condition1.code.text == "Diabetes mellitus"
        
        # Test with tuple (code, system, display)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        condition2 = builder2.add_medical_condition_history(
            code=("44054006", "http://snomed.info/sct", "Diabetes mellitus type 2")
        )
        assert condition2.code.coding[0].code == "44054006"
        assert condition2.code.coding[0].system == "http://snomed.info/sct"
        assert condition2.code.coding[0].display == "Diabetes mellitus type 2"
        assert condition2.code.text == "Diabetes mellitus type 2"
    
    def test_conditions_in_fhir_bundle(self, encounter_builder):
        """Test conditions appear correctly in FHIR bundle."""
        # Add both types of conditions
        encounter_builder.add_medical_condition_history(
            code="Hypertension",
            clinical_status=ConditionClinicalStatus.ACTIVE,
            severity=Severity.MILD
        )
        
        encounter_builder.add_medical_condition_encountered(
            code="Type 2 diabetes",
            severity=Severity.MODERATE
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find condition entries
        condition_entries = [entry for entry in bundle_dict["entry"]
                           if entry["resource"]["resourceType"] == "Condition"]
        
        assert len(condition_entries) == 2
        
        # Verify categories
        categories = [entry["resource"]["category"][0]["coding"][0]["code"] 
                     for entry in condition_entries]
        assert "problem-list-item" in categories
        assert "encounter-diagnosis" in categories
        
        # Verify specific conditions
        condition_codes = [entry["resource"]["code"]["text"] for entry in condition_entries]
        assert "Hypertension" in condition_codes
        assert "Type 2 diabetes" in condition_codes
    
    def test_multiple_conditions_same_type(self, encounter_builder):
        """Test adding multiple conditions of the same type."""
        condition1 = encounter_builder.add_medical_condition_history(
            code="Hypertension",
            severity=Severity.MILD
        )
        
        condition2 = encounter_builder.add_medical_condition_history(
            code="Diabetes",
            severity=Severity.MODERATE
        )
        
        condition3 = encounter_builder.add_medical_condition_encountered(
            code="Acute bronchitis"
        )
        
        # Verify all conditions have different IDs
        assert condition1.id != condition2.id != condition3.id
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        condition_entries = [entry for entry in bundle_dict["entry"]
                           if entry["resource"]["resourceType"] == "Condition"]
        
        assert len(condition_entries) == 3
    
    def test_condition_without_encounter(self):
        """Test condition creation without encounter."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Test Patient", age=(30, "years"))
        
        condition = builder.add_medical_condition_history(
            code="No Encounter Condition"
        )
        
        assert condition is not None
        assert condition.subject is not None  # Should have patient reference
        assert condition.encounter is None    # No encounter reference
    
    def test_condition_date_formats(self, encounter_builder):
        """Test different date formats for condition onset."""
        # Test with string date
        condition1 = encounter_builder.add_medical_condition_history(
            code="String Date Condition",
            onset="2020-01-01"
        )
        assert condition1.onsetDateTime is not None
        
        # Test with datetime object
        dt = datetime(2020, 1, 1, 0, 0, 0)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        condition2 = builder2.add_medical_condition_history(
            code="DateTime Condition",
            onset=dt
        )
        assert condition2.onsetDateTime.replace(tzinfo=None) == dt
    
    def test_condition_custom_id(self, encounter_builder):
        """Test condition creation with custom ID."""
        custom_id = "condition-12345"
        condition = encounter_builder.add_medical_condition_history(
            code="Custom ID Condition",
            id=custom_id
        )
        
        assert condition.id == custom_id
        
        # Verify in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        condition_entry = next((entry for entry in bundle_dict["entry"]
                              if entry["resource"]["resourceType"] == "Condition"
                              and entry["resource"]["id"] == custom_id), None)
        
        assert condition_entry is not None
    
    def test_encounter_vs_history_condition_differences(self, encounter_builder):
        """Test differences between encounter and history conditions."""
        # History condition
        history_condition = encounter_builder.add_medical_condition_history(
            code="History Condition"
        )
        
        # Encounter condition
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        encounter_condition = builder2.add_medical_condition_encountered(
            code="Encounter Condition"
        )
        
        # Verify different categories
        assert history_condition.category[0].coding[0].code == "problem-list-item"
        assert encounter_condition.category[0].coding[0].code == "encounter-diagnosis"
        
        # Verify default verification statuses
        # History conditions may not have default verification status
        assert encounter_condition.verificationStatus.coding[0].code == "confirmed"
