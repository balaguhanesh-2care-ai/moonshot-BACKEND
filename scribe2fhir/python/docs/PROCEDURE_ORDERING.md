---
title: "Procedure Ordering Element Documentation"
description: "Procedure Ordering elements represent procedures, imaging studies, and interventions that have been ordered for the patient. These create FHIR Service"
---
## Overview
Procedure Ordering elements represent procedures, imaging studies, and interventions that have been ordered for the patient. These create FHIR ServiceRequest resources for non-laboratory services.

## Function
```python
builder.add_procedure_prescribed(
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
- **code**: The procedure name or code

### Optional Parameters
- **date**: When the procedure should be performed
- **notes**: Special instructions or requirements  
- **priority**: Procedure priority level
- **reason**: Clinical reason for ordering the procedure
- **id**: Custom resource ID

## Basic Usage

### Simple Procedure Order (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Order imaging study
procedure_order = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Chest X-ray",
        code="399208008",
        system="http://snomed.info/sct",
        display="Chest X-ray"
    )
)
```

### Using String (Alternative)
```python
procedure_order = builder.add_procedure_prescribed(
    code="Chest X-ray"
)
```

### With Priority and Reason
```python
from datetime import datetime, timedelta

procedure_order = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Echocardiogram",
        code="40701008",
        system="http://snomed.info/sct"
    ),
    date=datetime.now() + timedelta(days=3),
    priority="urgent",
    reason=create_codeable_concept(
        text="Chest pain",
        code="29857009",
        system="http://snomed.info/sct"
    ),
    notes="Evaluate cardiac function and wall motion"
)
```

## Imaging Studies

### X-ray Examinations
```python
# Chest X-ray
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Chest X-ray PA and Lateral",
        code="399208008",
        system="http://snomed.info/sct"
    ),
    reason="Cough and shortness of breath"
)

# Abdominal X-ray
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Abdominal X-ray",
        code="168731009",
        system="http://snomed.info/sct"
    ),
    notes="KUB (kidneys, ureters, bladder) view"
)

# Extremity X-ray
procedure = builder.add_procedure_prescribed(
    code="Knee X-ray",
    reason="Joint pain and swelling",
    notes="AP and lateral views, bilateral if indicated"
)
```

### CT Scans
```python
# CT Head
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="CT Head without contrast",
        code="418714002",
        system="http://snomed.info/sct"
    ),
    priority="urgent",
    reason="Headache with neurological symptoms"
)

# CT Abdomen/Pelvis
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="CT Abdomen and Pelvis with contrast",
        code="169070004",
        system="http://snomed.info/sct"
    ),
    notes="IV contrast unless contraindicated, check creatinine"
)

# CT Chest
procedure = builder.add_procedure_prescribed(
    code="CT Chest",
    reason="Lung nodule evaluation",
    notes="High resolution technique, prone images if needed"
)
```

### MRI Studies
```python
# Brain MRI
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="MRI Brain with and without contrast",
        code="419775003",
        system="http://snomed.info/sct"
    ),
    reason="Multiple sclerosis workup"
)

# Spine MRI
procedure = builder.add_procedure_prescribed(
    code="MRI Lumbar Spine",
    reason="Lower back pain with radiculopathy",
    notes="Include sagittal and axial T1 and T2 sequences"
)

# Joint MRI
procedure = builder.add_procedure_prescribed(
    code="MRI Knee",
    reason="Sports injury evaluation",
    notes="Include sequences for meniscal and ligament evaluation"
)
```

### Ultrasound Studies
```python
# Abdominal ultrasound
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Abdominal Ultrasound",
        code="268447006",
        system="http://snomed.info/sct"
    ),
    notes="Fasting 8 hours required, include gallbladder"
)

# Echocardiogram
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Transthoracic Echocardiogram",
        code="40701008",
        system="http://snomed.info/sct"
    ),
    reason="Heart failure evaluation"
)

# Vascular ultrasound
procedure = builder.add_procedure_prescribed(
    code="Carotid Doppler Ultrasound",
    reason="Stroke risk assessment",
    notes="Bilateral carotid and vertebral arteries"
)
```

## Cardiac Procedures
```python
# ECG
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="12-lead ECG",
        code="164847006",
        system="http://snomed.info/sct"
    ),
    priority="stat",
    reason="Chest pain evaluation"
)

# Stress test
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Exercise Stress Test",
        code="18501007",
        system="http://snomed.info/sct"
    ),
    reason="Coronary artery disease screening",
    notes="Patient able to exercise, no contraindications"
)

# Holter monitor
procedure = builder.add_procedure_prescribed(
    code="24-hour Holter Monitor",
    reason="Palpitations and arrhythmia evaluation",
    notes="Patient diary of symptoms required"
)
```

## Gastrointestinal Procedures  
```python
# Upper endoscopy
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Upper Endoscopy",
        code="1919008",
        system="http://snomed.info/sct"
    ),
    reason="GERD and dysphagia evaluation",
    notes="NPO after midnight, arrange sedation"
)

# Colonoscopy
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Colonoscopy",
        code="73761001",
        system="http://snomed.info/sct"
    ),
    reason="Colorectal cancer screening",
    notes="Bowel preparation instructions provided"
)
```

## Pulmonary Function Testing
```python
procedure = builder.add_procedure_prescribed(
    code=create_codeable_concept(
        text="Spirometry",
        code="127783003",
        system="http://snomed.info/sct"
    ),
    reason="Dyspnea evaluation",
    notes="Withhold bronchodilators 6 hours before test"
)

# Sleep study
procedure = builder.add_procedure_prescribed(
    code="Polysomnography",
    reason="Sleep apnea evaluation",
    notes="Home sleep study if appropriate candidate"
)
```

## Priority-based Ordering

### Emergency Procedures (STAT)
```python
procedure = builder.add_procedure_prescribed(
    code="CT Head",
    priority="stat",
    reason="Altered mental status",
    notes="Trauma protocol if indicated"
)
```

### Urgent Procedures
```python
procedure = builder.add_procedure_prescribed(
    code="CT Pulmonary Angiogram",
    priority="urgent", 
    reason="Suspected pulmonary embolism",
    notes="IV contrast, check creatinine first"
)
```

### Scheduled Procedures
```python
procedure = builder.add_procedure_prescribed(
    code="MRI Knee",
    date=datetime.now() + timedelta(days=14),
    priority="routine",
    reason="Chronic knee pain",
    notes="Schedule within 2 weeks, no metal screening needed"
)
```

## Pre-procedure Requirements
```python
# With contrast requirements
procedure = builder.add_procedure_prescribed(
    code="CT Abdomen with contrast",
    notes="Check creatinine <48h old, NPO 4 hours, IV access required"
)

# Sedation procedures
procedure = builder.add_procedure_prescribed(
    code="Upper Endoscopy",
    notes="NPO after midnight, arrange ride home, conscious sedation planned"
)

# Prep requirements
procedure = builder.add_procedure_prescribed(
    code="Colonoscopy",
    date=datetime.now() + timedelta(days=7),
    notes="Bowel prep instructions given, clear liquid diet day before"
)
```

## Reason Documentation
```python
# Diagnostic workup
procedure = builder.add_procedure_prescribed(
    code="PET Scan",
    reason=create_codeable_concept(
        text="Cancer staging",
        code="254837009",
        system="http://snomed.info/sct"
    )
)

# Follow-up monitoring
procedure = builder.add_procedure_prescribed(
    code="CT Chest",
    reason="Post-treatment surveillance",
    notes="Compare with prior study from 3 months ago"
)
```

## Best Practices
1. Use create_codeable_concept with SNOMED CT or CPT codes for standardized procedures
2. Set appropriate priority based on clinical urgency  
3. Include detailed pre-procedure instructions and requirements
4. Document clinical indication clearly for authorization
5. Schedule procedures with realistic timeframes
6. Include contrast, sedation, and preparation requirements
7. Consider patient factors (allergies, kidney function, anxiety)
8. Provide clear post-procedure follow-up instructions

## Common Procedure Codes (SNOMED CT)
- **Chest X-ray**: `399208008`
- **CT Head**: `418714002`
- **MRI Brain**: `419775003`
- **Echocardiogram**: `40701008`
- **Colonoscopy**: `73761001`
- **Upper Endoscopy**: `1919008`
- **ECG**: `164847006`

## Notes
- Procedure orders create ServiceRequest resources with category "procedure"
- Priority levels help with scheduling and resource allocation
- Clinical reasons support medical necessity and insurance authorization
- Pre-procedure instructions ensure patient safety and study quality
- Integration with scheduling systems requires standardized procedure codes
