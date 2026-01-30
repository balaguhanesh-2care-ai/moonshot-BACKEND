"""
CarePlan and Communication Resource Builders - For advice and clinical notes.

FHIR Mapping:
- CarePlan: Used for patient instructions and care advice
- Communication: Used for clinical notes and messages

CarePlan is ideal for:
- Patient advice (lifestyle modifications, dietary instructions)
- Care instructions
- Treatment plans

Communication is ideal for:
- Clinical notes
- Prescription notes
- Messages about the encounter

Reference: 
- https://www.hl7.org/fhir/careplan.html
- https://www.hl7.org/fhir/communication.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.careplan import CarePlan, CarePlanActivity
from fhir.resources.communication import Communication, CommunicationPayload
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
)


class CarePlanStatus:
    """CarePlan status codes."""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class CarePlanIntent:
    """CarePlan intent codes."""
    PROPOSAL = "proposal"
    PLAN = "plan"
    ORDER = "order"
    OPTION = "option"


class CommunicationStatus:
    """Communication status codes."""
    PREPARATION = "preparation"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    ON_HOLD = "on-hold"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class AdviceBuilder:
    """
    Builder for creating FHIR CarePlan resources for patient advice.
    
    CarePlan is used to document care advice, lifestyle recommendations,
    and instructions given to patients.
    
    Example:
        advice = AdviceBuilder.build(
            advice_text="Drink plenty of water",
            category="lifestyle"
        )
    """
    
    CARE_PLAN_CATEGORY_SYSTEM = "http://hl7.org/fhir/us/core/CodeSystem/careplan-category"
    
    @staticmethod
    def build(
        advice_text: str,
        category: Optional[str] = None,
        status: str = CarePlanStatus.ACTIVE,
        intent: str = CarePlanIntent.PLAN,
        title: Optional[str] = None,
        description: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        author_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> CarePlan:
        """
        Build a FHIR CarePlan resource for patient advice.
        
        Args:
            advice_text: The advice/instruction text
            category: Category of advice (lifestyle, diet, medication, etc.)
            status: CarePlan status
            intent: CarePlan intent
            title: Title for the care plan
            description: Additional description
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            author_reference: Reference to author
            id: Resource ID
            
        Returns:
            FHIR CarePlan resource
            
        Example:
            advice = AdviceBuilder.build(
                advice_text="Drink plenty of water",
                category="lifestyle",
                title="Hydration advice"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Build category
        category_list = None
        if category:
            category_list = [
                CodeableConcept(
                    text=category
                )
            ]
        
        # Build activity with the advice using progress note
        # In FHIR R5/newer versions, CarePlanActivity uses progress for notes
        activity = CarePlanActivity(
            progress=[Annotation(text=advice_text)]
        )
        
        # Create the CarePlan resource
        care_plan = CarePlan(
            id=resource_id,
            status=status,
            intent=intent,
            title=title,
            description=description or advice_text,
            subject=subject_reference,
            encounter=encounter_reference,
            custodian=author_reference,  # Use custodian instead of author
            category=category_list,
            activity=[activity],
        )
        
        return care_plan
    
    @staticmethod
    def build_multiple(
        advice_texts: List[str],
        status: str = CarePlanStatus.ACTIVE,
        intent: str = CarePlanIntent.PLAN,
        title: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> CarePlan:
        """
        Build a CarePlan with multiple advice items.
        
        Args:
            advice_texts: List of advice/instruction texts
            status: CarePlan status
            intent: CarePlan intent
            title: Title for the care plan
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            id: Resource ID
            
        Returns:
            FHIR CarePlan with multiple activities
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Build activities for each advice
        activities = [
            CarePlanActivity(
                progress=[Annotation(text=text)]
            )
            for text in advice_texts
        ]
        
        # Create the CarePlan resource
        care_plan = CarePlan(
            id=resource_id,
            status=status,
            intent=intent,
            title=title or "Patient Advice",
            subject=subject_reference,
            encounter=encounter_reference,
            activity=activities,
        )
        
        return care_plan


class ClinicalNoteBuilder:
    """
    Builder for creating FHIR Communication resources for clinical notes.
    
    Communication is used for clinical notes, prescription notes,
    and other messages related to patient care.
    
    Example:
        note = ClinicalNoteBuilder.build(
            note_text="Patient is a 30 year old living in Bangalore",
            category="prescription-note"
        )
    """
    
    @staticmethod
    def build(
        note_text: str,
        category: Optional[str] = None,
        status: str = CommunicationStatus.COMPLETED,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        sender_reference: Optional[Reference] = None,
        sent: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> Communication:
        """
        Build a FHIR Communication resource for clinical notes.
        
        Args:
            note_text: The note text
            category: Category of note (clinical-note, prescription-note)
            status: Communication status
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            sender_reference: Reference to sender
            sent: When the note was sent/recorded
            id: Resource ID
            
        Returns:
            FHIR Communication resource
            
        Example:
            note = ClinicalNoteBuilder.build(
                note_text="Patient reports improved symptoms",
                category="clinical-note"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Build category
        category_list = None
        if category:
            category_list = [CodeableConcept(text=category)]
        
        # Build payload with the note
        # R5 removed contentString, use contentCodeableConcept for text
        payload = [
            CommunicationPayload(contentCodeableConcept=CodeableConcept(text=note_text))
        ]
        
        # Create the Communication resource
        communication = Communication(
            id=resource_id,
            status=status,
            category=category_list,
            subject=subject_reference,
            encounter=encounter_reference,
            sender=sender_reference,
            sent=format_datetime(sent) if sent else None,
            payload=payload,
        )
        
        return communication
