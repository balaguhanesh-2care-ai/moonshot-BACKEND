"""
Observation Resource Builder - Creates FHIR Observation resources for various findings.

FHIR Mapping:
- Observations represent measurements, assessments, and findings
- Categories define the type of observation:
  - vital-signs: Blood pressure, heart rate, temperature, etc.
  - laboratory: Lab test results
  - exam: Physical examination findings
  - survey: Patient-reported symptoms (handled in symptom.py)
  - social-history: Lifestyle factors, habits

Reference: https://www.hl7.org/fhir/observation.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.observation import Observation, ObservationComponent
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..enums import ObservationStatus, Interpretation
from ..types import (
    CodeInput,
    DateTimeInput,
    QuantityInput,
    CodingSystem,
    parse_code_input,
    parse_quantity_input,
    format_datetime,
    create_quantity,
)


class ObservationCategory:
    """Standard observation categories."""
    VITAL_SIGNS = ("vital-signs", "Vital Signs")
    LABORATORY = ("laboratory", "Laboratory")
    EXAM = ("exam", "Exam")
    SURVEY = ("survey", "Survey")
    SOCIAL_HISTORY = ("social-history", "Social History")
    IMAGING = ("imaging", "Imaging")
    PROCEDURE = ("procedure", "Procedure")
    ACTIVITY = ("activity", "Activity")


class VitalSignCodes:
    """Common vital sign LOINC codes."""
    BLOOD_PRESSURE = ("85354-9", "Blood pressure panel")
    SYSTOLIC_BP = ("8480-6", "Systolic blood pressure")
    DIASTOLIC_BP = ("8462-4", "Diastolic blood pressure")
    HEART_RATE = ("8867-4", "Heart rate")
    RESPIRATORY_RATE = ("9279-1", "Respiratory rate")
    BODY_TEMPERATURE = ("8310-5", "Body temperature")
    BODY_HEIGHT = ("8302-2", "Body height")
    BODY_WEIGHT = ("29463-7", "Body weight")
    BMI = ("39156-5", "Body mass index")
    OXYGEN_SATURATION = ("2708-6", "Oxygen saturation")
    HEAD_CIRCUMFERENCE = ("9843-4", "Head circumference")


class ObservationBuilder:
    """
    Builder for creating FHIR Observation resources.
    
    Supports various observation types including:
    - Vital signs (blood pressure, heart rate, etc.)
    - Laboratory findings
    - Examination findings
    - Social history (lifestyle factors)
    
    Example:
        # Vital sign
        bp = ObservationBuilder.build_vital(
            code=("Blood Pressure", ("85354-9", "http://loinc.org")),
            value="120/80",
            unit="mmHg",
            interpretation=Interpretation.NORMAL
        )
        
        # Lab finding
        hb = ObservationBuilder.build_lab(
            code="Hemoglobin",
            value=12.5,
            unit="g/dL",
            interpretation=Interpretation.NORMAL
        )
    """
    
    OBSERVATION_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/observation-category"
    INTERPRETATION_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"
    
    @staticmethod
    def _create_category(category: tuple) -> CodeableConcept:
        """Create a category CodeableConcept."""
        code, display = category
        return CodeableConcept(
            coding=[
                Coding(
                    system=ObservationBuilder.OBSERVATION_CATEGORY_SYSTEM,
                    code=code,
                    display=display
                )
            ]
        )
    
    @staticmethod
    def _create_interpretation(
        interpretation: Union[Interpretation, str]
    ) -> CodeableConcept:
        """Create an interpretation CodeableConcept."""
        if isinstance(interpretation, Interpretation):
            code = interpretation.value
            display = interpretation.display
        else:
            # Map common strings
            interp_map = {
                "normal": Interpretation.NORMAL,
                "abnormal": Interpretation.ABNORMAL,
                "low": Interpretation.LOW,
                "high": Interpretation.HIGH,
                "critical low": Interpretation.CRITICAL_LOW,
                "critical high": Interpretation.CRITICAL_HIGH,
                "positive": Interpretation.POSITIVE,
                "negative": Interpretation.NEGATIVE,
            }
            if interpretation.lower() in interp_map:
                interp = interp_map[interpretation.lower()]
                code = interp.value
                display = interp.display
            else:
                code = interpretation
                display = interpretation
        
        return CodeableConcept(
            coding=[
                Coding(
                    system=ObservationBuilder.INTERPRETATION_SYSTEM,
                    code=code,
                    display=display
                )
            ],
            text=display
        )
    
    @staticmethod
    def _build_observation(
        code: CodeInput,
        category: tuple,
        value: Optional[Union[str, float, bool, Quantity, CodeableConcept]] = None,
        unit: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        interpretation: Optional[Union[Interpretation, str]] = None,
        notes: Optional[str] = None,
        components: Optional[List[ObservationComponent]] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        performer_references: Optional[List[Reference]] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Internal method to build an Observation resource.
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse code
        observation_code = parse_code_input(code)
        
        # Handle status
        obs_status = status.value if isinstance(status, ObservationStatus) else status
        
        # Build category
        category_concept = ObservationBuilder._create_category(category)
        
        # Build value
        value_quantity = None
        value_string = None
        value_boolean = None
        value_codeable = None
        
        if value is not None:
            if isinstance(value, Quantity):
                value_quantity = value
            elif isinstance(value, CodeableConcept):
                value_codeable = value
            elif isinstance(value, bool):
                value_boolean = value
            elif isinstance(value, (int, float)) and unit:
                value_quantity = create_quantity(float(value), unit)
            else:
                value_string = str(value)
        
        # Build interpretation
        interpretation_concept = None
        if interpretation:
            interpretation_concept = [ObservationBuilder._create_interpretation(interpretation)]
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Create the Observation resource
        observation = Observation(
            id=resource_id,
            status=obs_status,
            category=[category_concept],
            code=observation_code,
            subject=subject_reference,
            encounter=encounter_reference,
            performer=performer_references,
            effectiveDateTime=format_datetime(date) if date else None,
            valueQuantity=value_quantity,
            valueString=value_string,
            valueBoolean=value_boolean,
            valueCodeableConcept=value_codeable,
            interpretation=interpretation_concept,
            component=components,
            note=note,
        )
        
        return observation
    
    @staticmethod
    def build_vital(
        code: CodeInput,
        value: Optional[Union[str, float, Quantity]] = None,
        unit: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        interpretation: Optional[Union[Interpretation, str]] = None,
        notes: Optional[str] = None,
        components: Optional[List[ObservationComponent]] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Build a vital signs Observation.
        
        Args:
            code: The vital sign type (e.g., "Blood Pressure", LOINC code)
            value: The measured value
            unit: Unit of measurement (e.g., "mmHg", "bpm")
            date: When the measurement was taken
            status: Observation status
            interpretation: Interpretation (normal, high, low, etc.)
            notes: Additional notes
            components: For compound vitals like BP (systolic/diastolic)
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            id: Resource ID
            
        Returns:
            FHIR Observation with vital-signs category
            
        Example:
            # Simple vital
            heart_rate = ObservationBuilder.build_vital(
                code="Heart Rate",
                value=72,
                unit="bpm",
                interpretation=Interpretation.NORMAL
            )
            
            # Blood pressure with components
            bp = ObservationBuilder.build_vital(
                code=("Blood Pressure", ("85354-9", "http://loinc.org")),
                value="120/80",
                unit="mmHg",
                components=[
                    ObservationComponent(
                        code=CodeableConcept(text="Systolic"),
                        valueQuantity=Quantity(value=120, unit="mmHg")
                    ),
                    ObservationComponent(
                        code=CodeableConcept(text="Diastolic"),
                        valueQuantity=Quantity(value=80, unit="mmHg")
                    )
                ]
            )
        """
        return ObservationBuilder._build_observation(
            code=code,
            category=ObservationCategory.VITAL_SIGNS,
            value=value,
            unit=unit,
            date=date,
            status=status,
            interpretation=interpretation,
            notes=notes,
            components=components,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            id=id,
        )
    
    @staticmethod
    def build_lab(
        code: CodeInput,
        value: Optional[Union[str, float, Quantity]] = None,
        unit: Optional[str] = None,
        date: Optional[DateTimeInput] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        interpretation: Optional[Union[Interpretation, str]] = None,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        performer_references: Optional[List[Reference]] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Build a laboratory Observation.
        
        Args:
            code: The lab test name/code
            value: The result value
            unit: Unit of measurement
            date: When the test was performed
            status: Observation status
            interpretation: Result interpretation
            notes: Additional notes
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            performer_references: References to lab/technician
            id: Resource ID
            
        Returns:
            FHIR Observation with laboratory category
            
        Example:
            hemoglobin = ObservationBuilder.build_lab(
                code="Hemoglobin",
                value=12.5,
                unit="g/dL",
                interpretation=Interpretation.NORMAL,
                notes="Within normal range"
            )
        """
        return ObservationBuilder._build_observation(
            code=code,
            category=ObservationCategory.LABORATORY,
            value=value,
            unit=unit,
            date=date,
            status=status,
            interpretation=interpretation,
            notes=notes,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            performer_references=performer_references,
            id=id,
        )
    
    @staticmethod
    def build_exam(
        code: CodeInput,
        value: Optional[Union[str, CodeableConcept]] = None,
        date: Optional[DateTimeInput] = None,
        status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        performer_references: Optional[List[Reference]] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Build an examination finding Observation.
        
        Args:
            code: The examination type (e.g., "Abdominal examination")
            value: Finding value (usually text description)
            date: When the examination was performed
            status: Observation status
            notes: Additional findings/notes
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            performer_references: References to examiner
            id: Resource ID
            
        Returns:
            FHIR Observation with exam category
            
        Example:
            exam = ObservationBuilder.build_exam(
                code="Hand examination",
                value="Swollen",
                notes="Mild swelling observed in right hand"
            )
        """
        return ObservationBuilder._build_observation(
            code=code,
            category=ObservationCategory.EXAM,
            value=value,
            date=date,
            status=status,
            notes=notes,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            performer_references=performer_references,
            id=id,
        )
    
    @staticmethod
    def build_social_history(
        code: CodeInput,
        value: Optional[Union[str, CodeableConcept]] = None,
        status_value: Optional[str] = None,  # Active, Inactive, etc.
        date: Optional[DateTimeInput] = None,
        observation_status: Union[ObservationStatus, str] = ObservationStatus.FINAL,
        notes: Optional[str] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Observation:
        """
        Build a social history Observation (lifestyle factors).
        
        Use this for lifestyle habits like smoking, drinking, diet, exercise, etc.
        
        Args:
            code: The lifestyle factor (e.g., "Smoking", "Alcohol use")
            value: Details about the factor
            status_value: Active/Inactive status of the habit
            date: When this was recorded
            observation_status: FHIR observation status
            notes: Additional notes
            subject_reference: Reference to patient
            encounter_reference: Reference to encounter
            id: Resource ID
            
        Returns:
            FHIR Observation with social-history category
            
        Example:
            smoking = ObservationBuilder.build_social_history(
                code="Smoking",
                status_value="Active",
                notes="10 cigarettes per day for 5 years"
            )
        """
        # Build value - combine status and any additional value
        observation_value = value
        if status_value and not value:
            observation_value = status_value
        elif status_value and value:
            observation_value = f"{status_value}: {value}"
        
        return ObservationBuilder._build_observation(
            code=code,
            category=ObservationCategory.SOCIAL_HISTORY,
            value=observation_value,
            date=date,
            status=observation_status,
            notes=notes,
            subject_reference=subject_reference,
            encounter_reference=encounter_reference,
            id=id,
        )


