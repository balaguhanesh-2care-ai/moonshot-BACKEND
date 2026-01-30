"""
Encounter Resource Builder - Creates FHIR Encounter resources.

FHIR Mapping:
- Encounter represents an interaction between patient and healthcare provider
- class: Type of encounter (ambulatory, emergency, inpatient, etc.)
- type/serviceType: More specific categorization
- period: When the encounter occurred
- serviceProvider: The facility/organization
- participant: Healthcare providers involved

Reference: https://www.hl7.org/fhir/encounter.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.encounter import Encounter, EncounterParticipant, EncounterLocation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.period import Period
from fhir.resources.reference import Reference

from ..types import DateTimeInput, format_datetime, create_period


class EncounterClass:
    """FHIR Encounter class codes (ActEncounterCode)."""
    AMBULATORY = ("AMB", "ambulatory")
    EMERGENCY = ("EMER", "emergency")
    FIELD = ("FLD", "field")
    HOME_HEALTH = ("HH", "home health")
    INPATIENT_ENCOUNTER = ("IMP", "inpatient encounter")
    INPATIENT_ACUTE = ("ACUTE", "inpatient acute")
    INPATIENT_NONACUTE = ("NONAC", "inpatient non-acute")
    OBSERVATION_ENCOUNTER = ("OBSENC", "observation encounter")
    PRE_ADMISSION = ("PRENC", "pre-admission")
    SHORT_STAY = ("SS", "short stay")
    VIRTUAL = ("VR", "virtual")


class EncounterStatus:
    """FHIR Encounter status codes."""
    PLANNED = "planned"
    ARRIVED = "arrived"
    TRIAGED = "triaged"
    IN_PROGRESS = "in-progress"
    ONLEAVE = "onleave"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class EncounterBuilder:
    """
    Builder for creating FHIR Encounter resources.
    
    An Encounter represents a clinical interaction between a patient and 
    healthcare provider(s) for the purpose of providing healthcare services.
    
    Example:
        encounter = EncounterBuilder.build(
            encounter_class="ambulatory",
            encounter_type="consultation",
            period_start="2024-01-14T10:00:00Z",
            facility_name="City Hospital",
            department="Cardiology"
        )
    """
    
    # Encounter class system
    ACT_ENCOUNTER_CODE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
    
    # Common encounter type systems
    ENCOUNTER_TYPE_SYSTEM = "http://terminology.hl7.org/CodeSystem/encounter-type"
    SNOMED_CT = "http://snomed.info/sct"
    
    @staticmethod
    def _parse_encounter_class(
        encounter_class: Union[str, Coding]
    ) -> Coding:
        """Parse encounter class into a Coding."""
        if isinstance(encounter_class, Coding):
            return encounter_class
        
        # Map string to standard codes
        class_map = {
            "ambulatory": EncounterClass.AMBULATORY,
            "amb": EncounterClass.AMBULATORY,
            "outpatient": EncounterClass.AMBULATORY,
            "opd": EncounterClass.AMBULATORY,
            "emergency": EncounterClass.EMERGENCY,
            "emer": EncounterClass.EMERGENCY,
            "er": EncounterClass.EMERGENCY,
            "inpatient": EncounterClass.INPATIENT_ENCOUNTER,
            "imp": EncounterClass.INPATIENT_ENCOUNTER,
            "ipd": EncounterClass.INPATIENT_ENCOUNTER,
            "home": EncounterClass.HOME_HEALTH,
            "hh": EncounterClass.HOME_HEALTH,
            "virtual": EncounterClass.VIRTUAL,
            "vr": EncounterClass.VIRTUAL,
            "teleconsultation": EncounterClass.VIRTUAL,
            "observation": EncounterClass.OBSERVATION_ENCOUNTER,
        }
        
        class_lower = encounter_class.lower()
        if class_lower in class_map:
            code, display = class_map[class_lower]
        else:
            # Use as-is if not recognized
            code = encounter_class
            display = encounter_class
        
        return Coding(
            system=EncounterBuilder.ACT_ENCOUNTER_CODE_SYSTEM,
            code=code,
            display=display
        )
    
    @staticmethod
    def build(
        encounter_class: Union[str, Coding] = "ambulatory",
        encounter_type: Optional[str] = None,
        encounter_subtype: Optional[str] = None,
        status: str = EncounterStatus.FINISHED,
        period_start: Optional[DateTimeInput] = None,
        period_end: Optional[DateTimeInput] = None,
        facility_name: Optional[str] = None,
        department: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        participant_references: Optional[List[Reference]] = None,
        service_provider_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Encounter:
        """
        Build a FHIR Encounter resource.
        
        Args:
            encounter_class: Type of encounter. Can be:
                            - str: "ambulatory", "emergency", "inpatient", "virtual", etc.
                            - Coding: Pre-built Coding object
            encounter_type: More specific type (e.g., "consultation", "follow-up")
            encounter_subtype: Sub-classification
            status: Encounter status (default: finished)
            period_start: When the encounter started
            period_end: When the encounter ended
            facility_name: Name of the healthcare facility
            department: Department within the facility
            subject_reference: Reference to the patient
            participant_references: References to practitioners
            service_provider_reference: Reference to organization
            id: Resource ID
            
        Returns:
            FHIR Encounter resource
            
        Example:
            encounter = EncounterBuilder.build(
                encounter_class="ambulatory",
                encounter_type="Consultation",
                period_start=datetime.now(),
                facility_name="City Hospital",
                department="General Medicine"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse encounter class
        class_coding = EncounterBuilder._parse_encounter_class(encounter_class)
        
        # Build encounter type
        type_concepts = []
        if encounter_type:
            type_concepts.append(
                CodeableConcept(
                    coding=[
                        Coding(
                            system=EncounterBuilder.ENCOUNTER_TYPE_SYSTEM,
                            code=encounter_type.lower().replace(" ", "-"),
                            display=encounter_type
                        )
                    ],
                    text=encounter_type
                )
            )
        
        # Build service type (can include department)
        service_type = None
        if department:
            service_type = CodeableConcept(
                text=department
            )
        
        # Build period
        period = None
        if period_start or period_end:
            period = create_period(period_start, period_end)
        
        # Build service provider (facility)
        service_provider = service_provider_reference
        if not service_provider and facility_name:
            service_provider = Reference(display=facility_name)
        
        # Build participants
        participants = None
        if participant_references:
            participants = [
                EncounterParticipant(actor=ref)
                for ref in participant_references
            ]
        
        # Create the Encounter resource
        # Create the Encounter resource
        # FHIR R5 updates:
        # - class is List[CodeableConcept], not Coding
        # - period is actualPeriod
        # - serviceType is List[CodeableReference]
        # - participant.individual is participant.actor

        # Wrap class coding in CodeableConcept
        class_concept = CodeableConcept(coding=[class_coding])

        # Convert serviceType to CodeableReference list if present
        service_type_val = None
        if service_type:
            # R5 serviceType is List[CodeableReference]
            from fhir.resources.codeablereference import CodeableReference
            service_type_val = [CodeableReference(concept=service_type)]

        # Update participants to use 'actor' instead of 'individual'
        if participants:
            for p in participants:
                 if p.individual:
                     p.actor = p.individual
                     p.individual = None

        encounter = Encounter(
            id=resource_id,
            status=status,
            class_fhir=[class_concept],
            type=type_concepts if type_concepts else None,
            serviceType=service_type_val,
            subject=subject_reference,
            participant=participants,
            actualPeriod=period,
            serviceProvider=service_provider,
        )
        
        return encounter


