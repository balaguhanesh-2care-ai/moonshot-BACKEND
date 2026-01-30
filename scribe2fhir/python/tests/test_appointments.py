"""
Test cases for Appointment resources (follow-up appointments).
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import FHIRDocumentBuilder


class TestAppointmentResource:
    """Test appointment (follow-up) functionality."""
    
    def test_basic_followup_appointment(self, encounter_builder, test_dates):
        """Test creating a basic follow-up appointment."""
        appointment = encounter_builder.add_followup(
            date=test_dates['future']
        )
        
        # Verify appointment was created
        assert appointment is not None
        assert appointment.get_resource_type() == "Appointment"
        assert appointment.id is not None
        
        # Verify default status
        assert appointment.status == "booked"
        
        # Verify start time (allow for microsecond differences)
        start_time = appointment.start.replace(tzinfo=None, microsecond=0)
        expected_time = test_dates['future'].replace(microsecond=0)
        assert start_time == expected_time
        
        # Verify patient participant
        assert len(appointment.participant) >= 1
        patient_participant = next((p for p in appointment.participant 
                                  if p.actor and "Patient/" in p.actor.reference), None)
        assert patient_participant is not None
        assert patient_participant.status == "accepted"
        # Note: required field is not set by current implementation
    
    def test_followup_with_all_properties(self, encounter_builder, test_dates):
        """Test comprehensive follow-up appointment."""
        appointment = encounter_builder.add_followup(
            date=test_dates['future'],
            ref_doctor="Dr. Smith",
            ref_specialty="Cardiology",
            notes="Come with empty stomach"
        )
        
        # Verify appointment date
        assert appointment.start.replace(tzinfo=None, microsecond=0) == test_dates['future'].replace(microsecond=0)
        
        # Verify practitioner participant
        practitioner_participant = next((p for p in appointment.participant 
                                       if p.actor and p.actor.display == "Dr. Smith"), None)
        assert practitioner_participant is not None
        assert practitioner_participant.status == "accepted"
        
        # Verify specialty
        assert len(appointment.specialty) >= 1
        assert appointment.specialty[0].text == "Cardiology"
        
        # Verify comment/notes
        assert len(appointment.note) == 1
        assert appointment.note[0].text == "Come with empty stomach"
    
    def test_followup_date_formats(self, encounter_builder):
        """Test different date formats for follow-up."""
        # Test with string date
        appointment1 = encounter_builder.add_followup(
            date="2025-05-21"
        )
        assert appointment1.start is not None
        
        # Test with datetime object
        dt = datetime(2025, 5, 21, 10, 0, 0)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        appointment2 = builder2.add_followup(date=dt)
        assert appointment2.start.replace(tzinfo=None) == dt
    
    def test_followup_with_doctor_only(self, encounter_builder, test_dates):
        """Test follow-up with doctor but no specialty."""
        appointment = encounter_builder.add_followup(
            date=test_dates['future'],
            ref_doctor="Dr. Johnson"
        )
        
        # Verify practitioner participant
        practitioner_participant = next((p for p in appointment.participant 
                                       if p.actor and p.actor.display == "Dr. Johnson"), None)
        assert practitioner_participant is not None
        
        # Should not have specific appointment type
        assert appointment.appointmentType is None
    
    def test_followup_with_specialty_only(self, encounter_builder, test_dates):
        """Test follow-up with specialty but no specific doctor."""
        appointment = encounter_builder.add_followup(
            date=test_dates['future'],
            ref_specialty="Neurology"
        )
        
        # Verify specialty
        assert appointment.specialty is not None
        assert appointment.specialty[0].text == "Neurology"
        
        # Should not have specific practitioner (only patient)
        practitioner_participants = [p for p in appointment.participant 
                                   if p.actor and "Practitioner/" in (p.actor.reference or "")]
        assert len(practitioner_participants) == 0
    
    def test_followup_with_notes_only(self, encounter_builder, test_dates):
        """Test follow-up with only notes."""
        appointment = encounter_builder.add_followup(
            date=test_dates['future'],
            notes="Follow-up in 2 weeks for test results"
        )
        
        assert appointment.note[0].text == "Follow-up in 2 weeks for test results"
        # Should only have patient participant
        assert len(appointment.participant) == 1
        assert "Patient/" in appointment.participant[0].actor.reference
    
    def test_multiple_followup_appointments(self, encounter_builder, test_dates):
        """Test creating multiple follow-up appointments."""
        # Immediate follow-up
        app1 = encounter_builder.add_followup(
            date=test_dates['future'],
            ref_doctor="Dr. Primary",
            notes="1 week follow-up"
        )
        
        # Later follow-up
        future_date = test_dates['future'] + timedelta(days=30)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        app2 = builder2.add_followup(
            date=future_date,
            ref_specialty="Cardiology",
            notes="1 month cardiology follow-up"
        )
        
        # Verify appointments have different IDs
        assert app1.id != app2.id
        
        # Verify different properties
        assert app1.note[0].text == "1 week follow-up"
        assert app2.note[0].text == "1 month cardiology follow-up"
    
    def test_followup_without_encounter(self):
        """Test follow-up creation without encounter."""
        builder = FHIRDocumentBuilder()
        builder.add_patient(name="Test Patient", age=(30, "years"))
        
        future_date = datetime.now() + timedelta(days=7)
        appointment = builder.add_followup(
            date=future_date,
            notes="No encounter follow-up"
        )
        
        assert appointment is not None
        # Should still have patient participant
        patient_participant = next((p for p in appointment.participant 
                                  if p.actor and "Patient/" in p.actor.reference), None)
        assert patient_participant is not None
    
    def test_followup_custom_id(self, encounter_builder, test_dates):
        """Test follow-up creation with custom ID."""
        custom_id = "appointment-followup-123"
        appointment = encounter_builder.add_followup(
            date=test_dates['future'],
            id=custom_id
        )
        
        assert appointment.id == custom_id
        
        # Verify in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        app_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "Appointment"
                         and entry["resource"]["id"] == custom_id), None)
        
        assert app_entry is not None


class TestAppointmentBundleIntegration:
    """Test appointment integration in FHIR bundles."""
    
    def test_appointment_in_fhir_bundle(self, encounter_builder, test_dates):
        """Test appointment appears correctly in FHIR bundle."""
        encounter_builder.add_followup(
            date=test_dates['future'],
            ref_doctor="Bundle Test Doctor",
            ref_specialty="Bundle Test Specialty",
            notes="Bundle test appointment"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find appointment entry
        app_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "Appointment"), None)
        
        assert app_entry is not None
        appointment = app_entry["resource"]
        
        # Verify appointment details
        assert appointment["status"] == "booked"
        assert appointment["note"][0]["text"] == "Bundle test appointment"
        
        # Verify start time
        assert "start" in appointment
        
        # Verify participants
        assert "participant" in appointment
        assert len(appointment["participant"]) >= 1
        
        # Check patient participant
        patient_participant = next((p for p in appointment["participant"]
                                  if p["actor"]["reference"].startswith("Patient/")), None)
        assert patient_participant is not None
        assert patient_participant["status"] == "accepted"
        # Note: required field is not set in current implementation
    
    def test_appointment_references_in_bundle(self, encounter_builder, test_dates):
        """Test appointment references in bundle."""
        encounter_builder.add_followup(
            date=test_dates['future'],
            ref_doctor="Reference Test Doctor"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        app_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "Appointment"), None)
        
        appointment = app_entry["resource"]
        
        # Verify patient reference
        patient_participant = next((p for p in appointment["participant"]
                                  if p["actor"]["reference"].startswith("Patient/")), None)
        assert patient_participant is not None
    
    def test_multiple_appointments_in_bundle(self, encounter_builder, test_dates):
        """Test multiple appointments in bundle."""
        # Note: Current implementation only supports one appointment per builder
        # This tests the behavior when multiple follow-ups are attempted
        
        app1 = encounter_builder.add_followup(
            date=test_dates['future'],
            notes="First appointment"
        )
        
        future_date2 = test_dates['future'] + timedelta(days=7)
        app2 = encounter_builder.add_followup(
            date=future_date2,
            notes="Second appointment"
        )
        
        # Second appointment should replace the first (based on current implementation)
        assert app2.id != app1.id
        
        bundle_dict = encounter_builder.convert_to_fhir()
        app_entries = [entry for entry in bundle_dict["entry"]
                      if entry["resource"]["resourceType"] == "Appointment"]
        
        # Should have both appointments in bundle (implementation supports multiple)
        assert len(app_entries) == 2
        # Verify both appointments are present
        notes_in_bundle = [entry["resource"]["note"][0]["text"] for entry in app_entries]
        assert "First appointment" in notes_in_bundle
        assert "Second appointment" in notes_in_bundle
    
    def test_appointment_specialties_and_doctors(self, encounter_builder, test_dates):
        """Test various specialties and doctor combinations."""
        specialties_and_doctors = [
            ("Cardiology", "Dr. Heart"),
            ("Neurology", "Dr. Brain"),
            ("Orthopedics", "Dr. Bone"),
            ("General Medicine", "Dr. Primary")
        ]
        
        for specialty, doctor in specialties_and_doctors:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            appointment = builder.add_followup(
                date=test_dates['future'],
                ref_doctor=doctor,
                ref_specialty=specialty
            )
            
            # Verify specialty
            assert appointment.specialty[0].text == specialty
            
            # Verify doctor
            practitioner_participant = next((p for p in appointment.participant 
                                           if p.actor and p.actor.display == doctor), None)
            assert practitioner_participant is not None
    
    def test_appointment_date_range_scenarios(self, encounter_builder):
        """Test different date scenarios for appointments."""
        now = datetime.now()
        
        # Same day follow-up
        same_day = now.replace(hour=17, minute=0, second=0, microsecond=0)
        app1 = encounter_builder.add_followup(
            date=same_day,
            notes="Same day follow-up"
        )
        
        # Next week follow-up
        next_week = now + timedelta(days=7)
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        builder2.add_encounter()
        
        app2 = builder2.add_followup(
            date=next_week,
            notes="Next week follow-up"
        )
        
        # Next month follow-up
        next_month = now + timedelta(days=30)
        builder3 = FHIRDocumentBuilder()
        builder3.add_patient(name="Test", age=(30, "years"))
        builder3.add_encounter()
        
        app3 = builder3.add_followup(
            date=next_month,
            notes="Next month follow-up"
        )
        
        # Verify all appointments have correct dates
        assert app1.start.replace(tzinfo=None) == same_day
        assert app2.start.replace(tzinfo=None, microsecond=0) == next_week.replace(microsecond=0)
        assert app3.start.replace(tzinfo=None, microsecond=0) == next_month.replace(microsecond=0)
    
    def test_appointment_notes_variations(self, encounter_builder, test_dates):
        """Test different types of appointment notes."""
        notes_examples = [
            "Come fasting for blood work",
            "Bring all previous reports",
            "Follow-up for medication review", 
            "Post-operative check-up",
            "Bring family member if possible"
        ]
        
        for notes in notes_examples:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            appointment = builder.add_followup(
                date=test_dates['future'],
                notes=notes
            )
            
            assert appointment.note[0].text == notes
