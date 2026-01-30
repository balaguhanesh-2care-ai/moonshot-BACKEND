"""
Procedure Resource Builder - Creates FHIR Procedure resources for procedure history.

FHIR Mapping:
- Procedure represents a procedure that has been performed
- status: preparation, in-progress, completed, etc.
- code: What procedure was performed
- performedDateTime/performedPeriod: When it was done
- bodySite: Where on the body

Reference: https://www.hl7.org/fhir/procedure.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.procedure import Procedure, ProcedurePerformer
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
    create_period,
)


class ProcedureStatus:
    """FHIR Procedure status codes."""
    PREPARATION = "preparation"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    ON_HOLD = "on-hold"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ProcedureBuilder:
    """
    Builder for creating FHIR Procedure resources.
    
    Procedure represents an action that was performed on a patient,
    including surgical procedures, diagnostic procedures, etc.
    
    Example:
        procedure = ProcedureBuilder.build(
            code="Appendectomy",
            performed_date="2023-06-15",
            status=ProcedureStatus.COMPLETED,
            notes="Laparoscopic approach"
        )
    """
    
    @staticmethod
    def build(
        code: CodeInput,
        status: str = ProcedureStatus.COMPLETED,
        performed_date: Optional[DateTimeInput] = None,
        performed_start: Optional[DateTimeInput] = None,
        performed_end: Optional[DateTimeInput] = None,
        body_site: Optional[CodeInput] = None,
        outcome: Optional[CodeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        performer_references: Optional[List[Reference]] = None,
        location_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Procedure:
        """
        Build a FHIR Procedure resource.
        
        Args:
            code: The procedure name/code
            status: Procedure status (default: completed)
            performed_date: When the procedure was performed (single point)
            performed_start: Start of procedure period
            performed_end: End of procedure period
            body_site: Body site where procedure was performed
            outcome: Outcome of the procedure
            notes: Additional notes
            reason: Reason for the procedure
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            performer_references: References to performers
            location_reference: Reference to location
            id: Resource ID
            
        Returns:
            FHIR Procedure resource
            
        Example:
            vasectomy = ProcedureBuilder.build(
                code="Vasectomy",
                performed_date="2022-03-15",
                status=ProcedureStatus.COMPLETED,
                notes="Successful procedure, no complications"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse code
        procedure_code = parse_code_input(code)
        
        # Build performed datetime/period
        performed_datetime = None
        performed_period = None
        if performed_date:
            performed_datetime = format_datetime(performed_date)
        elif performed_start or performed_end:
            performed_period = create_period(performed_start, performed_end)
        
        # Build body site
        body_site_list = None
        if body_site:
            body_site_list = [parse_code_input(body_site)]
        
        # Build outcome
        outcome_concept = None
        if outcome:
            outcome_concept = parse_code_input(outcome)
        
        # Build reason
        reason_code = None
        if reason:
            reason_code = [parse_code_input(reason)]
        
        # Build performers
        performers = None
        if performer_references:
            performers = [
                ProcedurePerformer(actor=ref)
                for ref in performer_references
            ]
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Prepare R5 compatible fields
        from fhir.resources.codeablereference import CodeableReference
        
        # reason is List[CodeableReference] in R5
        reason_val = None
        if reason_code:
            reason_val = [CodeableReference(concept=rc) for rc in reason_code]

        # Create the Procedure resource
        procedure = Procedure(
            id=resource_id,
            status=status,
            code=procedure_code,
            subject=subject_reference,
            encounter=encounter_reference,
            occurrenceDateTime=performed_datetime,
            occurrencePeriod=performed_period,
            performer=performers,
            location=location_reference,
            reason=reason_val,
            bodySite=body_site_list,
            outcome=outcome_concept,
            note=note,
        )
        
        return procedure


