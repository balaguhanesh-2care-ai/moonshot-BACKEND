---
title: "Examination Findings Element Documentation"
description: "Examination Findings elements represent results from physical examinations and clinical assessments performed by healthcare providers during patient e"
---
## Overview
Examination Findings elements represent results from physical examinations and clinical assessments performed by healthcare providers during patient encounters.

## Function
```python
builder.add_examination_finding(
    code: CodeInput,
    value: Optional[str] = None,
    date: Optional[DateTimeInput] = None,
    status: Union[ObservationStatus, str] = "final",
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> Observation
```

## Parameters

### Required Parameters
- **code**: The examination type or body system examined

### Optional Parameters
- **value**: The examination findings or result
- **date**: When the examination was performed
- **status**: Observation status (default: "final")
- **notes**: Additional details about the examination
- **id**: Custom resource ID

## Basic Usage

### Simple Examination (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add examination finding
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Heart sounds",
        code="364080008",
        system="http://snomed.info/sct",
        display="Heart sounds"
    ),
    value="Normal S1 and S2, no murmurs"
)
```

### Using String (Alternative)
```python
exam = builder.add_examination_finding(
    code="Heart sounds",
    value="Normal S1 and S2, no murmurs"
)
```

### Detailed Examination with Notes
```python
from datetime import datetime

exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Abdominal examination",
        code="271870009",
        system="http://snomed.info/sct"
    ),
    value="Soft, non-tender, no masses palpated",
    date=datetime.now(),
    notes="Patient cooperative throughout examination"
)
```

## Common Physical Examinations

### Cardiovascular System
```python
# Heart sounds
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Heart sounds",
        code="364080008",
        system="http://snomed.info/sct"
    ),
    value="Regular rate and rhythm, no murmurs"
)

# Peripheral pulses
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Peripheral pulses",
        code="43685005",
        system="http://snomed.info/sct" 
    ),
    value="All pulses palpable and equal bilaterally"
)
```

### Respiratory System
```python
# Lung sounds
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Lung sounds",
        code="28914005",
        system="http://snomed.info/sct"
    ),
    value="Clear to auscultation bilaterally"
)

# Chest wall inspection
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Chest wall examination",
        code="364088001",
        system="http://snomed.info/sct"
    ),
    value="Symmetric expansion, no retractions"
)
```

### Gastrointestinal System
```python
# Abdominal examination
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Abdominal examination", 
        code="271870009",
        system="http://snomed.info/sct"
    ),
    value="Soft, non-distended, bowel sounds present"
)

# Liver examination
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Liver palpation",
        code="64453007",
        system="http://snomed.info/sct"
    ),
    value="Not enlarged, no tenderness"
)
```

### Neurological System
```python
# Mental status
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Mental status examination",
        code="314548002",
        system="http://snomed.info/sct"
    ),
    value="Alert and oriented x 3"
)

# Reflexes
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Deep tendon reflexes",
        code="87572000",
        system="http://snomed.info/sct"
    ),
    value="2+ and symmetric throughout"
)

# Cranial nerves
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Cranial nerve examination",
        code="280151006",
        system="http://snomed.info/sct"
    ),
    value="Cranial nerves II-XII grossly intact"
)
```

### Musculoskeletal System
```python
# Joint examination
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Joint examination",
        code="309542004",
        system="http://snomed.info/sct"
    ),
    value="Full range of motion, no swelling or deformity"
)

# Muscle strength
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Muscle strength testing",
        code="271590003",
        system="http://snomed.info/sct"
    ),
    value="5/5 strength in all extremities"
)
```

### Skin Examination
```python
exam = builder.add_examination_finding(
    code=create_codeable_concept(
        text="Skin examination",
        code="274181009",
        system="http://snomed.info/sct"
    ),
    value="Warm, dry, intact. No rashes or lesions noted"
)
```

## Abnormal Findings

### Positive Findings
```python
exam = builder.add_examination_finding(
    code="Lymph node examination",
    value="Palpable lymph nodes in neck",
    notes="Bilateral cervical lymphadenopathy, mobile, non-tender"
)
```

### Negative Findings (Rule-outs)
```python
exam = builder.add_examination_finding(
    code="Neck stiffness assessment",
    value="No meningeal signs",
    notes="Full range of motion, no nuchal rigidity"
)
```

## Examination Status Options
```python
from fhir_sdk import ObservationStatus

# Preliminary examination
exam = builder.add_examination_finding(
    code="Initial assessment",
    value="Appears stable",
    status=ObservationStatus.PRELIMINARY
)

# Final examination
exam = builder.add_examination_finding(
    code="Complete physical exam",
    value="Within normal limits",
    status=ObservationStatus.FINAL
)
```

## Time-based Examinations
```python
from datetime import datetime

# Examination during current encounter
exam = builder.add_examination_finding(
    code="General appearance",
    value="Well-appearing, in no acute distress",
    date=datetime.now()
)
```

## Regional Examinations

### Head and Neck
```python
exam = builder.add_examination_finding(
    code="Head and neck examination",
    value="HEENT: PERRL, EOM intact, throat clear, no lymphadenopathy"
)
```

### Extremities
```python
exam = builder.add_examination_finding(
    code="Extremity examination",
    value="No clubbing, cyanosis, or edema. Capillary refill <2 seconds"
)
```

## Best Practices
1. Use create_codeable_concept with SNOMED CT codes for standardized examinations
2. Provide descriptive findings rather than just "normal" or "abnormal"
3. Include both positive and negative (rule-out) findings
4. Document examination date for temporal context
5. Use consistent terminology for similar findings
6. Include relevant anatomical details and severity
7. Note patient cooperation or limitations affecting examination

## Common Examination Values
- **Normal findings**: "Within normal limits", "No abnormalities detected"
- **Cardiovascular**: "Regular rate and rhythm", "No murmurs"
- **Respiratory**: "Clear to auscultation", "Equal air entry"
- **Abdominal**: "Soft, non-tender", "Bowel sounds present"
- **Neurological**: "Alert and oriented", "No focal deficits"
- **Musculoskeletal**: "Full range of motion", "No deformity"

## Notes
- Examination findings are categorized as "exam" observations
- Findings should be objective and descriptive
- Multiple examinations can comprehensively document physical assessment
- Date/time helps establish examination sequence during encounters
- Detailed findings support clinical decision-making and care planning
