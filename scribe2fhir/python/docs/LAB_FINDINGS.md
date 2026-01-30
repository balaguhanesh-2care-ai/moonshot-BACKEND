---
title: "Lab Findings Element Documentation"
description: "Lab Findings elements represent laboratory test results and their interpretations. These are clinical observations obtained through laboratory analysi"
---
## Overview
Lab Findings elements represent laboratory test results and their interpretations. These are clinical observations obtained through laboratory analysis of specimens.

## Function
```python
builder.add_lab_finding(
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
- **code**: The lab test name or code

### Optional Parameters
- **value**: The test result value (numeric or string)
- **unit**: Unit of measurement (e.g., "mg/dL", "mmol/L", "%")
- **date**: When the test was performed
- **interpretation**: Clinical interpretation of the result
- **notes**: Additional notes about the test or result
- **id**: Custom resource ID

## Basic Usage

### Simple Lab Result (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, Interpretation
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add lab result
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Hemoglobin",
        code="718-7",
        system="http://loinc.org",
        display="Hemoglobin [Mass/volume] in Blood"
    ),
    value=14.2,
    unit="g/dL",
    interpretation=Interpretation.NORMAL
)
```

### Using String (Alternative)
```python
lab = builder.add_lab_finding(
    code="Hemoglobin",
    value=14.2,
    unit="g/dL",
    interpretation="normal"
)
```

### Qualitative Result
```python
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Glucose, Urine",
        code="25428-4",
        system="http://loinc.org"
    ),
    value="Negative",
    interpretation=Interpretation.NORMAL
)
```

## Common Lab Tests with LOINC Codes

### Complete Blood Count (CBC)
```python
# Hemoglobin
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Hemoglobin",
        code="718-7",
        system="http://loinc.org"
    ),
    value=13.5,
    unit="g/dL"
)

# White Blood Cell Count
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="White Blood Cell Count",
        code="6690-2", 
        system="http://loinc.org"
    ),
    value=7200,
    unit="cells/μL"
)

# Platelet Count
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Platelet Count",
        code="777-3",
        system="http://loinc.org"
    ),
    value=250000,
    unit="platelets/μL"
)
```

### Basic Metabolic Panel
```python
# Glucose
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Glucose",
        code="2345-7",
        system="http://loinc.org"
    ),
    value=95,
    unit="mg/dL",
    interpretation=Interpretation.NORMAL
)

# Creatinine
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Creatinine", 
        code="2160-0",
        system="http://loinc.org"
    ),
    value=1.0,
    unit="mg/dL"
)

# Sodium
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Sodium",
        code="2951-2",
        system="http://loinc.org"
    ),
    value=140,
    unit="mmol/L"
)
```

### Lipid Panel
```python
# Total Cholesterol
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="Total Cholesterol",
        code="2093-3",
        system="http://loinc.org"
    ),
    value=180,
    unit="mg/dL",
    interpretation=Interpretation.NORMAL
)

# HDL Cholesterol
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="HDL Cholesterol",
        code="2085-9",
        system="http://loinc.org"
    ),
    value=55,
    unit="mg/dL"
)

# LDL Cholesterol  
lab = builder.add_lab_finding(
    code=create_codeable_concept(
        text="LDL Cholesterol",
        code="18262-6",
        system="http://loinc.org"
    ),
    value=110,
    unit="mg/dL"
)
```

## Interpretation with Different Result Types

### Numeric Results with Reference Ranges
```python
lab = builder.add_lab_finding(
    code="Creatinine",
    value=1.8,
    unit="mg/dL", 
    interpretation=Interpretation.HIGH,
    notes="Above normal range (0.6-1.2 mg/dL)"
)
```

### Qualitative Results
```python
# Negative result
lab = builder.add_lab_finding(
    code="Urine Protein",
    value="Negative",
    interpretation=Interpretation.NORMAL
)

# Positive result
lab = builder.add_lab_finding(
    code="Strep A Rapid Test",
    value="Positive", 
    interpretation=Interpretation.ABNORMAL
)
```

### Results with Interpretation Only
```python
# When exact value is not recorded
lab = builder.add_lab_finding(
    code="Liver Function Tests",
    interpretation=Interpretation.NORMAL,
    notes="All values within normal limits"
)
```

## Time-stamped Results
```python
from datetime import datetime, timedelta

# Test performed yesterday
lab = builder.add_lab_finding(
    code="Fasting Glucose",
    value=92,
    unit="mg/dL",
    date=datetime.now() - timedelta(days=1),
    notes="Fasting for 12 hours confirmed"
)
```

## Common Lab Units
- **Blood Chemistry**: "mg/dL", "mmol/L", "mEq/L"
- **Hematology**: "g/dL", "cells/μL", "%", "fL"
- **Lipids**: "mg/dL", "mmol/L"
- **Proteins**: "g/dL", "mg/dL"
- **Enzymes**: "U/L", "IU/L"
- **Hormones**: "ng/mL", "μg/dL", "mIU/mL"

## Special Lab Result Types

### Microbiology Results
```python
lab = builder.add_lab_finding(
    code="Blood Culture",
    value="No growth after 5 days",
    interpretation=Interpretation.NORMAL
)
```

### Pathology Results
```python
lab = builder.add_lab_finding(
    code="Tissue Biopsy",
    value="Benign epithelial tissue",
    notes="No evidence of malignancy"
)
```

### Molecular/Genetic Tests
```python
lab = builder.add_lab_finding(
    code="COVID-19 PCR",
    value="Not Detected",
    interpretation=Interpretation.NORMAL
)
```

## Best Practices
1. Use create_codeable_concept with LOINC codes for standardized lab tests
2. Include appropriate units for all numeric results
3. Add interpretation to highlight abnormal values
4. Record collection/testing date for result validity
5. Include notes for specimen quality or testing conditions
6. Use consistent units within test panels
7. Record "unable to obtain" or "insufficient sample" when applicable

## Notes
- Lab findings are categorized as "laboratory" observations
- Values can be numeric (with units) or string (for qualitative results)
- Interpretation helps clinicians identify critical values
- Date stamps are crucial for trending lab values over time
- Multiple lab results can be grouped logically (e.g., CBC panel, BMP panel)
