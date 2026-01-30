"""
scribe2fhir.core.document_builder - Main SDK class for building FHIR documents.

This is the primary entry point for the SDK. Users create a FHIRDocumentBuilder
instance and call methods like add_symptom(), add_medication_prescribed(), etc.
to build up a clinical document. Finally, convert_to_fhir() generates the
complete FHIR Bundle.

Example:
    builder = FHIRDocumentBuilder()
    
    # Add patient info (creates context for all resources)
    builder.add_patient(name="John Doe", age=(30, "years"), gender="male")
    
    # Add clinical findings
    builder.add_symptom(
        code=("25064002", "http://snomed.info/sct", "Headache"),
        severity=Severity.MODERATE,
        notes="Throbbing pain, worse in mornings"
    )
    
    builder.add_medical_condition_history(
        code="Hypertension",
        onset="2020-01-01",
        clinical_status=ConditionClinicalStatus.ACTIVE
    )
    
    builder.add_medication_prescribed(
        medication="Paracetamol 500mg",
        dosage=DosageBuilder.build(dose_value=1, dose_unit="tablet", frequency=3, period=1, period_unit="d")
    )
    
    # Generate FHIR Bundle
    fhir_json = builder.convert_to_fhir()
"""

import uuid
from typing import Optional, List, Union, Dict, Any, Tuple
from datetime import datetime

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.patient import Patient
from fhir.resources.encounter import Encounter
from fhir.resources.observation import Observation
from fhir.resources.condition import Condition
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.procedure import Procedure as FHIRProcedure
from fhir.resources.familymemberhistory import FamilyMemberHistory
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.immunization import Immunization
from fhir.resources.appointment import Appointment
from fhir.resources.careplan import CarePlan
from fhir.resources.communication import Communication
from fhir.resources.dosage import Dosage
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from fhir.resources.humanname import HumanName

from .enums import (
    ObservationStatus,
    ConditionClinicalStatus,
    ConditionVerificationStatus,
    Severity,
    Laterality,
    FindingStatus,
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationStatementStatus,
    Interpretation,
)
from .types import CodeInput, DateTimeInput, create_reference
from .resources.symptom import SymptomBuilder
from .resources.condition import ConditionBuilder
from .resources.medication import MedicationBuilder, DosageBuilder
from .resources.patient import PatientBuilder
from .resources.encounter import EncounterBuilder, EncounterStatus
from .resources.observation import ObservationBuilder
from .resources.service_request import ServiceRequestBuilder, ServiceRequestPriority
from .resources.procedure import ProcedureBuilder, ProcedureStatus
from .resources.family_history import FamilyMemberHistoryBuilder
from .resources.allergy import AllergyBuilder, AllergyCategory, AllergyClinicalStatus
from .resources.immunization import ImmunizationBuilder, ImmunizationStatus
from .resources.appointment import AppointmentBuilder, AppointmentStatus
from .resources.care_plan import AdviceBuilder, ClinicalNoteBuilder


class FHIRDocumentBuilder:
    """
    Main builder class for creating FHIR clinical documents.
    
    This class accumulates clinical information through its add_* methods
    and generates a complete FHIR Bundle when convert_to_fhir() is called.
    
    The generated Bundle contains all added FHIR resources including:
    - Patient and Encounter
    - Observations (symptoms, vitals, labs, examinations)
    - Conditions (medical history, diagnoses)
    - Medications (prescriptions, history)
    - ServiceRequests (lab tests, procedures ordered)
    - Procedures (procedure history)
    - FamilyMemberHistory
    - AllergyIntolerance
    - Immunizations
    - Appointments (follow-ups)
    - CarePlan (advice)
    - Communications (notes)
    """
    
    def __init__(self, bundle_id: Optional[str] = None):
        """
        Initialize a new FHIR Document Builder.
        
        Args:
            bundle_id: Optional ID for the bundle (auto-generated if not provided)
        """
        self.bundle_id = bundle_id or str(uuid.uuid4())
        
        # Core resources
        self.patient: Optional[Patient] = None
        self.encounter: Optional[Encounter] = None
        
        # Clinical resources
        self.observations: List[Observation] = []
        self.conditions: List[Condition] = []
        self.medication_requests: List[MedicationRequest] = []
        self.medication_statements: List[MedicationStatement] = []
        self.service_requests: List[ServiceRequest] = []
        self.procedures: List[FHIRProcedure] = []
        self.family_member_histories: List[FamilyMemberHistory] = []
        self.allergies: List[AllergyIntolerance] = []
        self.immunizations: List[Immunization] = []
        self.appointments: List[Appointment] = []
        self.care_plans: List[CarePlan] = []
        self.communications: List[Communication] = []
    
    def _get_patient_reference(self) -> Optional[Reference]:
        """Get a reference to the patient if one is set."""
        if self.patient and self.patient.id:
            return create_reference(
                resource_type="Patient",
                resource_id=self.patient.id,
                display=self._get_patient_display()
            )
        return None
    
    def _get_patient_display(self) -> Optional[str]:
        """Get display name for patient reference."""
        if self.patient and self.patient.name:
            name = self.patient.name[0]
            if name.text:
                return name.text
            parts = []
            if name.given:
                parts.extend(name.given)
            if name.family:
                parts.append(name.family)
            return " ".join(parts) if parts else None
        return None
    
    def _get_encounter_reference(self) -> Optional[Reference]:
        """Get a reference to the encounter if one is set."""
        if self.encounter and self.encounter.id:
            return create_reference(
                resource_type="Encounter",
                resource_id=self.encounter.id
            )
        return None
    
    # =========================================================================
    # PATIENT & ENCOUNTER
    # =========================================================================
    
    def add_patient(
        self,
        name: Union[str, dict, HumanName],
        age: Optional[Union[int, Tuple[int, str]]] = None,
        birth_date: Optional[DateTimeInput] = None,
        gender: Optional[str] = None,
        identifiers: Optional[List[Tuple[str, Union[str, Tuple[str, str]]]]] = None,
        address: Optional[Union[str, dict]] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Patient:
        """
        Add patient information.
        
        Args:
            name: Patient name (string, dict, or HumanName)
            age: Age as int (years) or tuple (value, unit)
            birth_date: Date of birth (alternative to age)
            gender: Gender (male, female, other, unknown)
            identifiers: List of (value, type) tuples, e.g., [("123", "MRN"), ("ABHA-456", "ABHA")]
            address: Address string or dict
            phone: Phone number
            email: Email address
            id: Resource ID
            
        Returns:
            The Patient resource
        """
        self.patient = PatientBuilder.build(
            name=name,
            age=age,
            birth_date=birth_date,
            gender=gender,
            identifiers=identifiers,
            address=address,
            phone=phone,
            email=email,
            id=id,
        )
        return self.patient
    
    def add_encounter(
        self,
        encounter_class: str = "ambulatory",
        encounter_type: Optional[str] = None,
        encounter_subtype: Optional[str] = None,
        period_start: Optional[DateTimeInput] = None,
        period_end: Optional[DateTimeInput] = None,
        facility_name: Optional[str] = None,
        department: Optional[str] = None,
        status: str = EncounterStatus.FINISHED,
        id: Optional[str] = None,
    ) -> Encounter:
        """
        Add encounter information.
        
        Args:
            encounter_class: Type (ambulatory, emergency, inpatient, virtual)
            encounter_type: More specific type
            encounter_subtype: Sub-classification
            period_start: When encounter started
            period_end: When encounter ended
            facility_name: Healthcare facility name
            department: Department name
            status: Encounter status
            id: Resource ID
            
        Returns:
            The Encounter resource
        """
        self.encounter = EncounterBuilder.build(
            encounter_class=encounter_class,
            encounter_type=encounter_type,
            encounter_subtype=encounter_subtype,
            period_start=period_start,
            period_end=period_end,
            facility_name=facility_name,
            department=department,
            status=status,
            subject_reference=self._get_patient_reference(),
            id=id,
        )
        return self.encounter
    
    # =========================================================================
    # SYMPTOM METHODS
    # =========================================================================
    
    def add_symptom(
        self,
        code: CodeInput,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        severity: Optional[Union[Severity, str]] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        notes: Optional[str] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        finding_status: Optional[Union[FindingStatus, str]] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Add a symptom to the document.
        
        Symptoms are represented as Observation resources with category 'survey'.
        """
        observation = SymptomBuilder.build(
            code=code,
            onset=onset,
            offset=offset,
            severity=severity,
            status=status,
            notes=notes,
            laterality=laterality,
            finding_status=finding_status,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.observations.append(observation)
        return observation
    
    # =========================================================================
    # CONDITION METHODS
    # =========================================================================
    
    def add_medical_condition_history(
        self,
        code: CodeInput,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        clinical_status: Union[ConditionClinicalStatus, str] = ConditionClinicalStatus.ACTIVE,
        verification_status: Optional[Union[ConditionVerificationStatus, str]] = None,
        severity: Optional[Union[Severity, str]] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Condition:
        """Add a medical condition from patient's history (problem-list-item)."""
        condition = ConditionBuilder.build_history(
            code=code,
            onset=onset,
            offset=offset,
            clinical_status=clinical_status,
            verification_status=verification_status,
            severity=severity,
            laterality=laterality,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.conditions.append(condition)
        return condition
    
    def add_medical_condition_encountered(
        self,
        code: CodeInput,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        clinical_status: Union[ConditionClinicalStatus, str] = ConditionClinicalStatus.ACTIVE,
        verification_status: Optional[Union[ConditionVerificationStatus, str]] = ConditionVerificationStatus.CONFIRMED,
        severity: Optional[Union[Severity, str]] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Condition:
        """Add a diagnosis made during the current encounter (encounter-diagnosis)."""
        condition = ConditionBuilder.build_encountered(
            code=code,
            onset=onset,
            offset=offset,
            clinical_status=clinical_status,
            verification_status=verification_status,
            severity=severity,
            laterality=laterality,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.conditions.append(condition)
        return condition
    
    # =========================================================================
    # OBSERVATION METHODS (Vitals, Labs, Exams)
    # =========================================================================
    
    def add_vital_finding(
        self,
        code: CodeInput,
        value: Optional[Union[str, float]] = None,
        unit: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        interpretation: Optional[Union[Interpretation, str]] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Add a vital sign finding.
        
        Args:
            code: The vital sign (e.g., "Blood Pressure", "Heart Rate")
            value: The measured value
            unit: Unit of measurement (e.g., "mmHg", "bpm")
            date: When measured
            interpretation: Interpretation (normal, high, low)
            notes: Additional notes
            id: Resource ID
        """
        observation = ObservationBuilder.build_vital(
            code=code,
            value=value,
            unit=unit,
            date=date,
            interpretation=interpretation,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.observations.append(observation)
        return observation
    
    def add_lab_finding(
        self,
        code: CodeInput,
        value: Optional[Union[str, float]] = None,
        unit: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        interpretation: Optional[Union[Interpretation, str]] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Add a laboratory finding.
        
        Args:
            code: The lab test name
            value: The result value
            unit: Unit of measurement
            date: When the test was done
            interpretation: Result interpretation
            notes: Additional notes
            id: Resource ID
        """
        observation = ObservationBuilder.build_lab(
            code=code,
            value=value,
            unit=unit,
            date=date,
            interpretation=interpretation,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.observations.append(observation)
        return observation
    
    def add_examination_finding(
        self,
        code: CodeInput,
        value: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Add a physical examination finding.
        
        Args:
            code: The examination type (e.g., "Abdominal examination")
            value: Finding description
            date: When the exam was done
            status: Observation status
            notes: Additional notes
            id: Resource ID
        """
        observation = ObservationBuilder.build_exam(
            code=code,
            value=value,
            date=date,
            status=status,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.observations.append(observation)
        return observation
    
    def add_lifestyle_history(
        self,
        code: CodeInput,
        status_value: Optional[str] = None,
        notes: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Add a lifestyle/social history observation.
        
        Use for smoking, drinking, diet, exercise, travel history, etc.
        
        Args:
            code: The lifestyle factor (e.g., "Smoking", "Alcohol use")
            status_value: Active/Inactive status
            notes: Details about the habit
            date: When recorded
            id: Resource ID
        """
        observation = ObservationBuilder.build_social_history(
            code=code,
            status_value=status_value,
            notes=notes,
            date=date,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.observations.append(observation)
        return observation
    
    # =========================================================================
    # MEDICATION METHODS
    # =========================================================================
    
    def add_medication_prescribed(
        self,
        medication: CodeInput,
        dosage: Optional[Union[Dosage, List[Dosage]]] = None,
        status: Union[MedicationRequestStatus, str] = MedicationRequestStatus.ACTIVE,
        intent: Union[MedicationRequestIntent, str] = MedicationRequestIntent.ORDER,
        duration_value: Optional[float] = None,
        duration_unit: Optional[str] = None,
        quantity_value: Optional[float] = None,
        quantity_unit: Optional[str] = None,
        refills: Optional[int] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        authored_on: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> MedicationRequest:
        """Add a prescribed medication."""
        medication_request = MedicationBuilder.build_prescribed(
            medication=medication,
            dosage=dosage,
            status=status,
            intent=intent,
            duration_value=duration_value,
            duration_unit=duration_unit,
            quantity_value=quantity_value,
            quantity_unit=quantity_unit,
            refills=refills,
            notes=notes,
            reason=reason,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            authored_on=authored_on,
            id=id,
        )
        
        self.medication_requests.append(medication_request)
        return medication_request
    
    def add_medication_history(
        self,
        medication: CodeInput,
        dosage: Optional[Union[Dosage, List[Dosage]]] = None,
        status: Union[MedicationStatementStatus, str] = MedicationStatementStatus.ACTIVE,
        effective_start: Optional[DateTimeInput] = None,
        effective_end: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        date_asserted: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> MedicationStatement:
        """Add a medication from patient's history."""
        medication_statement = MedicationBuilder.build_history(
            medication=medication,
            dosage=dosage,
            status=status,
            effective_start=effective_start,
            effective_end=effective_end,
            notes=notes,
            reason=reason,
            subject_reference=self._get_patient_reference(),
            date_asserted=date_asserted,
            id=id,
        )
        
        self.medication_statements.append(medication_statement)
        return medication_statement
    
    # =========================================================================
    # SERVICE REQUEST METHODS (Tests & Procedures Ordered)
    # =========================================================================
    
    def add_test_prescribed(
        self,
        code: CodeInput,
        date: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        priority: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        id: Optional[str] = None,
    ) -> ServiceRequest:
        """
        Add a lab test order.
        
        Args:
            code: The test name
            date: When the test should be done
            notes: Additional instructions
            priority: Priority (routine, urgent, asap, stat)
            reason: Reason for the test
            id: Resource ID
        """
        service_request = ServiceRequestBuilder.build_lab_test(
            code=code,
            occurrence_date=date,
            notes=notes,
            priority=priority,
            reason=reason,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.service_requests.append(service_request)
        return service_request
    
    def add_procedure_prescribed(
        self,
        code: CodeInput,
        date: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        priority: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        id: Optional[str] = None,
    ) -> ServiceRequest:
        """
        Add a procedure order.
        
        Args:
            code: The procedure name
            date: When the procedure should be done
            notes: Additional instructions
            priority: Priority
            reason: Reason for the procedure
            id: Resource ID
        """
        service_request = ServiceRequestBuilder.build_procedure(
            code=code,
            occurrence_date=date,
            notes=notes,
            priority=priority,
            reason=reason,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.service_requests.append(service_request)
        return service_request
    
    # =========================================================================
    # PROCEDURE HISTORY
    # =========================================================================
    
    def add_procedure_history(
        self,
        code: CodeInput,
        date: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        status: str = ProcedureStatus.COMPLETED,
        outcome: Optional[CodeInput] = None,
        id: Optional[str] = None,
    ) -> FHIRProcedure:
        """
        Add a past procedure to history.
        
        Args:
            code: The procedure name
            date: When it was performed
            notes: Additional notes
            status: Procedure status (default: completed)
            outcome: Outcome of the procedure
            id: Resource ID
        """
        procedure = ProcedureBuilder.build(
            code=code,
            performed_date=date,
            notes=notes,
            status=status,
            outcome=outcome,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.procedures.append(procedure)
        return procedure
    
    # =========================================================================
    # FAMILY HISTORY
    # =========================================================================
    
    def add_family_history(
        self,
        condition: CodeInput,
        relation: Union[str, tuple],
        onset: Optional[Union[str, int]] = None,
        status: str = "completed",
        notes: Optional[str] = None,
        deceased: Optional[bool] = None,
        id: Optional[str] = None,
    ) -> FamilyMemberHistory:
        """
        Add family medical history.
        
        Args:
            condition: The health condition
            relation: Family relationship (father, mother, brother, etc.)
            onset: When the condition started (year or age)
            status: History status
            notes: Additional notes
            deceased: Whether family member is deceased
            id: Resource ID
        """
        family_history = FamilyMemberHistoryBuilder.build(
            condition=condition,
            relationship=relation,
            onset=onset,
            status=status,
            notes=notes,
            deceased=deceased,
            subject_reference=self._get_patient_reference(),
            id=id,
        )
        
        self.family_member_histories.append(family_history)
        return family_history
    
    # =========================================================================
    # ALLERGY HISTORY
    # =========================================================================
    
    def add_allergy_history(
        self,
        code: CodeInput,
        category: Optional[str] = None,
        clinical_status: str = AllergyClinicalStatus.ACTIVE,
        criticality: Optional[str] = None,
        reaction: Optional[str] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> AllergyIntolerance:
        """
        Add an allergy or intolerance.
        
        Args:
            code: The allergen (drug, food, substance)
            category: Category (food, medication, environment, biologic)
            clinical_status: Status (active, inactive, resolved)
            criticality: Criticality (low, high)
            reaction: What happens during reaction
            notes: Additional notes
            id: Resource ID
        """
        allergy = AllergyBuilder.build(
            code=code,
            category=category,
            clinical_status=clinical_status,
            criticality=criticality,
            reaction_manifestation=reaction,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.allergies.append(allergy)
        return allergy
    
    # =========================================================================
    # IMMUNIZATION HISTORY
    # =========================================================================
    
    def add_immunisation_history(
        self,
        vaccine: CodeInput,
        occurrence_date: Optional[DateTimeInput] = None,
        status: str = ImmunizationStatus.COMPLETED,
        dose_number: Optional[int] = None,
        series_doses: Optional[int] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Immunization:
        """
        Add vaccination/immunization history.
        
        Args:
            vaccine: The vaccine name
            occurrence_date: When it was given
            status: Immunization status
            dose_number: Which dose in a series
            series_doses: Total doses in series
            notes: Additional notes
            id: Resource ID
        """
        immunization = ImmunizationBuilder.build(
            vaccine=vaccine,
            occurrence_date=occurrence_date,
            status=status,
            dose_number=dose_number,
            series_doses=series_doses,
            notes=notes,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.immunizations.append(immunization)
        return immunization
    
    # =========================================================================
    # FOLLOW-UP
    # =========================================================================
    
    def add_followup(
        self,
        date: DateTimeInput,
        ref_doctor: Optional[str] = None,
        ref_specialty: Optional[str] = None,
        notes: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Appointment:
        """
        Add a follow-up appointment.
        
        Args:
            date: Follow-up date
            ref_doctor: Doctor name for referral
            ref_specialty: Specialty for referral
            notes: Additional instructions
            id: Resource ID
        """
        appointment = AppointmentBuilder.build_followup(
            date=date,
            practitioner_name=ref_doctor,
            specialty=ref_specialty,
            notes=notes,
            patient_reference=self._get_patient_reference(),
            id=id,
        )
        
        self.appointments.append(appointment)
        return appointment
    
    # =========================================================================
    # ADVICE & NOTES
    # =========================================================================
    
    def add_advice(
        self,
        note: str,
        category: Optional[str] = None,
        id: Optional[str] = None,
    ) -> CarePlan:
        """
        Add patient advice/instruction.
        
        Args:
            note: The advice text
            category: Category of advice
            id: Resource ID
        """
        advice = AdviceBuilder.build(
            advice_text=note,
            category=category,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.care_plans.append(advice)
        return advice
    
    def add_notes(
        self,
        note: str,
        category: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Communication:
        """
        Add clinical notes.
        
        Args:
            note: The note text
            category: Note category
            id: Resource ID
        """
        communication = ClinicalNoteBuilder.build(
            note_text=note,
            category=category,
            subject_reference=self._get_patient_reference(),
            encounter_reference=self._get_encounter_reference(),
            id=id,
        )
        
        self.communications.append(communication)
        return communication
    
    # =========================================================================
    # BUNDLE GENERATION
    # =========================================================================
    
    def _create_bundle_entry(self, resource: Resource) -> BundleEntry:
        """Create a bundle entry for a resource."""
        return BundleEntry(
            fullUrl=f"urn:uuid:{resource.id}",
            resource=resource
        )
    
    def convert_to_fhir(self, bundle_type: str = "collection") -> Dict[str, Any]:
        """
        Convert all added resources to a FHIR Bundle.
        
        Args:
            bundle_type: Type of bundle (collection, document, transaction, etc.)
            
        Returns:
            Dictionary representation of the FHIR Bundle
        """
        entries = []
        
        # Core resources
        if self.patient:
            entries.append(self._create_bundle_entry(self.patient))
        
        if self.encounter:
            entries.append(self._create_bundle_entry(self.encounter))
        
        # Observations
        for observation in self.observations:
            entries.append(self._create_bundle_entry(observation))
        
        # Conditions
        for condition in self.conditions:
            entries.append(self._create_bundle_entry(condition))
        
        # Medications
        for medication_request in self.medication_requests:
            entries.append(self._create_bundle_entry(medication_request))
        
        for medication_statement in self.medication_statements:
            entries.append(self._create_bundle_entry(medication_statement))
        
        # Service Requests
        for service_request in self.service_requests:
            entries.append(self._create_bundle_entry(service_request))
        
        # Procedures
        for procedure in self.procedures:
            entries.append(self._create_bundle_entry(procedure))
        
        # Family History
        for family_history in self.family_member_histories:
            entries.append(self._create_bundle_entry(family_history))
        
        # Allergies
        for allergy in self.allergies:
            entries.append(self._create_bundle_entry(allergy))
        
        # Immunizations
        for immunization in self.immunizations:
            entries.append(self._create_bundle_entry(immunization))
        
        # Appointments
        for appointment in self.appointments:
            entries.append(self._create_bundle_entry(appointment))
        
        # Care Plans (Advice)
        for care_plan in self.care_plans:
            entries.append(self._create_bundle_entry(care_plan))
        
        # Communications (Notes)
        for communication in self.communications:
            entries.append(self._create_bundle_entry(communication))
        
        # Create the bundle
        bundle = Bundle(
            id=self.bundle_id,
            type=bundle_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            entry=entries if entries else None
        )
        
        return bundle.model_dump(mode='json', exclude_none=True)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.convert_to_fhir(), indent=indent)
    
    def get_bundle(self) -> Bundle:
        """Get the Bundle object directly."""
        entries = []
        
        if self.patient:
            entries.append(self._create_bundle_entry(self.patient))
        
        if self.encounter:
            entries.append(self._create_bundle_entry(self.encounter))
        
        for observation in self.observations:
            entries.append(self._create_bundle_entry(observation))
        
        for condition in self.conditions:
            entries.append(self._create_bundle_entry(condition))
        
        for medication_request in self.medication_requests:
            entries.append(self._create_bundle_entry(medication_request))
        
        for medication_statement in self.medication_statements:
            entries.append(self._create_bundle_entry(medication_statement))
        
        for service_request in self.service_requests:
            entries.append(self._create_bundle_entry(service_request))
        
        for procedure in self.procedures:
            entries.append(self._create_bundle_entry(procedure))
        
        for family_history in self.family_member_histories:
            entries.append(self._create_bundle_entry(family_history))
        
        for allergy in self.allergies:
            entries.append(self._create_bundle_entry(allergy))
        
        for immunization in self.immunizations:
            entries.append(self._create_bundle_entry(immunization))
        
        for appointment in self.appointments:
            entries.append(self._create_bundle_entry(appointment))
        
        for care_plan in self.care_plans:
            entries.append(self._create_bundle_entry(care_plan))
        
        for communication in self.communications:
            entries.append(self._create_bundle_entry(communication))
        
        return Bundle(
            id=self.bundle_id,
            type="collection",
            timestamp=datetime.utcnow().isoformat() + "Z",
            entry=entries if entries else None
        )
