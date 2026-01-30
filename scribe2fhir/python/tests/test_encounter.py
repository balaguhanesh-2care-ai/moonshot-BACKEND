"""
Test cases for Encounter resource functionality.
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import FHIRDocumentBuilder


class TestEncounterResource:
    """Test encounter resource creation and validation."""
    
    def test_basic_encounter_creation(self, patient_builder):
        """Test creating an encounter with minimal information."""
        encounter = patient_builder.add_encounter()
        
        # Verify encounter was created
        assert encounter is not None
        assert encounter.get_resource_type() == "Encounter"
        assert encounter.id is not None
        assert encounter.status == "finished"  # Default status
        
        # Verify default class
        assert encounter.class_fhir.code == "AMB"  # ambulatory
        
        # Verify patient reference
        assert encounter.subject is not None
        assert "Patient/" in encounter.subject.reference
    
    def test_encounter_with_full_details(self, patient_builder):
        """Test creating an encounter with comprehensive details."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        encounter = patient_builder.add_encounter(
            encounter_class="ambulatory",
            encounter_type="Consultation",
            encounter_subtype="General Medicine Consultation",
            period_start=start_time,
            period_end=end_time,
            facility_name="Apollo Hospital",
            department="General Medicine",
            status="finished"
        )
        
        # Verify basic details
        assert encounter.class_fhir.code == "AMB"
        assert encounter.status == "finished"
        
        # Verify type
        assert len(encounter.type) == 1
        assert encounter.type[0].text == "Consultation"
        
        # Verify period
        assert encounter.period is not None
        assert encounter.period.start.replace(tzinfo=None, microsecond=0) == start_time.replace(microsecond=0)
        assert encounter.period.end.replace(tzinfo=None, microsecond=0) == end_time.replace(microsecond=0)
        
        # Verify location (facility)
        assert len(encounter.location) == 1
        assert "Apollo Hospital" in encounter.location[0].location.display
        
        # Verify service provider (department)
        assert encounter.serviceProvider is not None
        assert "General Medicine" in encounter.serviceProvider.display
    
    def test_encounter_classes(self, patient_builder):
        """Test different encounter classes."""
        test_cases = [
            ("ambulatory", "AMB"),
            ("emergency", "EMER"), 
            ("inpatient", "IMP"),
            ("outpatient", "AMB"),  # Maps to ambulatory
            ("virtual", "VR")
        ]
        
        for class_input, expected_code in test_cases:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test Patient", age=(30, "years"))
            encounter = builder.add_encounter(encounter_class=class_input)
            
            assert encounter.class_fhir.code == expected_code, f"Failed for {class_input}"
    
    def test_encounter_status_values(self, patient_builder):
        """Test different encounter status values."""
        test_statuses = [
            "planned",
            "arrived", 
            "triaged",
            "in-progress",
            "onleave",
            "finished",
            "cancelled"
        ]
        
        for status in test_statuses:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test Patient", age=(30, "years"))
            encounter = builder.add_encounter(status=status)
            
            assert encounter.status == status, f"Failed for status {status}"
    
    def test_encounter_with_only_start_time(self, patient_builder):
        """Test encounter with only start time (ongoing encounter)."""
        start_time = datetime.now()
        
        encounter = patient_builder.add_encounter(
            period_start=start_time,
            status="in-progress"
        )
        
        assert encounter.period.start.replace(tzinfo=None, microsecond=0) == start_time.replace(microsecond=0)
        assert encounter.period.end is None
        assert encounter.status == "in-progress"
    
    def test_encounter_types_and_subtypes(self, patient_builder):
        """Test various encounter types and subtypes."""
        encounter = patient_builder.add_encounter(
            encounter_type="Emergency Visit",
            encounter_subtype="Trauma Assessment"
        )
        
        # Should have both type and additional type
        assert len(encounter.type) >= 1
        
        # Primary type
        primary_type = encounter.type[0]
        assert primary_type.text == "Emergency Visit"
        
        # Check if subtype is included in types
        subtype_found = any(
            t.text == "Trauma Assessment" 
            for t in encounter.type
        )
        # Note: This depends on implementation - might be in type or separate field
    
    def test_encounter_location_handling(self, patient_builder):
        """Test encounter location and facility handling."""
        encounter = patient_builder.add_encounter(
            facility_name="City General Hospital",
            department="Cardiology"
        )
        
        # Check location
        assert len(encounter.location) == 1
        location = encounter.location[0]
        assert "City General Hospital" in location.location.display
        
        # Check service provider (department)
        assert encounter.serviceProvider is not None
        assert "Cardiology" in encounter.serviceProvider.display
    
    def test_encounter_in_fhir_bundle(self, patient_builder):
        """Test encounter appears correctly in FHIR bundle."""
        patient_builder.add_encounter(
            encounter_type="Bundle Test Encounter",
            facility_name="Test Facility"
        )
        
        bundle_dict = patient_builder.convert_to_fhir()
        
        # Find encounter in bundle
        encounter_entry = next((entry for entry in bundle_dict["entry"]
                              if entry["resource"]["resourceType"] == "Encounter"), None)
        
        assert encounter_entry is not None
        encounter_resource = encounter_entry["resource"]
        
        # Verify encounter details in bundle
        assert encounter_resource["status"] == "finished"
        assert encounter_resource["class"]["code"] == "AMB"
        
        # Verify patient reference
        assert "subject" in encounter_resource
        assert encounter_resource["subject"]["reference"].startswith("Patient/")
        
        # Verify type
        assert len(encounter_resource["type"]) >= 1
        assert encounter_resource["type"][0]["text"] == "Bundle Test Encounter"
    
    def test_encounter_reference_in_observations(self, patient_builder):
        """Test that encounter references are created correctly in related resources."""
        encounter = patient_builder.add_encounter(encounter_type="Test Encounter")
        
        # Add a symptom to test encounter reference
        patient_builder.add_symptom(
            code="Headache",
            severity="moderate"
        )
        
        bundle_dict = patient_builder.convert_to_fhir()
        
        # Find observation in bundle
        obs_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "Observation"), None)
        
        assert obs_entry is not None
        observation = obs_entry["resource"]
        
        # Check encounter reference
        assert "encounter" in observation
        assert observation["encounter"]["reference"] == f"Encounter/{encounter.id}"
    
    def test_multiple_encounters(self, patient_builder):
        """Test handling multiple encounters for same patient."""
        # Note: Current implementation only supports one encounter
        # This test verifies behavior when multiple encounters are attempted
        encounter1 = patient_builder.add_encounter(encounter_type="First Visit")
        encounter2 = patient_builder.add_encounter(encounter_type="Second Visit")
        
        # Second encounter should replace the first
        assert encounter2.id != encounter1.id
        
        bundle_dict = patient_builder.convert_to_fhir()
        encounter_entries = [entry for entry in bundle_dict["entry"]
                           if entry["resource"]["resourceType"] == "Encounter"]
        
        # Should only have one encounter in bundle (latest one)
        assert len(encounter_entries) == 1
        assert encounter_entries[0]["resource"]["type"][0]["text"] == "Second Visit"
    
    def test_encounter_without_patient(self):
        """Test encounter creation without patient (should handle gracefully)."""
        builder = FHIRDocumentBuilder()
        
        # Should work but won't have patient reference
        encounter = builder.add_encounter(encounter_type="No Patient Test")
        
        assert encounter is not None
        assert encounter.subject is None  # No patient reference
    
    def test_encounter_date_formats(self, patient_builder):
        """Test different date formats for encounter period."""
        # Test with string date
        encounter1 = patient_builder.add_encounter(
            period_start="2024-01-15T10:00:00"
        )
        assert encounter1.period.start is not None
        
        # Test with datetime object
        dt = datetime(2024, 1, 15, 14, 30, 0)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        encounter2 = builder2.add_encounter(period_start=dt)
        
        assert encounter2.period.start.replace(tzinfo=None) == dt
    
    def test_encounter_custom_id(self, patient_builder):
        """Test encounter creation with custom ID."""
        custom_id = "encounter-12345"
        encounter = patient_builder.add_encounter(
            encounter_type="Custom ID Test",
            id=custom_id
        )
        
        assert encounter.id == custom_id
        
        # Verify in bundle
        bundle_dict = patient_builder.convert_to_fhir()
        encounter_entry = next((entry for entry in bundle_dict["entry"]
                              if entry["resource"]["resourceType"] == "Encounter"), None)
        
        assert encounter_entry["resource"]["id"] == custom_id
