"""
Test cases for Medical History resources (family history, allergies, immunizations, procedures).
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import (
    FHIRDocumentBuilder,
    AllergyCategory,
    AllergyClinicalStatus,
    AllergyCriticality,
    ImmunizationStatus,
    ProcedureStatus
)


class TestFamilyHistory:
    """Test family history functionality."""
    
    def test_basic_family_history(self, encounter_builder):
        """Test creating basic family history."""
        family_history = encounter_builder.add_family_history(
            condition="Hypertension",
            relation="Father"
        )
        
        # Verify family history was created
        assert family_history is not None
        assert family_history.get_resource_type() == "FamilyMemberHistory"
        assert family_history.id is not None
        
        # Verify default status
        assert family_history.status == "completed"
        
        # Verify condition
        assert len(family_history.condition) == 1
        condition = family_history.condition[0]
        assert condition.code.text == "Hypertension"
        
        # Verify relationship
        assert family_history.relationship.text == "father"
        
        # Verify patient reference
        assert family_history.patient is not None
        assert "Patient/" in family_history.patient.reference
    
    def test_family_history_with_all_properties(self, encounter_builder):
        """Test comprehensive family history."""
        family_history = encounter_builder.add_family_history(
            condition="Type 2 diabetes",
            relation="Mother",
            onset="1997",
            status="completed",
            notes="Mother is dead now",
            deceased=True
        )
        
        # Verify condition with onset
        condition = family_history.condition[0]
        assert condition.code.text == "Type 2 diabetes"
        assert condition.onsetString == "1997"
        
        # Verify relationship
        assert family_history.relationship.text == "mother"
        
        # Verify status
        assert family_history.status == "completed"
        
        # Verify deceased status
        assert family_history.deceasedBoolean is True
        
        # Verify notes
        assert len(family_history.note) == 1
        assert family_history.note[0].text == "Mother is dead now"
    
    def test_family_history_relationships(self, encounter_builder):
        """Test different family relationships."""
        relationships = [
            "Father",
            "Mother", 
            "Brother",
            "Sister",
            "Son",
            "Daughter",
            "Grandfather",
            "Grandmother"
        ]
        
        for relation in relationships:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            family_history = builder.add_family_history(
                condition="Test Condition",
                relation=relation
            )
            
            assert family_history.relationship.text == relation
    
    def test_family_history_onset_formats(self, encounter_builder):
        """Test different onset formats for family history."""
        # Test with age
        fh1 = encounter_builder.add_family_history(
            condition="Diabetes",
            relation="Father",
            onset=45  # Age
        )
        
        condition1 = fh1.condition[0]
        assert condition1.onsetAge.value == 45
        
        # Test with year string
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        
        fh2 = builder2.add_family_history(
            condition="Diabetes",
            relation="Mother",
            onset="2010"  # Year
        )
        
        condition2 = fh2.condition[0]
        assert condition2.onsetString == "2010"
    
    def test_multiple_family_history_entries(self, encounter_builder):
        """Test adding multiple family history entries."""
        fh1 = encounter_builder.add_family_history(
            condition="Hypertension",
            relation="Father"
        )
        
        fh2 = encounter_builder.add_family_history(
            condition="Diabetes",
            relation="Mother"
        )
        
        fh3 = encounter_builder.add_family_history(
            condition="Heart disease",
            relation="Grandfather"
        )
        
        # Verify all have different IDs
        assert fh1.id != fh2.id != fh3.id
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        fh_entries = [entry for entry in bundle_dict["entry"]
                     if entry["resource"]["resourceType"] == "FamilyMemberHistory"]
        
        assert len(fh_entries) == 3


class TestAllergyHistory:
    """Test allergy and intolerance functionality."""
    
    def test_basic_allergy_history(self, encounter_builder):
        """Test creating basic allergy."""
        allergy = encounter_builder.add_allergy_history(
            code="Pollen allergy",
            category=AllergyCategory.ENVIRONMENT
        )
        
        # Verify allergy was created
        assert allergy is not None
        assert allergy.get_resource_type() == "AllergyIntolerance"
        assert allergy.id is not None
        
        # Verify default clinical status
        assert allergy.clinicalStatus.coding[0].code == "active"
        
        # Verify code
        assert allergy.code.text == "Pollen allergy"
        
        # Verify category
        assert allergy.category[0] == "environment"
        
        # Verify patient reference
        assert allergy.patient is not None
        assert "Patient/" in allergy.patient.reference
    
    def test_allergy_with_all_properties(self, encounter_builder):
        """Test comprehensive allergy."""
        allergy = encounter_builder.add_allergy_history(
            code="Paracetamol",
            category=AllergyCategory.MEDICATION,
            clinical_status=AllergyClinicalStatus.ACTIVE,
            criticality=AllergyCriticality.HIGH,
            reaction="Skin rash",
            notes="Severe reaction - avoid all formulations"
        )
        
        # Verify properties
        assert allergy.code.text == "Paracetamol"
        assert allergy.category[0] == "medication"
        assert allergy.clinicalStatus.coding[0].code == "active"
        assert allergy.criticality == "high"
        
        # Verify reaction
        assert len(allergy.reaction) == 1
        reaction = allergy.reaction[0]
        assert len(reaction.manifestation) == 1
        assert reaction.manifestation[0].text == "Skin rash"
        
        # Verify notes
        assert len(allergy.note) == 1
        assert allergy.note[0].text == "Severe reaction - avoid all formulations"
    
    def test_allergy_categories(self, encounter_builder):
        """Test different allergy categories."""
        category_tests = [
            (AllergyCategory.FOOD, "food"),
            (AllergyCategory.MEDICATION, "medication"),
            (AllergyCategory.ENVIRONMENT, "environment"),
            (AllergyCategory.BIOLOGIC, "biologic")
        ]
        
        for category_enum, expected_value in category_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            allergy = builder.add_allergy_history(
                code="Test Allergen",
                category=category_enum
            )
            
            assert allergy.category[0] == expected_value
    
    def test_allergy_clinical_status_values(self, encounter_builder):
        """Test different clinical status values."""
        status_tests = [
            (AllergyClinicalStatus.ACTIVE, "active"),
            (AllergyClinicalStatus.INACTIVE, "inactive"),
            (AllergyClinicalStatus.RESOLVED, "resolved"),
            ("active", "active"),  # String input
            ("resolved", "resolved")
        ]
        
        for status_input, expected_code in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            allergy = builder.add_allergy_history(
                code="Test Allergen",
                clinical_status=status_input
            )
            
            assert allergy.clinicalStatus.coding[0].code == expected_code
    
    def test_allergy_criticality_values(self, encounter_builder):
        """Test different criticality values."""
        criticality_tests = [
            (AllergyCriticality.LOW, "low"),
            (AllergyCriticality.HIGH, "high"),
            ("low", "low"),  # String input
            ("high", "high")
        ]
        
        for criticality_input, expected_value in criticality_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            allergy = builder.add_allergy_history(
                code="Test Allergen",
                criticality=criticality_input
            )
            
            assert allergy.criticality == expected_value


class TestImmunizationHistory:
    """Test immunization/vaccination history functionality."""
    
    def test_basic_immunization_history(self, encounter_builder):
        """Test creating basic immunization."""
        immunization = encounter_builder.add_immunisation_history(
            vaccine="COVID vaccine"
        )
        
        # Verify immunization was created
        assert immunization is not None
        assert immunization.get_resource_type() == "Immunization"
        assert immunization.id is not None
        
        # Verify default status
        assert immunization.status == "completed"
        
        # Verify vaccine code
        assert immunization.vaccineCode.text == "COVID vaccine"
        
        # Verify patient reference
        assert immunization.patient is not None
        assert "Patient/" in immunization.patient.reference
    
    def test_immunization_with_all_properties(self, encounter_builder, test_dates):
        """Test comprehensive immunization."""
        immunization = encounter_builder.add_immunisation_history(
            vaccine="COVID-19 mRNA vaccine",
            occurrence_date=test_dates['month_ago'],
            status=ImmunizationStatus.COMPLETED,
            dose_number=2,
            series_doses=2,
            notes="Done during the second wave of COVID"
        )
        
        # Verify properties
        assert immunization.vaccineCode.text == "COVID-19 mRNA vaccine"
        assert immunization.status == "completed"
        
        # Verify occurrence date
        assert immunization.occurrenceDateTime.replace(tzinfo=None, microsecond=0) == test_dates['month_ago'].replace(microsecond=0)
        
        # Verify protocol applied (dose information)
        assert len(immunization.protocolApplied) == 1
        protocol = immunization.protocolApplied[0]
        assert protocol.doseNumberPositiveInt == 2
        assert protocol.seriesDosesPositiveInt == 2
        
        # Verify notes
        assert len(immunization.note) == 1
        assert immunization.note[0].text == "Done during the second wave of COVID"
    
    def test_immunization_status_values(self, encounter_builder):
        """Test different immunization status values."""
        status_tests = [
            (ImmunizationStatus.COMPLETED, "completed"),
            (ImmunizationStatus.ENTERED_IN_ERROR, "entered-in-error"),
            (ImmunizationStatus.NOT_DONE, "not-done"),
            ("completed", "completed"),  # String input
        ]
        
        for status_input, expected_status in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            immunization = builder.add_immunisation_history(
                vaccine="Test Vaccine",
                status=status_input
            )
            
            assert immunization.status == expected_status
    
    def test_immunization_series_tracking(self, encounter_builder):
        """Test immunization series tracking."""
        # First dose
        imm1 = encounter_builder.add_immunisation_history(
            vaccine="Hepatitis B",
            dose_number=1,
            series_doses=3
        )
        
        # Second dose
        builder2 = FHIRDocumentBuilder()
        builder2.add_patient(name="Test", age=(30, "years"))
        
        imm2 = builder2.add_immunisation_history(
            vaccine="Hepatitis B",
            dose_number=2,
            series_doses=3
        )
        
        # Verify dose tracking
        protocol1 = imm1.protocolApplied[0]
        assert protocol1.doseNumberPositiveInt == 1
        assert protocol1.seriesDosesPositiveInt == 3
        
        protocol2 = imm2.protocolApplied[0]
        assert protocol2.doseNumberPositiveInt == 2
        assert protocol2.seriesDosesPositiveInt == 3


class TestProcedureHistory:
    """Test procedure history functionality."""
    
    def test_basic_procedure_history(self, encounter_builder):
        """Test creating basic procedure history."""
        procedure = encounter_builder.add_procedure_history(
            code="Vasectomy"
        )
        
        # Verify procedure was created
        assert procedure is not None
        assert procedure.get_resource_type() == "Procedure"
        assert procedure.id is not None
        
        # Verify default status
        assert procedure.status == "completed"
        
        # Verify code
        assert procedure.code.text == "Vasectomy"
        
        # Verify patient reference
        assert procedure.subject is not None
        assert "Patient/" in procedure.subject.reference
    
    def test_procedure_history_with_all_properties(self, encounter_builder, test_dates):
        """Test comprehensive procedure history."""
        procedure = encounter_builder.add_procedure_history(
            code="Appendectomy",
            date=test_dates['year_ago'],
            notes="Laparoscopic approach",
            status=ProcedureStatus.COMPLETED,
            outcome="Successful removal"
        )
        
        # Verify properties
        assert procedure.code.text == "Appendectomy"
        assert procedure.status == "completed"
        
        # Verify performed date
        assert procedure.performedDateTime.replace(tzinfo=None, microsecond=0) == test_dates['year_ago'].replace(microsecond=0)
        
        # Verify notes
        assert len(procedure.note) == 1
        assert procedure.note[0].text == "Laparoscopic approach"
        
        # Verify outcome
        assert len(procedure.outcome.coding) >= 1 or procedure.outcome.text == "Successful removal"
    
    def test_procedure_status_values(self, encounter_builder):
        """Test different procedure status values."""
        status_tests = [
            (ProcedureStatus.PREPARATION, "preparation"),
            (ProcedureStatus.IN_PROGRESS, "in-progress"),
            (ProcedureStatus.COMPLETED, "completed"),
            (ProcedureStatus.STOPPED, "stopped"),
            ("completed", "completed"),  # String input
        ]
        
        for status_input, expected_status in status_tests:
            builder = FHIRDocumentBuilder()
            builder.add_patient(name="Test", age=(30, "years"))
            
            procedure = builder.add_procedure_history(
                code="Test Procedure",
                status=status_input
            )
            
            assert procedure.status == expected_status


class TestMedicalHistoryBundleIntegration:
    """Test medical history integration in FHIR bundles."""
    
    def test_all_history_types_in_bundle(self, encounter_builder):
        """Test all history types appear correctly in bundle."""
        # Add all types of history
        encounter_builder.add_family_history(
            condition="Diabetes",
            relation="Father"
        )
        
        encounter_builder.add_allergy_history(
            code="Penicillin",
            category=AllergyCategory.MEDICATION
        )
        
        encounter_builder.add_immunisation_history(
            vaccine="Flu vaccine"
        )
        
        encounter_builder.add_procedure_history(
            code="Tonsillectomy"
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Verify all resource types
        resource_types = [entry["resource"]["resourceType"] for entry in bundle_dict["entry"]]
        assert "FamilyMemberHistory" in resource_types
        assert "AllergyIntolerance" in resource_types
        assert "Immunization" in resource_types
        assert "Procedure" in resource_types
    
    def test_multiple_history_entries_same_type(self, encounter_builder):
        """Test multiple entries of same history type."""
        # Multiple allergies
        allergy1 = encounter_builder.add_allergy_history(
            code="Peanuts",
            category=AllergyCategory.FOOD
        )
        
        allergy2 = encounter_builder.add_allergy_history(
            code="Shellfish", 
            category=AllergyCategory.FOOD
        )
        
        # Multiple immunizations
        imm1 = encounter_builder.add_immunisation_history(
            vaccine="MMR"
        )
        
        imm2 = encounter_builder.add_immunisation_history(
            vaccine="Polio"
        )
        
        # Verify all have different IDs
        assert len({allergy1.id, allergy2.id, imm1.id, imm2.id}) == 4
        
        # Verify all appear in bundle
        bundle_dict = encounter_builder.convert_to_fhir()
        
        allergy_entries = [entry for entry in bundle_dict["entry"]
                          if entry["resource"]["resourceType"] == "AllergyIntolerance"]
        imm_entries = [entry for entry in bundle_dict["entry"]
                      if entry["resource"]["resourceType"] == "Immunization"]
        
        assert len(allergy_entries) == 2
        assert len(imm_entries) == 2
    
    def test_coded_history_entries(self, encounter_builder):
        """Test history entries with coded values."""
        # Coded allergy
        encounter_builder.add_allergy_history(
            code=("387207008", "http://snomed.info/sct", "Penicillin"),
            category=AllergyCategory.MEDICATION
        )
        
        # Coded vaccine
        encounter_builder.add_immunisation_history(
            vaccine=("207", "http://hl7.org/fhir/sid/cvx", "COVID-19 mRNA vaccine")
        )
        
        bundle_dict = encounter_builder.convert_to_fhir()
        
        # Verify allergy coding
        allergy_entry = next((entry for entry in bundle_dict["entry"]
                             if entry["resource"]["resourceType"] == "AllergyIntolerance"), None)
        assert allergy_entry is not None
        allergy = allergy_entry["resource"]
        assert allergy["code"]["coding"][0]["code"] == "387207008"
        assert allergy["code"]["coding"][0]["system"] == "http://snomed.info/sct"
        
        # Verify vaccine coding
        imm_entry = next((entry for entry in bundle_dict["entry"]
                         if entry["resource"]["resourceType"] == "Immunization"), None)
        assert imm_entry is not None
        immunization = imm_entry["resource"]
        assert immunization["vaccineCode"]["coding"][0]["code"] == "207"
        assert immunization["vaccineCode"]["coding"][0]["system"] == "http://hl7.org/fhir/sid/cvx"
