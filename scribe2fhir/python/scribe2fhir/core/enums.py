"""
FHIR SDK Enums - Standard value sets for FHIR resources.

These enums map to FHIR terminology CodeSystems and ValueSets.
"""

from enum import Enum


# =============================================================================
# OBSERVATION STATUS
# http://hl7.org/fhir/observation-status
# =============================================================================
class ObservationStatus(str, Enum):
    """Status of an observation (symptom, vital, lab finding, etc.)"""
    REGISTERED = "registered"      # Existence of observation is registered
    PRELIMINARY = "preliminary"    # Preliminary (early/unverified)
    FINAL = "final"               # Complete and verified
    AMENDED = "amended"           # Modified after being final
    CORRECTED = "corrected"       # Result has been corrected
    CANCELLED = "cancelled"       # Observation is unavailable
    ENTERED_IN_ERROR = "entered-in-error"  # Entry was made in error
    UNKNOWN = "unknown"           # Status is unknown


# =============================================================================
# CONDITION CLINICAL STATUS
# http://terminology.hl7.org/CodeSystem/condition-clinical
# =============================================================================
class ConditionClinicalStatus(str, Enum):
    """Clinical status of a condition."""
    ACTIVE = "active"             # Subject is currently experiencing
    RECURRENCE = "recurrence"     # Relapsed condition previously resolved
    RELAPSE = "relapse"           # Returned after a period of remission
    INACTIVE = "inactive"         # Not currently experiencing but has
    REMISSION = "remission"       # Not currently experiencing
    RESOLVED = "resolved"         # Has been eliminated


# =============================================================================
# CONDITION VERIFICATION STATUS
# http://terminology.hl7.org/CodeSystem/condition-ver-status
# =============================================================================
class ConditionVerificationStatus(str, Enum):
    """Verification status of a condition."""
    UNCONFIRMED = "unconfirmed"           # Provisional assertion
    PROVISIONAL = "provisional"            # Provisional diagnosis
    DIFFERENTIAL = "differential"          # One of a set of possibilities
    CONFIRMED = "confirmed"                # Sufficient evidence to confirm
    REFUTED = "refuted"                   # Refuted
    ENTERED_IN_ERROR = "entered-in-error"  # Entry made in error


# =============================================================================
# CONDITION CATEGORY
# http://terminology.hl7.org/CodeSystem/condition-category
# =============================================================================
class ConditionCategory(str, Enum):
    """Category of the condition."""
    PROBLEM_LIST_ITEM = "problem-list-item"    # Medical history
    ENCOUNTER_DIAGNOSIS = "encounter-diagnosis"  # Diagnosis during encounter


# =============================================================================
# SEVERITY
# http://snomed.info/sct - Severity value set
# =============================================================================
class Severity(str, Enum):
    """Severity of a condition, symptom, etc."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

    @property
    def snomed_code(self) -> str:
        """Get SNOMED CT code for severity."""
        codes = {
            "mild": "255604002",
            "moderate": "6736007",
            "severe": "24484000",
        }
        return codes[self.value]

    @property
    def display(self) -> str:
        """Get display text for severity."""
        return self.value.capitalize()


# =============================================================================
# LATERALITY
# http://snomed.info/sct - Laterality value set
# =============================================================================
class Laterality(str, Enum):
    """Laterality (side of body)."""
    LEFT = "left"
    RIGHT = "right"
    BILATERAL = "bilateral"

    @property
    def snomed_code(self) -> str:
        """Get SNOMED CT code for laterality."""
        codes = {
            "left": "7771000",
            "right": "24028007",
            "bilateral": "51440002",
        }
        return codes[self.value]

    @property
    def display(self) -> str:
        """Get display text for laterality."""
        return self.value.capitalize()


# =============================================================================
# MEDICATION REQUEST STATUS
# http://hl7.org/fhir/CodeSystem/medicationrequest-status
# =============================================================================
class MedicationRequestStatus(str, Enum):
    """Status of a medication request (prescription)."""
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    STOPPED = "stopped"
    DRAFT = "draft"
    UNKNOWN = "unknown"


# =============================================================================
# MEDICATION REQUEST INTENT
# http://hl7.org/fhir/CodeSystem/medicationrequest-intent
# =============================================================================
class MedicationRequestIntent(str, Enum):
    """Intent of a medication request."""
    PROPOSAL = "proposal"
    PLAN = "plan"
    ORDER = "order"
    ORIGINAL_ORDER = "original-order"
    REFLEX_ORDER = "reflex-order"
    FILLER_ORDER = "filler-order"
    INSTANCE_ORDER = "instance-order"
    OPTION = "option"


# =============================================================================
# MEDICATION STATEMENT STATUS
# http://hl7.org/fhir/CodeSystem/medication-statement-status
# =============================================================================
class MedicationStatementStatus(str, Enum):
    """Status of a medication statement (history)."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    INTENDED = "intended"
    STOPPED = "stopped"
    ON_HOLD = "on-hold"
    UNKNOWN = "unknown"
    NOT_TAKEN = "not-taken"


# =============================================================================
# INTERPRETATION CODES
# http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation
# =============================================================================
class Interpretation(str, Enum):
    """Interpretation of an observation value."""
    NORMAL = "N"           # Normal
    ABNORMAL = "A"         # Abnormal
    LOW = "L"              # Low
    HIGH = "H"             # High
    CRITICAL_LOW = "LL"    # Critical low
    CRITICAL_HIGH = "HH"   # Critical high
    POSITIVE = "POS"       # Positive
    NEGATIVE = "NEG"       # Negative

    @property
    def display(self) -> str:
        """Get display text for interpretation."""
        displays = {
            "N": "Normal",
            "A": "Abnormal",
            "L": "Low",
            "H": "High",
            "LL": "Critical Low",
            "HH": "Critical High",
            "POS": "Positive",
            "NEG": "Negative",
        }
        return displays[self.value]


# =============================================================================
# FINDING STATUS (Custom for symptoms)
# =============================================================================
class FindingStatus(str, Enum):
    """Status of a clinical finding (present/absent)."""
    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"


# =============================================================================
# TIMING CODES
# http://hl7.org/fhir/event-timing
# =============================================================================
class EventTiming(str, Enum):
    """When during a day the action should occur."""
    MORNING = "MORN"
    AFTERNOON = "AFT"
    EVENING = "EVE"
    NIGHT = "NIGHT"
    BEFORE_SLEEP = "HS"
    AFTER_WAKING = "WAKE"
    WITH_MEAL = "C"
    BEFORE_MEAL = "AC"
    AFTER_MEAL = "PC"
    BEFORE_BREAKFAST = "ACM"
    AFTER_BREAKFAST = "PCM"
    BEFORE_LUNCH = "ACD"
    AFTER_LUNCH = "PCD"
    BEFORE_DINNER = "ACV"
    AFTER_DINNER = "PCV"


# =============================================================================
# ROUTE CODES
# http://snomed.info/sct - Routes of administration
# =============================================================================
class RouteOfAdministration(str, Enum):
    """Route of medication administration."""
    ORAL = "oral"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    TOPICAL = "topical"
    INHALATION = "inhalation"
    NASAL = "nasal"
    OPHTHALMIC = "ophthalmic"
    OTIC = "otic"
    RECTAL = "rectal"
    SUBLINGUAL = "sublingual"
    TRANSDERMAL = "transdermal"
    VAGINAL = "vaginal"

    @property
    def snomed_code(self) -> str:
        """Get SNOMED CT code for route."""
        codes = {
            "oral": "26643006",
            "intravenous": "47625008",
            "intramuscular": "78421000",
            "subcutaneous": "34206005",
            "topical": "6064005",
            "inhalation": "18679011000001101",
            "nasal": "46713006",
            "ophthalmic": "54485002",
            "otic": "10547007",
            "rectal": "37161004",
            "sublingual": "37839007",
            "transdermal": "45890007",
            "vaginal": "16857009",
        }
        return codes[self.value]

    @property
    def display(self) -> str:
        """Get display text for route."""
        return self.value.capitalize()


