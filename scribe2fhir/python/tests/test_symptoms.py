"""
Test cases for Symptom and Observation resource functionality.
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import (
    FHIRDocumentBuilder,
    Severity,
    Laterality,
    FindingStatus,
    Interpretation,
    ObservationStatus
)


class TestSymptomResource:
    """Test symptom observation creation and validation."""
    
    def test_basic_symptom_creation(self, encounter_builder):
        """Test creating a symptom with minimal information."""
        observation = encounter_builder.add_symptom(
            code="Headache"
        )
        
        # Verify observation was created
        assert observation is not None
        assert observation.get_resource_type() == "Observation"
        assert observation.id is not None
        assert observation.status == "final"
        
        # Verify category
        assert len(observation.category) == 1
        assert observation.category[0].coding[0].code == "survey"
        
        # Verify code
        assert observation.code.text == "Headache"
        
        # Verify references
        assert observation.subject is not None
        assert "Patient/" in observation.subject.reference
        assert observation.encounter is not None
        assert "Encounter/" in observation.encounter.reference
    
    def test_symptom_with_all_properties(self, encounter_builder, test_dates):
        """Test creating a symptom with all available properties."""
        observation = encounter_builder.add_symptom(
            code="Headache",
            onset=test_dates['yesterday'],
            severity=Severity.MODERATE,
            laterality=Laterality.RIGHT,
            finding_status=FindingStatus.PRESENT,
            notes="Higher in the morning and decreases towards the evening",
            status=ObservationStatus.FINAL
        )
        
        # Verify basic properties
        assert observation.code.text == "Headache"
        assert observation.status == "final"
        
        # Verify onset
        assert observation.effectiveDateTime.replace(tzinfo=None, microsecond=0) == test_dates['yesterday'].replace(microsecond=0)
        
        # Verify severity component
        severity_comp = next((comp for comp in observation.component
                            if any(c.code == "SEV" for c in comp.code.coding)), None)
        assert severity_comp is not None
        assert severity_comp.valueCodeableConcept.text == "Moderate"
        
        # Verify laterality component
        laterality_comp = next((comp for comp in observation.component
                              if any(c.code == "272741003" for c in comp.code.coding)), None)
        assert laterality_comp is not None
        assert laterality_comp.valueCodeableConcept.text == "Right"
        
        # Verify finding status component
        finding_comp = next((comp for comp in observation.component
                           if any(c.code == "408729009" for c in comp.code.coding)), None)
        assert finding_comp is not None
        assert finding_comp.valueCodeableConcept.text == "Present"
        
        # Verify notes
        assert len(observation.note) == 1
        assert observation.note[0].text == "Higher in the morning and decreases towards the evening"
    
    def test_negative_symptom_finding(self, encounter_builder):
        """Test creating a negative symptom finding (absent)."""
        observation = encounter_builder.add_symptom(
            code="Leg pain",
            finding_status=FindingStatus.ABSENT
        )
        
        # Verify finding status component for negative finding
        finding_comp = next((comp for comp in observation.component
                           if any(c.code == "408729009" for c in comp.code.coding)), None)
        assert finding_comp is not None
        assert finding_comp.valueCodeableConcept.text == "Absent"
    
    def test_symptom_severity_values(self, encounter_builder):
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
            
            observation = builder.add_symptom(
                code="Test Symptom",
                severity=severity_input
            )
            
            severity_comp = next((comp for comp in observation.component
                                if any(c.code == "SEV" for c in comp.code.coding)), None)
            assert severity_comp is not None
            assert severity_comp.valueCodeableConcept.text == expected_text
    
    def test_symptom_laterality_values(self, encounter_builder):
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
            
            observation = builder.add_symptom(
                code="Test Symptom",
                laterality=laterality_input
            )
            
            laterality_comp = next((comp for comp in observation.component
                                  if any(c.code == "272741003" for c in comp.code.coding)), None)
            assert laterality_comp is not None
            assert laterality_comp.valueCodeableConcept.text == expected_text
    
    def test_symptom_with_offset(self, encounter_builder, test_dates):
        """Test symptom with both onset and offset times."""
        observation = encounter_builder.add_symptom(
            code="Fever",
            onset=test_dates['week_ago'],
            offset=test_dates['yesterday']
        )
        
        # Should have effective period instead of dateTime
        assert observation.effectivePeriod is not None
        assert observation.effectivePeriod.start.replace(tzinfo=None, microsecond=0) == test_dates['week_ago'].replace(microsecond=0)
        assert observation.effectivePeriod.end.replace(tzinfo=None, microsecond=0) == test_dates['yesterday'].replace(microsecond=0)
        assert observation.effectiveDateTime is None
    
    def test_symptom_coded_vs_text(self, encounter_builder):
        """Test symptom with coded vs text input."""
        # Test with simple text
        obs1 = encounter_builder.add_symptom(code="Headache")
        assert obs1.code.text == "Headache"
        
        # Test with tuple (code, system, display)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        obs2 = builder2.add_symptom(
            code=("25064002", "http://snomed.info/sct", "Headache")
        )
        assert obs2.code.coding[0].code == "25064002"
        assert obs2.code.coding[0].system == "http://snomed.info/sct"
        assert obs2.code.coding[0].display == "Headache"
        assert obs2.code.text == "Headache"
    
    def test_symptom_in_fhir_bundle(self, encounter_builder):
        """Test symptom appears correctly in FHIR bundle."""
        encounter_builder.add_symptom(
            code="Bundle Test Symptom",
            severity=Severity.MODERATE,
            notes="Test notes"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find symptom observation in bundle
        obs_entries = [entry for entry in bundle_dict["entry"]
                      if entry["resource"]["resourceType"] == "Observation"
                      and any(cat["coding"][0]["code"] == "survey" 
                             for cat in entry["resource"]["category"])]
        
        assert len(obs_entries) == 1
        observation = obs_entries[0]["resource"]
        
        # Verify symptom details in bundle
        assert observation["code"]["text"] == "Bundle Test Symptom"
        assert observation["status"] == "final"
        
        # Verify category
        assert observation["category"][0]["coding"][0]["code"] == "survey"
        
        # Verify severity component
        severity_comp = next((comp for comp in observation["component"]
                            if comp["code"]["coding"][0]["code"] == "SEV"), None)
        assert severity_comp is not None
        assert severity_comp["valueCodeableConcept"]["text"] == "Moderate"
    
    def test_multiple_symptoms(self, encounter_builder):
        """Test adding multiple symptoms."""
        obs1 = encounter_builder.add_symptom(code="Headache", severity=Severity.MILD)
        obs2 = encounter_builder.add_symptom(code="Nausea", severity=Severity.MODERATE)
        obs3 = encounter_builder.add_symptom(code="Dizziness", finding_status=FindingStatus.ABSENT)
        
        # Verify all symptoms have different IDs
        assert obs1.id != obs2.id != obs3.id
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        obs_entries = [entry for entry in bundle_dict["entry"]
                      if entry["resource"]["resourceType"] == "Observation"
                      and any(cat["coding"][0]["code"] == "survey" 
                             for cat in entry["resource"]["category"])]
        
        assert len(obs_entries) == 3
        
        # Verify specific symptoms
        symptom_codes = [obs["resource"]["code"]["text"] for obs in obs_entries]
        assert "Headache" in symptom_codes
        assert "Nausea" in symptom_codes
        assert "Dizziness" in symptom_codes
    
    def test_symptom_without_encounter(self):
        """Test symptom creation without encounter."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Test Patient", age=(30, "years"))
        
        observation = builder.add_symptom(
            code="No Encounter Symptom"
        )
        
        assert observation is not None
        assert observation.subject is not None  # Should have patient reference
        assert observation.encounter is None    # No encounter reference
    
    def test_symptom_custom_status(self, encounter_builder):
        """Test symptom with custom status values."""
        status_tests = ["preliminary", "final", "amended", "corrected"]
        
        for status in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            observation = builder.add_symptom(
                code="Status Test Symptom",
                status=status
            )
            
            assert observation.status == status
    
    def test_symptom_date_formats(self, encounter_builder):
        """Test different date formats for symptom onset."""
        # Test with string date
        obs1 = encounter_builder.add_symptom(
            code="String Date Symptom",
            onset="2024-01-15T10:00:00"
        )
        assert obs1.effectiveDateTime is not None
        
        # Test with datetime object
        dt = datetime(2024, 1, 15, 14, 30, 0)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        obs2 = builder2.add_symptom(
            code="DateTime Symptom",
            onset=dt
        )
        assert obs2.effectiveDateTime.replace(tzinfo=None) == dt
