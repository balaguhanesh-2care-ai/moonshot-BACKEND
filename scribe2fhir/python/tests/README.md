# FHIR SDK Test Suite

This directory contains comprehensive test cases for all FHIR SDK functionality.

## Overview

The test suite covers all elements and resources supported by the FHIR SDK:

### Core Resources
- **Patient** (`test_patient.py`) - Patient demographics, identifiers, contact info
- **Encounter** (`test_encounter.py`) - Healthcare encounters and visits

### Clinical Resources  
- **Symptoms** (`test_symptoms.py`) - Chief complaints and symptom observations
- **Conditions** (`test_conditions.py`) - Medical conditions, diagnoses, problem lists
- **Observations** (`test_observations.py`) - Vital signs, lab results, examinations
- **Medications** (`test_medications.py`) - Prescriptions, medication history, dosages

### Ordering & Procedures
- **Service Requests** (`test_service_requests.py`) - Lab tests, imaging, procedure orders
- **History** (`test_history.py`) - Family history, allergies, immunizations, past procedures

### Care Coordination
- **Appointments** (`test_appointments.py`) - Follow-up appointments and referrals  
- **Care Plans** (`test_care_plans.py`) - Patient advice and clinical notes

### Integration
- **Integration Tests** (`test_integration.py`) - End-to-end workflow validation

## Test Structure

Each test file contains:
- **Basic functionality tests** - Minimal required data
- **Comprehensive tests** - All available properties  
- **Validation tests** - Input validation and error handling
- **Bundle integration tests** - FHIR bundle generation
- **Edge case tests** - Boundary conditions and special scenarios

## Running Tests

### Quick Start
```bash
# Run all tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py -v

# Run with coverage report
python tests/run_tests.py -c

# Run specific test file
python tests/run_tests.py tests/test_patient.py

# Run specific test class
python tests/run_tests.py tests/test_patient.py::TestPatientResource

# Run specific test method
python tests/run_tests.py tests/test_patient.py::TestPatientResource::test_basic_patient_creation
```

### Using pytest directly
```bash
# Install dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=fhir_sdk --cov-report=html

# Run specific tests
pytest tests/test_patient.py -v
```

## Test Dependencies

The tests use the following dependencies:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting  

Install with:
```bash
pip install pytest pytest-cov
```

Or use the test runner:
```bash
python tests/run_tests.py --install-deps
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `builder` - Fresh FHIRDocumentBuilder instance
- `patient_builder` - Builder with patient already added
- `encounter_builder` - Builder with patient and encounter
- `sample_dosage` - Standard medication dosage for testing
- `test_dates` - Common date/time values for testing

## Test Coverage

The test suite aims for comprehensive coverage of:

### Input Validation
- Required vs optional parameters
- Different input formats (strings, tuples, enums)
- Date/time format handling
- Error conditions

### FHIR Compliance  
- Correct resource types and structures
- Required FHIR fields and extensions
- Reference consistency between resources
- Bundle structure and metadata

### Integration
- Multi-resource workflows
- Reference relationships
- Bundle generation and serialization
- Complete example recreation

## Example Test Patterns

### Basic Resource Test
```python
def test_basic_resource_creation(self, encounter_builder):
    """Test creating resource with minimal information."""
    resource = encounter_builder.add_resource(
        required_field="value"
    )
    
    assert resource is not None
    assert resource.resource_type == "ResourceType"
    assert resource.required_field == "value"
```

### Comprehensive Resource Test  
```python
def test_resource_with_all_properties(self, encounter_builder):
    """Test creating resource with all available properties."""
    resource = encounter_builder.add_resource(
        field1="value1",
        field2="value2", 
        optional_field="optional_value"
    )
    
    # Verify all properties
    assert resource.field1 == "value1"
    assert resource.field2 == "value2" 
    assert resource.optional_field == "optional_value"
```

### Bundle Integration Test
```python
def test_resource_in_fhir_bundle(self, encounter_builder):
    """Test resource appears correctly in FHIR bundle."""
    encounter_builder.add_resource(field="test_value")
    
    bundle_dict = encounter_builder.convert_to_fhir()
    
    # Find resource in bundle
    resource_entry = next((entry for entry in bundle_dict["entry"]
                          if entry["resource"]["resourceType"] == "ResourceType"), None)
    
    assert resource_entry is not None
    assert resource_entry["resource"]["field"] == "test_value"
```

## Validation Strategy

Tests validate:

1. **Resource Creation** - Objects are created with correct types and IDs
2. **Field Mapping** - Input parameters map correctly to FHIR fields  
3. **Default Values** - Appropriate defaults are applied
4. **References** - Patient/encounter references are created correctly
5. **Bundle Integration** - Resources appear correctly in generated bundles
6. **FHIR Compliance** - Generated resources conform to FHIR specifications

## Contributing

When adding new functionality to the SDK:

1. Add corresponding test cases following existing patterns
2. Include tests for basic usage, comprehensive usage, and edge cases
3. Verify bundle integration works correctly
4. Update this README if new test categories are added

## Performance Tests

The integration tests include basic performance validation to ensure:
- Resource creation scales reasonably with quantity
- Bundle generation completes in acceptable time
- Memory usage remains reasonable for typical workloads
