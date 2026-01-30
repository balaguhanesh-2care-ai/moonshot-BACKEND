---
title: "Immunization History Element Documentation"
description: "Immunization History elements document vaccines and immunizations received by the patient. This information is essential for preventive care planning"
---
## Overview
Immunization History elements document vaccines and immunizations received by the patient. This information is essential for preventive care planning and outbreak management.

## Function
```python
builder.add_immunisation_history(
    vaccine: CodeInput,
    occurrence_date: Optional[DateTimeInput] = None,
    status: str = "completed",
    dose_number: Optional[int] = None,
    series_doses: Optional[int] = None,
    notes: Optional[str] = None,
    id: Optional[str] = None,
) -> Immunization
```

## Parameters

### Required Parameters
- **vaccine**: The vaccine name or code

### Optional Parameters
- **occurrence_date**: When the vaccine was administered
- **status**: Immunization status (default: "completed")
- **dose_number**: Which dose in a multi-dose series
- **series_doses**: Total number of doses in the series
- **notes**: Additional information about the vaccination
- **id**: Custom resource ID

## Basic Usage

### Simple Immunization (Preferred with CodeableConcept)
```python
from fhir_sdk import FHIRDocumentBuilder, ImmunizationStatus
from fhir_sdk.types import create_codeable_concept

builder = FHIRDocumentBuilder()
builder.add_patient(name="John Doe", age=30)

# Add immunization record
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="COVID-19 mRNA vaccine",
        code="207",
        system="http://hl7.org/fhir/sid/cvx",
        display="COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose"
    ),
    occurrence_date="2021-04-15",
    status=ImmunizationStatus.COMPLETED
)
```

### Using String (Alternative)
```python
immunization = builder.add_immunisation_history(
    vaccine="COVID-19 vaccine",
    occurrence_date="2021-04-15"
)
```

### Multi-dose Series
```python
from datetime import datetime, timedelta

# First dose
immunization1 = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Hepatitis B vaccine",
        code="08",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date=datetime.now() - timedelta(days=180),
    dose_number=1,
    series_doses=3,
    notes="Standard 3-dose series initiated"
)

# Second dose
immunization2 = builder.add_immunisation_history(
    vaccine="Hepatitis B vaccine",
    occurrence_date=datetime.now() - timedelta(days=150),
    dose_number=2,
    series_doses=3,
    notes="Second dose of 3-dose series"
)

# Final dose  
immunization3 = builder.add_immunisation_history(
    vaccine="Hepatitis B vaccine",
    occurrence_date=datetime.now() - timedelta(days=30),
    dose_number=3,
    series_doses=3,
    notes="Series completed"
)
```

## Common Adult Immunizations

### COVID-19 Vaccines
```python
# mRNA vaccine
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="COVID-19 mRNA vaccine (Pfizer)",
        code="207",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="2021-03-15",
    notes="First dose, second dose scheduled in 3 weeks"
)

# Booster dose
immunization = builder.add_immunisation_history(
    vaccine="COVID-19 mRNA vaccine booster",
    occurrence_date="2021-09-15",
    dose_number=3,
    notes="Booster dose 6 months after initial series"
)
```

### Influenza Vaccines
```python
# Annual flu shot
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Seasonal influenza vaccine",
        code="141",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="2023-10-01",
    notes="Annual influenza vaccination"
)
```

### Hepatitis Vaccines
```python
# Hepatitis A
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Hepatitis A vaccine",
        code="83",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="2020-06-01",
    dose_number=1,
    series_doses=2
)

# Hepatitis B (as shown above in series example)
```

### Travel Vaccines
```python
# Yellow fever
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Yellow fever vaccine",
        code="37",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="2022-01-15",
    notes="Required for travel to endemic areas, valid for 10 years"
)

# Japanese encephalitis
immunization = builder.add_immunisation_history(
    vaccine="Japanese encephalitis vaccine",
    occurrence_date="2022-02-01",
    notes="Travel to rural Asia, 2-dose series completed"
)

# Typhoid
immunization = builder.add_immunisation_history(
    vaccine="Typhoid vaccine",
    occurrence_date="2022-01-20",
    notes="Oral vaccine series, valid for 5 years"
)
```

### Tetanus and Diphtheria
```python
# Tdap booster
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Tetanus, diphtheria, pertussis vaccine",
        code="115",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="2020-08-15",
    notes="10-year booster, next due 2030"
)
```

### Pneumococcal Vaccines
```python
# PCV13
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Pneumococcal conjugate vaccine",
        code="133",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="2021-11-01",
    notes="PCV13 for immunocompromised patient"
)

# PPSV23
immunization = builder.add_immunisation_history(
    vaccine="Pneumococcal polysaccharide vaccine",
    occurrence_date="2022-11-01",
    notes="PPSV23 given 1 year after PCV13"
)
```

## Childhood Immunizations (Historical)
```python
# MMR
immunization = builder.add_immunisation_history(
    vaccine=create_codeable_concept(
        text="Measles, mumps, rubella vaccine",
        code="03",
        system="http://hl7.org/fhir/sid/cvx"
    ),
    occurrence_date="1995-12-15",
    notes="Childhood immunization, records from pediatrician"
)

# Varicella
immunization = builder.add_immunisation_history(
    vaccine="Varicella vaccine",
    occurrence_date="1996-01-15",
    notes="Given after natural chickenpox infection ruled out"
)
```

## Immunization Status Options
```python
from fhir_sdk import ImmunizationStatus

# Completed immunization
immunization = builder.add_immunisation_history(
    vaccine="Shingles vaccine",
    status=ImmunizationStatus.COMPLETED,
    occurrence_date="2023-05-01"
)

# Not done (contraindicated or refused)
immunization = builder.add_immunisation_history(
    vaccine="Live virus vaccine",
    status=ImmunizationStatus.NOT_DONE,
    notes="Contraindicated due to immunosuppression"
)
```

## Special Populations

### Immunocompromised Patients
```python
immunization = builder.add_immunisation_history(
    vaccine="Inactivated influenza vaccine",
    occurrence_date="2023-09-15",
    notes="Live vaccines contraindicated due to immunosuppressive therapy"
)
```

### Pregnant Patients
```python
immunization = builder.add_immunisation_history(
    vaccine="Tdap vaccine",
    occurrence_date="2023-08-15",
    notes="Given at 28 weeks gestation for maternal and neonatal protection"
)
```

### Healthcare Workers
```python
immunization = builder.add_immunisation_history(
    vaccine="Hepatitis B vaccine series",
    occurrence_date="2020-01-15",
    notes="Occupational requirement, titers confirmed adequate"
)
```

## Catch-up Immunizations
```python
# Adult catch-up
immunization = builder.add_immunisation_history(
    vaccine="Meningococcal conjugate vaccine",
    occurrence_date="2021-06-01",
    notes="Catch-up vaccination for college attendance"
)
```

## Adverse Reactions
```python
immunization = builder.add_immunisation_history(
    vaccine="Influenza vaccine",
    occurrence_date="2022-10-15",
    status=ImmunizationStatus.COMPLETED,
    notes="Mild local reaction - soreness at injection site for 2 days"
)

# Serious adverse event
immunization = builder.add_immunisation_history(
    vaccine="HPV vaccine",
    occurrence_date="2021-05-01",
    dose_number=1,
    series_doses=3,
    notes="Severe allergic reaction, series discontinued, reported to VAERS"
)
```

## Unknown or Incomplete Records
```python
immunization = builder.add_immunisation_history(
    vaccine="Childhood vaccinations",
    notes="Patient reports receiving 'all childhood shots' but records unavailable"
)

# Titer-based evidence
immunization = builder.add_immunisation_history(
    vaccine="Measles vaccine (presumed)",
    notes="Immune titers positive, vaccination history or natural infection"
)
```

## Best Practices
1. Use create_codeable_concept with CVX codes for vaccine identification
2. Include exact dates when available for timing calculations
3. Track multi-dose series with dose numbers
4. Document adverse reactions and contraindications
5. Include lot numbers and manufacturer when available
6. Note catch-up schedules for missed immunizations
7. Record titer results for immunity verification
8. Update records with new immunizations promptly

## Common CVX Vaccine Codes
- **COVID-19 mRNA**: `207`, `208`
- **Influenza**: `140`, `141`, `150`
- **Tdap**: `115`
- **MMR**: `03`
- **Varicella**: `21`
- **Hepatitis B**: `08`
- **HPV**: `62`, `137`
- **Pneumococcal**: `133` (PCV13), `23` (PPSV23)

## Notes
- Immunization records create Immunization resources
- Dose tracking helps ensure complete series
- Date information supports timing calculations for boosters
- Status tracking manages completed vs planned immunizations
- Integration with immunization registries requires proper coding
