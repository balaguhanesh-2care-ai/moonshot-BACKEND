"""
FHIR SDK Types - Helper types and utilities for creating FHIR resources.

This module provides utility functions for creating common FHIR data types
like CodeableConcept, Coding, Quantity, etc.
"""

from typing import Optional, List, Tuple, Union
from datetime import datetime, date

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.period import Period
from fhir.resources.annotation import Annotation
from fhir.resources.reference import Reference


# Type aliases for commonly used input patterns
CodeInput = Union[
    str,  # Just a display name
    Tuple[str, str, str],  # (code, system, display)
    Tuple[str, Tuple[str, str]],  # (display, (code, system))
    CodeableConcept,  # Already a CodeableConcept
]

QuantityInput = Union[
    Tuple[float, str],  # (value, unit)
    Tuple[float, str, str, str],  # (value, unit, code, system)
    Quantity,  # Already a Quantity
]

DateTimeInput = Union[str, datetime, date, None]


# =============================================================================
# CODING SYSTEM URLS
# =============================================================================
class CodingSystem:
    """Standard coding system URLs."""
    SNOMED_CT = "http://snomed.info/sct"
    LOINC = "http://loinc.org"
    ICD10 = "http://hl7.org/fhir/sid/icd-10"
    ICD10_CM = "http://hl7.org/fhir/sid/icd-10-cm"
    RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
    UCUM = "http://unitsofmeasure.org"
    
    # FHIR terminology
    OBSERVATION_CATEGORY = "http://terminology.hl7.org/CodeSystem/observation-category"
    CONDITION_CATEGORY = "http://terminology.hl7.org/CodeSystem/condition-category"
    CONDITION_CLINICAL = "http://terminology.hl7.org/CodeSystem/condition-clinical"
    CONDITION_VERIFICATION = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
    INTERPRETATION = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_coding(
    code: str,
    system: str,
    display: Optional[str] = None
) -> Coding:
    """
    Create a FHIR Coding object.
    
    Args:
        code: The code value
        system: The coding system URL
        display: Human-readable display text
        
    Returns:
        Coding object
    """
    return Coding(
        code=code,
        system=system,
        display=display
    )


def create_codeable_concept(
    text: Optional[str] = None,
    codings: Optional[List[Coding]] = None,
    code: Optional[str] = None,
    system: Optional[str] = None,
    display: Optional[str] = None
) -> CodeableConcept:
    """
    Create a FHIR CodeableConcept object.
    
    Can be created either with a list of Coding objects or with code/system/display.
    
    Args:
        text: Plain text representation
        codings: List of Coding objects
        code: Code value (used if codings not provided)
        system: Coding system URL (used if codings not provided)
        display: Display text (used if codings not provided)
        
    Returns:
        CodeableConcept object
    """
    if codings is None and code is not None:
        codings = [create_coding(code, system or "", display)]
    
    return CodeableConcept(
        text=text or display,
        coding=codings
    )


def parse_code_input(code_input: CodeInput) -> CodeableConcept:
    """
    Parse various code input formats into a CodeableConcept.
    
    Supported formats:
    - str: Just a display name (no code/system)
    - (code, system, display): Full code specification
    - (display, (code, system)): Display with code tuple
    - CodeableConcept: Return as-is
    
    Args:
        code_input: Code input in various formats
        
    Returns:
        CodeableConcept object
    """
    if isinstance(code_input, CodeableConcept):
        return code_input
    
    if isinstance(code_input, str):
        return CodeableConcept(text=code_input)
    
    if isinstance(code_input, (list, tuple)):
        if len(code_input) == 3 and all(isinstance(x, str) for x in code_input):
            # (code, system, display)
            code, system, display = code_input
            return create_codeable_concept(
                text=display,
                code=code,
                system=system,
                display=display
            )
        elif len(code_input) == 2:
            display, code_tuple = code_input
            if isinstance(code_tuple, (list, tuple)) and len(code_tuple) == 2:
                # (display, (code, system))
                code, system = code_tuple
                return create_codeable_concept(
                    text=display,
                    code=code,
                    system=system,
                    display=display
                )
    
    raise ValueError(f"Invalid code input format: {code_input}")


def create_quantity(
    value: float,
    unit: str,
    code: Optional[str] = None,
    system: Optional[str] = None
) -> Quantity:
    """
    Create a FHIR Quantity object.
    
    Args:
        value: Numeric value
        unit: Unit string
        code: Unit code (defaults to unit string)
        system: Unit system URL (defaults to UCUM)
        
    Returns:
        Quantity object
    """
    return Quantity(
        value=value,
        unit=unit,
        code=code or unit,
        system=system or CodingSystem.UCUM
    )


def parse_quantity_input(quantity_input: QuantityInput) -> Quantity:
    """
    Parse various quantity input formats into a Quantity.
    
    Supported formats:
    - (value, unit): Simple value with unit
    - (value, unit, code, system): Full quantity specification
    - Quantity: Return as-is
    
    Args:
        quantity_input: Quantity input in various formats
        
    Returns:
        Quantity object
    """
    if isinstance(quantity_input, Quantity):
        return quantity_input
    
    if isinstance(quantity_input, (list, tuple)):
        if len(quantity_input) == 2:
            value, unit = quantity_input
            return create_quantity(value, unit)
        elif len(quantity_input) == 4:
            value, unit, code, system = quantity_input
            return create_quantity(value, unit, code, system)
    
    raise ValueError(f"Invalid quantity input format: {quantity_input}")


def create_period(
    start: Optional[DateTimeInput] = None,
    end: Optional[DateTimeInput] = None
) -> Period:
    """
    Create a FHIR Period object.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Period object
    """
    return Period(
        start=format_datetime(start) if start else None,
        end=format_datetime(end) if end else None
    )


def create_annotation(text: str, time: Optional[DateTimeInput] = None) -> Annotation:
    """
    Create a FHIR Annotation (note) object.
    
    Args:
        text: The note text
        time: When the note was made
        
    Returns:
        Annotation object
    """
    return Annotation(
        text=text,
        time=format_datetime(time) if time else None
    )


def create_reference(
    reference: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    display: Optional[str] = None
) -> Reference:
    """
    Create a FHIR Reference object.
    
    Args:
        reference: Full reference string (e.g., "Patient/123")
        resource_type: Resource type (used with resource_id)
        resource_id: Resource ID (used with resource_type)
        display: Display text for the reference
        
    Returns:
        Reference object
    """
    if reference is None and resource_type and resource_id:
        reference = f"{resource_type}/{resource_id}"
    
    return Reference(
        reference=reference,
        display=display
    )


def format_datetime(dt: DateTimeInput) -> Optional[str]:
    """
    Format datetime to FHIR datetime string.
    
    Args:
        dt: Input datetime (string, datetime, or date)
        
    Returns:
        FHIR-formatted datetime string
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        return dt
    
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return dt.isoformat()
    
    if isinstance(dt, date):
        return dt.isoformat()
    
    return str(dt)


def format_date(d: DateTimeInput) -> Optional[str]:
    """
    Format date to FHIR date string (YYYY-MM-DD).
    
    Args:
        d: Input date
        
    Returns:
        FHIR-formatted date string
    """
    if d is None:
        return None
    
    if isinstance(d, str):
        # Try to parse and reformat
        return d.split("T")[0] if "T" in d else d
    
    if isinstance(d, (datetime, date)):
        return d.strftime("%Y-%m-%d")
    
    return str(d)


