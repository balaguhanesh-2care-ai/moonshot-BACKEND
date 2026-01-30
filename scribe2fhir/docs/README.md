# FHIR SDK Documentation

## Overview
The FHIR SDK provides a simple, Pythonic interface for creating FHIR-compliant healthcare documents. This documentation covers all available elements and how to use them effectively.

## Quick Start
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

# Create document builder
builder = FHIRDocumentBuilder()

# Add patient (required for context)
builder.add_patient(
    name="John Doe", 
    age=30, 
    gender="male"
)

# Add clinical data
builder.add_encounter(
    encounter_type="Consultation",
    facility_name="General Hospital"
)

builder.add_symptom(
    code=create_codeable_concept(
        text="Headache",
        code="25064002",
        system="http://snomed.info/sct"
    )
)

# Generate FHIR Bundle
fhir_json = builder.convert_to_fhir()
```

## Element Documentation

### Core Elements
- **[Patient](PATIENT.md)** - Patient demographics and contact information
- **[Encounter](ENCOUNTER.md)** - Healthcare visits and interactions

### Clinical Observations  
- **[Symptoms](SYMPTOM.md)** - Patient-reported symptoms and chief complaints
- **[Vital Signs](VITAL_SIGNS.md)** - Measured physiological parameters
- **[Lab Findings](LAB_FINDINGS.md)** - Laboratory test results and interpretations
- **[Examination Findings](EXAMINATION_FINDINGS.md)** - Physical examination results
- **[Lifestyle History](LIFESTYLE_HISTORY.md)** - Social history and lifestyle factors

### Medical Conditions
- **[Medical Conditions](MEDICAL_CONDITION.md)** - Diagnoses, medical history, and health problems

### Medications
- **[Medication Prescriptions](MEDICATION_PRESCRIPTION.md)** - Prescribed medications and dosages  
- **[Medication History](MEDICATION_HISTORY.md)** - Current and past medication usage

### Orders and Requests
- **[Lab Test Ordering](LAB_TEST_ORDERING.md)** - Laboratory test orders and requirements
- **[Procedure Ordering](PROCEDURE_ORDERING.md)** - Imaging and procedure orders

### Medical History
- **[Family History](FAMILY_HISTORY.md)** - Family medical history and genetic factors
- **[Allergy History](ALLERGY_HISTORY.md)** - Allergies, intolerances, and adverse reactions
- **[Immunization History](IMMUNIZATION_HISTORY.md)** - Vaccination records and schedules
- **[Procedure History](PROCEDURE_HISTORY.md)** - Past surgical procedures and interventions

### Care Planning
- **[Follow-up Appointments](FOLLOWUP_APPOINTMENT.md)** - Scheduled appointments and referrals
- **[Patient Advice](PATIENT_ADVICE.md)** - Patient instructions and recommendations  
- **[Clinical Notes](CLINICAL_NOTES.md)** - Provider documentation and communication

## Code Input Best Practices

### Preferred: Using create_codeable_concept
```python
from fhir_sdk.types import create_codeable_concept

# With standard coding system
code = create_codeable_concept(
    text="Hypertension",
    code="38341003",
    system="http://snomed.info/sct",
    display="Hypertension"
)

builder.add_medical_condition_history(code=code)
```

### Alternative: Using String
```python
# Simple string input
builder.add_medical_condition_history(code="Hypertension")
```

## Standard Coding Systems

### SNOMED CT (Clinical Terms)
- **URL**: `http://snomed.info/sct`
- **Use for**: Conditions, procedures, medications, findings
- **Example**: Diabetes mellitus (`44054006`)

### LOINC (Lab and Clinical Observations)
- **URL**: `http://loinc.org`  
- **Use for**: Lab tests, vital signs, clinical measurements
- **Example**: Hemoglobin (`718-7`)

### RxNorm (Medications)
- **URL**: `http://www.nlm.nih.gov/research/umls/rxnorm`
- **Use for**: Medications and drug products
- **Example**: Acetaminophen 325mg (`313782`)

### CVX (Vaccines)
- **URL**: `http://hl7.org/fhir/sid/cvx`
- **Use for**: Vaccines and immunizations
- **Example**: COVID-19 mRNA vaccine (`207`)

## Workflow Example
```python
from fhir_sdk import FHIRDocumentBuilder, Severity, Interpretation
from fhir_sdk.types import create_codeable_concept
from datetime import datetime, timedelta

# 1. Create builder and add patient
builder = FHIRDocumentBuilder()
patient = builder.add_patient(
    name="Maria Garcia",
    age=42,
    gender="female"
)

# 2. Add encounter context
encounter = builder.add_encounter(
    encounter_type="Follow-up visit",
    facility_name="Primary Care Clinic"
)

# 3. Document symptoms
builder.add_symptom(
    code=create_codeable_concept(
        text="Chest pain",
        code="29857009", 
        system="http://snomed.info/sct"
    ),
    severity=Severity.MODERATE,
    onset=datetime.now() - timedelta(hours=6)
)

# 4. Record vital signs
builder.add_vital_finding(
    code=create_codeable_concept(
        text="Blood pressure",
        code="85354007",
        system="http://snomed.info/sct"
    ),
    value="145/92",
    unit="mmHg",
    interpretation=Interpretation.HIGH
)

# 5. Document medical history
builder.add_medical_condition_history(
    code=create_codeable_concept(
        text="Essential hypertension",
        code="59621000",
        system="http://snomed.info/sct"
    )
)

# 6. Prescribe medication
builder.add_medication_prescribed(
    medication=create_codeable_concept(
        text="Lisinopril 10mg",
        code="386872004",
        system="http://snomed.info/sct"
    )
)

# 7. Order tests
builder.add_test_prescribed(
    code=create_codeable_concept(
        text="Lipid panel",
        code="24331-1",
        system="http://loinc.org"
    )
)

# 8. Schedule follow-up
builder.add_followup(
    date=datetime.now() + timedelta(weeks=4),
    notes="Blood pressure recheck in 4 weeks"
)

# 9. Provide advice
builder.add_advice(
    note="Continue low-sodium diet and daily exercise",
    category="lifestyle-advice"
)

# 10. Generate FHIR bundle
fhir_bundle = builder.convert_to_fhir()
```

## Integration Notes
- Elements can be added in any order after patient/encounter
- Each element becomes a FHIR resource in the final bundle
- References between resources are automatically managed
- All elements support both coded and text-based input
- Bundle generation produces valid FHIR R5 JSON

## Error Handling
The SDK handles common issues gracefully:
- Missing patient creates resources without patient references
- Missing encounter creates resources without encounter context
- Invalid dates are handled with appropriate error messages
- Malformed input is validated and provides helpful feedback

## Performance Considerations
- Large numbers of elements (100+) are supported efficiently
- Bundle generation scales well with document size
- Memory usage is optimized for typical clinical documents
- JSON serialization is fast and reliable

## FHIR Compliance
- All generated resources conform to FHIR R5 specifications
- Required fields are automatically populated
- Extensions are used appropriately for additional data
- References maintain referential integrity within bundles
