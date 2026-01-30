"""
Immunization Resource Builder - Creates FHIR Immunization resources.

FHIR Mapping:
- Immunization represents vaccination events
- vaccineCode: The vaccine administered
- occurrenceDateTime: When it was given
- status: completed, entered-in-error, not-done
- site: Body site
- route: Route of administration

Reference: https://www.hl7.org/fhir/immunization.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.immunization import Immunization, ImmunizationPerformer, ImmunizationProtocolApplied
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
)


class ImmunizationStatus:
    """Immunization status codes."""
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    NOT_DONE = "not-done"


class ImmunizationBuilder:
    """
    Builder for creating FHIR Immunization resources.
    
    Immunization represents the event of a vaccine being administered.
    
    Example:
        immunization = ImmunizationBuilder.build(
            vaccine="COVID-19 vaccine",
            occurrence_date="2021-04-15",
            status=ImmunizationStatus.COMPLETED,
            notes="Second dose of Covishield"
        )
    """
    
    @staticmethod
    def build(
        vaccine: CodeInput,
        status: str = ImmunizationStatus.COMPLETED,
        occurrence_date: Optional[DateTimeInput] = None,
        occurrence_string: Optional[str] = None,
        lot_number: Optional[str] = None,
        expiration_date: Optional[DateTimeInput] = None,
        site: Optional[CodeInput] = None,
        route: Optional[CodeInput] = None,
        dose_quantity: Optional[float] = None,
        dose_unit: Optional[str] = None,
        dose_number: Optional[int] = None,
        series_doses: Optional[int] = None,
        reason: Optional[CodeInput] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        performer_reference: Optional[Reference] = None,
        manufacturer_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Immunization:
        """
        Build a FHIR Immunization resource.
        
        Args:
            vaccine: The vaccine code/name
            status: Immunization status (completed, not-done)
            occurrence_date: When the vaccine was given
            occurrence_string: Approximate date string (e.g., "2021")
            lot_number: Vaccine lot number
            expiration_date: Vaccine expiration date
            site: Body site where administered
            route: Route of administration
            dose_quantity: Dose amount
            dose_unit: Dose unit
            dose_number: Which dose in a series
            series_doses: Total doses in series
            reason: Reason for vaccination
            notes: Additional notes
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            performer_reference: Reference to who administered
            manufacturer_reference: Reference to manufacturer
            id: Resource ID
            
        Returns:
            FHIR Immunization resource
            
        Example:
            covid_vaccine = ImmunizationBuilder.build(
                vaccine="COVID-19 vaccine",
                occurrence_date="2021-04-15",
                dose_number=2,
                series_doses=2,
                notes="Received Covishield during second wave"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse vaccine code
        vaccine_code = parse_code_input(vaccine)
        
        # Build occurrence
        occurrence_datetime = None
        occurrence_str = None
        if occurrence_date:
            occurrence_datetime = format_datetime(occurrence_date)
        elif occurrence_string:
            occurrence_str = occurrence_string
        
        # Build site
        site_concept = None
        if site:
            site_concept = parse_code_input(site)
        
        # Build route
        route_concept = None
        if route:
            route_concept = parse_code_input(route)
        
        # Build dose quantity
        dose_qty = None
        if dose_quantity is not None:
            dose_qty = Quantity(
                value=dose_quantity,
                unit=dose_unit or "dose"
            )
        
        # Build reason
        reason_code = None
        if reason:
            reason_code = [parse_code_input(reason)]
        
        # Build performer
        performers = None
        if performer_reference:
            performers = [ImmunizationPerformer(actor=performer_reference)]
        
        # Build protocol applied (dose series info)
        protocol_applied = None
        if dose_number is not None or series_doses is not None:
            protocol_applied = [
                ImmunizationProtocolApplied(
                    doseNumberPositiveInt=dose_number,
                    seriesDosesPositiveInt=series_doses
                )
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

        # Create the Immunization resource
        # Create the Immunization resource
        immunization_kwargs = {
            "id": resource_id,
            "status": status,
            "vaccineCode": vaccine_code,
            "patient": subject_reference,
            "encounter": encounter_reference,
            "lotNumber": lot_number,
            "expirationDate": format_datetime(expiration_date) if expiration_date else None,
            "site": site_concept,
            "route": route_concept,
            "doseQuantity": dose_qty,
            "performer": performers,
            "manufacturer": manufacturer_reference,
            "reason": reason_val,
            "protocolApplied": protocol_applied,
            "note": note,
        }
        
        if occurrence_datetime:
            immunization_kwargs["occurrenceDateTime"] = occurrence_datetime
        elif occurrence_str:
            immunization_kwargs["occurrenceString"] = occurrence_str
        else:
            # occurrence[x] is mandatory in FHIR R5. Default to "Unknown" if not provided.
            immunization_kwargs["occurrenceString"] = "Unknown"

        immunization = Immunization(**immunization_kwargs)
        
        return immunization


