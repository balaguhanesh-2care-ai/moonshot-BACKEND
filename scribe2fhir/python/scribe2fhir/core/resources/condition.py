"""
Condition Resource Builder - Creates FHIR Condition resources for medical conditions.

FHIR Mapping:
- Medical conditions are represented as Condition resources
- Category "problem-list-item": For medical history (chronic conditions, past conditions)
- Category "encounter-diagnosis": For diagnoses made during the current encounter
- clinicalStatus: Current clinical status (active, resolved, etc.)
- verificationStatus: How certain we are about the diagnosis
- severity: How severe the condition is
- bodySite: Where on the body the condition is (includes laterality)

Reference: https://www.hl7.org/fhir/condition.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime, date

from fhir.resources.condition import Condition, ConditionStage
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.period import Period
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..enums import (
    ConditionClinicalStatus,
    ConditionVerificationStatus,
    ConditionCategory,
    Severity,
    Laterality,
)
from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
    create_codeable_concept,
    create_coding,
    create_period,
)


class ConditionBuilder:
    """
    Builder for creating FHIR Condition resources representing medical conditions.
    
    This builder supports two main categories:
    1. Problem List Items - For medical history (chronic/past conditions)
    2. Encounter Diagnoses - For conditions diagnosed during an encounter
    
    Example:
        builder = ConditionBuilder()
        
        # Medical history
        condition = builder.build_history(
            code=("38341003", "http://snomed.info/sct", "Hypertension"),
            onset="2020-01-01",
            clinical_status=ConditionClinicalStatus.ACTIVE,
            severity=Severity.MODERATE,
            notes="Well controlled with medication"
        )
        
        # Encounter diagnosis
        diagnosis = builder.build_encountered(
            code=("73211009", "http://snomed.info/sct", "Diabetes mellitus"),
            clinical_status=ConditionClinicalStatus.ACTIVE,
            severity=Severity.MILD
        )
    """
    
    @staticmethod
    def _build_condition(
        code: CodeInput,
        category: ConditionCategory,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        clinical_status: Union[ConditionClinicalStatus, str] = ConditionClinicalStatus.ACTIVE,
        verification_status: Optional[Union[ConditionVerificationStatus, str]] = None,
        severity: Optional[Union[Severity, str]] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        body_site: Optional[CodeInput] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        recorder_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Condition:
        """
        Internal method to build a FHIR Condition resource.
        
        Args:
            code: The condition code/name
            category: Category (problem-list-item or encounter-diagnosis)
            onset: When the condition started
            offset: When the condition ended/resolved (abatement)
            clinical_status: Current clinical status
            verification_status: How certain the diagnosis is
            severity: Severity of the condition
            laterality: Body side affected
            body_site: Body site where condition manifests
            notes: Additional notes
            subject_reference: Reference to the patient
            encounter_reference: Reference to the encounter
            recorder_reference: Reference to who recorded this
            id: Resource ID
            
        Returns:
            FHIR Condition resource
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse the condition code
        condition_code = parse_code_input(code)
        
        # Build category
        category_coding = category.value if isinstance(category, ConditionCategory) else category
        category_concept = CodeableConcept(
            coding=[
                Coding(
                    system=CodingSystem.CONDITION_CATEGORY,
                    code=category_coding,
                    display=category_coding.replace("-", " ").title()
                )
            ]
        )
        
        # Build clinical status
        status_value = clinical_status.value if isinstance(clinical_status, ConditionClinicalStatus) else clinical_status
        clinical_status_concept = CodeableConcept(
            coding=[
                Coding(
                    system=CodingSystem.CONDITION_CLINICAL,
                    code=status_value,
                    display=status_value.capitalize()
                )
            ]
        )
        
        # Build verification status (optional)
        verification_status_concept = None
        if verification_status:
            ver_value = verification_status.value if isinstance(verification_status, ConditionVerificationStatus) else verification_status
            verification_status_concept = CodeableConcept(
                coding=[
                    Coding(
                        system=CodingSystem.CONDITION_VERIFICATION,
                        code=ver_value,
                        display=ver_value.capitalize()
                    )
                ]
            )
        
        # Build severity (optional)
        severity_concept = None
        if severity:
            sev = severity if isinstance(severity, Severity) else Severity(severity.lower())
            severity_concept = CodeableConcept(
                coding=[
                    Coding(
                        system=CodingSystem.SNOMED_CT,
                        code=sev.snomed_code,
                        display=sev.display
                    )
                ],
                text=sev.display
            )
        
        # Build body site with laterality (optional)
        body_site_list = None
        if body_site or laterality:
            body_site_codings = []
            
            # Add body site coding if provided
            if body_site:
                body_site_concept = parse_code_input(body_site)
                if body_site_concept.coding:
                    body_site_codings.extend(body_site_concept.coding)
            
            # Add laterality as a qualifier
            if laterality:
                lat = laterality if isinstance(laterality, Laterality) else Laterality(laterality.lower())
                body_site_codings.append(
                    Coding(
                        system=CodingSystem.SNOMED_CT,
                        code=lat.snomed_code,
                        display=lat.display
                    )
                )
            
            if body_site_codings:
                # Create text description
                text_parts = []
                if body_site and isinstance(body_site, str):
                    text_parts.append(body_site)
                if laterality:
                    lat = laterality if isinstance(laterality, Laterality) else Laterality(laterality.lower())
                    text_parts.append(lat.display)
                
                body_site_list = [
                    CodeableConcept(
                        coding=body_site_codings,
                        text=" - ".join(text_parts) if text_parts else None
                    )
                ]
        
        # Build onset
        onset_datetime = None
        onset_period = None
        if onset:
            if offset:
                onset_period = create_period(onset, offset)
            else:
                onset_datetime = format_datetime(onset)
        
        # Build abatement (offset/resolution)
        abatement_datetime = None
        if offset and not onset:
            abatement_datetime = format_datetime(offset)
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Create the Condition resource
        condition = Condition(
            id=resource_id,
            clinicalStatus=clinical_status_concept,
            verificationStatus=verification_status_concept,
            category=[category_concept],
            severity=severity_concept,
            code=condition_code,
            bodySite=body_site_list,
            subject=subject_reference,
            encounter=encounter_reference,
            onsetDateTime=onset_datetime,
            onsetPeriod=onset_period,
            abatementDateTime=abatement_datetime,

            note=note,
        )
        
        return condition
    
    @staticmethod
    def build_history(
        code: CodeInput,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        clinical_status: Union[ConditionClinicalStatus, str] = ConditionClinicalStatus.ACTIVE,
        verification_status: Optional[Union[ConditionVerificationStatus, str]] = None,
        severity: Optional[Union[Severity, str]] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        body_site: Optional[CodeInput] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        recorder_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Condition:
        """
        Build a FHIR Condition resource for medical history (problem-list-item).
        
        Use this for:
        - Chronic conditions (hypertension, diabetes, etc.)
        - Past medical history
        - Ongoing health problems
        
        Args:
            code: The condition code/name
            onset: When the condition started
            offset: When the condition ended/resolved
            clinical_status: Current status (active, resolved, etc.)
            verification_status: How certain the diagnosis is
            severity: Severity (mild, moderate, severe)
            laterality: Body side affected (left, right, bilateral)
            body_site: Body site where condition manifests
            notes: Additional clinical notes
            subject_reference: Reference to the patient
            encounter_reference: Reference to the encounter
            recorder_reference: Reference to who recorded this
            id: Resource ID
            
        Returns:
            FHIR Condition resource with category "problem-list-item"
        """
        return ConditionBuilder._build_condition(
            code=code,
            category=ConditionCategory.PROBLEM_LIST_ITEM,
            onset=onset,
            offset=offset,
            clinical_status=clinical_status,
            verification_status=verification_status,
            severity=severity,
            laterality=laterality,
            body_site=body_site,
            notes=notes,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            recorder_reference=recorder_reference,
            id=id,
        )
    
    @staticmethod
    def build_encountered(
        code: CodeInput,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        clinical_status: Union[ConditionClinicalStatus, str] = ConditionClinicalStatus.ACTIVE,
        verification_status: Optional[Union[ConditionVerificationStatus, str]] = ConditionVerificationStatus.CONFIRMED,
        severity: Optional[Union[Severity, str]] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        body_site: Optional[CodeInput] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        recorder_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Condition:
        """
        Build a FHIR Condition resource for encounter diagnosis.
        
        Use this for:
        - Diagnoses made during the current encounter
        - New conditions identified today
        - Working diagnoses
        
        Args:
            code: The condition code/name
            onset: When the condition started
            offset: When the condition ended/resolved
            clinical_status: Current status (usually active for new diagnoses)
            verification_status: How certain the diagnosis is (default: confirmed)
            severity: Severity (mild, moderate, severe)
            laterality: Body side affected (left, right, bilateral)
            body_site: Body site where condition manifests
            notes: Additional clinical notes
            subject_reference: Reference to the patient
            encounter_reference: Reference to the encounter
            recorder_reference: Reference to who recorded this
            id: Resource ID
            
        Returns:
            FHIR Condition resource with category "encounter-diagnosis"
        """
        return ConditionBuilder._build_condition(
            code=code,
            category=ConditionCategory.ENCOUNTER_DIAGNOSIS,
            onset=onset,
            offset=offset,
            clinical_status=clinical_status,
            verification_status=verification_status,
            severity=severity,
            laterality=laterality,
            body_site=body_site,
            notes=notes,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            recorder_reference=recorder_reference,
            id=id,
        )


