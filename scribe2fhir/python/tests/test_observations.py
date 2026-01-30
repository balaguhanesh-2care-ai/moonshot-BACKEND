"""
Test cases for Vital Signs, Lab Findings, and Examination Observations.
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import (
    FHIRDocumentBuilder,
    Interpretation,
    ObservationStatus
)


class TestVitalSignsObservations:
    """Test vital signs observation creation and validation."""
    
    def test_basic_vital_sign_creation(self, encounter_builder):
        """Test creating a vital sign with minimal information."""
        observation = encounter_builder.add_vital_finding(
            code="Blood Pressure",
            value="120/80",
            unit="mmHg"
        )
        
        # Verify observation was created
        assert observation is not None
        assert observation.get_resource_type() == "Observation"
        assert observation.id is not None
        assert observation.status == "final"
        
        # Verify category
        assert len(observation.category) == 1
        assert observation.category[0].coding[0].code == "vital-signs"
        
        # Verify code and value
        assert observation.code.text == "Blood Pressure"
        assert observation.valueString == "120/80 mmHg"
        
        # Verify references
        assert observation.subject is not None
        assert "Patient/" in observation.subject.reference
        assert observation.encounter is not None
        assert "Encounter/" in observation.encounter.reference
    
    def test_vital_sign_with_interpretation(self, encounter_builder):
        """Test vital sign with interpretation."""
        observation = encounter_builder.add_vital_finding(
            code="Blood Pressure",
            value="120/80",
            unit="mmHg",
            interpretation=Interpretation.NORMAL,
            notes="Patient was at rest"
        )
        
        # Verify interpretation
        assert len(observation.interpretation) == 1
        assert observation.interpretation[0].coding[0].code == "N"
        assert observation.interpretation[0].text == "Normal"
        
        # Verify notes
        assert len(observation.note) == 1
        assert observation.note[0].text == "Patient was at rest"
    
    def test_vital_sign_numeric_value(self, encounter_builder):
        """Test vital sign with numeric value."""
        observation = encounter_builder.add_vital_finding(
            code="Heart Rate",
            value=72,
            unit="bpm",
            interpretation=Interpretation.NORMAL
        )
        
        # Verify numeric value
        assert observation.valueQuantity is not None
        assert observation.valueQuantity.value == 72
        assert observation.valueQuantity.unit == "bpm"
        assert observation.valueString is None
    
    def test_vital_sign_interpretations(self, encounter_builder):
        """Test different interpretation values."""
        interpretation_tests = [
            (Interpretation.NORMAL, "N", "Normal"),
            (Interpretation.HIGH, "H", "High"),
            (Interpretation.LOW, "L", "Low"),
            (Interpretation.ABNORMAL, "A", "Abnormal"),
            ("normal", "N", "Normal"),  # String input
            ("high", "H", "High")
        ]
        
        for interp_input, expected_code, expected_text in interpretation_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            observation = builder.add_vital_finding(
                code="Test Vital",
                value=100,
                unit="test",
                interpretation=interp_input
            )
            
            assert observation.interpretation[0].coding[0].code == expected_code
            assert observation.interpretation[0].text == expected_text
    
    def test_vital_sign_with_date(self, encounter_builder, test_dates):
        """Test vital sign with specific measurement date."""
        observation = encounter_builder.add_vital_finding(
            code="Temperature",
            value=98.6,
            unit="°F",
            date=test_dates['yesterday']
        )
        
        assert observation.effectiveDateTime.replace(tzinfo=None, microsecond=0) == test_dates['yesterday'].replace(microsecond=0)
    
    def test_vital_sign_without_value(self, encounter_builder):
        """Test vital sign without value (just observation)."""
        observation = encounter_builder.add_vital_finding(
            code="Weight measurement",
            notes="Patient unable to stand for measurement"
        )
        
        assert observation.code.text == "Weight measurement"
        assert observation.valueString is None
        assert observation.valueQuantity is None
        assert len(observation.note) == 1


class TestLabFindingObservations:
    """Test laboratory findings observation creation and validation."""
    
    def test_basic_lab_finding_creation(self, encounter_builder):
        """Test creating a lab finding with minimal information."""
        observation = encounter_builder.add_lab_finding(
            code="Hemoglobin",
            value=12,
            unit="percent"
        )
        
        # Verify observation was created
        assert observation is not None
        assert observation.get_resource_type() == "Observation"
        assert observation.status == "final"
        
        # Verify category
        assert len(observation.category) == 1
        assert observation.category[0].coding[0].code == "laboratory"
        
        # Verify value
        assert observation.valueQuantity.value == 12
        assert observation.valueQuantity.unit == "percent"
    
    def test_lab_finding_with_interpretation(self, encounter_builder):
        """Test lab finding with interpretation."""
        observation = encounter_builder.add_lab_finding(
            code="Hemoglobin",
            value=12,
            unit="percent",
            interpretation=Interpretation.NORMAL
        )
        
        assert observation.interpretation[0].text == "Normal"
    
    def test_lab_finding_without_value(self, encounter_builder):
        """Test lab finding with interpretation only."""
        observation = encounter_builder.add_lab_finding(
            code="PCM test",
            interpretation=Interpretation.NORMAL
        )
        
        assert observation.code.text == "PCM test"
        assert observation.valueQuantity is None
        assert observation.interpretation[0].text == "Normal"
    
    def test_lab_finding_string_value(self, encounter_builder):
        """Test lab finding with string result."""
        observation = encounter_builder.add_lab_finding(
            code="Urine Color",
            value="Yellow",
            interpretation=Interpretation.NORMAL
        )
        
        assert observation.valueString == "Yellow"
        assert observation.valueQuantity is None
    
    def test_lab_finding_with_date_and_notes(self, encounter_builder, test_dates):
        """Test lab finding with collection date and notes."""
        observation = encounter_builder.add_lab_finding(
            code="Complete Blood Count",
            value=5.5,
            unit="10^6/μL",
            date=test_dates['yesterday'],
            notes="Fasting sample collected"
        )
        
        assert observation.effectiveDateTime.replace(tzinfo=None, microsecond=0) == test_dates['yesterday'].replace(microsecond=0)
        assert observation.note[0].text == "Fasting sample collected"


class TestExaminationObservations:
    """Test physical examination observations."""
    
    def test_basic_examination_finding(self, encounter_builder):
        """Test creating an examination finding."""
        observation = encounter_builder.add_examination_finding(
            code="Hand examination",
            value="Swollen"
        )
        
        # Verify observation was created
        assert observation is not None
        assert observation.get_resource_type() == "Observation"
        assert observation.status == "final"
        
        # Verify category
        assert len(observation.category) == 1
        assert observation.category[0].coding[0].code == "exam"
        
        # Verify finding
        assert observation.code.text == "Hand examination"
        assert observation.valueString == "Swollen"
    
    def test_examination_with_notes_and_date(self, encounter_builder, test_dates):
        """Test examination with additional notes and date."""
        observation = encounter_builder.add_examination_finding(
            code="Abdominal examination",
            value="Soft, non-tender",
            date=test_dates['now'],
            notes="Patient cooperative during exam"
        )
        
        assert observation.valueString == "Soft, non-tender"
        assert observation.effectiveDateTime.replace(tzinfo=None, microsecond=0) == test_dates['now'].replace(microsecond=0)
        assert observation.note[0].text == "Patient cooperative during exam"
    
    def test_examination_custom_status(self, encounter_builder):
        """Test examination with custom status."""
        observation = encounter_builder.add_examination_finding(
            code="Neurological examination",
            value="Normal reflexes",
            status=ObservationStatus.PRELIMINARY
        )
        
        assert observation.status == "preliminary"


class TestLifestyleHistoryObservations:
    """Test lifestyle/social history observations."""
    
    def test_basic_lifestyle_history(self, encounter_builder):
        """Test creating a lifestyle history observation."""
        observation = encounter_builder.add_lifestyle_history(
            code="Smoking",
            status_value="Active"
        )
        
        # Verify observation was created
        assert observation is not None
        assert observation.get_resource_type() == "Observation"
        assert observation.status == "final"
        
        # Verify category
        assert len(observation.category) == 1
        assert observation.category[0].coding[0].code == "social-history"
        
        # Verify code and value
        assert observation.code.text == "Smoking"
        assert observation.valueString == "Active"
    
    def test_lifestyle_history_with_notes(self, encounter_builder):
        """Test lifestyle history with additional notes."""
        observation = encounter_builder.add_lifestyle_history(
            code="Drinking",
            status_value="Active",
            notes="Occasional drinker"
        )
        
        assert observation.valueString == "Active"
        assert observation.note[0].text == "Occasional drinker"
    
    def test_travel_history(self, encounter_builder):
        """Test travel history as lifestyle observation."""
        observation = encounter_builder.add_lifestyle_history(
            code="Traveled to Singapore",
            status_value="Active",
            notes="Came back a couple of weeks ago"
        )
        
        assert observation.code.text == "Traveled to Singapore"
        assert observation.valueString == "Active"
        assert observation.note[0].text == "Came back a couple of weeks ago"
    
    def test_lifestyle_history_with_date(self, encounter_builder, test_dates):
        """Test lifestyle history with specific date."""
        observation = encounter_builder.add_lifestyle_history(
            code="Exercise routine",
            status_value="Active",
            date=test_dates['yesterday'],
            notes="Daily morning walks"
        )
        
        assert observation.effectiveDateTime.replace(tzinfo=None, microsecond=0) == test_dates['yesterday'].replace(microsecond=0)


class TestObservationBundleIntegration:
    """Test observation integration in FHIR bundles."""
    
    def test_multiple_observation_types_in_bundle(self, encounter_builder):
        """Test multiple observation types appear correctly in bundle."""
        # Add different types of observations
        encounter_builder.add_vital_finding(
            code="Blood Pressure",
            value="120/80",
            unit="mmHg"
        )
        
        encounter_builder.add_lab_finding(
            code="Glucose",
            value=95,
            unit="mg/dL"
        )
        
        encounter_builder.add_examination_finding(
            code="Heart sounds",
            value="Normal S1, S2"
        )
        
        encounter_builder.add_lifestyle_history(
            code="Smoking status",
            status_value="Never"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find all observation entries
        obs_entries = [entry for entry in bundle_dict["entry"]
                      if entry["resource"]["resourceType"] == "Observation"]
        
        assert len(obs_entries) == 4
        
        # Verify different categories
        categories = []
        for entry in obs_entries:
            obs_category = entry["resource"]["category"][0]["coding"][0]["code"]
            categories.append(obs_category)
        
        assert "vital-signs" in categories
        assert "laboratory" in categories
        assert "exam" in categories
        assert "social-history" in categories
    
    def test_observation_references_in_bundle(self, encounter_builder):
        """Test observation references in bundle."""
        encounter_builder.add_vital_finding(
            code="Temperature",
            value=98.6,
            unit="°F"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find vital sign observation
        vital_entry = next((entry for entry in bundle_dict["entry"]
                           if entry["resource"]["resourceType"] == "Observation"
                           and entry["resource"]["category"][0]["coding"][0]["code"] == "vital-signs"), None)
        
        assert vital_entry is not None
        observation = vital_entry["resource"]
        
        # Verify references
        assert "subject" in observation
        assert observation["subject"]["reference"].startswith("Patient/")
        assert "encounter" in observation
        assert observation["encounter"]["reference"].startswith("Encounter/")
    
    def test_coded_observations_in_bundle(self, encounter_builder):
        """Test coded observations appear correctly in bundle."""
        # Test with SNOMED code
        encounter_builder.add_vital_finding(
            code=("85354007", "http://snomed.info/sct", "Blood pressure"),
            value="130/85",
            unit="mmHg"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        vital_entry = next((entry for entry in bundle_dict["entry"]
                           if entry["resource"]["resourceType"] == "Observation"
                           and entry["resource"]["category"][0]["coding"][0]["code"] == "vital-signs"), None)
        
        observation = vital_entry["resource"]
        
        # Verify coding
        assert observation["code"]["coding"][0]["code"] == "85354007"
        assert observation["code"]["coding"][0]["system"] == "http://snomed.info/sct"
        assert observation["code"]["coding"][0]["display"] == "Blood pressure"
        assert observation["code"]["text"] == "Blood pressure"
