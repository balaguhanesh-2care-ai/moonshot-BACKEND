"""
Symptom Resource Builder - Creates FHIR Observation resources for symptoms.

FHIR Mapping:
- Symptoms are represented as Observation resources
- Category: "survey" (patient-reported symptoms)
- Code: The symptom being reported (e.g., headache, cough)
- Value: Can be text (notes) or coded value
- effectivePeriod/effectiveDateTime: Onset and offset times
- Severity and laterality are captured as extensions or components

Reference: https://www.hl7.org/fhir/observation.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime, date

from fhir.resources.observation import Observation, ObservationComponent
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.period import Period
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..enums import ObservationStatus, Severity, Laterality, FindingStatus
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


class SymptomBuilder:
    """
    Builder for creating FHIR Observation resources representing symptoms.
    
    Symptoms are patient-reported clinical findings that are captured using
    the Observation resource with category 'survey'.
    
    Example:
        builder = SymptomBuilder()
        observation = builder.build(
            code=("25064002", "http://snomed.info/sct", "Headache"),
            onset="2024-01-14T08:00:00Z",
            severity=Severity.MODERATE,
            status=ObservationStatus.FINAL,
            notes="Throbbing pain on right side"
        )
    """
    
    # SNOMED CT codes for symptom-related concepts
    SEVERITY_CODE = "246112005"  # Severity (attribute)
    LATERALITY_CODE = "272741003"  # Laterality (attribute)
    FINDING_CONTEXT_CODE = "408729009"  # Finding context
    
    @staticmethod
    def build(
        code: CodeInput,
        onset: Optional[DateTimeInput] = None,
        offset: Optional[DateTimeInput] = None,
        severity: Optional[Union[Severity, str]] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        notes: Optional[str] = None,
        laterality: Optional[Union[Laterality, str]] = None,
        finding_status: Optional[Union[FindingStatus, str]] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Build a FHIR Observation resource for a symptom.
        
        Args:
            code: The symptom code/name. Can be:
                  - str: Just the symptom name
                  - (code, system, display): Full coded concept
                  - (display, (code, system)): Display with code tuple
                  - CodeableConcept: Already a CodeableConcept
            onset: When the symptom started (datetime)
            offset: When the symptom ended (datetime)
            severity: Severity of the symptom (mild, moderate, severe)
            status: Observation status (default: final)
            notes: Additional notes about the symptom
            laterality: Body side affected (left, right, bilateral)
            finding_status: Whether symptom is present or absent
            subject_reference: Reference to the patient
            encounter_reference: Reference to the encounter
            id: Resource ID (auto-generated if not provided)
            
        Returns:
            FHIR Observation resource
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse the symptom code
        symptom_code = parse_code_input(code)
        
        # Create the category - "survey" for patient-reported symptoms
        category = [
            CodeableConcept(
                coding=[
                    Coding(
                        system=CodingSystem.OBSERVATION_CATEGORY,
                        code="symptom",
                        display="Symptom"
                    )
                ],
                text="symptom"
            )
        ]
        
        # Handle status enum
        obs_status = status.value if isinstance(status, ObservationStatus) else status
        
        # Build effective period or dateTime
        effective = None
        effective_period = None
        if onset or offset:
            if offset:
                # Use period if we have both onset and offset
                effective_period = create_period(onset, offset)
            else:
                effective = format_datetime(onset)
        
        # Build components for severity, laterality, and finding status
        components = []
        
        # Add severity component
        if severity:
            sev = severity if isinstance(severity, Severity) else Severity(severity.lower())
            components.append(
                ObservationComponent(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=CodingSystem.SNOMED_CT,
                                code=SymptomBuilder.SEVERITY_CODE,
                                display="Severity"
                            )
                        ]
                    ),
                    valueCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                system=CodingSystem.SNOMED_CT,
                                code=sev.snomed_code,
                                display=sev.display
                            )
                        ],
                        text=sev.display
                    )
                )
            )
        
        # Add laterality component
        if laterality:
            lat = laterality if isinstance(laterality, Laterality) else Laterality(laterality.lower())
            components.append(
                ObservationComponent(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=CodingSystem.SNOMED_CT,
                                code=SymptomBuilder.LATERALITY_CODE,
                                display="Laterality"
                            )
                        ]
                    ),
                    valueCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                system=CodingSystem.SNOMED_CT,
                                code=lat.snomed_code,
                                display=lat.display
                            )
                        ],
                        text=lat.display
                    )
                )
            )
        
        # Add finding status component (present/absent)
        if finding_status:
            fs = finding_status if isinstance(finding_status, FindingStatus) else FindingStatus(finding_status.lower())
            components.append(
                ObservationComponent(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=CodingSystem.SNOMED_CT,
                                code=SymptomBuilder.FINDING_CONTEXT_CODE,
                                display="Finding context"
                            )
                        ]
                    ),
                    valueCodeableConcept=CodeableConcept(
                        text=fs.value.capitalize()
                    )
                )
            )
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Create the Observation resource
        observation = Observation(
            id=resource_id,
            status=obs_status,
            category=category,
            code=symptom_code,
            subject=subject_reference,
            encounter=encounter_reference,
            effectiveDateTime=effective,
            effectivePeriod=effective_period,
            component=components if components else None,
            note=note,
        )
        
        return observation


