---
title: "Patient Element Documentation"
description: "The Patient element represents a person who is the subject of healthcare services. This is typically the first element you'll add to any FHIR document"
---
## Overview
The Patient element represents a person who is the subject of healthcare services. This is typically the first element you'll add to any FHIR document, as it provides the context for all other clinical information.

## Function
```python
builder.add_patient(
    name: Union[str, dict, HumanName],
    age: Optional[Union[int, Tuple[int, str]]] = None,
    birth_date: Optional[DateTimeInput] = None,
    gender: Optional[str] = None,
    identifiers: Optional[List[Tuple[str, Union[str, Tuple[str, str]]]]] = None,
    address: Optional[Union[str, dict]] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    id: Optional[str] = None,
) -> Patient
```

## Parameters

### Required Parameters
- **name**: Patient's full name as a string (e.g., "John Doe")

### Optional Parameters
- **age**: Patient's age as integer (years) or tuple (value, unit)
- **birth_date**: Date of birth (alternative to age)
- **gender**: Patient's gender ("male", "female", "other", "unknown")
- **identifiers**: List of patient identifiers (ID number, ID type)
- **address**: Patient's address as string
- **phone**: Phone number
- **email**: Email address
- **id**: Custom resource ID

## Basic Usage

### Simple Patient
```python
from fhir_sdk import FHIRDocumentBuilder

builder = FHIRDocumentBuilder()

# Add patient with minimal information
patient = builder.add_patient(
    name="John Doe",
    age=30,
    gender="male"
)
```

### Comprehensive Patient
```python
# Add patient with full details
patient = builder.add_patient(
    name="Sarah Johnson",
    age=28,
    gender="female",
    identifiers=[
        ("ABHA-1234567890", "ABHA"),
        ("MRN-001234", "MRN"),
        ("9876543210", "mobile")
    ],
    address="123 Main Street, New York, NY 10001",
    phone="555-123-4567",
    email="sarah.johnson@email.com"
)
```

### Using Birth Date Instead of Age
```python
from datetime import date

patient = builder.add_patient(
    name="Michael Brown",
    birth_date=date(1990, 5, 15),
    gender="male"
)
```

## Identifier Types
Common identifier types supported:
- `"ABHA"` - Ayushman Bharat Health Account
- `"MRN"` - Medical Record Number
- `"mobile"` - Mobile phone number
- `"NI"` - National Identifier
- `"PPN"` - Passport Number
- `"DL"` - Driver's License
- `"SS"` - Social Security Number

## Name Formats
The name parameter accepts:
- **String**: `"John Doe"`
- **Dictionary**: `{"given": ["John"], "family": "Doe"}`
- **HumanName object**: For complex name structures

## Best Practices
1. Always add a patient before adding any other clinical elements
2. Include at least one identifier for patient matching
3. Use consistent name format throughout your application
4. Provide either age or birth_date for age-sensitive calculations
5. Include contact information for patient communication

## Notes
- Patient serves as the subject reference for all other clinical resources
- The patient ID is automatically used in references from other resources
- Multiple identifiers help with patient matching across systems
- Age is stored as an extension when provided (FHIR R5 standard)
