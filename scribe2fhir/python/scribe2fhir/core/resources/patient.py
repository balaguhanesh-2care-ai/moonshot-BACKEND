"""
Patient Resource Builder - Creates FHIR Patient resources.

FHIR Mapping:
- Patient resource contains demographic and administrative information
- Identifier: Various IDs (ABHA, MRN, mobile, etc.)
- Name: Patient's name
- Gender: administrative gender
- BirthDate: Date of birth (or calculate from age)
- Address: Physical address

Reference: https://www.hl7.org/fhir/patient.html
"""

import uuid
from typing import Optional, List, Union, Tuple
from datetime import datetime, date, timedelta

from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

from ..types import DateTimeInput, format_date


class IdentifierType:
    """Common identifier types for patients."""
    ABHA = ("ABHA", "http://nrces.in/ndhm/fhir/r5/CodeSystem/ndhm-identifier-type-code")
    MRN = ("MR", "http://terminology.hl7.org/CodeSystem/v2-0203")
    MOBILE = ("PHONE", "http://terminology.hl7.org/CodeSystem/v2-0203")
    NATIONAL_ID = ("NI", "http://terminology.hl7.org/CodeSystem/v2-0203")
    PASSPORT = ("PPN", "http://terminology.hl7.org/CodeSystem/v2-0203")
    DRIVERS_LICENSE = ("DL", "http://terminology.hl7.org/CodeSystem/v2-0203")
    SOCIAL_SECURITY = ("SS", "http://terminology.hl7.org/CodeSystem/v2-0203")


class Gender:
    """FHIR administrative gender codes."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientBuilder:
    """
    Builder for creating FHIR Patient resources.
    
    The Patient resource represents demographic information about an individual
    receiving healthcare services.
    
    Example:
        patient = PatientBuilder.build(
            name="John Doe",
            age=(30, "years"),
            gender="male",
            identifiers=[("1234567890", "ABHA")],
            address="123 Main St, City, State"
        )
    """
    
    @staticmethod
    def _parse_name(name: Union[str, dict, HumanName]) -> HumanName:
        """Parse various name formats into a HumanName."""
        if isinstance(name, HumanName):
            return name
        
        if isinstance(name, dict):
            return HumanName(
                text=name.get("text"),
                family=name.get("family"),
                given=name.get("given") if isinstance(name.get("given"), list) else [name.get("given")] if name.get("given") else None,
                prefix=name.get("prefix"),
                suffix=name.get("suffix")
            )
        
        # Simple string - try to parse into given/family
        if isinstance(name, str):
            parts = name.strip().split()
            if len(parts) == 1:
                return HumanName(text=name, given=[name])
            elif len(parts) == 2:
                return HumanName(text=name, given=[parts[0]], family=parts[1])
            else:
                # First parts are given names, last is family
                return HumanName(text=name, given=parts[:-1], family=parts[-1])
        
        raise ValueError(f"Invalid name format: {name}")
    
    @staticmethod
    def _calculate_birthdate_from_age(age: Union[int, Tuple[int, str]]) -> str:
        """Calculate approximate birth date from age."""
        if isinstance(age, int):
            age_value = age
            age_unit = "years"
        else:
            age_value, age_unit = age
        
        today = date.today()
        
        if age_unit.lower() in ("year", "years", "y"):
            birth_date = today.replace(year=today.year - age_value)
        elif age_unit.lower() in ("month", "months", "mo"):
            # Approximate calculation
            days = age_value * 30
            birth_date = today - timedelta(days=days)
        elif age_unit.lower() in ("day", "days", "d"):
            birth_date = today - timedelta(days=age_value)
        else:
            raise ValueError(f"Unknown age unit: {age_unit}")
        
        return birth_date.isoformat()
    
    @staticmethod
    def _create_identifier(
        value: str,
        id_type: Union[str, Tuple[str, str]],
        system: Optional[str] = None
    ) -> Identifier:
        """Create an identifier with type coding."""
        # Determine type code and system
        if isinstance(id_type, tuple):
            type_code, type_system = id_type
        else:
            # Map common type names to codes
            type_map = {
                "abha": IdentifierType.ABHA,
                "mrn": IdentifierType.MRN,
                "mobile": IdentifierType.MOBILE,
                "phone": IdentifierType.MOBILE,
                "national_id": IdentifierType.NATIONAL_ID,
                "passport": IdentifierType.PASSPORT,
                "drivers_license": IdentifierType.DRIVERS_LICENSE,
                "ssn": IdentifierType.SOCIAL_SECURITY,
            }
            if id_type.lower() in type_map:
                type_code, type_system = type_map[id_type.lower()]
            else:
                type_code = id_type
                type_system = "http://terminology.hl7.org/CodeSystem/v2-0203"
        
        return Identifier(
            value=value,
            type=CodeableConcept(
                coding=[
                    Coding(
                        system=type_system,
                        code=type_code,
                        display=type_code
                    )
                ]
            ),
            system=system
        )
    
    @staticmethod
    def _parse_address(address: Union[str, dict, Address]) -> Address:
        """Parse various address formats into an Address."""
        if isinstance(address, Address):
            return address
        
        if isinstance(address, dict):
            return Address(
                text=address.get("text"),
                line=address.get("line") if isinstance(address.get("line"), list) else [address.get("line")] if address.get("line") else None,
                city=address.get("city"),
                state=address.get("state"),
                postalCode=address.get("postalCode") or address.get("postal_code"),
                country=address.get("country"),
                district=address.get("district")
            )
        
        # Simple string - use as text and first line
        if isinstance(address, str):
            return Address(text=address, line=[address])
        
        raise ValueError(f"Invalid address format: {address}")
    
    @staticmethod
    def build(
        name: Union[str, dict, HumanName],
        age: Optional[Union[int, Tuple[int, str]]] = None,
        birth_date: Optional[DateTimeInput] = None,
        gender: Optional[str] = None,
        identifiers: Optional[List[Tuple[str, Union[str, Tuple[str, str]]]]] = None,
        address: Optional[Union[str, dict, Address]] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Patient:
        """
        Build a FHIR Patient resource.
        
        Args:
            name: Patient name. Can be:
                  - str: "John Doe" or "John"
                  - dict: {"given": ["John"], "family": "Doe"}
                  - HumanName: Pre-built object
            age: Patient age. Can be:
                 - int: Age in years (e.g., 30)
                 - tuple: (value, unit) e.g., (30, "years"), (6, "months")
            birth_date: Date of birth (alternative to age)
            gender: Administrative gender (male, female, other, unknown)
            identifiers: List of (value, type) tuples, e.g.:
                         [("1234", "MRN"), ("9876543210", "ABHA")]
            address: Address string, dict, or Address object
            phone: Phone number
            email: Email address
            id: Resource ID
            
        Returns:
            FHIR Patient resource
            
        Example:
            patient = PatientBuilder.build(
                name="John Doe",
                age=(30, "years"),
                gender="male",
                identifiers=[
                    ("ABHA-12345", "ABHA"),
                    ("MRN-001", "MRN"),
                    ("9876543210", "mobile")
                ],
                address="123 Main Street, Bangalore, Karnataka"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse name
        human_name = PatientBuilder._parse_name(name)
        
        # Calculate birth date from age if provided
        calculated_birth_date = None
        if birth_date:
            calculated_birth_date = format_date(birth_date)
        elif age:
            calculated_birth_date = PatientBuilder._calculate_birthdate_from_age(age)
        
        # Parse identifiers
        parsed_identifiers = None
        if identifiers:
            parsed_identifiers = [
                PatientBuilder._create_identifier(value, id_type)
                for value, id_type in identifiers
            ]
        
        # Parse address
        parsed_address = None
        if address:
            parsed_address = [PatientBuilder._parse_address(address)]
        
        # Build telecom
        telecom = []
        if phone:
            telecom.append(ContactPoint(system="phone", value=phone, use="mobile"))
        if email:
            telecom.append(ContactPoint(system="email", value=email))
        
        # Create the Patient resource
        patient = Patient(
            id=resource_id,
            name=[human_name],
            gender=gender,
            birthDate=calculated_birth_date,
            identifier=parsed_identifiers,
            address=parsed_address,
            telecom=telecom if telecom else None
        )
        
        return patient


