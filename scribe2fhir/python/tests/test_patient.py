"""
Test cases for Patient resource functionality.
"""

import pytest
import json
from datetime import datetime, date
from scribe2fhir.core import FHIRDocumentBuilder


class TestPatientResource:
    """Test patient resource creation and validation."""
    
    def test_basic_patient_creation(self, builder):
        """Test creating a patient with minimal information."""
        patient = builder.add_patient(
            name="John Doe",
            age=(30, "years"),
            gender="male"
        )
        
        # Verify patient was created
        assert patient is not None
        assert patient.get_resource_type() == "Patient"
        assert patient.id is not None
        assert patient.gender == "male"
        
        # Verify name
        assert len(patient.name) == 1
        assert patient.name[0].text == "John Doe"
        
        # Verify age extension
        assert patient.extension is not None
        age_ext = next((ext for ext in patient.extension 
                       if ext.url == "http://hl7.org/fhir/StructureDefinition/patient-age"), None)
        assert age_ext is not None
        assert age_ext.valueQuantity.value == 30
        assert age_ext.valueQuantity.unit == "years"
    
    def test_patient_with_full_details(self, builder):
        """Test creating a patient with comprehensive details."""
        identifiers = [
            ("MRN-001234", "MRN"),
            ("ABHA-1234567890", "ABHA"),
            ("9876543210", "mobile")
        ]
        
        patient = builder.add_patient(
            name="Rahul Sharma",
            age=(30, "years"),
            gender="male",
            identifiers=identifiers,
            address="123 Main Street, Koramangala, Bangalore, Karnataka 560034",
            phone="9876543210",
            email="rahul.sharma@email.com"
        )
        
        # Verify basic details
        assert patient.name[0].text == "Rahul Sharma"
        assert patient.gender == "male"
        
        # Verify identifiers
        assert len(patient.identifier) == 3
        mrn_id = next((id for id in patient.identifier 
                      if id.type.coding[0].code == "MR"), None)
        assert mrn_id is not None
        assert mrn_id.value == "MRN-001234"
        
        # Verify address
        assert len(patient.address) == 1
        assert "123 Main Street" in patient.address[0].text
        
        # Verify contact details
        assert len(patient.telecom) == 2
        phone_contact = next((t for t in patient.telecom if t.system == "phone"), None)
        assert phone_contact is not None
        assert phone_contact.value == "9876543210"
        
        email_contact = next((t for t in patient.telecom if t.system == "email"), None)
        assert email_contact is not None
        assert email_contact.value == "rahul.sharma@email.com"
    
    def test_patient_with_birth_date(self, builder):
        """Test creating patient with birth date instead of age."""
        birth_date = date(1994, 5, 15)
        
        patient = builder.add_patient(
            name="Jane Smith",
            birth_date=birth_date,
            gender="female"
        )
        
        assert patient.birthDate == birth_date
        # Age extension should not be present when birth_date is used
        age_ext = next((ext for ext in (patient.extension or [])
                       if ext.url == "http://hl7.org/fhir/StructureDefinition/patient-age"), None)
        assert age_ext is None
    
    def test_patient_name_variations(self, builder):
        """Test different ways to specify patient name."""
        # Test with dictionary
        name_dict = {
            "given": ["John", "Michael"],
            "family": "Smith",
            "text": "Dr. John Michael Smith"
        }
        
        patient = builder.add_patient(
            name=name_dict,
            age=(40, "years"),
            gender="male"
        )
        
        assert patient.name[0].text == "Dr. John Michael Smith"
        assert patient.name[0].given == ["John", "Michael"]
        assert patient.name[0].family == "Smith"
    
    def test_patient_identifier_variations(self, builder):
        """Test different identifier formats."""
        # Test with system URLs
        identifiers = [
            ("123456789", ("http://terminology.hl7.org/CodeSystem/v2-0203", "MR")),
            ("ABHA-123456", "ABHA")
        ]
        
        patient = builder.add_patient(
            name="Test Patient",
            age=(25, "years"),
            gender="other",
            identifiers=identifiers
        )
        
        assert len(patient.identifier) == 2
        
        # Check first identifier with system URL
        id1 = patient.identifier[0]
        assert id1.value == "123456789"
        assert id1.type.coding[0].system == "http://terminology.hl7.org/CodeSystem/v2-0203"
        assert id1.type.coding[0].code == "MR"
    
    def test_patient_in_fhir_bundle(self, builder):
        """Test patient appears correctly in FHIR bundle."""
        builder.add_patient(
            name="Bundle Test Patient",
            age=(35, "years"),
            gender="male"
        )
        
        bundle_dict = builder.convert_to_fhir()
        
        # Find patient in bundle
        patient_entry = next((entry for entry in bundle_dict["entry"]
                            if entry["resource"]["resourceType"] == "Patient"), None)
        
        assert patient_entry is not None
        patient_resource = patient_entry["resource"]
        assert patient_resource["name"][0]["text"] == "Bundle Test Patient"
        assert patient_resource["gender"] == "male"
    
    def test_patient_reference_creation(self, builder):
        """Test that patient references are created correctly."""
        patient = builder.add_patient(
            name="Reference Test",
            age=(28, "years"),
            gender="female"
        )
        
        # Add a symptom to test patient reference
        builder.add_symptom(
            code="Headache",
            severity="moderate"
        )
        
        bundle_dict = builder.convert_to_fhir()
        
        # Find observation in bundle
        obs_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "Observation"), None)
        
        assert obs_entry is not None
        observation = obs_entry["resource"]
        
        # Check patient reference
        assert "subject" in observation
        assert observation["subject"]["reference"] == f"Patient/{patient.id}"
        assert "Reference Test" in observation["subject"]["display"]
    
    def test_invalid_patient_data(self, builder):
        """Test handling of invalid patient data."""
        # Test with minimal required data
        patient = builder.add_patient(name="Minimal Patient")
        assert patient is not None
        assert patient.name[0].text == "Minimal Patient"
        
        # Gender should be optional
        assert patient.gender is None
    
    def test_patient_age_units(self, builder):
        """Test different age units."""
        # Test months
        patient1 = builder.add_patient(
            name="Baby Patient",
            age=(6, "months"),
            gender="male"
        )
        
        age_ext = next((ext for ext in patient1.extension 
                       if ext.url == "http://hl7.org/fhir/StructureDefinition/patient-age"), None)
        assert age_ext.valueQuantity.value == 6
        assert age_ext.valueQuantity.unit == "months"
        
        # Test days
        patient2 = builder.add_patient(
            name="Newborn Patient", 
            age=(10, "days"),
            gender="female"
        )
        
        age_ext = next((ext for ext in patient2.extension
                       if ext.url == "http://hl7.org/fhir/StructureDefinition/patient-age"), None)
        assert age_ext.valueQuantity.value == 10
        assert age_ext.valueQuantity.unit == "days"
