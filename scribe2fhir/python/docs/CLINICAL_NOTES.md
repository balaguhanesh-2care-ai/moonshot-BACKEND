---
title: "Clinical Notes Element Documentation"
description: "Clinical Notes elements document clinical observations, assessments, plans, and other healthcare provider communications. These create FHIR Communicat"
---
## Overview
Clinical Notes elements document clinical observations, assessments, plans, and other healthcare provider communications. These create FHIR Communication resources for structured clinical documentation.

## Function
```python
builder.add_notes(
    note: str,
    category: Optional[str] = None,
    id: Optional[str] = None,
) -> Communication
```

## Parameters

### Required Parameters
- **note**: The clinical note text

### Optional Parameters
- **category**: Type or category of clinical note
- **id**: Custom resource ID

## Basic Usage

### Simple Clinical Note
```python
from fhir_sdk import FHIRDocumentBuilder

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add basic clinical note
note = builder.add_notes(
    note="Patient tolerated procedure well with no complications"
)
```

### Categorized Clinical Note
```python
note = builder.add_notes(
    note="Patient is a 45-year-old male with history of hypertension and diabetes",
    category="history-note"
)
```

## Common Note Categories

### History and Background
```python
# Patient history summary
note = builder.add_notes(
    note="Patient is a 65-year-old retired teacher with a 20-year history of type 2 diabetes, hypertension, and hyperlipidemia. Lives independently with spouse.",
    category="history-note"
)

# Social history
note = builder.add_notes(
    note="Social history significant for 30 pack-year smoking history, quit 10 years ago. Drinks 1-2 glasses of wine weekly. Retired, financially stable, good family support.",
    category="social-history-note"
)

# Review of systems
note = builder.add_notes(
    note="ROS: Denies chest pain, palpitations, shortness of breath. No nausea, vomiting, or abdominal pain. No urinary symptoms or neurological complaints.",
    category="review-of-systems"
)
```

### Physical Examination Notes
```python
# General examination
note = builder.add_notes(
    note="Physical examination reveals well-appearing patient in no acute distress. Vital signs stable. HEENT normal, heart regular rate and rhythm, lungs clear bilaterally.",
    category="examination-note"
)

# Focused examination
note = builder.add_notes(
    note="Cardiovascular: Regular rate and rhythm, no murmurs, rubs, or gallops. No jugular venous distension. Peripheral pulses 2+ throughout.",
    category="cardiac-exam-note"
)

# Abnormal findings
note = builder.add_notes(
    note="Skin examination notable for 2cm pigmented lesion on left shoulder with irregular borders. Remainder of skin exam normal.",
    category="dermatologic-exam"
)
```

### Assessment and Clinical Impression
```python
# Primary assessment
note = builder.add_notes(
    note="Assessment: 1. Hypertension, well controlled on current regimen. 2. Type 2 diabetes with good glycemic control. 3. Hyperlipidemia, target LDL achieved.",
    category="assessment-note"
)

# Differential diagnosis
note = builder.add_notes(
    note="Differential diagnosis for chest pain includes musculoskeletal pain, GERD, and less likely cardiac etiology given normal ECG and enzymes.",
    category="differential-diagnosis"
)

# Clinical impression
note = builder.add_notes(
    note="Clinical impression: Acute upper respiratory infection, likely viral. No evidence of bacterial pneumonia or streptococcal pharyngitis.",
    category="clinical-impression"
)
```

### Treatment Plan
```python
# Medication plan
note = builder.add_notes(
    note="Plan: Continue current antihypertensive regimen. Start ACE inhibitor for cardioprotection. Recheck blood pressure in 4 weeks.",
    category="treatment-plan"
)

# Lifestyle interventions
note = builder.add_notes(
    note="Lifestyle plan: Weight loss goal of 10 pounds over 3 months. Increase physical activity to 30 minutes daily. Dietary consultation arranged.",
    category="lifestyle-plan"
)

# Follow-up plan
note = builder.add_notes(
    note="Follow-up plan: Return in 3 months for routine diabetes care. Sooner if blood sugars consistently >200 or symptoms of hyperglycemia.",
    category="follow-up-plan"
)
```

### Procedure Notes
```python
# Pre-procedure note
note = builder.add_notes(
    note="Pre-procedure: Patient consented for colonoscopy. Bowel prep completed adequately. No contraindications identified.",
    category="pre-procedure-note"
)

# Procedure description
note = builder.add_notes(
    note="Colonoscopy performed with conscious sedation. Complete examination to cecum achieved. Two small polyps identified and removed with snare technique.",
    category="procedure-note"
)

# Post-procedure note
note = builder.add_notes(
    note="Post-procedure: Patient tolerated procedure well. Vital signs stable. Discharged home with adult driver. Results discussed.",
    category="post-procedure-note"
)
```

### Progress Notes
```python
# Hospital progress note
note = builder.add_notes(
    note="Hospital day 3: Patient continues to improve. Pain well controlled. Ambulating independently. Wound healing appropriately. Plan for discharge tomorrow.",
    category="progress-note"
)

# Clinic progress note
note = builder.add_notes(
    note="Patient returns for 2-week follow-up. Reports significant improvement in symptoms. Medication well tolerated. Will continue current regimen.",
    category="progress-note"
)
```

### Prescription Notes
```python
# Prescription rationale
note = builder.add_notes(
    note="Prescribing antibiotic for confirmed streptococcal pharyngitis based on positive rapid strep test and clinical presentation.",
    category="prescription-note"
)

# Medication changes
note = builder.add_notes(
    note="Increasing metformin dose from 500mg to 1000mg twice daily due to elevated A1C. Patient counseled on potential GI side effects.",
    category="medication-adjustment"
)
```

### Discharge Notes
```python
# Hospital discharge
note = builder.add_notes(
    note="Patient discharged in stable condition after successful treatment of pneumonia. Completed 5-day course of IV antibiotics with good clinical response.",
    category="discharge-note"
)

# Emergency department discharge
note = builder.add_notes(
    note="ED discharge: Chest pain ruled out with negative troponins and normal ECG. Likely musculoskeletal etiology. Patient stable for home discharge.",
    category="ed-discharge-note"
)
```

### Consultation Notes
```python
# Specialist consultation
note = builder.add_notes(
    note="Cardiology consultation: Patient seen for chest pain evaluation. Stress test negative. Recommend continued medical management and risk factor modification.",
    category="consultation-note"
)

# Second opinion
note = builder.add_notes(
    note="Sought second opinion for treatment options. Concur with current management plan. Patient reassured about treatment approach.",
    category="second-opinion-note"
)
```

### Communication Notes
```python
# Phone call documentation
note = builder.add_notes(
    note="Phone call from patient reporting improved symptoms after 3 days of antibiotic therapy. Advised to complete full course.",
    category="phone-communication"
)

# Family communication
note = builder.add_notes(
    note="Discussed treatment plan with patient's daughter (medical POA). Family understands diagnosis and agrees with treatment approach.",
    category="family-communication"
)
```

### Quality and Safety Notes
```python
# Safety concerns
note = builder.add_notes(
    note="Patient education provided regarding medication interactions. Emphasized importance of informing all providers about current medications.",
    category="safety-note"
)

# Care coordination
note = builder.add_notes(
    note="Coordinated care with cardiology and endocrinology. All providers aware of current treatment plan and recent changes.",
    category="care-coordination"
)
```

## Structured Documentation

### SOAP Note Format
```python
# Subjective
note = builder.add_notes(
    note="Subjective: Patient reports 3 days of worsening chest pain, 7/10 severity, radiates to left arm, worse with exertion.",
    category="subjective-note"
)

# Objective  
note = builder.add_notes(
    note="Objective: VS: BP 140/90, HR 88, RR 16, O2 98% RA. Physical exam notable for regular heart rhythm, clear lungs, no peripheral edema.",
    category="objective-note"
)

# Assessment
note = builder.add_notes(
    note="Assessment: Chest pain, concerning for possible ACS given radiation pattern and exertional component. ECG shows no acute changes.",
    category="assessment-note"
)

# Plan
note = builder.add_notes(
    note="Plan: Serial troponins, stress test if enzymes negative. Cardiology consult. Continue aspirin, start beta-blocker.",
    category="plan-note"
)
```

### Problem-Oriented Documentation
```python
# Problem 1
note = builder.add_notes(
    note="Problem 1 - Hypertension: Well controlled on current ACE inhibitor. Blood pressure 128/82 today. Continue current dose, recheck in 3 months.",
    category="problem-note"
)

# Problem 2
note = builder.add_notes(
    note="Problem 2 - Type 2 diabetes: A1C improved to 7.2% from 8.1%. Continue metformin, add lifestyle counseling referral.",
    category="problem-note"
)
```

## Long-form Clinical Documentation
```python
# Comprehensive note
note = builder.add_notes(
    note="""Patient presents for routine follow-up of multiple chronic conditions. Since last visit, reports good adherence to medications and dietary modifications. Home blood pressure readings average 130/80. Blood sugars range 90-140 mg/dL. Denies chest pain, shortness of breath, or pedal edema. Physical examination notable for well-controlled hypertensive changes on fundoscopy, normal cardiac examination, and good peripheral circulation. Laboratory results show improved lipid profile and stable kidney function. Plan includes continuation of current medical regimen with minor adjustments as outlined above.""",
    category="comprehensive-note"
)
```

## Best Practices
1. Use clear, professional language appropriate for medical records
2. Document objectively with specific details and measurements
3. Include both normal and abnormal findings
4. Organize notes logically (chronological, by body system, by problem)
5. Use appropriate medical terminology and abbreviations
6. Include decision-making rationale for treatment changes
7. Document patient education and understanding
8. Note care coordination with other providers

## Note Categories
Common categories include:
- `"history-note"` - Patient history and background
- `"examination-note"` - Physical examination findings
- `"assessment-note"` - Clinical assessment and diagnosis
- `"plan-note"` - Treatment and management plans
- `"progress-note"` - Progress updates and status changes
- `"prescription-note"` - Medication-related documentation
- `"procedure-note"` - Procedure descriptions and outcomes
- `"discharge-note"` - Discharge summaries and instructions
- `"consultation-note"` - Specialist consultation findings

## Notes
- Clinical notes create Communication resources for provider documentation
- Multiple notes can be added for different aspects of care
- Categories help organize notes by purpose and content type
- Notes support clinical decision-making and continuity of care
- Proper documentation meets regulatory and quality requirements
