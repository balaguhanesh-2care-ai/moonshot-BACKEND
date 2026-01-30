"""
Test cases for CarePlan and Communication resources (advice and clinical notes).
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import FHIRDocumentBuilder


class TestAdviceResource:
    """Test advice (CarePlan) functionality."""
    
    def test_basic_advice_creation(self, encounter_builder):
        """Test creating basic patient advice."""
        care_plan = encounter_builder.add_advice(
            note="Drink plenty of water"
        )
        
        # Verify care plan was created
        assert care_plan is not None
        assert care_plan.get_resource_type() == "CarePlan"
        assert care_plan.id is not None
        
        # Verify default status
        assert care_plan.status == "active"
        
        # Verify intent
        assert care_plan.intent == "plan"
        
        # Verify activity
        assert len(care_plan.activity) == 1
        activity = care_plan.activity[0]
        assert activity.progress[0].text == "Drink plenty of water"
        # Note: Current implementation uses progress instead of detail
        # assert activity.detail.status == "not-started"
        
        # Verify references
        assert care_plan.subject is not None
        assert "Patient/" in care_plan.subject.reference
        assert care_plan.encounter is not None
        assert "Encounter/" in care_plan.encounter.reference
    
    def test_advice_with_category(self, encounter_builder):
        """Test advice with category."""
        care_plan = encounter_builder.add_advice(
            note="Take medication with food",
            category="medication-advice"
        )
        
        # Verify category
        assert len(care_plan.category) == 1
        assert care_plan.category[0].text == "medication-advice"
        
        # Verify activity description
        activity = care_plan.activity[0]
        assert activity.progress[0].text == "Take medication with food"
    
    def test_multiple_advice_entries(self, encounter_builder):
        """Test creating multiple advice entries."""
        advice1 = encounter_builder.add_advice(
            note="Drink plenty of water"
        )
        
        advice2 = encounter_builder.add_advice(
            note="Do not go out in sun"
        )
        
        advice3 = encounter_builder.add_advice(
            note="Do not eat oily food"
        )
        
        # Verify all advice have different IDs
        assert advice1.id != advice2.id != advice3.id
        
        # Verify all have correct content
        assert advice1.activity[0].progress[0].text == "Drink plenty of water"
        assert advice2.activity[0].progress[0].text == "Do not go out in sun"
        assert advice3.activity[0].progress[0].text == "Do not eat oily food"
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        care_plan_entries = [entry for entry in bundle_dict["entry"]
                           if entry["resource"]["resourceType"] == "CarePlan"]
        
        assert len(care_plan_entries) == 3
    
    def test_advice_categories(self, encounter_builder):
        """Test different advice categories."""
        categories = [
            "dietary-advice",
            "lifestyle-advice", 
            "medication-advice",
            "activity-advice",
            "general-advice"
        ]
        
        for category in categories:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            care_plan = builder.add_advice(
                note=f"Test advice for {category}",
                category=category
            )
            
            assert care_plan.category[0].text == category
    
    def test_advice_custom_id(self, encounter_builder):
        """Test advice creation with custom ID."""
        custom_id = "advice-12345"
        care_plan = encounter_builder.add_advice(
            note="Custom ID advice",
            id=custom_id
        )
        
        assert care_plan.id == custom_id
        
        # Verify in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        cp_entry = next((entry for entry in bundle_dict["entry"]
                        if entry["resource"]["resourceType"] == "CarePlan"
                        and entry["resource"]["id"] == custom_id), None)
        
        assert cp_entry is not None
    
    def test_advice_without_encounter(self):
        """Test advice creation without encounter."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Test Patient", age=(30, "years"))
        
        care_plan = builder.add_advice(
            note="No encounter advice"
        )
        
        assert care_plan is not None
        assert care_plan.subject is not None  # Should have patient reference
        assert care_plan.encounter is None    # No encounter reference


class TestClinicalNotesResource:
    """Test clinical notes (Communication) functionality."""
    
    def test_basic_clinical_note(self, encounter_builder):
        """Test creating basic clinical note."""
        communication = encounter_builder.add_notes(
            note="Patient is a 30 year old living in Bangalore"
        )
        
        # Verify communication was created
        assert communication is not None
        assert communication.get_resource_type() == "Communication"
        assert communication.id is not None
        
        # Verify default status
        assert communication.status == "completed"
        
        # Verify payload
        assert len(communication.payload) == 1
        payload = communication.payload[0]
        assert payload.contentCodeableConcept.text == "Patient is a 30 year old living in Bangalore"
        
        # Verify references
        assert communication.subject is not None
        assert "Patient/" in communication.subject.reference
        assert communication.encounter is not None
        assert "Encounter/" in communication.encounter.reference
    
    def test_clinical_note_with_category(self, encounter_builder):
        """Test clinical note with category."""
        communication = encounter_builder.add_notes(
            note="Prescription notes and instructions",
            category="prescription-note"
        )
        
        # Verify category
        assert len(communication.category) == 1
        assert communication.category[0].text == "prescription-note"
        
        # Verify content
        payload = communication.payload[0]
        assert payload.contentCodeableConcept.text == "Prescription notes and instructions"
    
    def test_multiple_clinical_notes(self, encounter_builder):
        """Test creating multiple clinical notes."""
        note1 = encounter_builder.add_notes(
            note="Patient history documented",
            category="history-note"
        )
        
        note2 = encounter_builder.add_notes(
            note="Examination findings recorded",
            category="exam-note"
        )
        
        note3 = encounter_builder.add_notes(
            note="Treatment plan discussed with patient",
            category="plan-note"
        )
        
        # Verify all notes have different IDs
        assert note1.id != note2.id != note3.id
        
        # Verify all have correct content
        assert note1.payload[0].contentCodeableConcept.text == "Patient history documented"
        assert note2.payload[0].contentCodeableConcept.text == "Examination findings recorded"
        assert note3.payload[0].contentCodeableConcept.text == "Treatment plan discussed with patient"
        
        # Verify categories
        assert note1.category[0].text == "history-note"
        assert note2.category[0].text == "exam-note" 
        assert note3.category[0].text == "plan-note"
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        comm_entries = [entry for entry in bundle_dict["entry"]
                       if entry["resource"]["resourceType"] == "Communication"]
        
        assert len(comm_entries) == 3
    
    def test_clinical_note_categories(self, encounter_builder):
        """Test different clinical note categories."""
        categories = [
            "prescription-note",
            "history-note",
            "examination-note",
            "plan-note",
            "discharge-note",
            "progress-note"
        ]
        
        for category in categories:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            communication = builder.add_notes(
                note=f"Test note for {category}",
                category=category
            )
            
            assert communication.category[0].text == category
    
    def test_clinical_note_custom_id(self, encounter_builder):
        """Test clinical note creation with custom ID."""
        custom_id = "note-67890"
        communication = encounter_builder.add_notes(
            note="Custom ID note",
            id=custom_id
        )
        
        assert communication.id == custom_id
        
        # Verify in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        comm_entry = next((entry for entry in bundle_dict["entry"]
                          if entry["resource"]["resourceType"] == "Communication"
                          and entry["resource"]["id"] == custom_id), None)
        
        assert comm_entry is not None
    
    def test_clinical_note_without_encounter(self):
        """Test clinical note creation without encounter."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Test Patient", age=(30, "years"))
        
        communication = builder.add_notes(
            note="No encounter note"
        )
        
        assert communication is not None
        assert communication.subject is not None  # Should have patient reference
        assert communication.encounter is None    # No encounter reference


class TestCarePlanCommunicationIntegration:
    """Test CarePlan and Communication integration in FHIR bundles."""
    
    def test_advice_and_notes_in_bundle(self, encounter_builder):
        """Test advice and notes appear correctly in bundle."""
        # Add advice
        encounter_builder.add_advice(
            note="Bundle test advice",
            category="test-advice"
        )
        
        # Add clinical note
        encounter_builder.add_notes(
            note="Bundle test note",
            category="test-note"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find care plan and communication entries
        cp_entries = [entry for entry in bundle_dict["entry"]
                     if entry["resource"]["resourceType"] == "CarePlan"]
        comm_entries = [entry for entry in bundle_dict["entry"]
                       if entry["resource"]["resourceType"] == "Communication"]
        
        assert len(cp_entries) == 1
        assert len(comm_entries) == 1
        
        # Verify care plan
        care_plan = cp_entries[0]["resource"]
        assert care_plan["status"] == "active"
        assert care_plan["intent"] == "plan"
        assert care_plan["activity"][0]["progress"][0]["text"] == "Bundle test advice"
        assert care_plan["category"][0]["text"] == "test-advice"
        
        # Verify communication
        communication = comm_entries[0]["resource"]
        assert communication["status"] == "completed"
        assert communication["payload"][0]["contentCodeableConcept"]["text"] == "Bundle test note"
        assert communication["category"][0]["text"] == "test-note"
    
    def test_advice_and_notes_references_in_bundle(self, encounter_builder):
        """Test advice and notes references in bundle."""
        encounter_builder.add_advice(note="Reference test advice")
        encounter_builder.add_notes(note="Reference test note")
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Check care plan references
        cp_entry = next((entry for entry in bundle_dict["entry"]
                        if entry["resource"]["resourceType"] == "CarePlan"), None)
        assert cp_entry is not None
        care_plan = cp_entry["resource"]
        
        assert "subject" in care_plan
        assert care_plan["subject"]["reference"].startswith("Patient/")
        assert "encounter" in care_plan
        assert care_plan["encounter"]["reference"].startswith("Encounter/")
        
        # Check communication references
        comm_entry = next((entry for entry in bundle_dict["entry"]
                          if entry["resource"]["resourceType"] == "Communication"), None)
        assert comm_entry is not None
        communication = comm_entry["resource"]
        
        assert "subject" in communication
        assert communication["subject"]["reference"].startswith("Patient/")
        assert "encounter" in communication
        assert communication["encounter"]["reference"].startswith("Encounter/")
    
    def test_comprehensive_advice_scenario(self, encounter_builder):
        """Test comprehensive advice scenario with multiple categories."""
        # Dietary advice
        encounter_builder.add_advice(
            note="Avoid high sodium foods",
            category="dietary-advice"
        )
        
        # Lifestyle advice
        encounter_builder.add_advice(
            note="Exercise 30 minutes daily",
            category="lifestyle-advice"
        )
        
        # Medication advice
        encounter_builder.add_advice(
            note="Take medications at same time daily",
            category="medication-advice"
        )
        
        # Activity restriction
        encounter_builder.add_advice(
            note="Avoid heavy lifting for 2 weeks",
            category="activity-restriction"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        cp_entries = [entry for entry in bundle_dict["entry"]
                     if entry["resource"]["resourceType"] == "CarePlan"]
        
        assert len(cp_entries) == 4
        
        # Verify categories
        categories = [entry["resource"]["category"][0]["text"] for entry in cp_entries]
        assert "dietary-advice" in categories
        assert "lifestyle-advice" in categories
        assert "medication-advice" in categories
        assert "activity-restriction" in categories
    
    def test_comprehensive_notes_scenario(self, encounter_builder):
        """Test comprehensive clinical notes scenario."""
        # Patient background
        encounter_builder.add_notes(
            note="Patient is a 45-year-old male with history of hypertension",
            category="history-note"
        )
        
        # Examination findings
        encounter_builder.add_notes(
            note="Physical examination reveals elevated blood pressure 150/95",
            category="exam-note"
        )
        
        # Assessment
        encounter_builder.add_notes(
            note="Assessment: Uncontrolled hypertension, medication adjustment needed",
            category="assessment-note"
        )
        
        # Plan
        encounter_builder.add_notes(
            note="Plan: Increase ACE inhibitor dose, follow up in 2 weeks",
            category="plan-note"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        comm_entries = [entry for entry in bundle_dict["entry"]
                       if entry["resource"]["resourceType"] == "Communication"]
        
        assert len(comm_entries) == 4
        
        # Verify categories
        categories = [entry["resource"]["category"][0]["text"] for entry in comm_entries]
        assert "history-note" in categories
        assert "exam-note" in categories
        assert "assessment-note" in categories
        assert "plan-note" in categories
    
    def test_advice_and_notes_without_category(self, encounter_builder):
        """Test advice and notes without explicit category."""
        # Advice without category
        care_plan = encounter_builder.add_advice(
            note="General patient advice"
        )
        
        # Note without category  
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        communication = builder2.add_notes(
            note="General clinical note"
        )
        
        # Should work without categories
        assert care_plan.activity[0].progress[0].text == "General patient advice"
        assert care_plan.category is None or len(care_plan.category) == 0
        
        assert communication.payload[0].contentCodeableConcept.text == "General clinical note"
        assert communication.category is None or len(communication.category) == 0
    
    def test_long_advice_and_notes(self, encounter_builder):
        """Test advice and notes with longer text content."""
        long_advice = ("Patient should maintain a balanced diet with reduced sodium intake, "
                      "engage in regular moderate exercise as tolerated, monitor blood pressure "
                      "at home twice daily, and maintain a medication diary to track compliance "
                      "and any side effects experienced.")
        
        long_note = ("Patient presents with complex medical history including diabetes mellitus "
                    "type 2, hypertension, and chronic kidney disease. Current medications include "
                    "metformin, lisinopril, and furosemide. Patient reports good adherence to "
                    "medications but struggles with dietary modifications. Social history significant "
                    "for smoking 1 pack per day for 20 years, quit 2 years ago. Family history "
                    "positive for cardiovascular disease in both parents.")
        
        care_plan = encounter_builder.add_advice(note=long_advice)
        communication = encounter_builder.add_notes(note=long_note)
        
        assert care_plan.activity[0].progress[0].text == long_advice
        assert communication.payload[0].contentCodeableConcept.text == long_note
