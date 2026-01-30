---
title: "Medication Prescription Element Documentation"
description: "Medication Prescription elements represent prescribed medications, including dosage instructions, duration, and administration details. These create F"
---
## Overview
Medication Prescription elements represent prescribed medications, including dosage instructions, duration, and administration details. These create FHIR MedicationRequest resources for active prescriptions.

## Function
```python
builder.add_medication_prescribed(
    medication: CodeInput,
    dosage: Optional[Union[Dosage, List[Dosage]]] = None,
    status: Union[MedicationRequestStatus, str] = "active",
    intent: Union[MedicationRequestIntent, str] = "order",
    duration_value: Optional[float] = None,
    duration_unit: Optional[str] = None,
    quantity_value: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    refills: Optional[int] = None,
    notes: Optional[str] = None,
    reason: Optional[CodeInput] = None,
    authored_on: Optional[DateTimeInput] = None,
    id: Optional[str] = None,
) -> MedicationRequest
```

## Parameters

### Required Parameters
- **medication**: The medication name or code

### Optional Parameters
- **dosage**: Detailed dosage instructions (see DosageBuilder)
- **status**: Prescription status (default: "active")
- **intent**: Prescription intent (default: "order")
- **duration_value**: Treatment duration (numeric)
- **duration_unit**: Duration unit (e.g., "d", "wk", "mo")
- **quantity_value**: Quantity to dispense
- **quantity_unit**: Quantity unit (e.g., "tablet", "ml")
- **refills**: Number of refills allowed
- **notes**: Additional prescription notes
- **reason**: Reason for prescription
- **authored_on**: When prescription was written
- **id**: Custom resource ID

## Basic Usage

### Simple Prescription (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, DosageBuilder, RouteOfAdministration
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Create dosage instructions
dosage = DosageBuilder.build(
    dose_value=500,
    dose_unit="mg",
    frequency=2,
    period=1,
    period_unit="d",
    route=RouteOfAdministration.ORAL,
    text="Take 500mg twice daily"
)

# Add prescription
prescription = builder.add_medication_prescribed(
    medication=create_codeable_concept(
        text="Amoxicillin 500mg",
        code="27658006",
        system="http://snomed.info/sct",
        display="Amoxicillin"
    ),
    dosage=dosage,
    duration_value=7,
    duration_unit="d"
)
```

### Using String (Alternative)
```python
prescription = builder.add_medication_prescribed(
    medication="Amoxicillin 500mg",
    duration_value=7,
    duration_unit="d",
    notes="Take twice daily with food"
)
```

## DosageBuilder Usage

### Basic Dosage
```python
from fhir_sdk import DosageBuilder, RouteOfAdministration, EventTiming

dosage = DosageBuilder.build(
    dose_value=1,
    dose_unit="tablet",
    frequency=3,
    period=1,
    period_unit="d",
    text="Take 1 tablet three times daily"
)
```

### Detailed Dosage with Route and Timing
```python
dosage = DosageBuilder.build(
    dose_value=10,
    dose_unit="ml",
    frequency=2,
    period=1,
    period_unit="d",
    route=RouteOfAdministration.ORAL,
    timing_code=EventTiming.AFTER_MEAL,
    text="Take 10ml twice daily after meals"
)
```

### Complex Dosage Schedules
```python
# Three times daily
dosage = DosageBuilder.build(
    dose_value=250,
    dose_unit="mg",
    frequency=3,
    period=1,
    period_unit="d"
)

# Weekly dosage
dosage = DosageBuilder.build(
    dose_value=25,
    dose_unit="mg",
    frequency=1,
    period=1,
    period_unit="wk"
)

# As needed (PRN)
dosage = DosageBuilder.build(
    dose_value=2,
    dose_unit="tablet",
    text="Take 2 tablets as needed for pain, maximum 6 tablets per day"
)
```

## Route of Administration
```python
from fhir_sdk import RouteOfAdministration

# Oral route
dosage = DosageBuilder.build(
    dose_value=5,
    dose_unit="mg",
    frequency=1,
    period=1,
    period_unit="d",
    route=RouteOfAdministration.ORAL
)

# Other routes
RouteOfAdministration.TOPICAL      # Topical application
RouteOfAdministration.INTRAVENOUS  # IV administration
RouteOfAdministration.INTRAMUSCULAR # IM injection
RouteOfAdministration.SUBCUTANEOUS # Subcutaneous injection
```

## Timing Codes
```python
from fhir_sdk import EventTiming

# Timing with meals
dosage = DosageBuilder.build(
    dose_value=1,
    dose_unit="tablet",
    frequency=2,
    period=1,
    period_unit="d",
    timing_code=EventTiming.AFTER_MEAL
)

# Other timing options
EventTiming.BEFORE_MEAL  # Before meals
EventTiming.BEDTIME      # At bedtime  
EventTiming.MORNING      # In the morning
EventTiming.EVENING      # In the evening
```

## Prescription Status and Intent
```python
from fhir_sdk import MedicationRequestStatus, MedicationRequestIntent

# Different statuses
prescription = builder.add_medication_prescribed(
    medication="Lisinopril 10mg",
    status=MedicationRequestStatus.ACTIVE  # Active prescription
)

prescription = builder.add_medication_prescribed(
    medication="Warfarin 5mg", 
    status=MedicationRequestStatus.ON_HOLD  # Temporarily suspended
)

# Different intents
prescription = builder.add_medication_prescribed(
    medication="Insulin",
    intent=MedicationRequestIntent.ORDER  # Direct order
)

prescription = builder.add_medication_prescribed(
    medication="Statin",
    intent=MedicationRequestIntent.PLAN  # Treatment plan
)
```

## Comprehensive Prescription Example
```python
from datetime import datetime

# Complete prescription with all details
dosage = DosageBuilder.build(
    dose_value=1,
    dose_unit="tablet",
    frequency=1,
    period=1, 
    period_unit="d",
    route=RouteOfAdministration.ORAL,
    timing_code=EventTiming.MORNING,
    text="Take 1 tablet once daily in the morning"
)

prescription = builder.add_medication_prescribed(
    medication=create_codeable_concept(
        text="Lisinopril 10mg",
        code="386872004",
        system="http://snomed.info/sct"
    ),
    dosage=dosage,
    status=MedicationRequestStatus.ACTIVE,
    intent=MedicationRequestIntent.ORDER,
    duration_value=30,
    duration_unit="d",
    quantity_value=30,
    quantity_unit="tablet",
    refills=2,
    notes="Monitor blood pressure weekly",
    reason=create_codeable_concept(
        text="Hypertension",
        code="38341003",
        system="http://snomed.info/sct"
    ),
    authored_on=datetime.now()
)
```

## Common Medication Examples

### Antibiotics
```python
# Amoxicillin course
dosage = DosageBuilder.build(
    dose_value=500,
    dose_unit="mg",
    frequency=3,
    period=1,
    period_unit="d",
    route=RouteOfAdministration.ORAL
)

prescription = builder.add_medication_prescribed(
    medication="Amoxicillin 500mg",
    dosage=dosage,
    duration_value=7,
    duration_unit="d",
    notes="Complete entire course even if feeling better"
)
```

### Pain Medications
```python
# PRN pain medication
dosage = DosageBuilder.build(
    dose_value=400,
    dose_unit="mg",
    frequency=1,
    period=6,
    period_unit="h",
    text="Take 400mg every 6 hours as needed for pain"
)

prescription = builder.add_medication_prescribed(
    medication="Ibuprofen 400mg",
    dosage=dosage,
    notes="Maximum 4 doses per day, take with food"
)
```

### Chronic Medications
```python
# Daily chronic medication
dosage = DosageBuilder.build(
    dose_value=20,
    dose_unit="mg",
    frequency=1,
    period=1,
    period_unit="d",
    timing_code=EventTiming.MORNING
)

prescription = builder.add_medication_prescribed(
    medication="Atorvastatin 20mg",
    dosage=dosage,
    duration_value=90,
    duration_unit="d",
    refills=3,
    reason="Hyperlipidemia"
)
```

## Best Practices
1. Use create_codeable_concept with RxNorm codes for medications when available
2. Always include clear dosage instructions using DosageBuilder
3. Specify route of administration for clarity
4. Include duration for antimicrobials and short courses
5. Add quantity and refills for chronic medications
6. Document indication/reason for prescription
7. Include important warnings or monitoring instructions in notes
8. Use appropriate timing codes (with meals, bedtime, etc.)

## Common Dosage Units
- **Tablets/Capsules**: "tablet", "capsule"
- **Liquids**: "ml", "mg/ml", "tsp"
- **Topical**: "g", "ml", "application"
- **Injections**: "mg", "unit", "ml"

## Notes
- Prescription creates a MedicationRequest resource
- Dosage instructions should be clear and unambiguous
- Multiple dosages can be provided for complex regimens
- Status tracking helps manage prescription lifecycle
- Integration with pharmacy systems requires proper coding
