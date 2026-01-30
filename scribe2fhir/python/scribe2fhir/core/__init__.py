"""
scribe2fhir.core - A Python SDK for creating FHIR documents from clinical data.

This SDK provides a simple, Pythonic interface for building FHIR-compliant
documents. It abstracts away the complexity of FHIR resource structures
while still allowing access to the full power of FHIR when needed.

Quick Start:
    from scribe2fhir.core import FHIRDocumentBuilder, DosageBuilder, Severity
    
    # Create a document builder
    builder = FHIRDocumentBuilder()
    
    # Add patient
    builder.add_patient(name="John Doe", age=(30, "years"), gender="male")
    
    # Add clinical data
    builder.add_symptom(code="Headache", severity=Severity.MODERATE)
    builder.add_medical_condition_history(code="Hypertension")
    builder.add_vital_finding(code="Blood Pressure", value="120/80", unit="mmHg")
    builder.add_lab_finding(code="Hemoglobin", value=12.5, unit="g/dL")
    builder.add_medication_prescribed(
        medication="Paracetamol 500mg",
        dosage=DosageBuilder.build(dose_value=1, dose_unit="tablet", frequency=3, period=1, period_unit="d")
    )
    builder.add_test_prescribed(code="CBC test", notes="Fasting required")
    builder.add_family_history(condition="Diabetes", relation="Mother")
    builder.add_allergy_history(code="Penicillin", category="medication")
    builder.add_immunisation_history(vaccine="COVID-19 vaccine")
    builder.add_followup(date="2024-05-21", ref_doctor="Dr. Smith")
    builder.add_advice(note="Drink plenty of water")
    
    # Generate FHIR Bundle
    fhir_json = builder.convert_to_fhir()
"""

# Main builder class
from .document_builder import FHIRDocumentBuilder

# Resource builders (for advanced usage)
from .resources.symptom import SymptomBuilder
from .resources.condition import ConditionBuilder
from .resources.medication import MedicationBuilder, DosageBuilder
from .resources.patient import PatientBuilder, IdentifierType, Gender
from .resources.encounter import EncounterBuilder, EncounterClass, EncounterStatus
from .resources.observation import ObservationBuilder, ObservationCategory, VitalSignCodes
from .resources.service_request import (
    ServiceRequestBuilder,
    ServiceRequestCategory,
    ServiceRequestStatus,
    ServiceRequestPriority,
)
from .resources.procedure import ProcedureBuilder, ProcedureStatus
from .resources.family_history import (
    FamilyMemberHistoryBuilder,
    FamilyRelationship,
    FamilyMemberHistoryStatus,
)
from .resources.allergy import (
    AllergyBuilder,
    AllergyCategory,
    AllergyType,
    AllergyClinicalStatus,
    AllergyCriticality,
    ReactionSeverity,
)
from .resources.immunization import ImmunizationBuilder, ImmunizationStatus
from .resources.appointment import AppointmentBuilder, AppointmentStatus, ParticipantStatus
from .resources.care_plan import AdviceBuilder, ClinicalNoteBuilder, CarePlanStatus, CommunicationStatus

# Enums for validated values
from .enums import (
    # Observation-related
    ObservationStatus,
    FindingStatus,
    Interpretation,
    
    # Condition-related
    ConditionClinicalStatus,
    ConditionVerificationStatus,
    ConditionCategory,
    
    # Common clinical
    Severity,
    Laterality,
    
    # Medication-related
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationStatementStatus,
    RouteOfAdministration,
    EventTiming,
)

# Type helpers
from .types import (
    CodeInput,
    DateTimeInput,
    QuantityInput,
    CodingSystem,
    create_codeable_concept,
    create_coding,
    create_quantity,
    create_period,
    create_annotation,
    create_reference,
    parse_code_input,
    parse_quantity_input,
)

__version__ = "0.1.0"

__all__ = [
    # Main builder
    "FHIRDocumentBuilder",
    
    # Resource builders
    "SymptomBuilder",
    "ConditionBuilder",
    "MedicationBuilder",
    "DosageBuilder",
    "PatientBuilder",
    "IdentifierType",
    "Gender",
    "EncounterBuilder",
    "EncounterClass",
    "EncounterStatus",
    "ObservationBuilder",
    "ObservationCategory",
    "VitalSignCodes",
    "ServiceRequestBuilder",
    "ServiceRequestCategory",
    "ServiceRequestStatus",
    "ServiceRequestPriority",
    "ProcedureBuilder",
    "ProcedureStatus",
    "FamilyMemberHistoryBuilder",
    "FamilyRelationship",
    "FamilyMemberHistoryStatus",
    "AllergyBuilder",
    "AllergyCategory",
    "AllergyType",
    "AllergyClinicalStatus",
    "AllergyCriticality",
    "ReactionSeverity",
    "ImmunizationBuilder",
    "ImmunizationStatus",
    "AppointmentBuilder",
    "AppointmentStatus",
    "ParticipantStatus",
    "AdviceBuilder",
    "ClinicalNoteBuilder",
    "CarePlanStatus",
    "CommunicationStatus",
    
    # Enums
    "ObservationStatus",
    "FindingStatus",
    "Interpretation",
    "ConditionClinicalStatus",
    "ConditionVerificationStatus",
    "ConditionCategory",
    "Severity",
    "Laterality",
    "MedicationRequestStatus",
    "MedicationRequestIntent",
    "MedicationStatementStatus",
    "RouteOfAdministration",
    "EventTiming",
    
    # Type helpers
    "CodeInput",
    "DateTimeInput",
    "QuantityInput",
    "CodingSystem",
    "create_codeable_concept",
    "create_coding",
    "create_quantity",
    "create_period",
    "create_annotation",
    "create_reference",
    "parse_code_input",
    "parse_quantity_input",
]
