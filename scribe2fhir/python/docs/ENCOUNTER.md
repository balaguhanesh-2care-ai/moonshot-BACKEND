---
title: "Encounter Element Documentation"
description: "The Encounter element represents a healthcare interaction between a patient and healthcare provider. It provides context for when and where clinical a"
---
## Overview
The Encounter element represents a healthcare interaction between a patient and healthcare provider. It provides context for when and where clinical activities occurred.

## Function
```python
builder.add_encounter(
    encounter_class: str = "ambulatory",
    encounter_type: Optional[str] = None,
    encounter_subtype: Optional[str] = None,
    period_start: Optional[DateTimeInput] = None,
    period_end: Optional[DateTimeInput] = None,
    facility_name: Optional[str] = None,
    department: Optional[str] = None,
    status: str = "finished",
    id: Optional[str] = None,
) -> Encounter
```

## Parameters

### Optional Parameters
- **encounter_class**: Type of encounter ("ambulatory", "emergency", "inpatient", "virtual")
- **encounter_type**: Specific type of encounter
- **encounter_subtype**: Sub-classification of encounter
- **period_start**: When the encounter started
- **period_end**: When the encounter ended
- **facility_name**: Healthcare facility name
- **department**: Department or service within facility
- **status**: Encounter status (default: "finished")
- **id**: Custom resource ID

## Basic Usage

### Simple Encounter
```python
from fhir_sdk import FHIRDocumentBuilder
from datetime import datetime

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add basic encounter
encounter = builder.add_encounter()
```

### Comprehensive Encounter
```python
# Add detailed encounter
encounter = builder.add_encounter(
    encounter_class="ambulatory",
    encounter_type="Consultation",
    encounter_subtype="General Medicine Consultation",
    period_start=datetime.now(),
    facility_name="City General Hospital",
    department="Cardiology",
    status="finished"
)
```

## Encounter Classes
- **"ambulatory"**: Outpatient visit
- **"emergency"**: Emergency department visit  
- **"inpatient"**: Hospital admission
- **"virtual"**: Telemedicine/remote consultation
- **"outpatient"**: Same as ambulatory

## Encounter Status Values
- **"planned"**: Scheduled but not started
- **"arrived"**: Patient has arrived
- **"in-progress"**: Currently happening
- **"finished"**: Completed (default)
- **"cancelled"**: Cancelled before completion

## Using CodeableConcept for Encounter Type

### Preferred: Using create_codeable_concept
```python
from fhir_sdk.types import create_codeable_concept

encounter = builder.add_encounter(
    encounter_type=create_codeable_concept(
        text="Emergency Consultation",
        code="EMER",
        system="http://terminology.hl7.org/CodeSystem/v3-ActCode",
        display="Emergency Consultation"
    )
)
```

### Alternative: Using String
```python
encounter = builder.add_encounter(
    encounter_type="Emergency Consultation"
)
```

## Date/Time Handling
```python
from datetime import datetime, timedelta

now = datetime.now()
encounter = builder.add_encounter(
    period_start=now,
    period_end=now + timedelta(hours=1)
)
```

## Common Encounter Types
- "Consultation"
- "Follow-up Visit" 
- "Emergency Visit"
- "Procedure Visit"
- "Therapy Session"
- "Vaccination Visit"

## Best Practices
1. Add encounter after patient but before clinical activities
2. Use appropriate encounter_class for the care setting
3. Include facility_name for location tracking
4. Set period_start for time-based analytics
5. Use "in-progress" status for ongoing encounters
6. Prefer create_codeable_concept for coded encounter types

## Notes
- Encounter provides context for all observations, procedures, and medications
- Multiple clinical activities can be associated with a single encounter
- The encounter ID is automatically referenced by related clinical resources
- Period information helps with care episode tracking
