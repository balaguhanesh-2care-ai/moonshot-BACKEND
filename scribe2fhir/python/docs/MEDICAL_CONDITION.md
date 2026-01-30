---
title: "Medical Condition Element Documentation"
description: "Medical Condition elements represent diseases, disorders, and health problems. The FHIR SDK supports two types: medical history conditions (problem-li"
---
## Overview
Medical Condition elements represent diseases, disorders, and health problems. The FHIR SDK supports two types: medical history conditions (problem-list-item) and encounter diagnoses (encounter-diagnosis).

## Functions

### Medical History Condition
```python
builder.add_medical_condition_history(
    code: CodeInput,
    onset: Optional[DateTimeInput] = None,
    offset: Optional[DateTimeInput] = None,
    clinical_status: Union[ConditionClinicalStatus, str] = "active",
    verification_status: Optional[Union[ConditionVerificationStatus, str]] = None,
    severity: Optional[Union[Severity, str]] = None,
    laterality: Optional[Union[Laterality, str]] = None,
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> Condition
```

### Encounter Diagnosis
```python
builder.add_medical_condition_encountered(
    code: CodeInput,
    onset: Optional[DateTimeInput] = None,
    offset: Optional[DateTimeInput] = None,
    clinical_status: Union[ConditionClinicalStatus, str] = "active",
    verification_status: Optional[Union[ConditionVerificationStatus, str]] = "confirmed",
    severity: Optional[Union[Severity, str]] = None,
    laterality: Optional[Union[Laterality, str]] = None,
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> Condition
```

## Parameters

### Required Parameters
- **code**: The condition name or medical code

### Optional Parameters
- **onset**: When the condition started
- **offset**: When the condition ended (if resolved)
- **clinical_status**: Current status of the condition
- **verification_status**: How certain the diagnosis is
- **severity**: Severity level of the condition
- **laterality**: Body side affected
- **notes**: Additional clinical notes
- **id**: Custom resource ID

## Basic Usage

### Medical History Condition (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, ConditionClinicalStatus
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add condition to medical history
condition = builder.add_medical_condition_history(
    code=create_codeable_concept(
        text="Hypertension",
        code="38341003",
        system="http://snomed.info/sct",
        display="Hypertension"
    ),
    clinical_status=ConditionClinicalStatus.ACTIVE
)
```

### Using String (Alternative)
```python
condition = builder.add_medical_condition_history(
    code="Hypertension",
    clinical_status="active"
)
```

### Encounter Diagnosis
```python
builder.add_encounter()

diagnosis = builder.add_medical_condition_encountered(
    code=create_codeable_concept(
        text="Type 2 diabetes",
        code="44054006", 
        system="http://snomed.info/sct",
        display="Type 2 diabetes mellitus"
    ),
    severity="mild"
)
```

## Clinical Status Options
```python
from fhir_sdk import ConditionClinicalStatus

# Using enum (preferred)
condition = builder.add_medical_condition_history(
    code="Diabetes",
    clinical_status=ConditionClinicalStatus.ACTIVE
)

# Using string (alternative) 
condition = builder.add_medical_condition_history(
    code="Diabetes",
    clinical_status="resolved"
)
```

Available clinical statuses:
- `ConditionClinicalStatus.ACTIVE` or `"active"`
- `ConditionClinicalStatus.INACTIVE` or `"inactive"`
- `ConditionClinicalStatus.RESOLVED` or `"resolved"`
- `ConditionClinicalStatus.RECURRENCE` or `"recurrence"`

## Verification Status Options
```python
from fhir_sdk import ConditionVerificationStatus

condition = builder.add_medical_condition_encountered(
    code="Pneumonia",
    verification_status=ConditionVerificationStatus.CONFIRMED
)
```

Available verification statuses:
- `ConditionVerificationStatus.UNCONFIRMED` or `"unconfirmed"`
- `ConditionVerificationStatus.PROVISIONAL` or `"provisional"`
- `ConditionVerificationStatus.DIFFERENTIAL` or `"differential"`
- `ConditionVerificationStatus.CONFIRMED` or `"confirmed"`
- `ConditionVerificationStatus.REFUTED` or `"refuted"`

## Severity and Laterality
```python
from fhir_sdk import Severity, Laterality

condition = builder.add_medical_condition_history(
    code=create_codeable_concept(
        text="Heart failure",
        code="84114007",
        system="http://snomed.info/sct"
    ),
    severity=Severity.MODERATE,
    laterality=Laterality.LEFT,
    notes="Left-sided heart failure, stable on medication"
)
```

## Time-based Conditions
```python
from datetime import datetime, timedelta

# Chronic condition (ongoing)
condition = builder.add_medical_condition_history(
    code="Hypertension",
    onset=datetime(2020, 1, 1),
    clinical_status="active"
)

# Resolved condition
condition = builder.add_medical_condition_history(
    code="Pneumonia",
    onset=datetime.now() - timedelta(days=14),
    offset=datetime.now() - timedelta(days=7),
    clinical_status="resolved"
)
```

## Common Medical Conditions with SNOMED CT
```python
# Hypertension
code=create_codeable_concept(
    text="Hypertension",
    code="38341003",
    system="http://snomed.info/sct"
)

# Type 2 Diabetes
code=create_codeable_concept(
    text="Type 2 diabetes mellitus",
    code="44054006",
    system="http://snomed.info/sct"
)

# Asthma  
code=create_codeable_concept(
    text="Asthma",
    code="195967001",
    system="http://snomed.info/sct"
)

# Depression
code=create_codeable_concept(
    text="Depression",
    code="35489007", 
    system="http://snomed.info/sct"
)
```

## Difference Between History and Encounter Diagnoses

### Medical History (`add_medical_condition_history`)
- Chronic conditions from patient's past
- Problem list items
- Long-term health issues
- Default verification status: None (not automatically confirmed)

### Encounter Diagnoses (`add_medical_condition_encountered`) 
- Conditions diagnosed during current visit
- Acute problems
- New diagnoses made today
- Default verification status: "confirmed"

## Best Practices
1. Use create_codeable_concept with SNOMED CT codes for interoperability
2. Choose appropriate function based on when condition was diagnosed
3. Set clinical_status accurately (active vs resolved)
4. Include onset dates for chronic conditions
5. Use verification_status to indicate diagnostic certainty
6. Add severity for conditions requiring monitoring
7. Include detailed notes for complex conditions

## Notes
- History conditions appear in problem lists
- Encounter diagnoses are associated with current visit
- Onset/offset dates help track condition progression
- Multiple conditions can be added to represent comorbidities
- Clinical status changes can be tracked over time
