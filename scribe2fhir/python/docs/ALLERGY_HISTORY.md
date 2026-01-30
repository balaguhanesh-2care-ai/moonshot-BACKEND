---
title: "Allergy History Element Documentation"
description: "Allergy History elements document allergic reactions, intolerances, and adverse reactions to substances including medications, foods, and environmenta"
---
## Overview
Allergy History elements document allergic reactions, intolerances, and adverse reactions to substances including medications, foods, and environmental factors. This information is critical for patient safety.

## Function
```python
builder.add_allergy_history(
    code: CodeInput,
    category: Optional[str] = None,
    clinical_status: str = "active",
    criticality: Optional[str] = None,
    reaction: Optional[str] = None,
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> AllergyIntolerance
```

## Parameters

### Required Parameters
- **code**: The allergen (substance causing the reaction)

### Optional Parameters
- **category**: Type of allergen (food, medication, environment, biologic)
- **clinical_status**: Current status of the allergy (default: "active")
- **criticality**: Severity potential (low, high)
- **reaction**: Description of the allergic reaction
- **notes**: Additional information about the allergy
- **id**: Custom resource ID

## Basic Usage

### Simple Allergy (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, AllergyCategory
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add medication allergy
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Penicillin",
        code="387207008",
        system="http://snomed.info/sct",
        display="Penicillin"
    ),
    category=AllergyCategory.MEDICATION
)
```

### Using String (Alternative)
```python
allergy = builder.add_allergy_history(
    code="Penicillin",
    category="medication"
)
```

### Detailed Allergy with Reaction
```python
from fhir_sdk import AllergyClinicalStatus, AllergyCriticality

allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Peanuts",
        code="256349002",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.FOOD,
    clinical_status=AllergyClinicalStatus.ACTIVE,
    criticality=AllergyCriticality.HIGH,
    reaction="Anaphylaxis with difficulty breathing",
    notes="Carries epinephrine auto-injector, avoid all tree nuts"
)
```

## Allergy Categories
```python
from fhir_sdk import AllergyCategory

# Medication allergies
allergy = builder.add_allergy_history(
    code="Sulfonamides",
    category=AllergyCategory.MEDICATION,
    reaction="Skin rash and hives"
)

# Food allergies  
allergy = builder.add_allergy_history(
    code="Shellfish",
    category=AllergyCategory.FOOD,
    criticality="high"
)

# Environmental allergies
allergy = builder.add_allergy_history(
    code="Pollen",
    category=AllergyCategory.ENVIRONMENT,
    reaction="Seasonal rhinitis and sneezing"
)

# Biologic allergies
allergy = builder.add_allergy_history(
    code="Latex",
    category=AllergyCategory.BIOLOGIC,
    reaction="Contact dermatitis"
)
```

## Clinical Status Options
```python
from fhir_sdk import AllergyClinicalStatus

# Active allergy
allergy = builder.add_allergy_history(
    code="Iodine contrast",
    clinical_status=AllergyClinicalStatus.ACTIVE
)

# Resolved allergy
allergy = builder.add_allergy_history(
    code="Milk protein",
    clinical_status=AllergyClinicalStatus.RESOLVED,
    notes="Childhood allergy, outgrew by age 5"
)

# Inactive allergy
allergy = builder.add_allergy_history(
    code="Eggs",
    clinical_status=AllergyClinicalStatus.INACTIVE,
    notes="Had reaction as child, now tolerates well"
)
```

## Criticality Levels
```python
from fhir_sdk import AllergyCriticality

# High criticality
allergy = builder.add_allergy_history(
    code="Bee venom",
    criticality=AllergyCriticality.HIGH,
    reaction="Anaphylaxis",
    notes="Requires immediate epinephrine if exposed"
)

# Low criticality
allergy = builder.add_allergy_history(
    code="Adhesive tape",
    criticality=AllergyCriticality.LOW,
    reaction="Mild skin irritation"
)
```

## Common Medication Allergies
```python
# Penicillin allergy
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Penicillin",
        code="387207008",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.MEDICATION,
    reaction="Skin rash and urticaria",
    notes="Avoid all penicillin derivatives"
)

# Sulfa allergy
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Sulfonamide",
        code="387406002",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.MEDICATION,
    reaction="Stevens-Johnson syndrome",
    criticality=AllergyCriticality.HIGH
)

# Codeine allergy
allergy = builder.add_allergy_history(
    code="Codeine",
    category=AllergyCategory.MEDICATION,
    reaction="Nausea and vomiting",
    notes="Avoid opioid combinations containing codeine"
)

# NSAIDs
allergy = builder.add_allergy_history(
    code="Ibuprofen",
    category=AllergyCategory.MEDICATION, 
    reaction="Gastric upset and bleeding",
    notes="History of GI bleeding with NSAIDs"
)
```

## Common Food Allergies
```python
# Tree nuts
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Tree nut",
        code="91935009",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.FOOD,
    criticality=AllergyCriticality.HIGH,
    reaction="Throat swelling and difficulty breathing"
)

# Dairy allergy
allergy = builder.add_allergy_history(
    code="Cow's milk protein",
    category=AllergyCategory.FOOD,
    reaction="Digestive upset and diarrhea",
    notes="Can tolerate lactose-free products"
)

# Shellfish
allergy = builder.add_allergy_history(
    code="Shellfish",
    category=AllergyCategory.FOOD,
    reaction="Hives and facial swelling",
    criticality=AllergyCriticality.HIGH
)

# Gluten sensitivity
allergy = builder.add_allergy_history(
    code="Gluten",
    category=AllergyCategory.FOOD,
    reaction="Abdominal pain and bloating",
    notes="Non-celiac gluten sensitivity"
)
```

## Environmental Allergies
```python
# Pollen allergies
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Tree pollen",
        code="256277009",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.ENVIRONMENT,
    reaction="Seasonal rhinitis, watery eyes, sneezing",
    notes="Worse in spring months (March-May)"
)

# Dust mites
allergy = builder.add_allergy_history(
    code="House dust mite",
    category=AllergyCategory.ENVIRONMENT,
    reaction="Asthma exacerbation and congestion",
    notes="Uses allergen-proof bedding"
)

# Pet dander
allergy = builder.add_allergy_history(
    code="Cat dander",
    category=AllergyCategory.ENVIRONMENT,
    reaction="Asthma and itchy eyes",
    notes="Symptoms within minutes of exposure"
)

# Mold
allergy = builder.add_allergy_history(
    code="Mold spores",
    category=AllergyCategory.ENVIRONMENT,
    reaction="Respiratory symptoms",
    notes="Worse in damp weather or basements"
)
```

## Contact Allergies
```python
# Latex
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Natural rubber latex",
        code="111088007",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.BIOLOGIC,
    reaction="Contact dermatitis and itching",
    notes="Use latex-free medical supplies"
)

# Nickel
allergy = builder.add_allergy_history(
    code="Nickel",
    category=AllergyCategory.ENVIRONMENT,
    reaction="Contact dermatitis",
    notes="Avoid jewelry containing nickel"
)
```

## Contrast and Dye Allergies
```python
# Iodine contrast
allergy = builder.add_allergy_history(
    code=create_codeable_concept(
        text="Iodinated contrast media",
        code="293586001",
        system="http://snomed.info/sct"
    ),
    category=AllergyCategory.MEDICATION,
    criticality=AllergyCriticality.HIGH,
    reaction="Anaphylactic reaction",
    notes="Premedication required if contrast studies needed"
)

# Gadolinium
allergy = builder.add_allergy_history(
    code="Gadolinium contrast",
    category=AllergyCategory.MEDICATION,
    reaction="Nausea and flushing",
    notes="Use alternative contrast agents for MRI"
)
```

## Drug Class Allergies
```python
# Entire drug class
allergy = builder.add_allergy_history(
    code="Beta-lactam antibiotics",
    category=AllergyCategory.MEDICATION,
    reaction="Urticaria and angioedema",
    notes="Includes penicillins and cephalosporins"
)

# ACE inhibitors
allergy = builder.add_allergy_history(
    code="ACE inhibitors",
    category=AllergyCategory.MEDICATION,
    reaction="Dry cough",
    notes="Switch to ARB if antihypertensive needed"
)
```

## Intolerance vs True Allergy
```python
# Drug intolerance (not immune-mediated)
allergy = builder.add_allergy_history(
    code="Metformin",
    category=AllergyCategory.MEDICATION,
    reaction="Gastrointestinal upset",
    notes="Intolerance - GI symptoms, not true allergic reaction"
)

# True allergic reaction
allergy = builder.add_allergy_history(
    code="Amoxicillin",
    category=AllergyCategory.MEDICATION,
    reaction="IgE-mediated urticaria",
    criticality=AllergyCriticality.HIGH,
    notes="Confirmed allergic reaction with eosinophilia"
)
```

## Best Practices
1. Use create_codeable_concept with SNOMED CT codes for allergens when available
2. Distinguish between allergies, intolerances, and side effects
3. Document specific reactions for clinical decision-making
4. Set appropriate criticality levels for risk assessment
5. Include avoidance strategies and alternative options
6. Update allergy status if reactions change over time
7. Document negative allergies (NKDA) when confirmed
8. Include drug class allergies to prevent cross-reactions

## Critical Allergy Information
Always document:
- **Specific allergen** and substance details
- **Type of reaction** and symptoms experienced
- **Severity** and criticality level
- **Alternative options** and cross-reactivity risks
- **Emergency treatment** requirements (epinephrine, etc.)

## Notes
- Allergy information is critical for medication safety
- Multiple allergies can be documented for comprehensive safety profiles
- Clinical status tracking helps manage resolved or inactive allergies
- Integration with prescribing systems helps prevent adverse reactions
- Regular review ensures allergy information stays current and accurate
