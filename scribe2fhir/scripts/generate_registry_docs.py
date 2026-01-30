#!/usr/bin/env python3
"""
Generate registry documentation for Scribe2FHIR
This script generates additional documentation content from the Python SDK
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

def generate_api_registry():
    """Generate API registry documentation"""
    
    # API endpoints documentation
    api_docs = {
        "title": "Scribe2FHIR API Registry",
        "description": "Complete registry of all Scribe2FHIR API endpoints and functions",
        "generated_at": datetime.now().isoformat(),
        "sections": [
            {
                "name": "Core Functions",
                "description": "Primary functions for creating FHIR resources",
                "functions": [
                    "add_patient()",
                    "add_encounter()",
                    "add_condition()",
                    "add_observation()",
                    "add_medication_prescription()",
                    "add_procedure()",
                    "add_allergy()",
                    "add_immunization()"
                ]
            },
            {
                "name": "Utility Functions", 
                "description": "Helper functions for data processing",
                "functions": [
                    "create_bundle()",
                    "export_json()",
                    "validate_resource()",
                    "find_patient_by_mrn()"
                ]
            },
            {
                "name": "Resource Types",
                "description": "Supported FHIR resource types",
                "resources": [
                    "Patient",
                    "Encounter", 
                    "Condition",
                    "Observation",
                    "MedicationStatement",
                    "MedicationRequest",
                    "Procedure",
                    "AllergyIntolerance",
                    "Immunization",
                    "FamilyMemberHistory",
                    "ServiceRequest",
                    "DiagnosticReport",
                    "CarePlan",
                    "Appointment"
                ]
            }
        ]
    }
    
    return api_docs

def generate_code_examples():
    """Generate code examples registry"""
    
    examples = {
        "basic_patient": {
            "title": "Basic Patient Creation",
            "description": "Create a simple patient record",
            "code": '''
from scribe2fhir.core import DocumentBuilder
from scribe2fhir.core.types import PatientInfo

builder = DocumentBuilder()
patient_info = PatientInfo(
    first_name="John",
    last_name="Doe",
    date_of_birth=date(1980, 5, 15),
    gender="male",
    mrn="MRN12345678"
)
patient = builder.add_patient(patient_info)
'''
        },
        "complete_encounter": {
            "title": "Complete Encounter Example", 
            "description": "Create patient with encounter and clinical data",
            "code": '''
# Create patient
patient = builder.add_patient(patient_info)

# Add encounter
encounter = builder.add_encounter(
    EncounterInfo(
        encounter_type="outpatient",
        encounter_date=datetime.now(),
        provider_name="Dr. Smith"
    ),
    patient_id=patient.id
)

# Add vital signs
builder.add_observation(
    ObservationInfo(
        observation_type="vital_signs",
        measurement_type="blood_pressure", 
        systolic_value=120,
        diastolic_value=80,
        unit="mmHg"
    ),
    patient_id=patient.id
)
'''
        }
    }
    
    return examples

def main():
    """Main function to generate registry documentation"""
    
    print("Generating Scribe2FHIR registry documentation...")
    
    try:
        # No longer generating any registry docs since code examples were removed
        print("✓ Registry documentation generation skipped (code examples removed)")
        return 0
    
    except Exception as e:
        print(f"✗ Error generating registry documentation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
