---
title: "Lab Test Ordering Element Documentation"
description: "Lab Test Ordering elements represent laboratory tests that have been ordered for the patient. These create FHIR ServiceRequest resources for diagnosti"
---
## Overview
Lab Test Ordering elements represent laboratory tests that have been ordered for the patient. These create FHIR ServiceRequest resources for diagnostic testing and specimen collection.

## Function
```python
builder.add_test_prescribed(
    code: CodeInput,
    date: Optional[DateTimeInput] = None,
    notes: Optional[str] = None,
    priority: Optional[str] = None,
    reason: Optional[CodeInput] = None,
    id: Optional[str] = None,
) -> ServiceRequest
```

## Parameters

### Required Parameters
- **code**: The lab test name or code

### Optional Parameters
- **date**: When the test should be performed
- **notes**: Special instructions or requirements
- **priority**: Test priority level
- **reason**: Clinical reason for ordering the test
- **id**: Custom resource ID

## Basic Usage

### Simple Lab Test Order (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Order lab test
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Complete Blood Count",
        code="26604007",
        system="http://snomed.info/sct",
        display="Complete blood count"
    )
)
```

### Using String (Alternative)
```python
test_order = builder.add_test_prescribed(
    code="Complete Blood Count"
)
```

### With Priority and Instructions
```python
from datetime import datetime, timedelta

test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Fasting Blood Glucose",
        code="2345-7",
        system="http://loinc.org"
    ),
    date=datetime.now() + timedelta(days=1),
    priority="routine",
    notes="Patient should fast for 12 hours before test"
)
```

## Priority Levels
```python
# STAT (immediate)
test_order = builder.add_test_prescribed(
    code="Cardiac Enzymes",
    priority="stat",
    notes="Suspected MI - process immediately"
)

# Urgent (within hours)
test_order = builder.add_test_prescribed(
    code="Blood Culture",
    priority="urgent",
    reason="Suspected sepsis"
)

# ASAP (as soon as possible)
test_order = builder.add_test_prescribed(
    code="Arterial Blood Gas",
    priority="asap",
    notes="Respiratory distress evaluation"
)

# Routine (normal scheduling)
test_order = builder.add_test_prescribed(
    code="Lipid Panel",
    priority="routine",
    notes="Annual screening"
)
```

## Common Lab Test Orders

### Basic Metabolic Panel
```python
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Basic Metabolic Panel",
        code="51990-0",
        system="http://loinc.org"
    ),
    notes="Fasting not required"
)
```

### Complete Blood Count
```python
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Complete Blood Count with Differential",
        code="58410-2", 
        system="http://loinc.org"
    ),
    priority="routine"
)
```

### Liver Function Tests
```python
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Liver Function Tests",
        code="24362-6",
        system="http://loinc.org"
    ),
    reason=create_codeable_concept(
        text="Monitor medication effects",
        code="182856006",
        system="http://snomed.info/sct"
    )
)
```

### Lipid Panel
```python
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Lipid Panel",
        code="24331-1",
        system="http://loinc.org"
    ),
    notes="12-hour fasting required",
    reason="Cardiovascular risk assessment"
)
```

### Hemoglobin A1C
```python
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Hemoglobin A1C",
        code="4548-4",
        system="http://loinc.org"
    ),
    reason=create_codeable_concept(
        text="Diabetes monitoring",
        code="390906007",
        system="http://snomed.info/sct"
    )
)
```

### Thyroid Function Tests
```python
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Thyroid Stimulating Hormone",
        code="3016-3",
        system="http://loinc.org"
    ),
    reason="Fatigue workup"
)

test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Free T4",
        code="3024-7",
        system="http://loinc.org"
    )
)
```

### Inflammatory Markers
```python
# ESR
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Erythrocyte Sedimentation Rate",
        code="4537-7",
        system="http://loinc.org"
    ),
    reason="Inflammatory condition workup"
)

# CRP
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="C-Reactive Protein",
        code="1988-5",
        system="http://loinc.org"
    )
)
```

### Infectious Disease Testing
```python
# COVID-19 PCR
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="COVID-19 PCR",
        code="94500-6",
        system="http://loinc.org"
    ),
    priority="urgent",
    notes="Symptomatic patient, isolate pending results"
)

# Hepatitis Panel
test_order = builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Hepatitis Panel",
        code="22314-9",
        system="http://loinc.org"
    ),
    reason="Pre-operative screening"
)
```

## Scheduled Testing
```python
from datetime import datetime, timedelta

# Morning collection
test_order = builder.add_test_prescribed(
    code="Fasting Glucose",
    date=datetime.now().replace(hour=8, minute=0) + timedelta(days=1),
    notes="Schedule for 8 AM, patient fasting from midnight"
)

# Follow-up in 3 months
test_order = builder.add_test_prescribed(
    code="Hemoglobin A1C",
    date=datetime.now() + timedelta(days=90),
    reason="Diabetes monitoring",
    notes="3-month follow-up per guidelines"
)
```

## Specimen-Specific Instructions
```python
# Urine collection
test_order = builder.add_test_prescribed(
    code="Urine Culture",
    notes="Clean catch midstream specimen, refrigerate if transport delayed"
)

# Blood culture
test_order = builder.add_test_prescribed(
    code="Blood Culture",
    priority="urgent",
    notes="Draw from peripheral vein, collect before antibiotics"
)

# 24-hour urine
test_order = builder.add_test_prescribed(
    code="24-hour Urine Protein",
    notes="Patient education provided for complete collection"
)
```

## Test Panels and Profiles
```python
# Comprehensive Metabolic Panel
test_order = builder.add_test_prescribed(
    code="Comprehensive Metabolic Panel",
    notes="Include glucose, electrolytes, kidney and liver function"
)

# Cardiac Risk Profile  
test_order = builder.add_test_prescribed(
    code="Cardiac Risk Assessment Panel",
    notes="Include lipids, CRP, homocysteine"
)

# Anemia Workup
test_order = builder.add_test_prescribed(
    code="Iron Studies",
    reason="Anemia evaluation",
    notes="Include serum iron, TIBC, ferritin, transferrin saturation"
)
```

## Reason for Testing
```python
# Diagnostic workup
test_order = builder.add_test_prescribed(
    code="Chest X-ray",
    reason=create_codeable_concept(
        text="Chest pain evaluation",
        code="29857009",
        system="http://snomed.info/sct"
    )
)

# Monitoring
test_order = builder.add_test_prescribed(
    code="INR",
    reason="Warfarin monitoring",
    notes="Patient on chronic anticoagulation"
)

# Screening
test_order = builder.add_test_prescribed(
    code="Mammogram",
    reason="Annual screening",
    notes="Age-appropriate cancer screening"
)
```

## Best Practices
1. Use create_codeable_concept with LOINC codes for standardized test identification
2. Include specific collection or preparation instructions in notes
3. Set appropriate priority based on clinical urgency
4. Document clinical reason for test ordering
5. Schedule tests with appropriate timing (fasting requirements, medication timing)
6. Group related tests logically (panels, profiles)
7. Include follow-up scheduling for monitoring tests
8. Consider patient convenience and compliance when scheduling

## Common LOINC Codes for Lab Tests
- **CBC**: `26604007` (SNOMED), `57021-8` (LOINC)
- **Basic Metabolic Panel**: `51990-0`
- **Lipid Panel**: `24331-1`
- **Liver Function**: `24362-6`
- **Hemoglobin A1C**: `4548-4`
- **TSH**: `3016-3`
- **Creatinine**: `2160-0`
- **Glucose**: `2345-7`

## Notes
- Lab test orders create ServiceRequest resources with category "laboratory"
- Tests can be scheduled for future dates or marked as STAT for immediate processing
- Clinical reason helps justify medical necessity
- Special instructions ensure proper specimen collection
- Integration with lab systems requires proper test coding
