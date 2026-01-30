---
title: "scribe2fhir Element Requirements and Constraints"
description: "This document defines the specific requirements and constraints for each scribe2fhir SDK element, specifying exactly what FHIR resources should contai"
---
This document defines the specific requirements and constraints for each scribe2fhir SDK element, specifying exactly what FHIR resources should contain to ensure consistency across all language implementations.

## Element Categories

### Core Elements
Elements that establish context for clinical data:
- **Patient**: Demographics and administrative information
- **Encounter**: Healthcare interaction context

### Clinical Observation Elements  
Elements that represent clinical findings and measurements:
- **Symptom**: Patient-reported symptoms (Observation category: survey)
- **Vital Signs**: Physiological measurements (Observation category: vital-signs)
- **Lab Findings**: Laboratory results (Observation category: laboratory)
- **Examination Findings**: Physical exam results (Observation category: exam)
- **Lifestyle History**: Social history factors (Observation category: social-history)

### Medical History Elements
Elements that document patient's medical background:
- **Medical Condition History**: Problem list conditions (Condition category: problem-list-item)
- **Medical Condition Encountered**: Current visit diagnoses (Condition category: encounter-diagnosis)

### Medication Elements
Elements related to medications:
- **Medication Prescription**: Active prescriptions (MedicationRequest)
- **Medication History**: Current/past medications (MedicationStatement)

### Service Request Elements
Elements for ordering services:
- **Lab Test Ordering**: Laboratory test orders (ServiceRequest category: laboratory)
- **Procedure Ordering**: Procedure/imaging orders (ServiceRequest category: procedure)

### Historical Information Elements
Elements documenting patient's medical background:
- **Family History**: Family medical conditions (FamilyMemberHistory)
- **Allergy History**: Allergies and intolerances (AllergyIntolerance)  
- **Immunization History**: Vaccination records (Immunization)
- **Procedure History**: Past procedures (Procedure)

### Care Coordination Elements
Elements for care planning and communication:
- **Follow-up Appointment**: Scheduled appointments (Appointment)
- **Patient Advice**: Care instructions (CarePlan)
- **Clinical Notes**: Provider documentation (Communication)

## Resource Field Requirements by Element

### Patient Resource Requirements
```json
{
  "resourceType": "Patient",
  "id": "{uuid-v4}",
  "name": [
    {
      "text": "{patient-name}",
      "given": ["{first-name}"],
      "family": "{last-name}"
    }
  ],
  "gender": "{male|female|other|unknown}",
  "birthDate": "{YYYY-MM-DD}",
  "extension": [
    {
      "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
      "valueQuantity": {
        "value": 30,
        "unit": "years",
        "system": "http://unitsofmeasure.org",
        "code": "a"
      }
    }
  ],
  "identifier": [
    {
      "value": "{identifier-value}",
      "type": {
        "coding": [
          {
            "system": "{identifier-system}",
            "code": "{identifier-code}"
          }
        ]
      }
    }
  ],
  "address": [
    {
      "text": "{address-string}"
    }
  ],
  "telecom": [
    {
      "system": "phone",
      "value": "{phone-number}"
    },
    {
      "system": "email", 
      "value": "{email-address}"
    }
  ]
}
```

**Constraints**:
- Name MUST include text field
- Either birthDate OR age extension (not both)
- Age extension MUST use specified URL and UCUM units
- Identifiers MUST include type with coding
- Address stored as single text field
- Telecom limited to phone and email

### Observation Resource Requirements (All Types)
```json
{
  "resourceType": "Observation", 
  "id": "{uuid-v4}",
  "status": "{final|preliminary|registered|cancelled}",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "{survey|vital-signs|laboratory|exam|social-history}",
          "display": "{category-display}"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "{coding-system}",
        "code": "{code-value}",
        "display": "{display-name}"
      }
    ],
    "text": "{observation-name}"
  },
  "subject": {
    "reference": "Patient/{patient-id}",
    "display": "{patient-name}"
  },
  "encounter": {
    "reference": "Encounter/{encounter-id}"
  },
  "effectiveDateTime": "{iso-datetime}",
  "effectivePeriod": {
    "start": "{iso-datetime}",
    "end": "{iso-datetime}"
  },
  "valueQuantity": {
    "value": 120,
    "unit": "mmHg",
    "system": "http://unitsofmeasure.org",
    "code": "mm[Hg]"
  },
  "valueString": "{text-value}",
  "interpretation": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "{N|H|L|A}",
          "display": "{Normal|High|Low|Abnormal}"
        }
      ],
      "text": "{interpretation-text}"
    }
  ],
  "component": [
    {
      "code": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "{component-code}",
            "display": "{component-display}"
          }
        ],
        "text": "{component-name}"
      },
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "{value-code}",
            "display": "{value-display}"
          }
        ],
        "text": "{value-text}"
      }
    }
  ],
  "note": [
    {
      "text": "{note-text}"
    }
  ]
}
```

**Constraints by Observation Type**:

**Symptoms (category: survey)**:
- Default status: "final"
- Components for severity (SEV), laterality (272741003), finding status (408729009)
- Use effectiveDateTime for single point, effectivePeriod for onset/offset

**Vital Signs (category: vital-signs)**:
- Numeric values use valueQuantity, compound values use valueString
- String values include unit in text (e.g., "120/80 mmHg")

**Lab Findings (category: laboratory)**:
- Support both numeric and string values
- Interpretation required for abnormal values

**Examination Findings (category: exam)**:
- Primarily text-based findings in valueString
- Minimal use of interpretation

**Lifestyle History (category: social-history)**:
- Status values in valueString ("Active", "Inactive", "Former", "Never")

### Condition Resource Requirements
```json
{
  "resourceType": "Condition",
  "id": "{uuid-v4}",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "{active|inactive|resolved|recurrence}",
        "display": "{status-display}"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "code": "{unconfirmed|provisional|differential|confirmed|refuted}",
        "display": "{verification-display}"
      }
    ]
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-category",
          "code": "{problem-list-item|encounter-diagnosis}",
          "display": "{category-display}"
        }
      ]
    }
  ],
  "severity": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "{severity-code}",
        "display": "{severity-display}"
      }
    ],
    "text": "{severity-text}"
  },
  "code": {
    "coding": [
      {
        "system": "{coding-system}",
        "code": "{condition-code}",
        "display": "{condition-display}"
      }
    ],
    "text": "{condition-name}"
  },
  "bodySite": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "{laterality-code}",
          "display": "{laterality-display}"
        }
      ],
      "text": "{body-site-text}"
    }
  ],
  "subject": {
    "reference": "Patient/{patient-id}",
    "display": "{patient-name}"
  },
  "encounter": {
    "reference": "Encounter/{encounter-id}"
  },
  "onsetDateTime": "{iso-datetime}",
  "onsetPeriod": {
    "start": "{iso-datetime}",
    "end": "{iso-datetime}"
  },
  "abatementDateTime": "{iso-datetime}",
  "note": [
    {
      "text": "{note-text}"
    }
  ]
}
```

**Constraints**:
- History conditions: category "problem-list-item", no default verification
- Encounter diagnoses: category "encounter-diagnosis", default verification "confirmed"
- Severity stored in severity field (not extension)
- Laterality stored in bodySite array
- Use onsetPeriod when both onset and offset provided

### MedicationRequest Resource Requirements
```json
{
  "resourceType": "MedicationRequest",
  "id": "{uuid-v4}",
  "status": "{active|on-hold|cancelled|completed}",
  "intent": "{proposal|plan|order|original-order}",
  "medication": {
    "coding": [
      {
        "system": "{medication-system}",
        "code": "{medication-code}",
        "display": "{medication-display}"
      }
    ],
    "text": "{medication-name}"
  },
  "subject": {
    "reference": "Patient/{patient-id}",
    "display": "{patient-name}"
  },
  "encounter": {
    "reference": "Encounter/{encounter-id}"
  },
  "authoredOn": "{iso-datetime}",
  "dosageInstruction": [
    {
      "text": "{dosage-text}",
      "route": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "{route-code}",
            "display": "{route-display}"
          }
        ],
        "text": "{route-text}"
      },
      "timing": {
        "repeat": {
          "frequency": 3,
          "period": 1,
          "periodUnit": "d",
          "when": ["{timing-code}"]
        }
      },
      "doseAndRate": [
        {
          "doseQuantity": {
            "value": 1,
            "unit": "tablet",
            "system": "http://unitsofmeasure.org"
          }
        }
      ]
    }
  ],
  "dispenseRequest": {
    "quantity": {
      "value": 30,
      "unit": "tablet"
    },
    "expectedSupplyDuration": {
      "value": 7,
      "unit": "d",
      "system": "http://unitsofmeasure.org"
    },
    "numberOfRepeatsAllowed": 2
  },
  "reasonCode": [
    {
      "text": "{reason-text}"
    }
  ],
  "note": [
    {
      "text": "{note-text}"
    }
  ]
}
```

**Constraints**:
- Default status: "active", intent: "order"
- Timing codes stored in timing.repeat.when array (not timing.code)
- Route codes from SNOMED CT
- Duration and quantity create dispenseRequest object

### ServiceRequest Resource Requirements
```json
{
  "resourceType": "ServiceRequest",
  "id": "{uuid-v4}",
  "status": "{draft|active|on-hold|revoked|completed}",
  "intent": "{proposal|plan|directive|order}",
  "category": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "{108252007|387713003}",
          "display": "{Laboratory procedure|Surgical procedure}"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "{coding-system}",
        "code": "{service-code}",
        "display": "{service-display}"
      }
    ],
    "text": "{service-name}"
  },
  "subject": {
    "reference": "Patient/{patient-id}",
    "display": "{patient-name}"
  },
  "encounter": {
    "reference": "Encounter/{encounter-id}"
  },
  "occurrenceDateTime": "{iso-datetime}",
  "priority": "{routine|urgent|asap|stat}",
  "reasonCode": [
    {
      "text": "{reason-text}"
    }
  ],
  "note": [
    {
      "text": "{note-text}"
    }
  ]
}
```

**Constraints**:
- Lab tests: category code "108252007" (Laboratory procedure)
- Procedures: category code "387713003" (Surgical procedure)
- Default status: "active", intent: "order"

## Standard Coding Systems Required

### SNOMED CT (http://snomed.info/sct)
**Usage**: Conditions, procedures, medications, clinical findings
**Examples**:
- Headache: "25064002"
- Hypertension: "38341003"
- Blood pressure: "85354007"
- Severity codes: "255604002" (mild), "6736007" (moderate), "24484000" (severe)

### LOINC (http://loinc.org)  
**Usage**: Lab tests, vital signs, clinical observations
**Examples**:
- Hemoglobin: "718-7"
- Blood pressure: "85354007" 
- Complete Blood Count: "26604007"

### HL7 Terminology Systems
**Observation Category**: `http://terminology.hl7.org/CodeSystem/observation-category`
**Condition Category**: `http://terminology.hl7.org/CodeSystem/condition-category`
**Condition Clinical Status**: `http://terminology.hl7.org/CodeSystem/condition-clinical`
**Interpretation**: `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation`

### CVX Vaccine Codes (http://hl7.org/fhir/sid/cvx)
**Usage**: Immunizations and vaccines
**Examples**:
- COVID-19 mRNA: "207"
- Influenza: "141" 
- Hepatitis B: "08"

## Default Values and Behavior

### Resource IDs
- MUST be UUID v4 format
- MUST be unique within bundle
- MUST be auto-generated if not provided

### Status Defaults
- **Observation**: "final"
- **Condition**: "active" (clinical status)
- **MedicationRequest**: "active" 
- **MedicationStatement**: "active"
- **ServiceRequest**: "active"
- **Procedure**: "completed"
- **FamilyMemberHistory**: "completed" 
- **AllergyIntolerance**: "active"
- **Immunization**: "completed"
- **Appointment**: "booked"
- **CarePlan**: "active"
- **Communication**: "completed"

### Intent Defaults
- **MedicationRequest**: "order"
- **ServiceRequest**: "order"
- **CarePlan**: "plan"

### Required Categories
Each resource type MUST include appropriate category:
- **Symptom Observations**: survey
- **Vital Sign Observations**: vital-signs
- **Lab Finding Observations**: laboratory  
- **Exam Finding Observations**: exam
- **Lifestyle Observations**: social-history
- **History Conditions**: problem-list-item
- **Encounter Conditions**: encounter-diagnosis
- **Lab ServiceRequests**: Laboratory procedure (108252007)
- **Procedure ServiceRequests**: Surgical procedure (387713003)

## Reference Management Requirements

### Automatic References
When Patient exists:
- ALL resources MUST include patient reference in subject/patient field
- Reference display MUST include patient name

When Encounter exists:
- Clinical resources MUST include encounter reference in encounter field
- Applicable resources: Observation, Condition, MedicationRequest, ServiceRequest, AllergyIntolerance, CarePlan, Communication

### Reference Format
```json
{
  "reference": "{ResourceType}/{resource-id}",
  "display": "{human-readable-text}"
}
```

## Component Structure for Observations

### Severity Component
```json
{
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "SEV",
        "display": "Severity"
      }
    ],
    "text": "Severity"
  },
  "valueCodeableConcept": {
    "coding": [
      {
        "system": "http://snomed.info/sct", 
        "code": "{severity-snomed-code}",
        "display": "{Mild|Moderate|Severe}"
      }
    ],
    "text": "{Mild|Moderate|Severe}"
  }
}
```

### Laterality Component
```json
{
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "272741003",
        "display": "Laterality"
      }
    ],
    "text": "Laterality"
  },
  "valueCodeableConcept": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "{laterality-snomed-code}",
        "display": "{Left|Right|Bilateral}"
      }
    ],
    "text": "{Left|Right|Bilateral}"
  }
}
```

### Finding Status Component  
```json
{
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "408729009",
        "display": "Finding context"
      }
    ],
    "text": "Finding Status"
  },
  "valueCodeableConcept": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "{finding-snomed-code}",
        "display": "{Present|Absent}"
      }
    ],
    "text": "{Present|Absent}"
  }
}
```

## Dosage Structure Requirements

### Complete Dosage Object
```json
{
  "text": "{human-readable-instruction}",
  "route": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "{route-code}",
        "display": "{route-display}"
      }
    ],
    "text": "{route-text}"
  },
  "timing": {
    "repeat": {
      "frequency": 3,
      "period": 1,
      "periodUnit": "d",
      "when": ["{timing-code}"]
    }
  },
  "doseAndRate": [
    {
      "doseQuantity": {
        "value": 1,
        "unit": "tablet",
        "system": "http://unitsofmeasure.org"
      }
    }
  ]
}
```

**Constraints**:
- Text field MUST contain human-readable instructions
- Timing codes stored in timing.repeat.when array
- Route codes from SNOMED CT
- Dose values use UCUM units

## Value Handling Rules

### Code Input Processing
SDK implementations MUST support two input formats:

**CodeableConcept Object**: Use directly
**String Input**: Convert to CodeableConcept with text field only

### DateTime Input Processing
SDK implementations MUST accept:
- ISO 8601 strings
- Native datetime objects
- Date objects (for date-only fields)

All output MUST be ISO 8601 with timezone information.

### Quantity Processing
Numeric values with units MUST create Quantity objects with:
- value: numeric value
- unit: unit string  
- system: "http://unitsofmeasure.org"
- code: UCUM code when available

## Validation Rules

### Bundle Level
1. Bundle ID MUST be UUID v4
2. Timestamp MUST be current time in ISO format
3. Entry fullUrls MUST match resource IDs
4. Resource order MUST follow specification

### Resource Level
1. All resources MUST have UUID v4 IDs
2. Required fields MUST be present
3. References MUST point to existing bundle resources
4. Categories MUST use correct coding systems
5. Status values MUST be from allowed value sets

### Cross-Resource
1. Patient references MUST be consistent
2. Encounter references MUST be consistent  
3. No circular references allowed
4. Display names MUST be populated

## Error Handling Requirements

SDK implementations MUST:
1. Generate valid resources even with minimal input
2. Provide clear error messages for invalid input
3. Handle missing optional parameters gracefully
4. Validate reference integrity before bundle generation
5. Support partial document creation (patient-only, etc.)

## Extension Usage

### Patient Age Extension
When age provided instead of birthDate:
```json
{
  "extension": [
    {
      "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
      "valueQuantity": {
        "value": 30,
        "unit": "years",
        "system": "http://unitsofmeasure.org",
        "code": "a"
      }
    }
  ]
}
```

### No Other Extensions
scribe2fhir SDK limits extension usage to patient age only for simplicity and consistency.

## Multi-Resource Scenarios

### Multiple Resources of Same Type
- Each resource MUST have unique ID
- All resources MUST appear in bundle
- Order preserved based on creation sequence

### Cross-Resource Relationships
- Medications can reference conditions in reasonCode
- Service requests can reference conditions in reasonCode  
- All clinical resources reference patient and encounter when available

## Output Format Requirements

### JSON Structure
Final output MUST be valid JSON with:
- Proper escaping of strings
- Correct array and object nesting
- No undefined or null required fields
- Consistent field ordering (when specified)

### Serialization Rules
1. Exclude fields with null/empty values (exclude_none behavior)
2. Use camelCase for field names (FHIR standard)
3. Preserve exact decimal precision for numeric values
4. Include timezone information in all datetime fields

This specification ensures that all scribe2fhir SDK implementations across different programming languages produce identical FHIR output for identical input, maintaining interoperability and consistency.
