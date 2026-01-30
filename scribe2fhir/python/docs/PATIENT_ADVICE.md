---
title: "Patient Advice Element Documentation"
description: "Patient Advice elements document instructions, recommendations, and guidance provided to patients about their care, lifestyle modifications, and treat"
---
## Overview
Patient Advice elements document instructions, recommendations, and guidance provided to patients about their care, lifestyle modifications, and treatment adherence. These create FHIR CarePlan resources.

## Function
```python
builder.add_advice(
    note: str,
    category: Optional[str] = None,
    id: Optional[str] = None,
) -> CarePlan
```

## Parameters

### Required Parameters
- **note**: The advice or instruction text

### Optional Parameters
- **category**: Type or category of advice
- **id**: Custom resource ID

## Basic Usage

### Simple Advice
```python
from fhir_sdk import FHIRDocumentBuilder

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add basic advice
advice = builder.add_advice(
    note="Drink plenty of water"
)
```

### Categorized Advice
```python
advice = builder.add_advice(
    note="Avoid high-sodium foods and processed meals",
    category="dietary-advice"
)
```

## Common Advice Categories

### Dietary Advice
```python
# General dietary guidance
advice = builder.add_advice(
    note="Follow a low-sodium diet with less than 2000mg sodium per day",
    category="dietary-advice"
)

advice = builder.add_advice(
    note="Increase fiber intake with fruits, vegetables, and whole grains", 
    category="dietary-advice"
)

advice = builder.add_advice(
    note="Limit saturated fats and choose lean proteins",
    category="dietary-advice"
)

# Specific dietary restrictions
advice = builder.add_advice(
    note="Avoid grapefruit and grapefruit juice while taking this medication",
    category="dietary-restriction"
)

advice = builder.add_advice(
    note="Follow diabetic diet with consistent carbohydrate counting",
    category="dietary-management"
)
```

### Lifestyle Advice
```python
# Exercise and activity
advice = builder.add_advice(
    note="Engage in 150 minutes of moderate aerobic activity per week",
    category="exercise-advice"
)

advice = builder.add_advice(
    note="Start with 10-minute walks and gradually increase duration",
    category="activity-modification"
)

# Sleep hygiene
advice = builder.add_advice(
    note="Maintain consistent sleep schedule, aim for 7-9 hours per night",
    category="sleep-hygiene"
)

# Stress management
advice = builder.add_advice(
    note="Practice stress reduction techniques such as meditation or deep breathing",
    category="stress-management"
)

# Smoking cessation
advice = builder.add_advice(
    note="Consider nicotine replacement therapy and smoking cessation program",
    category="smoking-cessation"
)
```

### Medication Advice
```python
# Adherence instructions
advice = builder.add_advice(
    note="Take medications at the same time each day to maintain consistent levels",
    category="medication-adherence"
)

advice = builder.add_advice(
    note="Do not stop blood pressure medications suddenly - taper as directed",
    category="medication-safety"
)

# Administration instructions
advice = builder.add_advice(
    note="Take iron supplements on empty stomach, separate from calcium by 2 hours",
    category="medication-administration"
)

# Monitoring advice
advice = builder.add_advice(
    note="Monitor blood sugar levels twice daily and keep a log",
    category="self-monitoring"
)
```

### Activity and Movement
```python
# Activity restrictions
advice = builder.add_advice(
    note="Avoid heavy lifting over 10 pounds for 6 weeks after surgery",
    category="activity-restriction"
)

advice = builder.add_advice(
    note="No driving while taking narcotic pain medications",
    category="safety-restriction"
)

# Rehabilitation advice
advice = builder.add_advice(
    note="Perform physical therapy exercises as demonstrated 3 times daily",
    category="rehabilitation"
)

# Gradual activity increase
advice = builder.add_advice(
    note="Gradually return to normal activities as tolerated over 2 weeks",
    category="activity-progression"
)
```

### Self-Care and Monitoring
```python
# Symptom monitoring
advice = builder.add_advice(
    note="Monitor for signs of infection: fever, increased redness, or drainage",
    category="symptom-monitoring"
)

advice = builder.add_advice(
    note="Check blood pressure daily and record in log book",
    category="self-monitoring"
)

# Wound care
advice = builder.add_advice(
    note="Keep surgical incision clean and dry, change dressing daily",
    category="wound-care"
)

# Pain management
advice = builder.add_advice(
    note="Use ice packs for 15-20 minutes every 2-3 hours for swelling",
    category="pain-management"
)
```

### Prevention and Health Maintenance
```python
# Vaccination advice
advice = builder.add_advice(
    note="Schedule annual influenza vaccination each fall",
    category="prevention"
)

# Screening advice
advice = builder.add_advice(
    note="Schedule mammography annually starting at age 40",
    category="screening"
)

# Sun protection
advice = builder.add_advice(
    note="Use sunscreen SPF 30+ daily and avoid peak sun exposure 10am-4pm",
    category="prevention"
)
```

### Hydration and Nutrition
```python
# Hydration
advice = builder.add_advice(
    note="Drink at least 8 glasses of water daily unless fluid restricted"
)

advice = builder.add_advice(
    note="Increase fluid intake during hot weather and exercise",
    category="hydration"
)

# Nutrition for specific conditions
advice = builder.add_advice(
    note="Eat regular meals to prevent blood sugar fluctuations",
    category="diabetes-management"
)

advice = builder.add_advice(
    note="Include calcium-rich foods or supplements for bone health",
    category="bone-health"
)
```

### Emergency and Safety Instructions
```python
# When to seek care
advice = builder.add_advice(
    note="Call 911 or go to ER immediately for chest pain, shortness of breath, or severe headache",
    category="emergency-instructions"
)

advice = builder.add_advice(
    note="Contact office if temperature exceeds 101°F or wound shows signs of infection",
    category="warning-signs"
)

# Safety precautions
advice = builder.add_advice(
    note="Rise slowly from sitting or lying position to prevent dizziness",
    category="safety-precaution"
)
```

### Follow-up Instructions
```python
# Appointment scheduling
advice = builder.add_advice(
    note="Schedule follow-up appointment in 2 weeks or sooner if symptoms worsen",
    category="follow-up-instruction"
)

# Test scheduling
advice = builder.add_advice(
    note="Schedule lab work in 1 week, results will be reviewed at next visit",
    category="testing-instruction"
)
```

## Condition-Specific Advice

### Diabetes Management
```python
advice = builder.add_advice(
    note="Check feet daily for cuts, sores, or signs of infection",
    category="diabetes-care"
)

advice = builder.add_advice(
    note="Rotate insulin injection sites to prevent lipodystrophy",
    category="diabetes-care"
)
```

### Hypertension Management
```python
advice = builder.add_advice(
    note="Limit sodium intake to less than 2300mg per day",
    category="hypertension-management"
)

advice = builder.add_advice(
    note="Monitor blood pressure at home and keep a record",
    category="hypertension-monitoring"
)
```

### Heart Disease Management
```python
advice = builder.add_advice(
    note="Stop activity and rest if you experience chest pain or shortness of breath",
    category="cardiac-precaution"
)

advice = builder.add_advice(
    note="Take aspirin daily as prescribed for heart protection",
    category="cardiac-medication"
)
```

### Mental Health Support
```python
advice = builder.add_advice(
    note="Continue therapy sessions and practice coping strategies discussed",
    category="mental-health"
)

advice = builder.add_advice(
    note="Maintain social connections and engage in enjoyable activities",
    category="mental-wellness"
)
```

## Multiple Related Advice Items
```python
# Comprehensive discharge instructions
advice1 = builder.add_advice(
    note="Take pain medication as needed, do not exceed maximum daily dose",
    category="post-operative-care"
)

advice2 = builder.add_advice(
    note="Keep incision clean and dry, shower after 48 hours",
    category="wound-care"
)

advice3 = builder.add_advice(
    note="No heavy lifting or strenuous activity for 2 weeks",
    category="activity-restriction"
)

advice4 = builder.add_advice(
    note="Call office for fever >101°F, increased pain, or wound drainage",
    category="warning-signs"
)
```

## Long-term Care Instructions
```python
# Chronic disease self-management
advice = builder.add_advice(
    note="Continue current medications as prescribed, monitor for side effects, and maintain regular follow-up appointments. Keep a daily symptom log and bring to all visits. Contact healthcare provider before making any changes to your treatment plan.",
    category="chronic-disease-management"
)
```

## Best Practices
1. Use clear, actionable language that patients can understand
2. Organize advice by category for easier patient comprehension
3. Include specific measurements and timeframes when applicable
4. Provide both positive actions (do this) and restrictions (avoid this)
5. Include emergency contact information and warning signs
6. Tailor advice to patient's specific condition and circumstances
7. Use teach-back methods to ensure patient understanding
8. Document advice in patient-friendly language

## Advice Categories
Common categories include:
- `"dietary-advice"` - Nutrition and diet guidance
- `"exercise-advice"` - Physical activity recommendations
- `"medication-adherence"` - Taking medications properly
- `"self-monitoring"` - Home monitoring instructions
- `"safety-precaution"` - Safety measures and restrictions
- `"symptom-monitoring"` - What symptoms to watch for
- `"lifestyle-modification"` - Behavior change recommendations
- `"emergency-instructions"` - When to seek immediate care

## Notes
- Advice creates CarePlan resources with patient instructions
- Multiple advice items can be provided for comprehensive care planning
- Categories help organize instructions by topic
- Clear documentation supports patient education and compliance
- Advice should be culturally appropriate and health literacy appropriate
