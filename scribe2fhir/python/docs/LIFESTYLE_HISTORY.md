---
title: "Lifestyle History Element Documentation"
description: "Lifestyle History elements represent social history factors, habits, and lifestyle-related observations that can impact patient health. These include"
---
## Overview
Lifestyle History elements represent social history factors, habits, and lifestyle-related observations that can impact patient health. These include smoking, alcohol use, diet, exercise, travel history, and other social determinants.

## Function
```python
builder.add_lifestyle_history(
    code: CodeInput,
    status_value: Optional[str] = None,
    notes: Optional[str] = None,
    date: Optional[DateTimeInput] = None,
    id: Optional[str] = None,
) -> Observation
```

## Parameters

### Required Parameters
- **code**: The lifestyle factor or habit being documented

### Optional Parameters
- **status_value**: Current status of the lifestyle factor (e.g., "Active", "Inactive")
- **notes**: Additional details about the lifestyle factor
- **date**: When this information was recorded
- **id**: Custom resource ID

## Basic Usage

### Simple Lifestyle Factor (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)
builder.add_encounter()

# Add smoking status
lifestyle = builder.add_lifestyle_history(
    code=create_codeable_concept(
        text="Smoking status",
        code="72166-2",
        system="http://loinc.org",
        display="Tobacco smoking status"
    ),
    status_value="Former smoker"
)
```

### Using String (Alternative)
```python
lifestyle = builder.add_lifestyle_history(
    code="Smoking status",
    status_value="Never smoker"
)
```

### With Detailed Notes
```python
lifestyle = builder.add_lifestyle_history(
    code=create_codeable_concept(
        text="Alcohol use",
        code="74013-4",
        system="http://loinc.org"
    ),
    status_value="Active",
    notes="2-3 drinks per week, mainly wine with dinner"
)
```

## Common Lifestyle Factors

### Tobacco Use
```python
# Current smoker
lifestyle = builder.add_lifestyle_history(
    code=create_codeable_concept(
        text="Smoking status",
        code="72166-2", 
        system="http://loinc.org"
    ),
    status_value="Current smoker",
    notes="1 pack per day for 15 years"
)

# Former smoker
lifestyle = builder.add_lifestyle_history(
    code="Smoking status",
    status_value="Former smoker",
    notes="Quit 5 years ago, smoked 10 years"
)

# Never smoker
lifestyle = builder.add_lifestyle_history(
    code="Smoking status", 
    status_value="Never smoker"
)
```

### Alcohol Use
```python
# Active drinker
lifestyle = builder.add_lifestyle_history(
    code=create_codeable_concept(
        text="Alcohol use",
        code="74013-4",
        system="http://loinc.org"
    ),
    status_value="Active",
    notes="Social drinker, 4-5 drinks per week"
)

# Non-drinker
lifestyle = builder.add_lifestyle_history(
    code="Alcohol use",
    status_value="Never",
    notes="Has never consumed alcohol"
)

# Former drinker
lifestyle = builder.add_lifestyle_history(
    code="Alcohol use",
    status_value="Former",
    notes="Stopped drinking 3 years ago"
)
```

### Drug Use
```python
lifestyle = builder.add_lifestyle_history(
    code=create_codeable_concept(
        text="Illicit drug use",
        code="74204-9",
        system="http://loinc.org"
    ),
    status_value="Never",
    notes="Denies any recreational drug use"
)
```

### Diet and Nutrition
```python
# Dietary habits
lifestyle = builder.add_lifestyle_history(
    code="Dietary habits",
    status_value="Vegetarian",
    notes="Follows lacto-vegetarian diet for 5 years"
)

# Special diet
lifestyle = builder.add_lifestyle_history(
    code="Special diet",
    status_value="Active",
    notes="Low-sodium diet for hypertension management"
)
```

### Exercise and Physical Activity
```python
lifestyle = builder.add_lifestyle_history(
    code=create_codeable_concept(
        text="Exercise",
        code="LA11834-1",
        system="http://loinc.org"
    ),
    status_value="Regular",
    notes="Walks 30 minutes daily, gym 3x per week"
)

# Sedentary lifestyle
lifestyle = builder.add_lifestyle_history(
    code="Physical activity level",
    status_value="Sedentary",
    notes="Desk job, minimal physical activity"
)
```

### Sleep Patterns
```python
lifestyle = builder.add_lifestyle_history(
    code="Sleep patterns",
    status_value="Normal",
    notes="7-8 hours per night, no sleep disturbances"
)

# Sleep problems
lifestyle = builder.add_lifestyle_history(
    code="Sleep quality",
    status_value="Poor",
    notes="Difficulty falling asleep, frequent awakenings"
)
```

### Occupational History
```python
lifestyle = builder.add_lifestyle_history(
    code="Occupation",
    status_value="Active",
    notes="Software engineer, primarily desk work"
)

# Occupational hazards
lifestyle = builder.add_lifestyle_history(
    code="Occupational exposure",
    status_value="Previous",
    notes="Worked in construction for 10 years, asbestos exposure"
)
```

### Travel History
```python
from datetime import datetime, timedelta

# Recent travel
lifestyle = builder.add_lifestyle_history(
    code="Recent travel",
    status_value="Yes",
    notes="Returned from Thailand 2 weeks ago",
    date=datetime.now() - timedelta(days=14)
)

# No recent travel
lifestyle = builder.add_lifestyle_history(
    code="Travel history",
    status_value="None",
    notes="No international travel in past 2 years"
)
```

### Living Situation
```python
lifestyle = builder.add_lifestyle_history(
    code="Living situation",
    status_value="Independent",
    notes="Lives alone in apartment, able to perform ADLs"
)

# Social support
lifestyle = builder.add_lifestyle_history(
    code="Social support",
    status_value="Good",
    notes="Strong family support, married with 2 children"
)
```

### Sexual History
```python
lifestyle = builder.add_lifestyle_history(
    code="Sexual activity",
    status_value="Active",
    notes="Monogamous relationship, uses barrier contraception"
)
```

### Environmental Exposures
```python
lifestyle = builder.add_lifestyle_history(
    code="Environmental exposures",
    status_value="None reported",
    notes="No known toxic exposures, lives in suburban area"
)

# Pet allergies/exposures
lifestyle = builder.add_lifestyle_history(
    code="Pet ownership",
    status_value="Yes",
    notes="Has 2 cats, no known allergies"
)
```

## Status Values
Common status values used:
- **"Active"** - Currently engaged in the behavior
- **"Inactive"** - Not currently engaged but may have history
- **"Former"** - Previously engaged but stopped
- **"Never"** - Never engaged in the behavior
- **"Unknown"** - Status is unknown or unclear
- **"Occasional"** - Infrequent or sporadic engagement

## Time-based Documentation
```python
from datetime import datetime

# Current assessment
lifestyle = builder.add_lifestyle_history(
    code="Exercise habits",
    status_value="Improved",
    notes="Started regular exercise program 6 months ago",
    date=datetime.now()
)
```

## Quantified Lifestyle Factors
```python
# Smoking with pack-years
lifestyle = builder.add_lifestyle_history(
    code="Smoking history",
    status_value="Former smoker",
    notes="20 pack-year history (1 PPD x 20 years), quit 2019"
)

# Alcohol with units
lifestyle = builder.add_lifestyle_history(
    code="Alcohol consumption",
    status_value="Moderate",
    notes="14 units per week (within recommended limits)"
)
```

## Best Practices
1. Use create_codeable_concept with LOINC codes when available for standardized social history
2. Be non-judgmental in documentation - focus on health relevance
3. Include quantitative details when possible (pack-years, drinks per week)
4. Document both current status and historical information
5. Update lifestyle factors periodically as they may change
6. Include relevant timeframes for risk assessment
7. Consider cultural and social context in documentation

## Common LOINC Codes for Social History
- **Smoking status**: `72166-2`
- **Alcohol use**: `74013-4`
- **Drug use**: `74204-9`
- **Exercise**: `LA11834-1`
- **Occupation**: `85658-3`
- **Education level**: `82589-3`

## Notes
- Lifestyle history observations are categorized as "social-history"
- Information helps assess health risks and plan interventions
- Regular updates help track behavior changes over time
- Sensitive information should be documented with appropriate privacy considerations
- Multiple lifestyle factors contribute to comprehensive social history assessment
