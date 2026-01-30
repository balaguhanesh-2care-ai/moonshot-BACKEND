"""
Appointment Resource Builder - Creates FHIR Appointment resources.

FHIR Mapping:
- Appointment represents scheduled healthcare encounters
- status: proposed, pending, booked, arrived, fulfilled, cancelled, etc.
- serviceType: Type of service
- start/end: Scheduled time
- participant: Who/what is involved

Reference: https://www.hl7.org/fhir/appointment.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime

from fhir.resources.appointment import Appointment, AppointmentParticipant
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..types import (
    CodeInput,
    DateTimeInput,
    CodingSystem,
    parse_code_input,
    format_datetime,
)


class AppointmentStatus:
    """Appointment status codes."""
    PROPOSED = "proposed"
    PENDING = "pending"
    BOOKED = "booked"
    ARRIVED = "arrived"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    NOSHOW = "noshow"
    ENTERED_IN_ERROR = "entered-in-error"
    CHECKED_IN = "checked-in"
    WAITLIST = "waitlist"


class ParticipantStatus:
    """Participant status in an appointment."""
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    NEEDS_ACTION = "needs-action"


class AppointmentBuilder:
    """
    Builder for creating FHIR Appointment resources.
    
    Appointment represents a booking of a healthcare event.
    Used for scheduling follow-up visits, referrals, etc.
    
    Example:
        followup = AppointmentBuilder.build(
            start="2024-01-21T10:00:00Z",
            status=AppointmentStatus.BOOKED,
            service_type="Follow-up consultation",
            notes="Come with empty stomach"
        )
    """
    
    @staticmethod
    def build(
        start: Optional[DateTimeInput] = None,
        end: Optional[DateTimeInput] = None,
        status: str = AppointmentStatus.BOOKED,
        service_type: Optional[CodeInput] = None,
        specialty: Optional[CodeInput] = None,
        appointment_type: Optional[CodeInput] = None,
        reason: Optional[CodeInput] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        minutes_duration: Optional[int] = None,
        patient_reference: Optional[Reference] = None,
        practitioner_reference: Optional[Reference] = None,
        practitioner_name: Optional[str] = None,
        location_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Appointment:
        """
        Build a FHIR Appointment resource.
        
        Args:
            start: Scheduled start time
            end: Scheduled end time
            status: Appointment status (booked, pending, etc.)
            service_type: Type of service (follow-up, consultation)
            specialty: Medical specialty
            appointment_type: Type of appointment
            reason: Reason for the appointment
            description: Short description
            notes: Additional notes/instructions
            minutes_duration: Duration in minutes
            patient_reference: Reference to patient
            practitioner_reference: Reference to practitioner
            practitioner_name: Name of practitioner (if no reference)
            location_reference: Reference to location
            id: Resource ID
            
        Returns:
            FHIR Appointment resource
            
        Example:
            followup = AppointmentBuilder.build(
                start="2024-05-21T00:00:00Z",
                status=AppointmentStatus.BOOKED,
                practitioner_name="Dr. Smith",
                specialty="Cardiology",
                notes="Come with empty stomach"
            )
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Build service type
        service_type_list = None
        if service_type:
            service_type_list = [parse_code_input(service_type)]
        
        # Build specialty
        specialty_list = None
        if specialty:
            specialty_list = [parse_code_input(specialty)]
        
        # Build appointment type
        appointment_type_concept = None
        if appointment_type:
            appointment_type_concept = parse_code_input(appointment_type)
        
        # Build reason
        reason_code = None
        if reason:
            reason_code = [parse_code_input(reason)]
        
        # Build participants
        participants = []
        
        # Add patient
        if patient_reference:
            participants.append(
                AppointmentParticipant(
                    actor=patient_reference,
                    status=ParticipantStatus.ACCEPTED
                )
            )
        
        # Add practitioner
        if practitioner_reference or practitioner_name:
            actor = practitioner_reference or Reference(display=practitioner_name)
            participants.append(
                AppointmentParticipant(
                    actor=actor,
                    status=ParticipantStatus.ACCEPTED
                )
            )
        
        # Add location
        if location_reference:
            participants.append(
                AppointmentParticipant(
                    actor=location_reference,
                    status=ParticipantStatus.ACCEPTED
                )
            )
        
        # Build comment/notes
        comment = None
        if notes:
            comment = notes
        
        # Prepare R5 compatible fields
        from fhir.resources.codeablereference import CodeableReference
        
        # serviceType is List[CodeableReference] in R5
        service_type_val = None
        if service_type_list:
            service_type_val = [CodeableReference(concept=st) for st in service_type_list]

        # reason is List[CodeableReference] in R5
        reason_val = None
        if reason_code:
            reason_val = [CodeableReference(concept=rc) for rc in reason_code]
            
        # comments are notes in R5
        note_val = None
        if notes:
            note_val = [Annotation(text=notes)]

        # Create the Appointment resource
        appointment = Appointment(
            id=resource_id,
            status=status,
            serviceType=service_type_val,
            specialty=specialty_list,
            appointmentType=appointment_type_concept,
            reason=reason_val,
            description=description,
            start=format_datetime(start) if start else None,
            end=format_datetime(end) if end else None,
            minutesDuration=minutes_duration,
            participant=participants,
            note=note_val,
        )
        
        return appointment
    
    @staticmethod
    def build_followup(
        date: DateTimeInput,
        practitioner_name: Optional[str] = None,
        specialty: Optional[str] = None,
        notes: Optional[str] = None,
        patient_reference: Optional[Reference] = None,
        id: Optional[str] = None,
    ) -> Appointment:
        """
        Convenience method for building a follow-up appointment.
        
        Args:
            date: Follow-up date
            practitioner_name: Name of doctor for follow-up
            specialty: Medical specialty for referral
            notes: Additional instructions
            patient_reference: Reference to patient
            id: Resource ID
            
        Returns:
            FHIR Appointment for follow-up
            
        Example:
            followup = AppointmentBuilder.build_followup(
                date="2024-05-21",
                practitioner_name="Dr. Sharma",
                specialty="Endocrinology",
                notes="Bring all previous lab reports"
            )
        """
        return AppointmentBuilder.build(
            start=date,
            status=AppointmentStatus.BOOKED,
            service_type="Follow-up",
            specialty=specialty,
            practitioner_name=practitioner_name,
            patient_reference=patient_reference,
            notes=notes,
            id=id,
        )


