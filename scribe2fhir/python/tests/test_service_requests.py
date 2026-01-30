"""
Test cases for ServiceRequest resources (lab tests and procedures ordering).
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import FHIRDocumentBuilder


class TestLabTestOrdering:
    """Test lab test ordering via ServiceRequest."""
    
    def test_basic_lab_test_order(self, encounter_builder):
        """Test creating a basic lab test order."""
        service_request = encounter_builder.add_test_prescribed(
            code="CBC test"
        )
        
        # Verify service request was created
        assert service_request is not None
        assert service_request.get_resource_type() == "ServiceRequest"
        assert service_request.id is not None
        
        # Verify default values
        assert service_request.status == "active"
        assert service_request.intent == "order"
        
        # Verify category (diagnostic service)
        assert len(service_request.category) == 1
        assert service_request.category[0].coding[0].code == "108252007"
        assert service_request.category[0].coding[0].display == "Laboratory procedure"
        
        # Verify code
        assert service_request.code.text == "CBC test"
        
        # Verify references
        assert service_request.subject is not None
        assert "Patient/" in service_request.subject.reference
        assert service_request.encounter is not None
        assert "Encounter/" in service_request.encounter.reference
    
    def test_lab_test_with_all_properties(self, encounter_builder, test_dates):
        """Test creating a comprehensive lab test order."""
        service_request = encounter_builder.add_test_prescribed(
            code="Fasting blood sugar test",
            date=test_dates['future'],
            notes="Should be done on empty stomach",
            priority="routine",
            reason="Diabetes screening"
        )
        
        # Verify basic properties
        assert service_request.code.text == "Fasting blood sugar test"
        assert service_request.priority == "routine"
        
        # Verify occurrence date
        assert service_request.occurrenceDateTime.replace(tzinfo=None, microsecond=0) == test_dates['future'].replace(microsecond=0)
        
        # Verify notes
        assert len(service_request.note) == 1
        assert service_request.note[0].text == "Should be done on empty stomach"
        
        # Verify reason
        assert len(service_request.reasonCode) == 1
        assert service_request.reasonCode[0].text == "Diabetes screening"
    
    def test_lab_test_priority_values(self, encounter_builder):
        """Test different priority values for lab tests."""
        priority_tests = [
            "routine",
            "urgent", 
            "asap",
            "stat"
        ]
        
        for priority in priority_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            service_request = builder.add_test_prescribed(
                code="Priority Test",
                priority=priority
            )
            
            assert service_request.priority == priority
    
    def test_lab_test_coded_vs_text(self, encounter_builder):
        """Test lab test with coded vs text input."""
        # Test with simple text
        sr1 = encounter_builder.add_test_prescribed(code="Complete Blood Count")
        assert sr1.code.text == "Complete Blood Count"
        
        # Test with tuple (code, system, display)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        sr2 = builder2.add_test_prescribed(
            code=("26604007", "http://snomed.info/sct", "Complete blood count")
        )
        assert sr2.code.coding[0].code == "26604007"
        assert sr2.code.coding[0].system == "http://snomed.info/sct"
        assert sr2.code.coding[0].display == "Complete blood count"
        assert sr2.code.text == "Complete blood count"
    
    def test_lab_test_without_date(self, encounter_builder):
        """Test lab test order without specific date."""
        service_request = encounter_builder.add_test_prescribed(
            code="Routine Lab Test",
            notes="Schedule at patient convenience"
        )
        
        assert service_request.code.text == "Routine Lab Test"
        assert service_request.occurrenceDateTime is None
        assert service_request.note[0].text == "Schedule at patient convenience"
    
    def test_multiple_lab_tests(self, encounter_builder):
        """Test ordering multiple lab tests."""
        sr1 = encounter_builder.add_test_prescribed(code="CBC", priority="routine")
        sr2 = encounter_builder.add_test_prescribed(code="Lipid Panel", priority="urgent")
        sr3 = encounter_builder.add_test_prescribed(code="HbA1c", notes="For diabetes monitoring")
        
        # Verify all tests have different IDs
        assert sr1.id != sr2.id != sr3.id
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        sr_entries = [entry for entry in bundle_dict["entry"]
                     if entry["resource"]["resourceType"] == "ServiceRequest"]
        
        assert len(sr_entries) == 3
        
        # Verify specific tests
        test_codes = [entry["resource"]["code"]["coding"][0]["display"] for entry in sr_entries]
        assert "CBC" in test_codes
        assert "Lipid Panel" in test_codes
        assert "HbA1c" in test_codes


class TestProcedureOrdering:
    """Test procedure ordering via ServiceRequest."""
    
    def test_basic_procedure_order(self, encounter_builder):
        """Test creating a basic procedure order."""
        service_request = encounter_builder.add_procedure_prescribed(
            code="X-ray chest"
        )
        
        # Verify service request was created
        assert service_request is not None
        assert service_request.get_resource_type() == "ServiceRequest"
        
        # Verify category (procedure)
        assert len(service_request.category) == 1
        assert service_request.category[0].coding[0].code == "387713003"
        assert service_request.category[0].coding[0].display == "Surgical procedure"
        
        # Verify code
        assert service_request.code.text == "X-ray chest"
    
    def test_procedure_with_all_properties(self, encounter_builder, test_dates):
        """Test creating a comprehensive procedure order."""
        service_request = encounter_builder.add_procedure_prescribed(
            code="Echocardiogram",
            date=test_dates['future'],
            notes="Assess cardiac function",
            priority="urgent",
            reason="Chest pain evaluation"
        )
        
        # Verify properties
        assert service_request.code.text == "Echocardiogram"
        assert service_request.priority == "urgent"
        assert service_request.occurrenceDateTime.replace(tzinfo=None, microsecond=0) == test_dates['future'].replace(microsecond=0)
        assert service_request.note[0].text == "Assess cardiac function"
        assert service_request.reasonCode[0].text == "Chest pain evaluation"
    
    def test_imaging_procedure_order(self, encounter_builder):
        """Test ordering imaging procedures."""
        imaging_tests = [
            "CT scan abdomen",
            "MRI brain",
            "Ultrasound pelvis",
            "X-ray knee"
        ]
        
        for test in imaging_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            service_request = builder.add_procedure_prescribed(code=test)
            
            assert service_request.code.text == test
            assert service_request.category[0].coding[0].display == "Surgical procedure"


class TestServiceRequestBundleIntegration:
    """Test service request integration in FHIR bundles."""
    
    def test_service_requests_in_fhir_bundle(self, encounter_builder):
        """Test service requests appear correctly in FHIR bundle."""
        # Add lab test
        encounter_builder.add_test_prescribed(
            code="Bundle Lab Test",
            priority="routine"
        )
        
        # Add procedure
        encounter_builder.add_procedure_prescribed(
            code="Bundle Procedure",
            priority="urgent"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find service request entries
        sr_entries = [entry for entry in bundle_dict["entry"]
                     if entry["resource"]["resourceType"] == "ServiceRequest"]
        
        assert len(sr_entries) == 2
        
        # Verify categories
        categories = [entry["resource"]["category"][0]["coding"][0]["display"] for entry in sr_entries]
        assert "Laboratory procedure" in categories
        assert "Surgical procedure" in categories
        
        # Verify codes
        codes = [entry["resource"]["code"]["coding"][0]["display"] for entry in sr_entries]
        assert "Bundle Lab Test" in codes
        assert "Bundle Procedure" in codes
    
    def test_service_request_references_in_bundle(self, encounter_builder):
        """Test service request references in bundle."""
        encounter_builder.add_test_prescribed(
            code="Reference Test",
            notes="Test references"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        sr_entry = next((entry for entry in bundle_dict["entry"]
                        if entry["resource"]["resourceType"] == "ServiceRequest"), None)
        
        assert sr_entry is not None
        service_request = sr_entry["resource"]
        
        # Verify references
        assert "subject" in service_request
        assert service_request["subject"]["reference"].startswith("Patient/")
        assert "encounter" in service_request
        assert service_request["encounter"]["reference"].startswith("Encounter/")
    
    def test_service_request_without_encounter(self):
        """Test service request creation without encounter."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Test Patient", age=(30, "years"))
        
        service_request = builder.add_test_prescribed(
            code="No Encounter Test"
        )
        
        assert service_request is not None
        assert service_request.subject is not None  # Should have patient reference
        assert service_request.encounter is None    # No encounter reference
    
    def test_service_request_date_formats(self, encounter_builder):
        """Test different date formats for service request occurrence."""
        # Test with string date
        sr1 = encounter_builder.add_test_prescribed(
            code="String Date Test",
            date="2024-05-21T10:00:00"
        )
        assert sr1.occurrenceDateTime is not None
        
        # Test with datetime object
        dt = datetime(2024, 5, 21, 14, 30, 0)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        sr2 = builder2.add_test_prescribed(
            code="DateTime Test",
            date=dt
        )
        assert sr2.occurrenceDateTime.replace(tzinfo=None) == dt
    
    def test_service_request_custom_id(self, encounter_builder):
        """Test service request creation with custom ID."""
        custom_id = "servicerequest-12345"
        service_request = encounter_builder.add_test_prescribed(
            code="Custom ID Test",
            id=custom_id
        )
        
        assert service_request.id == custom_id
        
        # Verify in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        sr_entry = next((entry for entry in bundle_dict["entry"]
                        if entry["resource"]["resourceType"] == "ServiceRequest"
                        and entry["resource"]["id"] == custom_id), None)
        
        assert sr_entry is not None
    
    def test_lab_vs_procedure_category_differences(self, encounter_builder):
        """Test differences between lab and procedure service requests."""
        # Lab test
        lab_sr = encounter_builder.add_test_prescribed(code="Lab Test")
        
        # Procedure
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        proc_sr = builder2.add_procedure_prescribed(code="Procedure Test")
        
        # Verify different categories
        assert lab_sr.category[0].coding[0].code == "108252007"
        assert lab_sr.category[0].coding[0].display == "Laboratory procedure"
        
        assert proc_sr.category[0].coding[0].code == "387713003"
        assert proc_sr.category[0].coding[0].display == "Surgical procedure"
    
    def test_complex_service_request_scenario(self, encounter_builder, test_dates):
        """Test complex scenario with multiple service requests."""
        # Emergency lab workup
        encounter_builder.add_test_prescribed(
            code="Complete Blood Count",
            priority="stat",
            reason="Suspected infection",
            notes="STAT - patient febrile"
        )
        
        encounter_builder.add_test_prescribed(
            code="Blood Culture",
            priority="stat", 
            reason="Suspected sepsis"
        )
        
        # Follow-up imaging
        encounter_builder.add_procedure_prescribed(
            code="Chest X-ray",
            date=test_dates['future'],
            priority="routine",
            reason="Follow-up pneumonia",
            notes="PA and lateral views"
        )
        
        # Scheduled procedure
        encounter_builder.add_procedure_prescribed(
            code="Echocardiogram",
            date=test_dates['future'],
            priority="routine",
            reason="Cardiac assessment"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        sr_entries = [entry for entry in bundle_dict["entry"]
                     if entry["resource"]["resourceType"] == "ServiceRequest"]
        
        assert len(sr_entries) == 4
        
        # Verify priorities
        priorities = [entry["resource"]["priority"] for entry in sr_entries]
        assert priorities.count("stat") == 2
        assert priorities.count("routine") == 2
        
        # Verify categories
        lab_entries = [entry for entry in sr_entries
                       if entry["resource"]["category"][0]["coding"][0]["display"] == "Laboratory procedure"]
        proc_entries = [entry for entry in sr_entries
                        if entry["resource"]["category"][0]["coding"][0]["display"] == "Surgical procedure"]
        
        assert len(lab_entries) == 2
        assert len(proc_entries) == 2
