"""
ServiceRequest Resource Builder - Creates FHIR ServiceRequest for orders.

FHIR Mapping:
- ServiceRequest represents requests for services like lab tests, procedures
- category: Type of service (laboratory, imaging, procedure, etc.)
- code: What is being requested
- intent: order, plan, proposal
- status: draft, active, completed, etc.

Reference: https://www.hl7.org/fhir/servicerequest.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation
from fhir.resources.period import Period

from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
    create_period,
)


class ServiceRequestCategory:
    """Common ServiceRequest categories."""
    LABORATORY = ("108252007", "Laboratory procedure", CodingSystem.SNOMED_CT)
    IMAGING = ("363679005", "Imaging", CodingSystem.SNOMED_CT)
    PROCEDURE = ("387713003", "Surgical procedure", CodingSystem.SNOMED_CT)
    COUNSELLING = ("409063005", "Counseling", CodingSystem.SNOMED_CT)
    EDUCATION = ("409073007", "Education", CodingSystem.SNOMED_CT)


class ServiceRequestStatus:
    """ServiceRequest status codes."""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ServiceRequestIntent:
    """ServiceRequest intent codes."""
    PROPOSAL = "proposal"
    PLAN = "plan"
    DIRECTIVE = "directive"
    ORDER = "order"
    ORIGINAL_ORDER = "original-order"
    REFLEX_ORDER = "reflex-order"
    FILLER_ORDER = "filler-order"
    INSTANCE_ORDER = "instance-order"
    OPTION = "option"


class ServiceRequestPriority:
    """ServiceRequest priority codes."""
    ROUTINE = "routine"
    URGENT = "urgent"
    ASAP = "asap"
    STAT = "stat"


class ServiceRequestBuilder:
    """
    Builder for creating FHIR ServiceRequest resources.
    
    ServiceRequest is used for ordering diagnostic tests, procedures,
    and other clinical services.
    
    Example:
        # Lab test order
        cbc_test = ServiceRequestBuilder.build_lab_test(
            code="CBC test",
            notes="Fasting required",
            priority=ServiceRequestPriority.ROUTINE
        )
        
        # Procedure order
        xray = ServiceRequestBuilder.build_procedure(
            code="Chest X-ray",
            notes="PA and lateral views"
        )
    """
    
    SERVICE_REQUEST_CATEGORY_SYSTEM = "http://snomed.info/sct"
    
    @staticmethod
    def _build_service_request(
        code: CodeInput,
        category: tuple,
        status: str = ServiceRequestStatus.ACTIVE,
        intent: str = ServiceRequestIntent.ORDER,
        priority: Optional[str] = None,
        occurrence_date: Optional[DateTimeInput] = None,
        occurrence_period_start: Optional[DateTimeInput] = None,
        occurrence_period_end: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        requester_reference: Optional[Reference] = None,
        performer_references: Optional[List[Reference]] = None,
        id: Optional[str] = None,
    ) -> ServiceRequest:
        """
        Internal method to build a ServiceRequest.
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse code
        service_code = parse_code_input(code)
        
        # Build category
        cat_code, cat_display, cat_system = category
        category_concept = CodeableConcept(
            coding=[
                Coding(
                    system=cat_system,
                    code=cat_code,
                    display=cat_display
                )
            ]
        )
        
        # Build occurrence
        occurrence_datetime = None
        occurrence_period = None
        if occurrence_date:
            occurrence_datetime = format_datetime(occurrence_date)
        elif occurrence_period_start or occurrence_period_end:
            occurrence_period = create_period(occurrence_period_start, occurrence_period_end)
        
        # Build reason
        reason_code = None
        if reason:
            reason_code = [parse_code_input(reason)]
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Prepare R5 compatible fields
        from fhir.resources.codeablereference import CodeableReference
        
        # code is CodeableReference in R5
        service_code_ref = CodeableReference(concept=service_code)
        
        # reason is List[CodeableReference] in R5
        reason_val = None
        if reason_code:
            reason_val = [CodeableReference(concept=rc) for rc in reason_code]

        # Create the ServiceRequest resource
        service_request = ServiceRequest(
            id=resource_id,
            status=status,
            intent=intent,
            priority=priority,
            category=[category_concept],
            code=service_code_ref,
            subject=subject_reference,
            encounter=encounter_reference,
            occurrenceDateTime=occurrence_datetime,
            occurrencePeriod=occurrence_period,
            requester=requester_reference,
            performer=performer_references,
            reason=reason_val,
            note=note,
        )
        
        return service_request
    
    @staticmethod
    def build_lab_test(
        code: CodeInput,
        status: str = ServiceRequestStatus.ACTIVE,
        intent: str = ServiceRequestIntent.ORDER,
        priority: Optional[str] = None,
        occurrence_date: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        requester_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> ServiceRequest:
        """
        Build a ServiceRequest for a laboratory test.
        
        Args:
            code: The lab test name/code
            status: Request status (default: active)
            intent: Request intent (default: order)
            priority: Priority (routine, urgent, asap, stat)
            occurrence_date: When the test should be performed
            notes: Additional instructions
            reason: Reason for ordering the test
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            requester_reference: Reference to ordering provider
            id: Resource ID
            
        Returns:
            FHIR ServiceRequest for laboratory test
            
        Example:
            cbc = ServiceRequestBuilder.build_lab_test(
                code="CBC test",
                notes="Patient should fast for 8 hours"
            )
        """
        return ServiceRequestBuilder._build_service_request(
            code=code,
            category=ServiceRequestCategory.LABORATORY,
            status=status,
            intent=intent,
            priority=priority,
            occurrence_date=occurrence_date,
            notes=notes,
            reason=reason,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            requester_reference=requester_reference,
            id=id,
        )
    
    @staticmethod
    def build_procedure(
        code: CodeInput,
        status: str = ServiceRequestStatus.ACTIVE,
        intent: str = ServiceRequestIntent.ORDER,
        priority: Optional[str] = None,
        occurrence_date: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        requester_reference: Optional[Reference] = None,
        performer_references: Optional[List[Reference]] = None,
        id: Optional[str] = None,
    ) -> ServiceRequest:
        """
        Build a ServiceRequest for a procedure.
        
        Args:
            code: The procedure name/code
            status: Request status (default: active)
            intent: Request intent (default: order)
            priority: Priority (routine, urgent, asap, stat)
            occurrence_date: When the procedure should be performed
            notes: Additional instructions
            reason: Reason for the procedure
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            requester_reference: Reference to ordering provider
            performer_references: References to performers
            id: Resource ID
            
        Returns:
            FHIR ServiceRequest for procedure
            
        Example:
            ecg = ServiceRequestBuilder.build_procedure(
                code="ECG",
                notes="12-lead ECG required"
            )
        """
        return ServiceRequestBuilder._build_service_request(
            code=code,
            category=ServiceRequestCategory.PROCEDURE,
            status=status,
            intent=intent,
            priority=priority,
            occurrence_date=occurrence_date,
            notes=notes,
            reason=reason,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            requester_reference=requester_reference,
            performer_references=performer_references,
            id=id,
        )
    
    @staticmethod
    def build_imaging(
        code: CodeInput,
        status: str = ServiceRequestStatus.ACTIVE,
        intent: str = ServiceRequestIntent.ORDER,
        priority: Optional[str] = None,
        occurrence_date: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        requester_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> ServiceRequest:
        """
        Build a ServiceRequest for an imaging study.
        
        Args:
            code: The imaging study name/code (e.g., "Chest X-ray")
            status: Request status
            intent: Request intent
            priority: Priority
            occurrence_date: When the imaging should be performed
            notes: Additional instructions
            reason: Reason for the study
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            requester_reference: Reference to ordering provider
            id: Resource ID
            
        Returns:
            FHIR ServiceRequest for imaging
        """
        return ServiceRequestBuilder._build_service_request(
            code=code,
            category=ServiceRequestCategory.IMAGING,
            status=status,
            intent=intent,
            priority=priority,
            occurrence_date=occurrence_date,
            notes=notes,
            reason=reason,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            requester_reference=requester_reference,
            id=id,
        )


