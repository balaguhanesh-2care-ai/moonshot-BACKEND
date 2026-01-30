---
title: "Family History Element Documentation"
description: "Family History elements document medical conditions and health information about the patient's family members. This information helps assess genetic r"
---
## Overview
Family History elements document medical conditions and health information about the patient's family members. This information helps assess genetic risk factors and guide preventive care decisions.

## Function
```python
builder.add_family_history(
    condition: CodeInput,
    relation: Union[str, tuple],
    onset: Optional[Union[str, int]] = None,
    status: str = "completed",
    notes: Optional[str] = None,
    deceased: Optional[bool] = None,
    id: Optional[str] = None,
) -> FamilyMemberHistory
```

## Parameters

### Required Parameters
- **condition**: The medical condition or health problem
- **relation**: Family relationship (father, mother, brother, etc.)

### Optional Parameters
- **onset**: When the condition started (age or year)
- **status**: Status of the family history record (default: "completed")
- **notes**: Additional information about the condition or family member
- **deceased**: Whether the family member is deceased
- **id**: Custom resource ID

## Basic Usage

### Simple Family History (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add family history
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Hypertension",
        code="38341003",
        system="http://snomed.info/sct",
        display="Hypertension"
    ),
    relation="Father"
)
```

### Using String (Alternative)
```python
family_history = builder.add_family_history(
    condition="Hypertension",
    relation="Father"
)
```

### With Onset and Additional Details
```python
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Type 2 diabetes mellitus",
        code="44054006",
        system="http://snomed.info/sct"
    ),
    relation="Mother",
    onset=55,  # Age at onset
    deceased=True,
    notes="Diagnosed at age 55, complications included neuropathy"
)
```

## Family Relationships
```python
# Immediate family
family_history = builder.add_family_history(condition="Heart disease", relation="Father")
family_history = builder.add_family_history(condition="Breast cancer", relation="Mother")
family_history = builder.add_family_history(condition="Asthma", relation="Brother")
family_history = builder.add_family_history(condition="Diabetes", relation="Sister")

# Children
family_history = builder.add_family_history(condition="ADHD", relation="Son")
family_history = builder.add_family_history(condition="Allergies", relation="Daughter")

# Extended family
family_history = builder.add_family_history(condition="Alzheimer disease", relation="Grandmother")
family_history = builder.add_family_history(condition="Prostate cancer", relation="Grandfather")
family_history = builder.add_family_history(condition="Depression", relation="Aunt")
family_history = builder.add_family_history(condition="Substance abuse", relation="Uncle")
```

## Common Family History Conditions

### Cardiovascular Conditions
```python
# Heart disease
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Coronary artery disease",
        code="53741008",
        system="http://snomed.info/sct"
    ),
    relation="Father",
    onset=62,
    notes="Had MI at age 62, underwent bypass surgery"
)

# Hypertension
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Essential hypertension",
        code="59621000",
        system="http://snomed.info/sct"
    ),
    relation="Mother",
    onset="middle age",
    notes="Well controlled with medication"
)

# Stroke
family_history = builder.add_family_history(
    condition="Stroke",
    relation="Grandfather",
    onset=75,
    deceased=True,
    notes="Ischemic stroke, died 2 years later"
)
```

### Cancer History
```python
# Breast cancer
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Breast cancer",
        code="254837009",
        system="http://snomed.info/sct"
    ),
    relation="Mother",
    onset=48,
    notes="Stage II, treated with surgery and chemotherapy, now in remission"
)

# Colon cancer
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Colorectal cancer",
        code="363346000",
        system="http://snomed.info/sct"
    ),
    relation="Father",
    onset=65,
    notes="Adenocarcinoma, detected during screening colonoscopy"
)

# Prostate cancer
family_history = builder.add_family_history(
    condition="Prostate cancer",
    relation="Grandfather",
    notes="Diagnosed in 80s, slow-growing type"
)
```

### Diabetes and Metabolic
```python
# Type 2 diabetes
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Type 2 diabetes mellitus",
        code="44054006",
        system="http://snomed.info/sct"
    ),
    relation="Mother",
    onset="2010",  # Year of diagnosis
    notes="Good control with metformin and lifestyle"
)

# Type 1 diabetes
family_history = builder.add_family_history(
    condition="Type 1 diabetes mellitus",
    relation="Sister",
    onset=12,  # Age at diagnosis
    notes="Childhood onset, insulin dependent"
)

# Thyroid disease
family_history = builder.add_family_history(
    condition="Hypothyroidism",
    relation="Mother",
    notes="Requires levothyroxine replacement therapy"
)
```

### Mental Health Conditions
```python
# Depression
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Major depressive disorder",
        code="35489007",
        system="http://snomed.info/sct"
    ),
    relation="Brother",
    onset="early 30s",
    notes="Responds well to antidepressant therapy"
)

# Bipolar disorder
family_history = builder.add_family_history(
    condition="Bipolar disorder",
    relation="Uncle",
    notes="Managed with mood stabilizers"
)

# Anxiety disorders
family_history = builder.add_family_history(
    condition="Generalized anxiety disorder",
    relation="Sister",
    onset=25,
    notes="Treated with therapy and medication"
)
```

### Neurological Conditions
```python
# Alzheimer disease
family_history = builder.add_family_history(
    condition=create_codeable_concept(
        text="Alzheimer disease",
        code="26929004",
        system="http://snomed.info/sct"
    ),
    relation="Grandmother",
    onset=78,
    deceased=True,
    notes="Progressive dementia, died at age 85"
)

# Parkinson disease
family_history = builder.add_family_history(
    condition="Parkinson disease", 
    relation="Grandfather",
    onset=72,
    notes="Tremor and mobility issues, managed with medications"
)
```

### Genetic Conditions
```python
# Hereditary conditions
family_history = builder.add_family_history(
    condition="Sickle cell disease",
    relation="Brother",
    notes="Confirmed by genetic testing, requires regular monitoring"
)

# Carrier status
family_history = builder.add_family_history(
    condition="Cystic fibrosis carrier",
    relation="Sister",
    notes="Identified through partner screening"
)
```

## Onset Documentation

### Age at Onset
```python
# Specific age
family_history = builder.add_family_history(
    condition="Diabetes",
    relation="Father",
    onset=45
)
```

### Year of Diagnosis
```python  
# Specific year
family_history = builder.add_family_history(
    condition="Cancer",
    relation="Mother", 
    onset="2015"
)
```

### Approximate Timing
```python
# General timeframe
family_history = builder.add_family_history(
    condition="Heart disease",
    relation="Grandfather",
    onset="elderly",
    notes="Developed heart problems in his 70s"
)
```

## Deceased Family Members
```python
family_history = builder.add_family_history(
    condition="Lung cancer",
    relation="Father",
    onset=68,
    deceased=True,
    notes="Smoker for 40 years, died 6 months after diagnosis"
)
```

## Negative Family History
```python
# Document absence of significant conditions
family_history = builder.add_family_history(
    condition="No known heart disease",
    relation="Family",
    notes="No family history of coronary artery disease, MI, or sudden cardiac death"
)

family_history = builder.add_family_history(
    condition="No known cancer history",
    relation="Family",
    notes="No family history of breast, colon, or other cancers"
)
```

## Multiple Conditions in Same Family Member
```python
# Father with multiple conditions
family_history = builder.add_family_history(
    condition="Hypertension",
    relation="Father",
    onset=45,
    notes="Also has diabetes and high cholesterol"
)

family_history = builder.add_family_history(
    condition="Type 2 diabetes",
    relation="Father", 
    onset=50,
    notes="Developed 5 years after hypertension diagnosis"
)
```

## Unknown or Incomplete History
```python
family_history = builder.add_family_history(
    condition="Unknown medical history",
    relation="Biological father",
    notes="Patient adopted, biological family history unknown"
)

family_history = builder.add_family_history(
    condition="Heart problems", 
    relation="Grandfather",
    notes="Patient recalls heart issues but doesn't know specifics"
)
```

## Best Practices
1. Use create_codeable_concept with SNOMED CT codes for standardized conditions
2. Document both positive and negative family history
3. Include age at onset when known for risk assessment
4. Note deceased status and cause of death when relevant
5. Record multiple conditions per family member separately
6. Include approximate onset even if exact age unknown
7. Document adoption or unknown family history situations
8. Update family history as new information becomes available

## Common Medical Conditions for Family History
- **Cardiovascular**: Heart disease, hypertension, stroke
- **Cancer**: Breast, colon, prostate, lung, ovarian
- **Metabolic**: Diabetes, thyroid disease, obesity
- **Neurological**: Dementia, Parkinson's, epilepsy
- **Mental Health**: Depression, bipolar, anxiety, substance abuse
- **Other**: Asthma, arthritis, kidney disease, bleeding disorders

## Notes
- Family history helps assess genetic and familial risk factors
- Information guides screening recommendations and preventive care
- Multiple family members can have the same condition
- Onset timing helps estimate age-related risks
- Regular updates capture new diagnoses in family members
- Documentation supports genetic counseling referrals when appropriate
