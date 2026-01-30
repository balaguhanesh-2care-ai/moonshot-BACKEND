---
title: "Implementation Guide for New Language SDKs"
description: "This guide provides step-by-step instructions for implementing scribe2fhir SDKs in new programming languages while ensuring output compatibility with"
---
This guide provides step-by-step instructions for implementing scribe2fhir SDKs in new programming languages while ensuring output compatibility with the Python reference implementation.

## Prerequisites

Before implementing a new language SDK:
1. Review [SDK Specification](../sdk_specification) for complete FHIR output requirements
2. Review [Element Requirements](../element_requirements) for detailed constraints
3. Set up FHIR R5 library for your target language
4. Establish JSON serialization capabilities
5. Implement UUID v4 generation

## Implementation Phases

### Phase 1: Core Infrastructure

#### 1.1 Project Structure
Create directory structure following repository pattern:
```
{language}/
├── core/                    # Core SDK implementation
├── docs/                    # Language-specific documentation  
├── tests/                   # Comprehensive test suite
├── examples/                # Usage examples
├── {language-config-files}  # setup.py, package.json, etc.
└── README.md               # Language SDK documentation
```

#### 1.2 Base Classes and Types
Implement foundational classes:

**DocumentBuilder Class**:
```
class DocumentBuilder {
    // Private collections for each resource type
    patient: Patient | null
    encounter: Encounter | null
    observations: Observation[]
    conditions: Condition[]
    medicationRequests: MedicationRequest[]
    medicationStatements: MedicationStatement[]
    serviceRequests: ServiceRequest[]
    procedures: Procedure[]
    familyMemberHistories: FamilyMemberHistory[]
    allergies: AllergyIntolerance[]
    immunizations: Immunization[]
    appointments: Appointment[]
    carePlans: CarePlan[]
    communications: Communication[]
    
    constructor(bundleId?: string)
    convertToFHIR(): Bundle
}
```

**CodeableConcept Helper**:
```
function createCodeableConcept(
    text?: string,
    code?: string,
    system?: string,
    display?: string
): CodeableConcept

function parseCodeInput(input: string | CodeableConcept): CodeableConcept
```

#### 1.3 Enumeration Values
Implement exact enum values matching Python SDK:

**Severity**: "mild", "moderate", "severe" with SNOMED CT codes
**Laterality**: "left", "right", "bilateral" with SNOMED CT codes
**FindingStatus**: "present", "absent" with SNOMED CT codes
**Interpretation**: "normal", "high", "low", "abnormal" with HL7 codes

### Phase 2: Resource Builders

#### 2.1 Patient Builder
Implement patient resource creation:
- Support name as string or structured object
- Handle age vs birthDate (mutually exclusive)
- Process identifier arrays with type mapping
- Create address and telecom arrays
- Generate patient age extension when needed

#### 2.2 Encounter Builder  
Implement encounter resource creation:
- Map encounter classes to FHIR codes
- Create period from start/end times
- Handle location and service provider references
- Set default status to "finished"

#### 2.3 Observation Builders
Implement five observation types with correct categories:
- **Symptom**: category "survey", support components
- **Vital Signs**: category "vital-signs", handle numeric/string values
- **Lab Findings**: category "laboratory", support interpretations
- **Examination**: category "exam", primarily text findings
- **Lifestyle**: category "social-history", status values

**Key Requirements**:
- Correct category coding for each type
- Proper effective time handling (DateTime vs Period)
- Component support for severity, laterality, finding status
- Value handling (Quantity vs String)

#### 2.4 Condition Builder
Implement condition creation:
- Support history vs encounter diagnosis categories
- Handle clinical and verification status
- Store severity in severity field (not extension)
- Process onset/offset into appropriate time fields
- Create body site from laterality

#### 2.5 Medication Builders
Implement two medication types:
- **MedicationRequest**: For prescriptions
- **MedicationStatement**: For medication history

**Dosage Builder Requirements**:
- Create complete Dosage objects with text, timing, route, dose
- Store timing codes in timing.repeat.when array
- Support SNOMED CT route codes
- Handle frequency/period calculations

#### 2.6 Service Request Builder
Implement service ordering:
- Lab tests with laboratory category
- Procedures with surgical procedure category  
- Priority handling
- Occurrence date scheduling

#### 2.7 History Builders
Implement historical information:
- **Family History**: Relationship handling, condition arrays
- **Allergy**: Category classification, reaction documentation
- **Immunization**: Dose tracking, series management
- **Procedure**: Past procedure documentation

#### 2.8 Care Coordination Builders
Implement care planning:
- **Appointment**: Participant management, scheduling
- **CarePlan**: Activity with progress annotations
- **Communication**: Payload with CodeableConcept content

### Phase 3: Document Builder Methods

#### 3.1 Method Implementation
Implement all 20 add_* methods with exact signatures:

```
addPatient(name, age?, birthDate?, gender?, identifiers?, address?, phone?, email?, id?)
addEncounter(encounterClass?, encounterType?, period_start?, period_end?, facilityName?, department?, status?, id?)
addSymptom(code, onset?, offset?, severity?, status?, notes?, laterality?, findingStatus?, id?)
addMedicalConditionHistory(code, onset?, offset?, clinicalStatus?, verificationStatus?, severity?, laterality?, notes?, id?)
addMedicalConditionEncountered(code, onset?, offset?, clinicalStatus?, verificationStatus?, severity?, laterality?, notes?, id?)
addVitalFinding(code, value?, unit?, date?, interpretation?, notes?, id?)
addLabFinding(code, value?, unit?, date?, interpretation?, notes?, id?)
addExaminationFinding(code, value?, date?, status?, notes?, id?)
addLifestyleHistory(code, statusValue?, notes?, date?, id?)
addMedicationPrescribed(medication, dosage?, status?, intent?, durationValue?, durationUnit?, quantityValue?, quantityUnit?, refills?, notes?, reason?, authoredOn?, id?)
addMedicationHistory(medication, dosage?, status?, effectiveStart?, effectiveEnd?, notes?, reason?, dateAsserted?, id?)
addTestPrescribed(code, date?, notes?, priority?, reason?, id?)
addProcedurePrescribed(code, date?, notes?, priority?, reason?, id?)
addProcedureHistory(code, date?, notes?, status?, outcome?, id?)
addFamilyHistory(condition, relation, onset?, status?, notes?, deceased?, id?)
addAllergyHistory(code, category?, clinicalStatus?, criticality?, reaction?, notes?, id?)
addImmunisationHistory(vaccine, occurrenceDate?, status?, doseNumber?, seriesDoses?, notes?, id?)
addFollowup(date, refDoctor?, refSpecialty?, notes?, id?)
addAdvice(note, category?, id?)
addNotes(note, category?, id?)
```

#### 3.2 Reference Management
Each method MUST:
- Generate UUID v4 for resource ID
- Add patient reference if patient exists
- Add encounter reference if encounter exists and applicable
- Populate reference display names
- Store resource in appropriate collection

#### 3.3 Bundle Generation
The convertToFHIR() method MUST:
1. Create Bundle with proper metadata
2. Add resources in specified order
3. Create BundleEntry for each resource
4. Generate fullUrl with urn:uuid format
5. Return as JSON/dictionary structure

### Phase 4: Validation and Testing

#### 4.1 Unit Testing
Create comprehensive tests covering:
- Each element type with minimal and maximal parameters
- Code input processing (string vs CodeableConcept)
- DateTime handling and timezone conversion
- Reference creation and validation
- Bundle structure and metadata
- Edge cases and error conditions

#### 4.2 Integration Testing
Test complete workflows:
- Multi-element documents
- Cross-resource references  
- Bundle serialization
- Large document performance

#### 4.3 Compatibility Testing
Verify output matches Python SDK:
- Generate identical bundles for identical input
- Compare JSON output field-by-field
- Validate against FHIR R5 schemas
- Test reference integrity

### Phase 5: Documentation

#### 5.1 API Documentation
Create language-specific documentation:
- Installation and setup instructions
- API reference for all methods
- Code examples for each element type
- Best practices and patterns

#### 5.2 Element Documentation
Adapt element documentation from Python SDK:
- Update syntax for target language
- Maintain example consistency
- Emphasize CodeableConcept usage
- Include coding system recommendations

## Language-Specific Considerations

### Type Systems
- **Strongly typed languages**: Create type definitions for all FHIR resources
- **Dynamically typed languages**: Provide runtime validation
- **All languages**: Support union types for flexible input

### Date/Time Handling
- Use native datetime libraries
- Ensure timezone handling capability
- Support ISO 8601 parsing and formatting
- Handle date-only vs datetime fields appropriately

### JSON Serialization
- Ensure camelCase field names
- Exclude null/undefined fields
- Preserve numeric precision
- Handle nested object serialization

### Error Handling
- Provide clear error messages
- Validate input parameters
- Handle missing required fields gracefully
- Support partial document creation

## Testing Strategy

### Minimum Test Coverage
Each SDK implementation MUST include tests for:
- All 20 element types with basic usage
- All element types with comprehensive parameters
- Bundle generation and structure
- Reference creation and validation
- Error handling and edge cases
- Integration workflows

### Cross-Language Compatibility Tests
Create shared test data and expected outputs:
- JSON files with input parameters
- Expected FHIR bundle outputs
- Automated comparison tools
- Regression test suites

## Quality Assurance

### Code Quality
- Follow language-specific style guidelines
- Include comprehensive documentation
- Use appropriate design patterns
- Implement proper error handling

### FHIR Compliance
- Validate against FHIR R5 schemas
- Test with FHIR validation tools
- Ensure proper resource relationships
- Verify coding system usage

### Performance Requirements
- Handle 100+ resources efficiently
- Bundle generation under 5 seconds
- Memory usage appropriate for typical documents
- Support concurrent usage

## Release Process

### Version Synchronization
- Maintain version parity across languages
- Coordinate breaking changes
- Update documentation consistently
- Test cross-language compatibility

### Documentation Updates
- Keep element documentation synchronized
- Update examples across all languages
- Maintain specification compliance
- Provide migration guides for updates

## Common Implementation Pitfalls

### Field Mapping Issues
- FHIR field names may differ from intuitive names
- Some fields are arrays when single values expected
- Extension usage is limited in scribe2fhir
- Component structures have specific requirements

### Reference Management
- Patient/encounter references must be auto-generated
- Display names are required for human readability
- Reference format must match specification exactly
- Missing references cause validation failures

### Category and Status Values
- Each resource type has required categories
- Status defaults must match specification
- Coding systems must be exact matches
- Display values should match code meanings

### DateTime Handling
- All datetime values must include timezone
- ISO 8601 format required throughout  
- Period vs DateTime selection based on input
- String datetime input must be properly parsed

This implementation guide ensures that new language SDKs maintain compatibility and consistency with the scribe2fhir specification while following language-specific best practices.
