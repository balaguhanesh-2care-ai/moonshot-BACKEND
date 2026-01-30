---
title: Example Usage
description: Complete example showing how to use Scribe2FHIR to process medical data and create FHIR resources.
---
This example demonstrates the complete workflow of using Scribe2FHIR to convert medical transcription data into FHIR-compliant resources.

## Basic Patient and Encounter Example

Here's a comprehensive example that shows how to create a patient record and associated medical encounter:

```python
from scribe2fhir.core.document_builder import DocumentBuilder
from scribe2fhir.core.types import (
    PatientInfo, EncounterInfo, MedicalConditionInfo, 
    ObservationInfo, MedicationInfo
)
from datetime import datetime, date

# Initialize the document builder
builder = DocumentBuilder()

# Create patient information
patient_info = PatientInfo(
    first_name="John",
    last_name="Doe", 
    date_of_birth=date(1980, 5, 15),
    gender="male",
    mrn="MRN12345678"
)

# Add patient to the document
patient = builder.add_patient(patient_info)
print(f"Created patient: {patient.id}")

# Create encounter information
encounter_info = EncounterInfo(
    encounter_type="outpatient",
    encounter_date=datetime.now(),
    provider_name="Dr. Jane Smith",
    location="General Medicine Clinic"
)

# Add encounter
encounter = builder.add_encounter(encounter_info, patient_id=patient.id)
print(f"Created encounter: {encounter.id}")

# Add a medical condition
condition_info = MedicalConditionInfo(
    condition_name="Type 2 Diabetes Mellitus",
    icd_code="E11.9",
    status="active",
    onset_date=date(2020, 3, 10)
)

condition = builder.add_condition(condition_info, patient_id=patient.id)
print(f"Created condition: {condition.id}")

# Add vital signs observation
vital_info = ObservationInfo(
    observation_type="vital_signs",
    measurement_type="blood_pressure",
    systolic_value=140,
    diastolic_value=90,
    unit="mmHg",
    observation_date=datetime.now()
)

observation = builder.add_observation(vital_info, patient_id=patient.id)
print(f"Created observation: {observation.id}")

# Add medication
medication_info = MedicationInfo(
    medication_name="Metformin",
    dosage="500mg",
    frequency="twice daily",
    route="oral",
    start_date=date(2020, 3, 15)
)

medication = builder.add_medication_prescription(
    medication_info, 
    patient_id=patient.id,
    encounter_id=encounter.id
)
print(f"Created medication: {medication.id}")

# Generate the complete FHIR bundle
bundle = builder.create_bundle()
print(f"Created FHIR bundle with {len(bundle.entry)} resources")

# Export to JSON
fhir_json = builder.export_json()
print("FHIR JSON generated successfully")

# Save to file
with open("patient_record.json", "w") as f:
    f.write(fhir_json)
print("FHIR bundle saved to patient_record.json")
```

## Processing Clinical Notes

Here's an example of processing unstructured clinical notes:

```python
from scribe2fhir.core.document_builder import DocumentBuilder
from scribe2fhir.core.types import ClinicalNotesInfo

# Clinical notes text
clinical_text = """
Patient presents with chief complaint of chest pain and shortness of breath.
Vital signs: BP 150/95, HR 88, Temp 98.6F, O2 Sat 96% on room air.
Assessment: Possible acute coronary syndrome. 
Plan: ECG, cardiac enzymes, chest X-ray. Start aspirin 81mg daily.
"""

builder = DocumentBuilder()

# Process clinical notes
notes_info = ClinicalNotesInfo(
    notes_text=clinical_text,
    note_type="progress_note",
    author="Dr. John Smith",
    date_created=datetime.now()
)

# This would typically involve NLP processing to extract structured data
# For this example, we'll manually create the extracted information

# Create patient
patient = builder.add_patient(PatientInfo(
    first_name="Jane",
    last_name="Smith",
    date_of_birth=date(1975, 8, 22),
    gender="female",
    mrn="MRN87654321"
))

# Add vital signs from notes
vitals = [
    ("blood_pressure", 150, 95, "mmHg"),
    ("heart_rate", 88, None, "beats/min"), 
    ("body_temperature", 98.6, None, "F"),
    ("oxygen_saturation", 96, None, "%")
]

for vital_type, value1, value2, unit in vitals:
    if vital_type == "blood_pressure":
        obs_info = ObservationInfo(
            observation_type="vital_signs",
            measurement_type=vital_type,
            systolic_value=value1,
            diastolic_value=value2,
            unit=unit,
            observation_date=datetime.now()
        )
    else:
        obs_info = ObservationInfo(
            observation_type="vital_signs", 
            measurement_type=vital_type,
            value=value1,
            unit=unit,
            observation_date=datetime.now()
        )
    
    builder.add_observation(obs_info, patient_id=patient.id)

# Add extracted condition
condition = builder.add_condition(
    MedicalConditionInfo(
        condition_name="Chest pain, unspecified",
        icd_code="R06.02", 
        status="active",
        onset_date=date.today()
    ),
    patient_id=patient.id
)

# Generate final bundle
bundle = builder.create_bundle()
print(f"Processed clinical notes into {len(bundle.entry)} FHIR resources")
```

## Batch Processing Multiple Patients

For processing multiple patients efficiently:

```python
import json
from scribe2fhir.core.document_builder import DocumentBuilder

def process_patient_batch(patient_data_list):
    """Process a batch of patient data"""
    results = []
    
    for patient_data in patient_data_list:
        builder = DocumentBuilder()
        
        try:
            # Create patient
            patient = builder.add_patient(PatientInfo(**patient_data['patient']))
            
            # Add encounter if present
            if 'encounter' in patient_data:
                encounter = builder.add_encounter(
                    EncounterInfo(**patient_data['encounter']),
                    patient_id=patient.id
                )
            
            # Add conditions
            for condition_data in patient_data.get('conditions', []):
                builder.add_condition(
                    MedicalConditionInfo(**condition_data),
                    patient_id=patient.id
                )
            
            # Add observations
            for obs_data in patient_data.get('observations', []):
                builder.add_observation(
                    ObservationInfo(**obs_data),
                    patient_id=patient.id
                )
            
            # Generate bundle
            bundle = builder.create_bundle()
            results.append({
                'patient_id': patient.id,
                'bundle': bundle,
                'status': 'success'
            })
            
        except Exception as e:
            results.append({
                'patient_data': patient_data,
                'error': str(e),
                'status': 'error'
            })
    
    return results

# Example batch data
batch_data = [
    {
        'patient': {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'female',
            'mrn': 'MRN001'
        },
        'conditions': [
            {
                'condition_name': 'Hypertension',
                'icd_code': 'I10',
                'status': 'active'
            }
        ]
    },
    {
        'patient': {
            'first_name': 'Bob',
            'last_name': 'Wilson', 
            'date_of_birth': date(1985, 6, 15),
            'gender': 'male',
            'mrn': 'MRN002'
        },
        'observations': [
            {
                'observation_type': 'vital_signs',
                'measurement_type': 'weight',
                'value': 180,
                'unit': 'lb',
                'observation_date': datetime.now()
            }
        ]
    }
]

# Process the batch
results = process_patient_batch(batch_data)

# Review results
for result in results:
    if result['status'] == 'success':
        print(f"Successfully processed patient {result['patient_id']}")
    else:
        print(f"Error processing patient: {result['error']}")
```

## Integration with Healthcare Systems

Example of integrating with a FHIR server:

```python
import requests
from scribe2fhir.core.document_builder import DocumentBuilder

class FHIRServerIntegration:
    def __init__(self, server_url, auth_token=None):
        self.server_url = server_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
    
    def upload_bundle(self, bundle):
        """Upload a FHIR bundle to the server"""
        url = f"{self.server_url}/Bundle"
        
        response = requests.post(
            url, 
            json=bundle.dict(),
            headers=self.headers
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
    def search_patient(self, mrn):
        """Search for a patient by MRN"""
        url = f"{self.server_url}/Patient"
        params = {'identifier': mrn}
        
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Search failed: {response.status_code} - {response.text}")

# Example usage with FHIR server
def upload_patient_to_server():
    # Create FHIR resources
    builder = DocumentBuilder()
    
    patient = builder.add_patient(PatientInfo(
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        mrn="TEST123456"
    ))
    
    bundle = builder.create_bundle()
    
    # Upload to FHIR server
    fhir_client = FHIRServerIntegration(
        server_url="https://hapi.fhir.org/baseR5",
        auth_token="your_auth_token_here"  # Optional
    )
    
    try:
        result = fhir_client.upload_bundle(bundle)
        print(f"Successfully uploaded bundle: {result.get('id')}")
        return result
    except Exception as e:
        print(f"Upload error: {e}")
        return None

# Run the upload
upload_result = upload_patient_to_server()
```

## Next Steps

Now that you've seen these examples, you can:

1. **[Check Python SDK Documentation](../python-sdk/readme)** - Dive deeper into the API
2. **[Review FHIR Specification](../fhir-specification/readme)** - Understand FHIR standards implementation

For more advanced examples and use cases, check the [GitHub repository](https://github.com/MedScribeAlliance/scribe2fhir).
