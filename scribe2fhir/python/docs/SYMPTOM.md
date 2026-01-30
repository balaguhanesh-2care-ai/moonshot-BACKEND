---
title: "Symptom Element Documentation" 
description: "The Symptom element represents patient-reported symptoms and chief complaints. Symptoms are recorded as FHIR Observations with category survey to distinguish them from clinical findings."
---
## Overview
The Symptom element represents patient-reported symptoms and chief complaints. Symptoms are recorded as FHIR Observations with category "survey" to distinguish them from clinical findings.

## Function
```python
builder.add_symptom(
    code: CodeInput,
    onset: Optional[DateTimeInput] = None,
    offset: Optional[DateTimeInput] = None,
    severity: Optional[Union[Severity, str]] = None,
    status: Union[ObservationStatus, str] = "final",
    notes: Optional[str] = None,
    laterality: Optional[Union[Laterality, str]] = None,
    finding_status: Optional[Union[FindingStatus, str]] = None,
    id: Optional[str] = None,
) -> Observation
```

## Parameters

### Required Parameters
- **code**: The symptom name or code

### Optional Parameters
- **onset**: When the symptom started
- **offset**: When the symptom ended (if resolved)
- **severity**: How severe the symptom is (mild, moderate, severe)
- **status**: Observation status (default: "final")
- **notes**: Additional details about the symptom
- **laterality**: Body side affected (left, right, bilateral)
- **finding_status**: Whether symptom is present or absent
- **id**: Custom resource ID

## Basic Usage

### Simple Symptom
```python
from fhir_sdk import FHIRDocumentBuilder

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add basic symptom
symptom = builder.add_symptom(code="Headache")
```

### Using CodeableConcept (Preferred)
```python
from fhir_sdk.types import create_codeable_concept

symptom = builder.add_symptom(
    code=create_codeable_concept(
        text="Headache",
        code="25064002",
        system="http://snomed.info/sct",
        display="Headache"
    )
)
```

### Using String (Alternative)
```python
symptom = builder.add_symptom(code="Headache")
```

### Comprehensive Symptom
```python
from fhir_sdk import Severity, Laterality, FindingStatus
from datetime import datetime, timedelta

symptom = builder.add_symptom(
    code=create_codeable_concept(
        text="Chest pain",
        code="29857009",
        system="http://snomed.info/sct",
        display="Chest pain"
    ),
    onset=datetime.now() - timedelta(hours=2),
    severity=Severity.MODERATE,
    laterality=Laterality.LEFT,
    finding_status=FindingStatus.PRESENT,
    notes="Sharp pain, worse with deep breathing"
)
```

## Severity Levels
```python
from fhir_sdk import Severity

# Using enum (preferred)
symptom = builder.add_symptom(
    code="Pain",
    severity=Severity.MILD
)

# Using string (alternative)
symptom = builder.add_symptom(
    code="Pain", 
    severity="moderate"
)
```

Available severity levels:
- `Severity.MILD` or `"mild"`
- `Severity.MODERATE` or `"moderate"`
- `Severity.SEVERE` or `"severe"`

## Laterality Options
```python
from fhir_sdk import Laterality

# Using enum (preferred)
symptom = builder.add_symptom(
    code="Knee pain",
    laterality=Laterality.RIGHT
)
```

Available laterality options:
- `Laterality.LEFT` or `"left"`
- `Laterality.RIGHT` or `"right"`
- `Laterality.BILATERAL` or `"bilateral"`

## Finding Status
```python
from fhir_sdk import FindingStatus

# Positive finding (symptom present)
symptom = builder.add_symptom(
    code="Nausea",
    finding_status=FindingStatus.PRESENT
)

# Negative finding (symptom absent)
symptom = builder.add_symptom(
    code="Chest pain",
    finding_status=FindingStatus.ABSENT
)
```

## Time-based Symptoms
```python
from datetime import datetime, timedelta

# Ongoing symptom (onset only)
symptom = builder.add_symptom(
    code="Fatigue",
    onset=datetime.now() - timedelta(days=3)
)

# Resolved symptom (onset and offset)
symptom = builder.add_symptom(
    code="Fever",
    onset=datetime.now() - timedelta(days=2),
    offset=datetime.now() - timedelta(hours=6)
)
```

## Common Symptoms
Use create_codeable_concept with SNOMED CT codes for better interoperability:

```python
# Headache
code=create_codeable_concept(
    text="Headache",
    code="25064002", 
    system="http://snomed.info/sct"
)

# Chest pain
code=create_codeable_concept(
    text="Chest pain",
    code="29857009",
    system="http://snomed.info/sct"
)

# Nausea
code=create_codeable_concept(
    text="Nausea", 
    code="422587007",
    system="http://snomed.info/sct"
)
```

## Best Practices
1. Always use create_codeable_concept with SNOMED CT codes when available
2. Include onset time for symptom progression tracking
3. Use severity levels for triage and monitoring
4. Record negative findings (absent symptoms) for completeness
5. Add detailed notes for complex or unusual symptoms
6. Use laterality for body-part-specific symptoms

## Notes
- Symptoms are categorized as "survey" observations (patient-reported)
- Multiple symptoms can be added for comprehensive chief complaints
- Onset/offset creates effective periods for symptom duration
- Finding status helps distinguish between present and ruled-out symptoms
