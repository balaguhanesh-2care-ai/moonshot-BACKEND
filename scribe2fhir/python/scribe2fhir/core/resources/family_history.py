"""
FamilyMemberHistory Resource Builder - Creates FHIR FamilyMemberHistory resources.

FHIR Mapping:
- FamilyMemberHistory represents health conditions in family members
- relationship: The family relationship (father, mother, sibling, etc.)
- condition: The health condition the family member had
- age/deceased: Age information

Reference: https://www.hl7.org/fhir/familymemberhistory.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.familymemberhistory import FamilyMemberHistory, FamilyMemberHistoryCondition
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation
from fhir.resources.age import Age

from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
)


class FamilyRelationship:
    """FHIR family relationship codes (v3-RoleCode)."""
    # Parents
    FATHER = ("FTH", "father")
    MOTHER = ("MTH", "mother")
    NATURAL_PARENT = ("NPRN", "natural parent")
    ADOPTIVE_PARENT = ("ADOPTP", "adoptive parent")
    
    # Grandparents
    GRANDFATHER = ("GRFTH", "grandfather")
    GRANDMOTHER = ("GRMTH", "grandmother")
    MATERNAL_GRANDFATHER = ("MGRFTH", "maternal grandfather")
    MATERNAL_GRANDMOTHER = ("MGRMTH", "maternal grandmother")
    PATERNAL_GRANDFATHER = ("PGRFTH", "paternal grandfather")
    PATERNAL_GRANDMOTHER = ("PGRMTH", "paternal grandmother")
    
    # Siblings
    SIBLING = ("SIB", "sibling")
    BROTHER = ("BRO", "brother")
    SISTER = ("SIS", "sister")
    HALF_SIBLING = ("HSIB", "half-sibling")
    
    # Children
    CHILD = ("CHILD", "child")
    SON = ("SON", "son")
    DAUGHTER = ("DAU", "daughter")
    
    # Extended family
    AUNT = ("AUNT", "aunt")
    UNCLE = ("UNCLE", "uncle")
    COUSIN = ("COUSN", "cousin")
    
    # Other
    FAMILY_MEMBER = ("FAMMEMB", "family member")
    SIGNIFICANT_OTHER = ("SIGOTHR", "significant other")


class FamilyMemberHistoryStatus:
    """FamilyMemberHistory status codes."""
    PARTIAL = "partial"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    HEALTH_UNKNOWN = "health-unknown"


class FamilyMemberHistoryBuilder:
    """
    Builder for creating FHIR FamilyMemberHistory resources.
    
    FamilyMemberHistory is used to document health conditions that
    run in the patient's family.
    
    Example:
        history = FamilyMemberHistoryBuilder.build(
            condition="Hypertension",
            relationship="father",
            onset="1997",
            status="completed",
            notes="Father has been on medication since 1997"
        )
    """
    
    RELATIONSHIP_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"
    
    @staticmethod
    def _parse_relationship(
        relationship: Union[str, tuple, CodeableConcept]
    ) -> CodeableConcept:
        """Parse relationship into CodeableConcept."""
        if isinstance(relationship, CodeableConcept):
            return relationship
        
        if isinstance(relationship, tuple):
            code, display = relationship
            return CodeableConcept(
                coding=[
                    Coding(
                        system=FamilyMemberHistoryBuilder.RELATIONSHIP_SYSTEM,
                        code=code,
                        display=display
                    )
                ],
                text=display
            )
        
        # Map common strings to codes
        relationship_map = {
            "father": FamilyRelationship.FATHER,
            "mother": FamilyRelationship.MOTHER,
            "brother": FamilyRelationship.BROTHER,
            "sister": FamilyRelationship.SISTER,
            "sibling": FamilyRelationship.SIBLING,
            "son": FamilyRelationship.SON,
            "daughter": FamilyRelationship.DAUGHTER,
            "child": FamilyRelationship.CHILD,
            "grandfather": FamilyRelationship.GRANDFATHER,
            "grandmother": FamilyRelationship.GRANDMOTHER,
            "aunt": FamilyRelationship.AUNT,
            "uncle": FamilyRelationship.UNCLE,
            "cousin": FamilyRelationship.COUSIN,
            "family member": FamilyRelationship.FAMILY_MEMBER,
            "spouse": FamilyRelationship.SIGNIFICANT_OTHER,
        }
        
        relationship_lower = relationship.lower()
        if relationship_lower in relationship_map:
            code, display = relationship_map[relationship_lower]
        else:
            # Use as-is
            code = relationship.upper()
            display = relationship.capitalize()
        
        return CodeableConcept(
            coding=[
                Coding(
                    system=FamilyMemberHistoryBuilder.RELATIONSHIP_SYSTEM,
                    code=code,
                    display=display
                )
            ],
            text=display
        )
    
    @staticmethod
    def build(
        condition: CodeInput,
        relationship: Union[str, tuple, CodeableConcept],
        status: str = FamilyMemberHistoryStatus.COMPLETED,
        onset: Optional[Union[str, int]] = None,  # Can be year, age, or datetime
        outcome: Optional[str] = None,
        deceased: Optional[bool] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        date: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> FamilyMemberHistory:
        """
        Build a FHIR FamilyMemberHistory resource.
        
        Args:
            condition: The health condition
            relationship: Family relationship (father, mother, brother, etc.)
            status: History status (default: completed)
            onset: When the condition started (year, age, or datetime)
            outcome: Outcome if known (e.g., "deceased", "resolved")
            deceased: Whether the family member is deceased
            notes: Additional notes
            subject_reference: Reference to the patient
            date: When this was recorded
            id: Resource ID
            
        Returns:
            FHIR FamilyMemberHistory resource
            
        Example:
            # Father with hypertension
            history = FamilyMemberHistoryBuilder.build(
                condition="Hypertension",
                relationship="Father",
                onset="1997",
                status="completed"
            )
            
            # Mother with diabetes, deceased
            history = FamilyMemberHistoryBuilder.build(
                condition="Type 2 diabetes",
                relationship="Mother",
                deceased=True,
                notes="Mother passed away in 2020"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse condition
        condition_code = parse_code_input(condition)
        
        # Parse relationship
        relationship_concept = FamilyMemberHistoryBuilder._parse_relationship(relationship)
        
        # Build condition with onset
        condition_item = FamilyMemberHistoryCondition(code=condition_code)
        
        # Handle onset - can be age, year, or string
        if onset:
            if isinstance(onset, int):
                if onset > 1900:  # Likely a year
                    condition_item.onsetString = str(onset)
                else:  # Likely an age
                    condition_item.onsetAge = Age(value=onset, unit="years", system="http://unitsofmeasure.org", code="a")
            else:
                condition_item.onsetString = str(onset)
        
        # Handle outcome
        if outcome:
            condition_item.outcome = CodeableConcept(text=outcome)
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Add note to condition if provided
        if notes:
            condition_item.note = [Annotation(text=notes)]
        
        # Create the FamilyMemberHistory resource
        family_history = FamilyMemberHistory(
            id=resource_id,
            status=status,
            patient=subject_reference,
            date=format_datetime(date) if date else None,
            relationship=relationship_concept,
            deceasedBoolean=deceased,
            condition=[condition_item],
            note=note,
        )
        
        return family_history


