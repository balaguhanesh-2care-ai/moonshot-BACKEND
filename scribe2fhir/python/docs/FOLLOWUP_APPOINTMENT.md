---
title: "Follow-up Appointment Element Documentation"
description: "Follow-up Appointment elements represent scheduled appointments for continued patient care, including referrals to specialists and routine follow-up v"
---
## Overview
Follow-up Appointment elements represent scheduled appointments for continued patient care, including referrals to specialists and routine follow-up visits. These help ensure continuity of care.

## Function
```python
builder.add_followup(
    date: DateTimeInput,
    ref_doctor: Optional[str] = None,
    ref_specialty: Optional[str] = None,
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> Appointment
```

## Parameters

### Required Parameters
- **date**: The scheduled appointment date and time

### Optional Parameters
- **ref_doctor**: Name of the doctor for the appointment
- **ref_specialty**: Medical specialty for referral
- **notes**: Special instructions or requirements
- **id**: Custom resource ID

## Basic Usage

### Simple Follow-up
```python
from fhir_sdk import FHIRDocumentBuilder
from datetime import datetime, timedelta

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Schedule follow-up in 2 weeks
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=14)
)
```

### Follow-up with Specific Doctor
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=7),
    ref_doctor="Dr. Sarah Smith",
    notes="1-week follow-up for wound check"
)
```

### Specialist Referral
```python
# Referral to specialist
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=30),
    ref_specialty="Cardiology",
    notes="Cardiology consultation for chest pain evaluation"
)
```

### Comprehensive Follow-up
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=21),
    ref_doctor="Dr. Michael Johnson",
    ref_specialty="Endocrinology", 
    notes="Bring all previous lab results and current medication list"
)
```

## Common Specialty Referrals

### Medical Specialties
```python
# Cardiology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=2),
    ref_specialty="Cardiology",
    notes="Evaluation for cardiac murmur, bring recent ECG"
)

# Endocrinology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=3),
    ref_specialty="Endocrinology",
    notes="Diabetes management consultation, fasting labs needed"
)

# Gastroenterology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=4),
    ref_specialty="Gastroenterology",
    notes="Evaluation for IBD, bring symptom diary"
)

# Neurology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=6),
    ref_specialty="Neurology",
    notes="Headache evaluation, keep headache log until visit"
)

# Pulmonology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=2),
    ref_specialty="Pulmonology",
    notes="Chronic cough evaluation, bring chest X-rays"
)
```

### Surgical Specialties
```python
# Orthopedics
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=1),
    ref_specialty="Orthopedic Surgery",
    notes="Knee injury evaluation, bring MRI results"
)

# General Surgery
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=10),
    ref_specialty="General Surgery",
    notes="Post-operative wound check and suture removal"
)

# Urology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=3),
    ref_specialty="Urology",
    notes="Kidney stone management, bring recent imaging"
)
```

### Mental Health
```python
# Psychiatry
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=2),
    ref_specialty="Psychiatry",
    notes="Medication management for depression"
)

# Psychology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=1),
    ref_specialty="Psychology",
    notes="Cognitive behavioral therapy for anxiety"
)
```

### Women's Health
```python
# Obstetrics and Gynecology
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=4),
    ref_specialty="Obstetrics and Gynecology",
    notes="Annual well-woman exam and pap smear"
)

# Maternal-Fetal Medicine
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=2),
    ref_specialty="Maternal-Fetal Medicine",
    notes="High-risk pregnancy consultation"
)
```

## Routine Follow-up Types

### Post-procedure Follow-up
```python
# Surgical follow-up
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=7),
    ref_doctor="Dr. Anderson",
    notes="Post-operative check, suture removal if healed"
)

# Post-hospitalization
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=3),
    notes="Post-discharge follow-up within 72 hours as planned"
)
```

### Chronic Disease Management
```python
# Diabetes follow-up
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=90),
    notes="Quarterly diabetes check, A1C and foot exam"
)

# Hypertension monitoring
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=4),
    notes="Blood pressure recheck after medication adjustment"
)

# Cancer surveillance
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=180),
    ref_specialty="Oncology",
    notes="6-month cancer surveillance visit with imaging"
)
```

### Preventive Care
```python
# Annual physical
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=365),
    notes="Annual physical exam and health maintenance"
)

# Screening appointments
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=8),
    notes="Mammography screening appointment scheduled"
)
```

## Urgent Follow-up
```python
# Next day follow-up
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=1),
    notes="Urgent follow-up for blood pressure >180/110, check in 24 hours"
)

# Same week follow-up
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=3),
    ref_doctor="Dr. Emergency",
    notes="Follow-up for chest pain, if symptoms worsen go to ER"
)
```

## Special Instructions

### Fasting Requirements
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=14),
    notes="Come fasting for 12 hours, morning appointment for lab work"
)
```

### Preparation Instructions
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=2),
    ref_specialty="Gastroenterology",
    notes="Bring completed bowel prep questionnaire and medication list"
)
```

### Documentation to Bring
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=3),
    ref_doctor="Dr. Specialist",
    notes="Bring all imaging CDs, lab reports from last 6 months, and current medication bottles"
)
```

### Family or Caregiver Instructions
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=10),
    notes="Please bring family member to discuss treatment options and care plan"
)
```

## Scheduling Considerations

### Morning Appointments
```python
followup = builder.add_followup(
    date=datetime.now().replace(hour=9, minute=0) + timedelta(days=7),
    notes="Morning appointment preferred for fasting lab work"
)
```

### Flexible Scheduling
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=4),
    notes="Schedule within 4 weeks, patient has flexible availability"
)
```

### Telemedicine Follow-up
```python
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=7),
    notes="Virtual visit for medication review and symptom check"
)
```

## Multiple Follow-up Appointments
```python
# Primary care follow-up
followup1 = builder.add_followup(
    date=datetime.now() + timedelta(days=14),
    notes="Primary care follow-up for medication adjustment"
)

# Specialist follow-up  
followup2 = builder.add_followup(
    date=datetime.now() + timedelta(days=30),
    ref_specialty="Nephrology",
    notes="Kidney function evaluation in 1 month"
)
```

## Patient Education and Instructions
```python
# Lifestyle counseling follow-up
followup = builder.add_followup(
    date=datetime.now() + timedelta(weeks=6),
    notes="Review progress with diet and exercise plan, bring food diary"
)

# Medication education
followup = builder.add_followup(
    date=datetime.now() + timedelta(days=7),
    notes="Medication education session with pharmacist"
)
```

## Best Practices
1. Schedule follow-up appointments at appropriate intervals based on condition severity
2. Include specific instructions for preparation or documentation needed
3. Specify whether appointment is with primary care or specialist
4. Provide clear timeframes (urgent vs routine)
5. Include contact information for scheduling
6. Document rationale for follow-up timing
7. Consider patient preferences and availability
8. Include emergency contact instructions between visits

## Common Follow-up Intervals
- **Urgent conditions**: 1-3 days
- **Acute conditions**: 1-2 weeks  
- **Medication changes**: 2-4 weeks
- **Chronic stable conditions**: 3-6 months
- **Preventive care**: 6-12 months
- **Cancer surveillance**: 3-6 months
- **Post-surgical**: 1-2 weeks initially

## Notes
- Follow-up appointments create Appointment resources
- Patient and provider references are automatically included
- Scheduling helps ensure continuity of care
- Instructions support patient preparation and compliance
- Integration with scheduling systems facilitates appointment booking
