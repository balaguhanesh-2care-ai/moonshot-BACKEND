"""
AllergyIntolerance Resource Builder - Creates FHIR AllergyIntolerance resources.

FHIR Mapping:
- AllergyIntolerance represents allergies and intolerances
- category: food, medication, environment, biologic
- type: allergy vs intolerance
- criticality: low, high, unable-to-assess
- clinicalStatus: active, inactive, resolved
- code: The allergen

Reference: https://www.hl7.org/fhir/allergyintolerance.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.allergyintolerance import AllergyIntolerance, AllergyIntoleranceReaction
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
)


class AllergyCategory:
    """Allergy category codes."""
    FOOD = "food"
    MEDICATION = "medication"
    ENVIRONMENT = "environment"
    BIOLOGIC = "biologic"


class AllergyType:
    """Allergy type codes."""
    ALLERGY = "allergy"
    INTOLERANCE = "intolerance"


class AllergyCriticality:
    """Allergy criticality codes."""
    LOW = "low"
    HIGH = "high"
    UNABLE_TO_ASSESS = "unable-to-assess"


class AllergyClinicalStatus:
    """Allergy clinical status codes."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESOLVED = "resolved"


class AllergyVerificationStatus:
    """Allergy verification status codes."""
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


class ReactionSeverity:
    """Reaction severity codes."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class AllergyBuilder:
    """
    Builder for creating FHIR AllergyIntolerance resources.
    
    AllergyIntolerance represents a propensity for adverse reaction
    to a substance (medications, food, environmental factors).
    
    Example:
        # Drug allergy
        allergy = AllergyBuilder.build(
            code="Paracetamol",
            category=AllergyCategory.MEDICATION,
            clinical_status=AllergyClinicalStatus.ACTIVE,
            criticality=AllergyCriticality.HIGH
        )
        
        # Food allergy
        allergy = AllergyBuilder.build(
            code="Peanuts",
            category=AllergyCategory.FOOD,
            reaction_manifestation="Anaphylaxis",
            reaction_severity=ReactionSeverity.SEVERE
        )
    """
    
    CLINICAL_STATUS_SYSTEM = "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical"
    VERIFICATION_STATUS_SYSTEM = "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification"
    
    @staticmethod
    def _create_clinical_status(status: str) -> CodeableConcept:
        """Create clinical status CodeableConcept."""
        return CodeableConcept(
            coding=[
                Coding(
                    system=AllergyBuilder.CLINICAL_STATUS_SYSTEM,
                    code=status,
                    display=status.capitalize()
                )
            ]
        )
    
    @staticmethod
    def _create_verification_status(status: str) -> CodeableConcept:
        """Create verification status CodeableConcept."""
        return CodeableConcept(
            coding=[
                Coding(
                    system=AllergyBuilder.VERIFICATION_STATUS_SYSTEM,
                    code=status,
                    display=status.capitalize()
                )
            ]
        )
    
    @staticmethod
    def build(
        code: CodeInput,
        category: Optional[str] = None,
        allergy_type: Optional[str] = None,
        clinical_status: str = AllergyClinicalStatus.ACTIVE,
        verification_status: Optional[str] = None,
        criticality: Optional[str] = None,
        onset: Optional[DateTimeInput] = None,
        reaction_manifestation: Optional[Union[str, CodeInput]] = None,
        reaction_severity: Optional[str] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        recorder_reference: Optional[Reference] = None,
        recorded_date: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> AllergyIntolerance:
        """
        Build a FHIR AllergyIntolerance resource.
        
        Args:
            code: The allergen (drug name, food, substance)
            category: Category (food, medication, environment, biologic)
            allergy_type: Type (allergy vs intolerance)
            clinical_status: Clinical status (active, inactive, resolved)
            verification_status: Verification status (confirmed, unconfirmed)
            criticality: Criticality level (low, high)
            onset: When the allergy was first noted
            reaction_manifestation: What happens during reaction
            reaction_severity: Severity of reaction
            notes: Additional notes
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            recorder_reference: Reference to who recorded
            recorded_date: When this was recorded
            id: Resource ID
            
        Returns:
            FHIR AllergyIntolerance resource
            
        Example:
            # Drug allergy
            paracetamol_allergy = AllergyBuilder.build(
                code="Paracetamol",
                category=AllergyCategory.MEDICATION,
                clinical_status=AllergyClinicalStatus.ACTIVE
            )
            
            # Environmental allergy
            pollen = AllergyBuilder.build(
                code="Pollen allergy",
                category=AllergyCategory.ENVIRONMENT,
                reaction_manifestation="Rhinitis",
                reaction_severity=ReactionSeverity.MILD
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse allergen code
        allergen_code = parse_code_input(code)
        
        # Build clinical status
        clinical_status_concept = AllergyBuilder._create_clinical_status(clinical_status)
        
        # Build verification status
        verification_status_concept = None
        if verification_status:
            verification_status_concept = AllergyBuilder._create_verification_status(verification_status)
        
        # Build category list
        category_list = None
        if category:
            category_list = [category]
        
        # Build reaction
        reactions = None
        if reaction_manifestation or reaction_severity:
            reaction = AllergyIntoleranceReaction()
            
            if reaction_manifestation:
                if isinstance(reaction_manifestation, str):
                    reaction.manifestation = [CodeableConcept(text=reaction_manifestation)]
                else:
                    reaction.manifestation = [parse_code_input(reaction_manifestation)]
            else:
                # Manifestation is required if reaction is present
                reaction.manifestation = [CodeableConcept(text="Unknown")]
            
            if reaction_severity:
                reaction.severity = reaction_severity
            
            reactions = [reaction]
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Create the AllergyIntolerance resource
        allergy = AllergyIntolerance(
            id=resource_id,
            clinicalStatus=clinical_status_concept,
            verificationStatus=verification_status_concept,
            type=allergy_type,
            category=category_list,
            criticality=criticality,
            code=allergen_code,
            patient=subject_reference,
            encounter=encounter_reference,
            onsetDateTime=format_datetime(onset) if onset else None,
            recordedDate=format_datetime(recorded_date) if recorded_date else None,
            reaction=reactions,
            note=note,
        )
        
        return allergy
    
    @staticmethod
    def build_drug_allergy(
        drug_name: CodeInput,
        clinical_status: str = AllergyClinicalStatus.ACTIVE,
        criticality: Optional[str] = None,
        reaction_manifestation: Optional[str] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> AllergyIntolerance:
        """
        Convenience method for building a drug allergy.
        
        Args:
            drug_name: Name of the drug
            clinical_status: Clinical status
            criticality: Criticality level
            reaction_manifestation: What happens during reaction
            notes: Additional notes
            subject_reference: Reference to patient
            id: Resource ID
            
        Returns:
            FHIR AllergyIntolerance for medication
        """
        return AllergyBuilder.build(
            code=drug_name,
            category=AllergyCategory.MEDICATION,
            allergy_type=AllergyType.ALLERGY,
            clinical_status=clinical_status,
            criticality=criticality,
            reaction_manifestation=reaction_manifestation,
            notes=notes,
            subject_reference=subject_reference,
            id=id,
        )
    
    @staticmethod
    def build_food_allergy(
        food: CodeInput,
        clinical_status: str = AllergyClinicalStatus.ACTIVE,
        criticality: Optional[str] = None,
        reaction_manifestation: Optional[str] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> AllergyIntolerance:
        """
        Convenience method for building a food allergy.
        """
        return AllergyBuilder.build(
            code=food,
            category=AllergyCategory.FOOD,
            allergy_type=AllergyType.ALLERGY,
            clinical_status=clinical_status,
            criticality=criticality,
            reaction_manifestation=reaction_manifestation,
            notes=notes,
            subject_reference=subject_reference,
            id=id,
        )


