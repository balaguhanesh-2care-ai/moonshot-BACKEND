---
title: "Medication History Element Documentation"
description: "Medication History elements represent medications the patient is currently taking or has taken in the past. These create FHIR MedicationStatement reso"
---
## Overview
Medication History elements represent medications the patient is currently taking or has taken in the past. These create FHIR MedicationStatement resources to document medication history and current medications.

## Function
```python
builder.add_medication_history(
    medication: CodeInput,
    dosage: Optional[Union[Dosage, List[Dosage]]] = None,
    status: Union[MedicationStatementStatus, str] = "active",
    effective_start: Optional[DateTimeInput] = None,
    effective_end: Optional[DateTimeInput] = None,
    notes: Optional[str] = None,
    reason: Optional[CodeInput] = None,
    date_asserted: Optional[DateTimeInput] = None,
    id: Optional[str] = None,
) -> MedicationStatement
```

## Parameters

### Required Parameters
- **medication**: The medication name or code

### Optional Parameters
- **dosage**: How the medication is/was taken (see DosageBuilder)
- **status**: Current status of medication use (default: "active")
- **effective_start**: When patient started taking the medication
- **effective_end**: When patient stopped taking the medication
- **notes**: Additional notes about medication use
- **reason**: Why the medication is/was being taken
- **date_asserted**: When this information was recorded
- **id**: Custom resource ID

## Basic Usage

### Current Medication (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, MedicationStatementStatus
from fhir_sdk.types import create_codeable_concept
from datetime import datetime, timedelta

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add current medication
med_history = builder.add_medication_history(
    medication=create_codeable_concept(
        text="Lisinopril 10mg",
        code="386872004",
        system="http://snomed.info/sct",
        display="Lisinopril"
    ),
    status=MedicationStatementStatus.ACTIVE,
    effective_start=datetime.now() - timedelta(days=180),
    notes="Taking daily for blood pressure control"
)
```

### Using String (Alternative)
```python
med_history = builder.add_medication_history(
    medication="Lisinopril 10mg",
    status="active",
    notes="Taking daily for blood pressure"
)
```

### With Dosage Information
```python
from fhir_sdk import DosageBuilder, RouteOfAdministration, EventTiming

# Create dosage
dosage = DosageBuilder.build(
    dose_value=10,
    dose_unit="mg",
    frequency=1,
    period=1,
    period_unit="d",
    route=RouteOfAdministration.ORAL,
    timing_code=EventTiming.MORNING,
    text="Take 10mg once daily in the morning"
)

med_history = builder.add_medication_history(
    medication="Lisinopril 10mg",
    dosage=dosage,
    effective_start=datetime.now() - timedelta(days=90),
    reason="Hypertension"
)
```

## Medication Status Options
```python
from fhir_sdk import MedicationStatementStatus

# Active medication
med = builder.add_medication_history(
    medication="Metformin 500mg",
    status=MedicationStatementStatus.ACTIVE
)

# Completed course
med = builder.add_medication_history(
    medication="Amoxicillin 500mg",
    status=MedicationStatementStatus.COMPLETED,
    effective_start=datetime.now() - timedelta(days=14),
    effective_end=datetime.now() - timedelta(days=7)
)

# Stopped medication
med = builder.add_medication_history(
    medication="Aspirin 81mg",
    status=MedicationStatementStatus.STOPPED,
    notes="Stopped due to gastric irritation"
)
```

Available medication statuses:
- `MedicationStatementStatus.ACTIVE` or `"active"` - Currently taking
- `MedicationStatementStatus.COMPLETED` or `"completed"` - Finished course  
- `MedicationStatementStatus.INTENDED` or `"intended"` - Planned to start
- `MedicationStatementStatus.STOPPED` or `"stopped"` - Discontinued

## Common Current Medications

### Cardiovascular Medications
```python
# ACE Inhibitor
med = builder.add_medication_history(
    medication=create_codeable_concept(
        text="Lisinopril 10mg",
        code="386872004",
        system="http://snomed.info/sct"
    ),
    status="active",
    effective_start=datetime.now() - timedelta(days=365),
    reason="Hypertension",
    notes="Well tolerated, good BP control"
)

# Beta Blocker
med = builder.add_medication_history(
    medication=create_codeable_concept(
        text="Metoprolol 50mg",
        code="386864001", 
        system="http://snomed.info/sct"
    ),
    status="active",
    notes="Twice daily for heart rate control"
)
```

### Diabetes Medications
```python
# Metformin
med = builder.add_medication_history(
    medication=create_codeable_concept(
        text="Metformin 1000mg",
        code="387467008",
        system="http://snomed.info/sct"
    ),
    status="active",
    effective_start=datetime.now() - timedelta(days=730),
    reason="Type 2 diabetes mellitus",
    notes="Twice daily with meals, good glucose control"
)

# Insulin
med = builder.add_medication_history(
    medication=create_codeable_concept(
        text="Insulin glargine",
        code="411529005",
        system="http://snomed.info/sct"
    ),
    status="active",
    notes="20 units at bedtime"
)
```

### Pain and Anti-inflammatory
```python
# NSAIDs
med = builder.add_medication_history(
    medication="Ibuprofen 400mg",
    status="active",
    notes="As needed for arthritis pain, maximum 3 times daily"
)

# Acetaminophen
med = builder.add_medication_history(
    medication="Acetaminophen 500mg",
    status="stopped",
    effective_start=datetime.now() - timedelta(days=30),
    effective_end=datetime.now() - timedelta(days=15),
    notes="Stopped after completing course for headaches"
)
```

### Psychiatric Medications
```python
med = builder.add_medication_history(
    medication=create_codeable_concept(
        text="Sertraline 50mg",
        code="387467007",
        system="http://snomed.info/sct"
    ),
    status="active",
    effective_start=datetime.now() - timedelta(days=180),
    reason="Depression",
    notes="Daily dose, patient reports improved mood"
)
```

## Medication History with Reason
```python
med = builder.add_medication_history(
    medication="Crocin 650mg",
    status="active",
    effective_start=datetime.now() - timedelta(days=90),
    reason=create_codeable_concept(
        text="Pain management",
        code="278414003",
        system="http://snomed.info/sct"
    ),
    notes="Takes as needed for chronic back pain"
)
```

## Over-the-Counter Medications
```python
# Vitamins
med = builder.add_medication_history(
    medication="Vitamin D3 2000 IU",
    status="active",
    notes="Daily supplement for vitamin D deficiency"
)

# Herbal supplements
med = builder.add_medication_history(
    medication="Turmeric supplement",
    status="active",
    notes="500mg daily, patient reports joint pain improvement"
)
```

## Medication Adherence Documentation
```python
med = builder.add_medication_history(
    medication="Warfarin 5mg",
    status="active",
    notes="Good adherence, takes same time daily, regular INR monitoring"
)

# Poor adherence
med = builder.add_medication_history(
    medication="Metformin 500mg",
    status="active", 
    notes="Patient admits to missing doses frequently"
)
```

## Stopped Medications
```python
med = builder.add_medication_history(
    medication="Aspirin 81mg",
    status="stopped",
    effective_start=datetime.now() - timedelta(days=365),
    effective_end=datetime.now() - timedelta(days=30),
    reason="Cardiac prophylaxis",
    notes="Discontinued due to GI bleeding risk"
)
```

## Time Periods
```python
# Ongoing medication (start only)
med = builder.add_medication_history(
    medication="Thyroid hormone",
    status="active",
    effective_start=datetime(2020, 1, 1)
)

# Completed course (start and end)
med = builder.add_medication_history(
    medication="Prednisone 20mg",
    status="completed",
    effective_start=datetime.now() - timedelta(days=21),
    effective_end=datetime.now() - timedelta(days=1),
    notes="Tapered course for inflammation"
)
```

## Best Practices
1. Use create_codeable_concept with RxNorm or SNOMED CT codes when available
2. Include start dates for chronic medications
3. Document reasons for medication use
4. Record adherence information when relevant
5. Include notes about effectiveness, side effects, or concerns
6. Update status when medications are changed or stopped
7. Use detailed dosage instructions when known
8. Document both prescription and over-the-counter medications

## Notes
- Medication history creates MedicationStatement resources
- Different from prescriptions (MedicationRequest) - this documents actual usage
- Effective periods help track medication duration
- Status changes track medication lifecycle
- Important for medication reconciliation and interaction checking
