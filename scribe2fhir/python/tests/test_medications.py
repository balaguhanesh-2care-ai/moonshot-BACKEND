"""
Test cases for Medication resources (prescriptions and history).
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import (
    FHIRDocumentBuilder,
    DosageBuilder,
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationStatementStatus,
    RouteOfAdministration,
    EventTiming
)


class TestMedicationPrescriptions:
    """Test medication prescription (MedicationRequest) functionality."""
    
    def test_basic_medication_prescription(self, encounter_builder, sample_dosage):
        """Test creating a medication prescription with minimal information."""
        medication_request = encounter_builder.add_medication_prescribed(
            medication="Paracetamol 500mg",
            dosage=sample_dosage
        )
        
        # Verify medication request was created
        assert medication_request is not None
        assert medication_request.get_resource_type() == "MedicationRequest"
        assert medication_request.id is not None
        
        # Verify default values
        assert medication_request.status == "active"
        assert medication_request.intent == "order"
        
        # Verify medication
        assert medication_request.medication.text == "Paracetamol 500mg"
        
        # Verify dosage
        assert len(medication_request.dosageInstruction) == 1
        dosage = medication_request.dosageInstruction[0]
        assert dosage.text == "Take 1 tablet three times daily after meals"
        
        # Verify references
        assert medication_request.subject is not None
        assert "Patient/" in medication_request.subject.reference
        assert medication_request.encounter is not None
        assert "Encounter/" in medication_request.encounter.reference
    
    def test_medication_prescription_with_all_properties(self, encounter_builder, sample_dosage, test_dates):
        """Test creating a comprehensive medication prescription."""
        medication_request = encounter_builder.add_medication_prescribed(
            medication="Dolo 650 Tablet",
            dosage=sample_dosage,
            status=MedicationRequestStatus.ACTIVE,
            intent=MedicationRequestIntent.ORDER,
            duration_value=7,
            duration_unit="d",
            quantity_value=21,
            quantity_unit="tablet",
            refills=2,
            notes="Dose: 1 tablet",
            reason="Fever and pain",
            authored_on=test_dates['now']
        )
        
        # Verify basic properties
        assert medication_request.medication.text == "Dolo 650 Tablet"
        assert medication_request.status == "active"
        assert medication_request.intent == "order"
        
        # Verify authored date
        assert medication_request.authoredOn.replace(tzinfo=None, microsecond=0) == test_dates['now'].replace(microsecond=0)
        
        # Verify dispense request
        assert medication_request.dispenseRequest is not None
        dispense = medication_request.dispenseRequest
        
        # Duration
        assert dispense.expectedSupplyDuration is not None
        assert dispense.expectedSupplyDuration.value == 7
        assert dispense.expectedSupplyDuration.unit == "d"
        
        # Quantity
        assert dispense.quantity is not None
        assert dispense.quantity.value == 21
        assert dispense.quantity.unit == "tablet"
        
        # Refills
        assert dispense.numberOfRepeatsAllowed == 2
        
        # Verify notes
        assert len(medication_request.note) == 1
        assert medication_request.note[0].text == "Dose: 1 tablet"
        
        # Verify reason
        assert len(medication_request.reasonCode) == 1
        assert medication_request.reasonCode[0].text == "Fever and pain"
    
    def test_medication_request_status_values(self, encounter_builder, sample_dosage):
        """Test different medication request status values."""
        status_tests = [
            (MedicationRequestStatus.ACTIVE, "active"),
            (MedicationRequestStatus.ON_HOLD, "on-hold"),
            (MedicationRequestStatus.CANCELLED, "cancelled"),
            (MedicationRequestStatus.COMPLETED, "completed"),
            ("active", "active"),  # String input
            ("completed", "completed")
        ]
        
        for status_input, expected_status in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            med_request = builder.add_medication_prescribed(
                medication="Test Medication",
                dosage=sample_dosage,
                status=status_input
            )
            
            assert med_request.status == expected_status
    
    def test_medication_request_intent_values(self, encounter_builder, sample_dosage):
        """Test different medication request intent values."""
        intent_tests = [
            (MedicationRequestIntent.PROPOSAL, "proposal"),
            (MedicationRequestIntent.PLAN, "plan"),
            (MedicationRequestIntent.ORDER, "order"),
            (MedicationRequestIntent.ORIGINAL_ORDER, "original-order"),
            ("order", "order"),  # String input
            ("plan", "plan")
        ]
        
        for intent_input, expected_intent in intent_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            builder.add_encounter()
            
            med_request = builder.add_medication_prescribed(
                medication="Test Medication",
                dosage=sample_dosage,
                intent=intent_input
            )
            
            assert med_request.intent == expected_intent
    
    def test_medication_prescription_without_dosage(self, encounter_builder):
        """Test medication prescription without dosage instructions."""
        medication_request = encounter_builder.add_medication_prescribed(
            medication="Simple Medication",
            notes="As directed by physician"
        )
        
        assert medication_request.medication.text == "Simple Medication"
        assert medication_request.dosageInstruction is None or len(medication_request.dosageInstruction) == 0
        assert medication_request.note[0].text == "As directed by physician"


class TestDosageBuilder:
    """Test dosage builder functionality."""
    
    def test_basic_dosage_creation(self):
        """Test creating a basic dosage."""
        dosage = DosageBuilder.build(
            dose_value=1,
            dose_unit="tablet",
            frequency=2,
            period=1,
            period_unit="d"
        )
        
        assert dosage is not None
        assert dosage.doseAndRate[0].doseQuantity.value == 1
        assert dosage.doseAndRate[0].doseQuantity.unit == "tablet"
        
        # Verify timing
        assert dosage.timing.repeat.frequency == 2
        assert dosage.timing.repeat.period == 1
        assert dosage.timing.repeat.periodUnit == "d"
    
    def test_dosage_with_route_and_timing(self):
        """Test dosage with route of administration and timing."""
        dosage = DosageBuilder.build(
            dose_value=5,
            dose_unit="ml",
            frequency=3,
            period=1,
            period_unit="d",
            route=RouteOfAdministration.ORAL,
            timing_code=EventTiming.AFTER_MEAL,
            text="Take 5ml three times daily after meals"
        )
        
        # Verify route
        assert dosage.route is not None
        assert dosage.route.coding[0].code == "26643006"
        assert dosage.route.text == "Oral"
        
        # Verify timing code (stored in when field)
        assert dosage.timing.repeat.when is not None
        assert "PC" in dosage.timing.repeat.when  # After meals
        
        # Verify text
        assert dosage.text == "Take 5ml three times daily after meals"
    
    def test_dosage_route_values(self):
        """Test different route of administration values."""
        route_tests = [
            (RouteOfAdministration.ORAL, "26643006", "Oral"),
            (RouteOfAdministration.TOPICAL, "6064005", "Topical"),
            (RouteOfAdministration.INTRAVENOUS, "47625008", "Intravenous"),
            (RouteOfAdministration.INTRAMUSCULAR, "78421000", "Intramuscular"),
        ]
        
        for route_enum, expected_code, expected_text in route_tests:
            dosage = DosageBuilder.build(
                dose_value=1,
                dose_unit="unit",
                frequency=1,
                period=1,
                period_unit="d",
                route=route_enum
            )
            
            assert dosage.route.coding[0].code == expected_code
            assert dosage.route.text == expected_text
    
    def test_dosage_timing_codes(self):
        """Test different timing codes."""
        timing_tests = [
            (EventTiming.BEFORE_MEAL, "AC", "Before meals"),
            (EventTiming.AFTER_MEAL, "PC", "After meals"),
            (EventTiming.BEDTIME, "HS", "At bedtime"),
            (EventTiming.MORNING, "MORN", "Morning"),
        ]
        
        for timing_enum, expected_code, expected_text in timing_tests:
            dosage = DosageBuilder.build(
                dose_value=1,
                dose_unit="tablet",
                frequency=1,
                period=1,
                period_unit="d",
                timing_code=timing_enum
            )
            
            # Verify timing code is in when field
            assert dosage.timing.repeat.when is not None
            assert expected_code in dosage.timing.repeat.when
    
    def test_dosage_complex_frequency(self):
        """Test complex dosage frequencies."""
        # BID (twice daily)
        dosage_bid = DosageBuilder.build(
            dose_value=2,
            dose_unit="capsule",
            frequency=2,
            period=1,
            period_unit="d"
        )
        
        assert dosage_bid.timing.repeat.frequency == 2
        assert dosage_bid.timing.repeat.period == 1
        assert dosage_bid.timing.repeat.periodUnit == "d"
        
        # QID (four times daily)
        dosage_qid = DosageBuilder.build(
            dose_value=1,
            dose_unit="tablet",
            frequency=4,
            period=1,
            period_unit="d"
        )
        
        assert dosage_qid.timing.repeat.frequency == 4
    
    def test_dosage_weekly_frequency(self):
        """Test weekly dosage frequency."""
        dosage = DosageBuilder.build(
            dose_value=10,
            dose_unit="mg",
            frequency=1,
            period=1,
            period_unit="wk"
        )
        
        assert dosage.timing.repeat.frequency == 1
        assert dosage.timing.repeat.period == 1
        assert dosage.timing.repeat.periodUnit == "wk"


class TestMedicationHistory:
    """Test medication history (MedicationStatement) functionality."""
    
    def test_basic_medication_history(self, encounter_builder, sample_dosage):
        """Test creating a medication history with minimal information."""
        medication_statement = encounter_builder.add_medication_history(
            medication="Crocin 600"
        )
        
        # Verify medication statement was created
        assert medication_statement is not None
        assert medication_statement.get_resource_type() == "MedicationStatement"
        assert medication_statement.id is not None
        
        # Verify default status
        assert medication_statement.status == "active"
        
        # Verify medication
        assert medication_statement.medication.text == "Crocin 600"
        
        # Verify references
        assert medication_statement.subject is not None
        assert "Patient/" in medication_statement.subject.reference
    
    def test_medication_history_with_all_properties(self, encounter_builder, sample_dosage, test_dates):
        """Test creating comprehensive medication history."""
        medication_statement = encounter_builder.add_medication_history(
            medication="Crocin 600",
            dosage=sample_dosage,
            status=MedicationStatementStatus.ACTIVE,
            effective_start=test_dates['month_ago'],
            effective_end=test_dates['now'],
            notes="Every week once",
            reason="Pain management",
            date_asserted=test_dates['now']
        )
        
        # Verify basic properties
        assert medication_statement.medication.text == "Crocin 600"
        assert medication_statement.status == "active"
        
        # Verify effective period
        assert medication_statement.effectivePeriod is not None
        assert medication_statement.effectivePeriod.start.replace(tzinfo=None, microsecond=0) == test_dates['month_ago'].replace(microsecond=0)
        assert medication_statement.effectivePeriod.end.replace(tzinfo=None, microsecond=0) == test_dates['now'].replace(microsecond=0)
        
        # Verify dosage
        assert len(medication_statement.dosage) == 1
        
        # Verify notes
        assert len(medication_statement.note) == 1
        assert medication_statement.note[0].text == "Every week once"
        
        # Verify reason
        assert len(medication_statement.reasonCode) == 1
        assert medication_statement.reasonCode[0].text == "Pain management"
        
        # Verify date asserted
        assert medication_statement.dateAsserted.replace(tzinfo=None, microsecond=0) == test_dates['now'].replace(microsecond=0)
    
    def test_medication_statement_status_values(self, encounter_builder):
        """Test different medication statement status values."""
        status_tests = [
            (MedicationStatementStatus.ACTIVE, "active"),
            (MedicationStatementStatus.COMPLETED, "completed"),
            (MedicationStatementStatus.INTENDED, "intended"),
            (MedicationStatementStatus.STOPPED, "stopped"),
            ("active", "active"),  # String input
            ("completed", "completed")
        ]
        
        for status_input, expected_status in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            med_statement = builder.add_medication_history(
                medication="Test Medication",
                status=status_input
            )
            
            assert med_statement.status == expected_status
    
    def test_medication_history_with_start_only(self, encounter_builder, test_dates):
        """Test medication history with only start date (ongoing)."""
        medication_statement = encounter_builder.add_medication_history(
            medication="Ongoing Medication",
            effective_start=test_dates['month_ago']
        )
        
        assert medication_statement.effectivePeriod.start.replace(tzinfo=None, microsecond=0) == test_dates['month_ago'].replace(microsecond=0)
        assert medication_statement.effectivePeriod.end is None


class TestMedicationBundleIntegration:
    """Test medication integration in FHIR bundles."""
    
    def test_medications_in_fhir_bundle(self, encounter_builder, sample_dosage):
        """Test medications appear correctly in FHIR bundle."""
        # Add prescription
        encounter_builder.add_medication_prescribed(
            medication="Prescribed Med",
            dosage=sample_dosage,
            duration_value=7,
            duration_unit="d"
        )
        
        # Add history
        encounter_builder.add_medication_history(
            medication="History Med",
            status=MedicationStatementStatus.ACTIVE
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Find medication entries
        med_request_entries = [entry for entry in bundle_dict["entry"]
                              if entry["resource"]["resourceType"] == "MedicationRequest"]
        med_statement_entries = [entry for entry in bundle_dict["entry"]
                               if entry["resource"]["resourceType"] == "MedicationStatement"]
        
        assert len(med_request_entries) == 1
        assert len(med_statement_entries) == 1
        
        # Verify medication request
        med_request = med_request_entries[0]["resource"]
        assert med_request["medication"]["text"] == "Prescribed Med"
        assert med_request["status"] == "active"
        assert med_request["intent"] == "order"
        
        # Verify medication statement
        med_statement = med_statement_entries[0]["resource"]
        assert med_statement["medication"]["text"] == "History Med"
        assert med_statement["status"] == "active"
    
    def test_multiple_medications_same_type(self, encounter_builder, sample_dosage):
        """Test multiple medications of same type."""
        # Multiple prescriptions
        med1 = encounter_builder.add_medication_prescribed(
            medication="Med 1",
            dosage=sample_dosage
        )
        
        med2 = encounter_builder.add_medication_prescribed(
            medication="Med 2",
            dosage=sample_dosage
        )
        
        # Multiple history
        hist1 = encounter_builder.add_medication_history(
            medication="History Med 1"
        )
        
        hist2 = encounter_builder.add_medication_history(
            medication="History Med 2"
        )
        
        # Verify all have different IDs
        assert len({med1.id, med2.id, hist1.id, hist2.id}) == 4
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        
        med_request_entries = [entry for entry in bundle_dict["entry"]
                              if entry["resource"]["resourceType"] == "MedicationRequest"]
        med_statement_entries = [entry for entry in bundle_dict["entry"]
                               if entry["resource"]["resourceType"] == "MedicationStatement"]
        
        assert len(med_request_entries) == 2
        assert len(med_statement_entries) == 2
    
    def test_medication_references_in_bundle(self, encounter_builder, sample_dosage):
        """Test medication references in bundle."""
        encounter_builder.add_medication_prescribed(
            medication="Reference Test Med",
            dosage=sample_dosage
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        med_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "MedicationRequest"), None)
        
        assert med_entry is not None
        medication = med_entry["resource"]
        
        # Verify references
        assert "subject" in medication
        assert medication["subject"]["reference"].startswith("Patient/")
        assert "encounter" in medication
        assert medication["encounter"]["reference"].startswith("Encounter/")
    
    def test_coded_medications_in_bundle(self, encounter_builder):
        """Test coded medications appear correctly in bundle."""
        # Test with RxNorm code
        encounter_builder.add_medication_prescribed(
            medication=("313782", "http://www.nlm.nih.gov/research/umls/rxnorm", "Acetaminophen 325 MG Oral Tablet")
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        med_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "MedicationRequest"), None)
        
        medication = med_entry["resource"]
        
        # Verify coding
        assert medication["medication"]["coding"][0]["code"] == "313782"
        assert medication["medication"]["coding"][0]["system"] == "http://www.nlm.nih.gov/research/umls/rxnorm"
        assert medication["medication"]["coding"][0]["display"] == "Acetaminophen 325 MG Oral Tablet"
        assert medication["medication"]["text"] == "Acetaminophen 325 MG Oral Tablet"
