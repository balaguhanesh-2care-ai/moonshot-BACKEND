---
title: "Vital Signs Element Documentation"
description: "Vital Signs elements represent measured physiological parameters like blood pressure, heart rate, temperature, and other clinical measurements taken d"
---
## Overview
Vital Signs elements represent measured physiological parameters like blood pressure, heart rate, temperature, and other clinical measurements taken during patient care.

## Function
```python
builder.add_vital_finding(
    code: CodeInput,
    value: Optional[Union[str, float]] = None,
    unit: Optional[str] = None,
    date: Optional[DateTimeInput] = None,
    interpretation: Optional[Union[Interpretation, str]] = None,
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> Observation
```

## Parameters

### Required Parameters
- **code**: The vital sign type or measurement name

### Optional Parameters
- **value**: The measured value (numeric or string)
- **unit**: Unit of measurement (e.g., "mmHg", "bpm", "°C")
- **date**: When the measurement was taken
- **interpretation**: Clinical interpretation of the result
- **notes**: Additional notes about the measurement
- **id**: Custom resource ID

## Basic Usage

### Simple Vital Sign (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add blood pressure measurement
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Blood Pressure",
        code="85354007",
        system="http://snomed.info/sct",
        display="Blood pressure"
    ),
    value="120/80",
    unit="mmHg"
)
```

### Using String (Alternative)
```python
vital = builder.add_vital_finding(
    code="Blood Pressure",
    value="120/80",
    unit="mmHg"
)
```

### Numeric Value with Interpretation
```python
from fhir_sdk import Interpretation

vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Heart Rate",
        code="364075005",
        system="http://snomed.info/sct"
    ),
    value=72,
    unit="bpm",
    interpretation=Interpretation.NORMAL
)
```

## Interpretation Options
```python
from fhir_sdk import Interpretation

# Using enum (preferred)
vital = builder.add_vital_finding(
    code="Temperature",
    value=38.5,
    unit="°C",
    interpretation=Interpretation.HIGH
)

# Using string (alternative)
vital = builder.add_vital_finding(
    code="Temperature", 
    value=36.7,
    unit="°C",
    interpretation="normal"
)
```

Available interpretations:
- `Interpretation.NORMAL` or `"normal"`
- `Interpretation.HIGH` or `"high"`
- `Interpretation.LOW` or `"low"`
- `Interpretation.ABNORMAL` or `"abnormal"`

## Common Vital Signs with LOINC Codes

### Blood Pressure
```python
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Blood Pressure",
        code="85354007", 
        system="http://snomed.info/sct",
        display="Blood pressure"
    ),
    value="120/80",
    unit="mmHg",
    interpretation=Interpretation.NORMAL
)
```

### Heart Rate
```python
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Heart Rate",
        code="8867-4",
        system="http://loinc.org",
        display="Heart rate"
    ),
    value=75,
    unit="bpm"
)
```

### Body Temperature
```python
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Body Temperature",
        code="8310-5",
        system="http://loinc.org",
        display="Body temperature"
    ),
    value=98.6,
    unit="°F"
)
```

### Respiratory Rate
```python
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Respiratory Rate",
        code="9279-1",
        system="http://loinc.org"
    ),
    value=16,
    unit="breaths/min"
)
```

### Body Weight
```python
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Body Weight",
        code="29463-7",
        system="http://loinc.org"
    ),
    value=70,
    unit="kg"
)
```

### Height
```python
vital = builder.add_vital_finding(
    code=create_codeable_concept(
        text="Body Height",
        code="8302-2",
        system="http://loinc.org"
    ),
    value=175,
    unit="cm"
)
```

## Value Types and Units

### Numeric Values
```python
# Integer values
vital = builder.add_vital_finding(code="Heart Rate", value=72, unit="bpm")

# Decimal values  
vital = builder.add_vital_finding(code="Temperature", value=98.6, unit="°F")
```

### String Values
```python
# Compound measurements
vital = builder.add_vital_finding(code="Blood Pressure", value="120/80", unit="mmHg")

# Qualitative results
vital = builder.add_vital_finding(code="Pain Scale", value="5/10")
```

## Time-stamped Measurements
```python
from datetime import datetime

vital = builder.add_vital_finding(
    code="Blood Pressure",
    value="130/85", 
    unit="mmHg",
    date=datetime.now(),
    notes="Taken after 5 minutes rest"
)
```

## Measurements Without Values
```python
# For measurements that couldn't be taken
vital = builder.add_vital_finding(
    code="Weight",
    notes="Unable to obtain - patient unable to stand"
)
```

## Common Units
- **Blood Pressure**: "mmHg"
- **Heart Rate**: "bpm" (beats per minute)  
- **Temperature**: "°C", "°F"
- **Weight**: "kg", "lb"
- **Height**: "cm", "in"
- **Respiratory Rate**: "breaths/min"
- **Oxygen Saturation**: "%"

## Best Practices
1. Use create_codeable_concept with LOINC codes for vital signs when available
2. Include appropriate units for all numeric measurements
3. Add interpretation for values outside normal ranges
4. Record measurement time for trend analysis
5. Include notes for unusual circumstances or measurement conditions
6. Use consistent units within your application
7. Record "unable to obtain" measurements with explanatory notes

## Notes
- Vital signs are categorized as "vital-signs" observations
- Values can be numeric (with units) or string (for complex measurements)
- Interpretation helps identify abnormal values quickly
- Multiple measurements can track trends over time
- Date/time stamps are important for monitoring changes
