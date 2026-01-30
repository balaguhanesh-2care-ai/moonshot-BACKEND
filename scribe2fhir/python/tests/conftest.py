"""
Test configuration and fixtures for scribe2fhir.core tests.
"""

import pytest
from datetime import datetime, timedelta
from scribe2fhir.core import (
    FHIRDocumentBuilder,
    DosageBuilder,
    Severity,
    Laterality,
    FindingStatus,
    ConditionClinicalStatus,
    MedicationStatementStatus,
    RouteOfAdministration,
    EventTiming,
    Interpretation,
    AllergyCategory,
    AllergyCriticality,
)


@pytest.fixture
def builder():
    """Create a fresh FHIRDocumentBuilder for each test."""
    return FHIRDocumentBuilder()


@pytest.fixture
def patient_builder():
    """Create a builder with a patient already added."""
    builder = FHIRDocumentBuilder()
    builder.add_patient(
        name="John Doe",
        age=(30, "years"),
        gender="male",
        identifiers=[("MRN-001234", "MRN"), ("9876543210", "mobile")],
        address="123 Main Street, Test City",
        phone="9876543210",
        email="john.doe@example.com"
    )
    return builder


@pytest.fixture
def encounter_builder():
    """Create a builder with patient and encounter."""
    builder = FHIRDocumentBuilder()
    builder.add_patient(
        name="John Doe",
        age=(30, "years"),
        gender="male"
    )
    builder.add_encounter(
        encounter_class="ambulatory",
        encounter_type="Consultation",
        facility_name="Test Hospital",
        department="General Medicine",
        period_start=datetime.now()
    )
    return builder


# Common test data
@pytest.fixture
def sample_dosage():
    """Sample dosage for medication tests."""
    return DosageBuilder.build(
        dose_value=1,
        dose_unit="tablet",
        frequency=3,
        period=1,
        period_unit="d",
        route=RouteOfAdministration.ORAL,
        timing_code=EventTiming.AFTER_MEAL,
        text="Take 1 tablet three times daily after meals"
    )


@pytest.fixture
def test_dates():
    """Common test dates."""
    now = datetime.now()
    return {
        'now': now,
        'yesterday': now - timedelta(days=1),
        'week_ago': now - timedelta(days=7),
        'month_ago': now - timedelta(days=30),
        'year_ago': now - timedelta(days=365),
        'future': now + timedelta(days=30)
    }
