---
title: "scribe2fhir FHIR Specification"
description: "This document defines the FHIR resource specifications and output requirements for all scribe2fhir SDK implementations across different programming la"
---
This document defines the FHIR resource specifications and output requirements for all scribe2fhir SDK implementations across different programming languages. All language implementations MUST produce identical FHIR Bundle structures to ensure interoperability.

## Bundle Structure Requirements

### Bundle Metadata
All scribe2fhir SDKs MUST generate FHIR Bundles with:
- **resourceType**: `"Bundle"`  
- **id**: UUID v4 format (e.g., "12345678-1234-1234-1234-123456789012")
- **type**: `"collection"` (default) or specified type
- **timestamp**: ISO 8601 datetime with timezone (e.g., "2024-01-15T10:30:00.000Z")
- **entry**: Array of BundleEntry objects containing resources

### Bundle Entry Structure
Each entry MUST contain:
- **fullUrl**: `"urn:uuid:{resource-id}"`
- **resource**: Complete FHIR resource object

### Resource Ordering in Bundle
Resources MUST appear in this order:
1. Patient (if present)
2. Encounter (if present)
3. Observations (all types)
4. Conditions
5. MedicationRequests
6. MedicationStatements
7. ServiceRequests
8. Procedures
9. FamilyMemberHistory
10. AllergyIntolerance
11. Immunizations
12. Appointments
13. CarePlans
14. Communications

## Supported Elements and FHIR Resource Mapping

### 1. Patient Element → Patient Resource

**Purpose**: Demographics and administrative information  
**Cardinality**: 0..1 (optional but recommended)

**Required Fields**:
- `id`: UUID v4
- `name`: Array with at least one HumanName containing `text` field

**Optional Fields**:
- `gender`: "male" | "female" | "other" | "unknown"
- `birthDate`: ISO date (YYYY-MM-DD)
- `extension`: Patient age extension when age provided instead of birthDate
- `identifier`: Array of Identifier objects
- `address`: Array of Address objects  
- `telecom`: Array of ContactPoint objects

**SDK-Specific Constraints**:
- Age provided as tuple (value, unit) creates extension with URL `"http://hl7.org/fhir/StructureDefinition/patient-age"`
- Name is stored as single HumanName with text field
- Maximum one address and multiple telecom entries (phone, email)

**Reference Pattern**:
- Referenced by all other resources in `subject` or `patient` field
- Display name includes patient name for human readability

---

### 2. Encounter Element → Encounter Resource

**Purpose**: Healthcare interaction context  
**Cardinality**: 0..1 (optional but recommended for clinical context)

**Required Fields**:
- `id`: UUID v4
- `status`: "planned" | "arrived" | "triaged" | "in-progress" | "onleave" | "finished" | "cancelled"
- `class`: CodeableConcept with encounter class code

**Optional Fields**:
- `type`: Array of CodeableConcept for encounter types
- `period`: Period with start and optional end
- `location`: Array with location references
- `serviceProvider`: Reference to providing organization
- `subject`: Reference to Patient

**SDK-Specific Constraints**:
- Default status: "finished"
- Class codes: "AMB" (ambulatory), "EMER" (emergency), "IMP" (inpatient), "VR" (virtual)
- Facility name creates location reference
- Department creates serviceProvider reference

**Reference Pattern**:
- Referenced by clinical resources in `encounter` field

---

### 3. Symptom Element → Observation Resource

**Purpose**: Patient-reported symptoms and chief complaints  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "registered" | "preliminary" | "final" | "amended" | "corrected" | "cancelled"
- `category`: Array with CodeableConcept containing survey category
- `code`: CodeableConcept for symptom
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `effectiveDateTime`: ISO datetime for single point in time
- `effectivePeriod`: Period for onset/offset range
- `component`: Array for severity, laterality, finding status
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Category MUST be "survey" (code: "survey", system: "http://terminology.hl7.org/CodeSystem/observation-category")
- Default status: "final"
- Severity component uses code "SEV" with SNOMED CT values
- Laterality component uses code "272741003" (SNOMED CT)  
- Finding status component uses code "408729009" (SNOMED CT)
- When both onset and offset provided, use effectivePeriod instead of effectiveDateTime

**Component Structure**:
```json
{
  "component": [
    {
      "code": {
        "coding": [{"system": "http://snomed.info/sct", "code": "SEV"}],
        "text": "Severity"
      },
      "valueCodeableConcept": {
        "text": "Moderate",
        "coding": [{"system": "http://snomed.info/sct", "code": "6736007", "display": "Moderate"}]
      }
    }
  ]
}
```

---

### 4. Vital Signs Element → Observation Resource

**Purpose**: Physiological measurements and vital signs  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: Default "final"
- `category`: Array with vital-signs category
- `code`: CodeableConcept for vital sign type
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `effectiveDateTime`: When measured
- `valueQuantity`: Numeric value with unit
- `valueString`: String value (for compound measurements)
- `interpretation`: Array of CodeableConcept
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Category MUST be "vital-signs" (code: "vital-signs", system: "http://terminology.hl7.org/CodeSystem/observation-category")
- String values include unit in text (e.g., "120/80 mmHg")
- Numeric values use separate unit field
- Interpretation codes from http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation

---

### 5. Lab Findings Element → Observation Resource

**Purpose**: Laboratory test results and interpretations  
**Cardinality**: 0..*

**Required Fields**: Same as Vital Signs
**Optional Fields**: Same as Vital Signs

**SDK-Specific Constraints**:
- Category MUST be "laboratory" (code: "laboratory", system: "http://terminology.hl7.org/CodeSystem/observation-category")
- Values can be numeric (valueQuantity) or text (valueString)
- Interpretation same as vital signs

---

### 6. Examination Findings Element → Observation Resource

**Purpose**: Physical examination results  
**Cardinality**: 0..*

**Required Fields**: Same structure as other Observations
**SDK-Specific Constraints**:
- Category MUST be "exam" (code: "exam", system: "http://terminology.hl7.org/CodeSystem/observation-category")
- Values typically text descriptions of findings
- No interpretation field typically used

---

### 7. Lifestyle History Element → Observation Resource

**Purpose**: Social history and lifestyle factors  
**Cardinality**: 0..*

**Required Fields**: Same structure as other Observations
**SDK-Specific Constraints**:
- Category MUST be "social-history" (code: "social-history", system: "http://terminology.hl7.org/CodeSystem/observation-category")
- Values are typically status strings ("Active", "Inactive", "Former", "Never")

---

### 8. Medical Condition Elements → Condition Resource

**Purpose**: Medical diagnoses and health problems  
**Cardinality**: 0..*  
**Types**: History conditions and encounter diagnoses

**Required Fields**:
- `id`: UUID v4
- `clinicalStatus`: CodeableConcept with status
- `category`: Array with condition category
- `code`: CodeableConcept for condition
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `verificationStatus`: CodeableConcept for verification
- `severity`: CodeableConcept for severity (direct field, not extension)
- `bodySite`: Array for laterality/body site
- `onsetDateTime`: Single point onset
- `onsetPeriod`: Period for onset/offset range
- `abatementDateTime`: Resolution time
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:

**History Conditions**:
- Category: "problem-list-item" (code: "problem-list-item", system: "http://terminology.hl7.org/CodeSystem/condition-category")
- Default clinicalStatus: "active"
- No default verificationStatus

**Encounter Diagnoses**:
- Category: "encounter-diagnosis" (code: "encounter-diagnosis", system: "http://terminology.hl7.org/CodeSystem/condition-category")
- Default clinicalStatus: "active"
- Default verificationStatus: "confirmed"

**Status Codes**:
- Clinical: "active" | "inactive" | "resolved" | "recurrence"
- Verification: "unconfirmed" | "provisional" | "differential" | "confirmed" | "refuted"

---

### 9. Medication Prescription Element → MedicationRequest Resource

**Purpose**: Prescribed medications with dosage instructions  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "active" | "on-hold" | "cancelled" | "completed"
- `intent`: "proposal" | "plan" | "order" | "original-order"
- `medication`: CodeableConcept for medication
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `authoredOn`: ISO datetime when prescribed
- `dosageInstruction`: Array of Dosage objects
- `dispenseRequest`: DispenseRequest with quantity/duration
- `note`: Array of Annotation objects
- `reasonCode`: Array of CodeableConcept

**SDK-Specific Constraints**:
- Default status: "active"
- Default intent: "order"
- Medication stored in `medication` field (CodeableConcept)
- Duration creates dispenseRequest.expectedSupplyDuration
- Quantity creates dispenseRequest.quantity
- Refills creates dispenseRequest.numberOfRepeatsAllowed

**Dosage Structure Requirements**:
- `text`: Human-readable instruction
- `route`: CodeableConcept with route code
- `timing`: Timing object with repeat and optional code
- `doseAndRate`: Array with doseQuantity

---

### 10. Medication History Element → MedicationStatement Resource

**Purpose**: Patient's medication history and current medications  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "active" | "completed" | "entered-in-error" | "intended" | "stopped" | "on-hold"
- `medication`: CodeableConcept for medication
- `subject`: Reference to Patient

**Optional Fields**:
- `effectivePeriod`: When medication was/is being taken
- `dateAsserted`: When information was recorded
- `dosage`: Array of Dosage objects
- `reasonCode`: Array of CodeableConcept
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default status: "active"
- Effective period from start/end dates
- Same dosage structure as MedicationRequest

---

### 11. Lab Test Ordering Element → ServiceRequest Resource

**Purpose**: Laboratory test orders  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "draft" | "active" | "on-hold" | "revoked" | "completed"
- `intent`: "proposal" | "plan" | "directive" | "order"
- `category`: Array with laboratory category
- `code`: CodeableConcept for test
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `occurrenceDateTime`: When test should be performed
- `priority`: "routine" | "urgent" | "asap" | "stat"
- `reasonCode`: Array of CodeableConcept
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default status: "active"
- Default intent: "order"
- Category MUST be laboratory procedure (code: "108252007", system: "http://snomed.info/sct", display: "Laboratory procedure")

---

### 12. Procedure Ordering Element → ServiceRequest Resource

**Purpose**: Procedure and imaging orders  
**Cardinality**: 0..*

**Required Fields**: Same as Lab Test Ordering
**SDK-Specific Constraints**:
- Category MUST be surgical procedure (code: "387713003", system: "http://snomed.info/sct", display: "Surgical procedure")

---

### 13. Family History Element → FamilyMemberHistory Resource

**Purpose**: Family medical history  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "partial" | "completed" | "entered-in-error" | "health-unknown"
- `patient`: Reference to Patient
- `relationship`: CodeableConcept for family relationship
- `condition`: Array with condition information

**Optional Fields**:
- `deceasedBoolean`: Whether family member is deceased
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default status: "completed"
- Relationship text stored directly (e.g., "father", "mother", "brother")
- Condition array contains objects with:
  - `code`: CodeableConcept for condition
  - `onsetAge`: Age at onset (if provided as integer)
  - `onsetString`: Year or description (if provided as string)

---

### 14. Allergy History Element → AllergyIntolerance Resource

**Purpose**: Allergies and adverse reactions  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `clinicalStatus`: CodeableConcept with status
- `code`: CodeableConcept for allergen
- `patient`: Reference to Patient
- `category`: Array of category strings

**Optional Fields**:
- `encounter`: Reference to Encounter
- `criticality`: "low" | "high"
- `reaction`: Array with reaction information
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default clinicalStatus: "active"
- Categories: "food" | "medication" | "environment" | "biologic"
- Reaction array contains objects with `manifestation` array containing reaction descriptions

---

### 15. Immunization History Element → Immunization Resource

**Purpose**: Vaccination records  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "completed" | "entered-in-error" | "not-done"
- `vaccineCode`: CodeableConcept for vaccine
- `patient`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `occurrenceDateTime`: When vaccine was given
- `protocolApplied`: Array with dose information
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default status: "completed"
- Protocol applied contains doseNumber and seriesDoses when provided
- Use CVX codes in vaccineCode when available

---

### 16. Procedure History Element → Procedure Resource

**Purpose**: Past surgical procedures and interventions  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "preparation" | "in-progress" | "not-done" | "on-hold" | "stopped" | "completed"
- `code`: CodeableConcept for procedure
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `performedDateTime`: When procedure was done
- `outcome`: CodeableConcept for result
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default status: "completed"
- Performed date stored in performedDateTime (not performedPeriod)

---

### 17. Follow-up Appointment Element → Appointment Resource

**Purpose**: Scheduled appointments and referrals  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "proposed" | "pending" | "booked" | "arrived" | "fulfilled" | "cancelled"
- `start`: ISO datetime for appointment
- `participant`: Array with patient and optional practitioner

**Optional Fields**:
- `serviceType`: Array of CodeableReference for service
- `specialty`: Array of CodeableConcept for medical specialty
- `note`: Array of Annotation objects

**SDK-Specific Constraints**:
- Default status: "booked"
- Patient participant always included with status "accepted"
- Practitioner participant added when doctor name provided
- Specialty stored in specialty array, not appointmentType
- Notes stored in note array as Annotation objects

---

### 18. Patient Advice Element → CarePlan Resource

**Purpose**: Patient instructions and care recommendations  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "draft" | "active" | "on-hold" | "revoked" | "completed"
- `intent`: "proposal" | "plan" | "order" | "option"
- `subject`: Reference to Patient
- `activity`: Array with activity information

**Optional Fields**:
- `encounter`: Reference to Encounter
- `category`: Array of CodeableConcept
- `title`: Plan title
- `description`: Plan description

**SDK-Specific Constraints**:
- Default status: "active"
- Default intent: "plan"
- Activity array contains objects with `progress` array
- Advice text stored in activity.progress[0].text (Annotation)
- Category text stored directly when provided

---

### 19. Clinical Notes Element → Communication Resource

**Purpose**: Provider documentation and clinical notes  
**Cardinality**: 0..*

**Required Fields**:
- `id`: UUID v4
- `status`: "preparation" | "in-progress" | "not-done" | "on-hold" | "stopped" | "completed"
- `payload`: Array with content
- `subject`: Reference to Patient

**Optional Fields**:
- `encounter`: Reference to Encounter
- `category`: Array of CodeableConcept
- `sent`: ISO datetime when sent/recorded

**SDK-Specific Constraints**:
- Default status: "completed"
- Payload uses contentCodeableConcept.text (not contentString)
- Category text stored directly when provided

## Data Type Standards

### CodeableConcept Structure
All CodeableConcept objects MUST follow this pattern:
```json
{
  "coding": [
    {
      "system": "http://snomed.info/sct",
      "code": "25064002", 
      "display": "Headache"
    }
  ],
  "text": "Headache"
}
```

When only text provided, structure becomes:
```json
{
  "text": "Headache"
}
```

### Reference Structure
All references MUST follow this pattern:
```json
{
  "reference": "Patient/12345678-1234-1234-1234-123456789012",
  "display": "John Doe"
}
```

### DateTime Format
All datetime fields MUST use ISO 8601 format with timezone:
- `"2024-01-15T10:30:00.000Z"` (UTC)
- `"2024-01-15T10:30:00+05:30"` (with timezone offset)

### Quantity Structure
Numeric values with units MUST follow:
```json
{
  "value": 120,
  "unit": "mmHg",
  "system": "http://unitsofmeasure.org",
  "code": "mm[Hg]"
}
```

### Annotation Structure
Notes and comments MUST use:
```json
{
  "text": "Additional information about the finding"
}
```

## Enumerated Values

### Severity Levels
- Code: SNOMED CT system
- Values: "mild" | "moderate" | "severe"
- Codes: "255604002" (mild), "6736007" (moderate), "24484000" (severe)

### Laterality Values  
- Code: SNOMED CT system
- Values: "left" | "right" | "bilateral"
- Codes: "7771000" (left), "24028007" (right), "51440002" (bilateral)

### Finding Status
- Code: SNOMED CT system
- Values: "present" | "absent"
- Codes: "52101004" (present), "2667000" (absent)

### Interpretation Values
- System: "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"
- Values: "normal" (N), "high" (H), "low" (L), "abnormal" (A)

## Validation Requirements

### Bundle Validation
1. Bundle MUST contain valid resourceType and id
2. All entries MUST have fullUrl with urn:uuid format
3. All resource IDs within bundle MUST be unique
4. All references MUST point to existing resources in bundle

### Resource Validation
1. All resources MUST have required fields populated
2. All CodeableConcept objects MUST have either coding or text
3. All references MUST follow reference format specification
4. All datetime values MUST be timezone-aware
5. All UUIDs MUST be valid UUID v4 format

### Reference Validation
1. Patient references MUST exist when patient is added
2. Encounter references MUST exist when encounter is added
3. Reference display names MUST be populated when available
4. Circular references MUST be avoided

## Implementation Requirements for Language SDKs

### 1. Builder Pattern
All implementations MUST use builder pattern:
```
DocumentBuilder builder = new DocumentBuilder()
builder.addPatient(name, age, gender)
builder.addSymptom(code, severity)
Bundle bundle = builder.convertToFHIR()
```

### 2. Method Naming Convention
Method names MUST follow pattern: `add{ElementType}()`
- addPatient()
- addEncounter() 
- addSymptom()
- addMedicalConditionHistory()
- addMedicalConditionEncountered()
- addVitalFinding()
- addLabFinding()
- addExaminationFinding()
- addLifestyleHistory()
- addMedicationPrescribed()
- addMedicationHistory()
- addTestPrescribed()
- addProcedurePrescribed()
- addProcedureHistory()
- addFamilyHistory()
- addAllergyHistory()
- addImmunisationHistory()
- addFollowup()
- addAdvice()
- addNotes()

### 3. Parameter Requirements
Each method MUST accept:
- Required parameters as defined above
- Optional parameters with documented defaults
- Code parameters accepting both CodeableConcept objects and strings
- DateTime parameters accepting multiple formats

### 4. Reference Management
Implementations MUST:
- Auto-generate UUID v4 IDs for all resources
- Automatically create patient references when patient exists
- Automatically create encounter references when encounter exists  
- Populate reference display names
- Validate reference integrity

### 5. Bundle Generation
The convertToFHIR() method MUST:
- Return valid FHIR R5 Bundle as JSON/dictionary
- Include all added resources in specified order
- Generate proper fullUrl for each entry
- Include bundle metadata (id, type, timestamp)

## Testing Requirements

All language implementations MUST include test suites that verify:
1. Each element type can be created with minimal and comprehensive parameters
2. Generated FHIR resources match specification exactly
3. Bundle structure follows requirements
4. Reference relationships are correct
5. Edge cases and error conditions are handled
6. Cross-element integration works properly

## Compliance Verification

Language implementations can verify compliance by:
1. Generating identical output for the same input across languages
2. Validating against FHIR R5 schemas
3. Testing reference integrity within bundles
4. Comparing JSON output structure element-by-element

This specification ensures that all scribe2fhir SDK implementations produce identical FHIR output regardless of the programming language used.
