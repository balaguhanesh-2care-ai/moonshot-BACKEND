---
title: "Procedure History Element Documentation"
description: "Procedure History elements document surgical procedures, interventions, and other medical procedures that the patient has undergone in the past. This"
---
## Overview
Procedure History elements document surgical procedures, interventions, and other medical procedures that the patient has undergone in the past. This information provides important context for current care decisions.

## Function
```python
builder.add_procedure_history(
    code: CodeInput,
    date: Optional[DateTimeInput] = None,
    notes: Optional[str] = None,
    status: str = "completed",
    outcome: Optional[CodeInput] = None,
    id: Optional[str] = None,
) -> Procedure
```

## Parameters

### Required Parameters
- **code**: The procedure name or code

### Optional Parameters
- **date**: When the procedure was performed
- **notes**: Additional details about the procedure
- **status**: Procedure status (default: "completed")
- **outcome**: Result or outcome of the procedure
- **id**: Custom resource ID

## Basic Usage

### Simple Procedure History (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, ProcedureStatus
from fhir_sdk.types import create_codeable_concept
from datetime import datetime, timedelta

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add procedure history
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Appendectomy",
        code="80146002",
        system="http://snomed.info/sct",
        display="Appendectomy"
    ),
    date=datetime.now() - timedelta(days=365),
    status=ProcedureStatus.COMPLETED
)
```

### Using String (Alternative)
```python
procedure = builder.add_procedure_history(
    code="Appendectomy",
    date="2020-05-15",
    status="completed"
)
```

### With Detailed Information
```python
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Laparoscopic cholecystectomy",
        code="45595009",
        system="http://snomed.info/sct"
    ),
    date=datetime(2021, 8, 15),
    notes="Uncomplicated laparoscopic approach, 4 ports used",
    outcome=create_codeable_concept(
        text="Successful procedure",
        code="385669000",
        system="http://snomed.info/sct"
    )
)
```

## Common Surgical Procedures

### General Surgery
```python
# Appendectomy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Laparoscopic appendectomy",
        code="80146002",
        system="http://snomed.info/sct"
    ),
    date="2019-03-20",
    notes="Uncomplicated procedure, discharged same day"
)

# Hernia repair
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Inguinal hernia repair",
        code="112802009",
        system="http://snomed.info/sct"
    ),
    date="2018-11-10",
    notes="Open tension-free repair with mesh"
)

# Gallbladder removal
procedure = builder.add_procedure_history(
    code="Cholecystectomy",
    date="2017-09-15",
    notes="Laparoscopic approach, stones removed"
)
```

### Cardiac Procedures
```python
# Cardiac catheterization
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Cardiac catheterization",
        code="41976001",
        system="http://snomed.info/sct"
    ),
    date="2020-12-05",
    notes="Diagnostic catheterization, normal coronary arteries"
)

# Angioplasty
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Percutaneous coronary intervention",
        code="415070008",
        system="http://snomed.info/sct"
    ),
    date="2021-02-20",
    notes="Single vessel PCI with drug-eluting stent to LAD"
)

# Pacemaker insertion
procedure = builder.add_procedure_history(
    code="Pacemaker insertion",
    date="2019-07-30",
    notes="Dual chamber pacemaker for complete heart block"
)
```

### Orthopedic Procedures
```python
# Knee replacement
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Total knee arthroplasty",
        code="179344006",
        system="http://snomed.info/sct"
    ),
    date="2018-04-25",
    notes="Right total knee replacement, good range of motion post-op"
)

# Arthroscopy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Arthroscopic meniscectomy",
        code="112693009", 
        system="http://snomed.info/sct"
    ),
    date="2020-09-10",
    notes="Left knee, partial medial meniscectomy"
)

# Fracture repair
procedure = builder.add_procedure_history(
    code="Open reduction internal fixation",
    date="2017-12-03",
    notes="Left radius fracture, plate and screws placed"
)
```

### Gynecological Procedures
```python
# Hysterectomy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Total abdominal hysterectomy",
        code="236886002",
        system="http://snomed.info/sct"
    ),
    date="2019-06-20",
    notes="For uterine fibroids, ovaries preserved"
)

# C-section
procedure = builder.add_procedure_history(
    code="Cesarean section",
    date="2018-03-15",
    notes="Primary C-section for breech presentation"
)
```

### Urological Procedures
```python
# Vasectomy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Vasectomy",
        code="22523008",
        system="http://snomed.info/sct"
    ),
    date="2019-11-15",
    notes="No-scalpel technique, outpatient procedure"
)

# Cystoscopy
procedure = builder.add_procedure_history(
    code="Cystoscopy",
    date="2021-05-30",
    notes="Diagnostic cystoscopy for hematuria, no abnormalities found"
)
```

### Gastrointestinal Procedures
```python
# Colonoscopy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Colonoscopy",
        code="73761001",
        system="http://snomed.info/sct"
    ),
    date="2022-01-20",
    notes="Screening colonoscopy, 2 small polyps removed and sent for biopsy"
)

# Upper endoscopy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Esophagogastroduodenoscopy",
        code="1919008",
        system="http://snomed.info/sct"
    ),
    date="2021-07-10",
    notes="EGD for GERD evaluation, mild esophagitis noted"
)
```

### Dermatological Procedures
```python
# Skin biopsy
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Skin biopsy",
        code="240977001",
        system="http://snomed.info/sct"
    ),
    date="2022-08-05",
    notes="Punch biopsy of suspicious mole, pathology benign"
)

# Mohs surgery
procedure = builder.add_procedure_history(
    code="Mohs micrographic surgery",
    date="2021-04-18",
    notes="For basal cell carcinoma, clear margins achieved"
)
```

## Procedure Status Options
```python
from fhir_sdk import ProcedureStatus

# Completed procedure (most common)
procedure = builder.add_procedure_history(
    code="Tonsillectomy",
    status=ProcedureStatus.COMPLETED,
    date="2015-07-20"
)

# Stopped procedure
procedure = builder.add_procedure_history(
    code="Cardiac catheterization",
    status=ProcedureStatus.STOPPED,
    notes="Procedure stopped due to contrast reaction"
)

# In-progress (ongoing)
procedure = builder.add_procedure_history(
    code="Physical therapy",
    status=ProcedureStatus.IN_PROGRESS,
    notes="3x weekly sessions for post-surgical rehabilitation"
)
```

## Outcomes Documentation
```python
# Successful outcome
procedure = builder.add_procedure_history(
    code="Cataract extraction",
    date="2022-03-15",
    outcome=create_codeable_concept(
        text="Successful procedure",
        code="385669000",
        system="http://snomed.info/sct"
    ),
    notes="Vision improved significantly post-operatively"
)

# Complication
procedure = builder.add_procedure_history(
    code="Hernia repair",
    date="2020-06-10",
    outcome="Surgical site infection",
    notes="Post-operative wound infection, treated with antibiotics"
)
```

## Emergency Procedures
```python
procedure = builder.add_procedure_history(
    code=create_codeable_concept(
        text="Emergency tracheostomy",
        code="48387007",
        system="http://snomed.info/sct"
    ),
    date="2019-12-01",
    notes="Performed for airway obstruction, later reversed"
)

procedure = builder.add_procedure_history(
    code="Emergency appendectomy",
    date="2018-08-20",
    notes="Perforated appendix, complicated by peritonitis"
)
```

## Preventive Procedures
```python
# Cancer screening
procedure = builder.add_procedure_history(
    code="Mammography",
    date="2023-01-15",
    notes="Annual screening mammogram, BIRADS 1 (negative)"
)

# Dental procedures
procedure = builder.add_procedure_history(
    code="Dental prophylaxis",
    date="2023-06-01",
    notes="Routine dental cleaning and examination"
)
```

## Multiple Related Procedures
```python
# Staged procedures
procedure1 = builder.add_procedure_history(
    code="First stage revision surgery",
    date="2021-01-15",
    notes="Hardware removal from previous fracture repair"
)

procedure2 = builder.add_procedure_history(
    code="Second stage revision surgery", 
    date="2021-03-15",
    notes="New implant placement after infection clearance"
)
```

## Best Practices
1. Use create_codeable_concept with SNOMED CT or CPT codes for standardized procedures
2. Include specific dates for temporal relationship analysis
3. Document approach (open vs laparoscopic) and technique details
4. Record outcomes and complications honestly
5. Note any follow-up procedures or revisions required
6. Include anesthesia type and duration for complex procedures
7. Document functional outcomes and recovery progress
8. Link related procedures (staged surgeries, revisions)

## Common Procedure Codes (SNOMED CT)
- **Appendectomy**: `80146002`
- **Cholecystectomy**: `45595009`
- **Colonoscopy**: `73761001`
- **Cardiac catheterization**: `41976001`
- **Knee replacement**: `179344006`
- **Vasectomy**: `22523008`
- **Cataract surgery**: `54885007`

## Notes
- Procedure history creates Procedure resources
- Past procedures influence current care planning
- Surgical history affects anesthetic and surgical risk assessment
- Procedure dates help establish medical timeline
- Outcomes documentation supports quality improvement and research
