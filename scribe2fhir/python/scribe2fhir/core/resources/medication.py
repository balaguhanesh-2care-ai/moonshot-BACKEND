"""
Medication Resource Builder - Creates FHIR MedicationRequest and MedicationStatement resources.

FHIR Mapping:
- MedicationRequest: For prescribed medications (orders, prescriptions)
- MedicationStatement: For medication history (what patient is/was taking)

Key elements:
- medicationCodeableConcept: The drug being prescribed/taken
- dosageInstruction/dosage: How to take the medication (Dosage type)
- status: Current status of the medication
- intent (MedicationRequest): Purpose of the request (order, plan, etc.)

Reference: 
- https://www.hl7.org/fhir/medicationrequest.html
- https://www.hl7.org/fhir/medicationstatement.html
- https://www.hl7.org/fhir/dosage.html
"""

import uuid
from typing import Optional, List, Union
from datetime import datetime, date

from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.dosage import Dosage
from fhir.resources.timing import Timing, TimingRepeat
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.range import Range
from fhir.resources.duration import Duration
from fhir.resources.reference import Reference
from fhir.resources.annotation import Annotation

from ..enums import (
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationStatementStatus,
    RouteOfAdministration,
    EventTiming,
)
from ..types import (
    CodeInput,
    DateTimeInput,
    QuantityInput,
    CodingSystem,
    parse_code_input,
    parse_quantity_input,
    format_datetime,
    create_quantity,
    create_period,
)


class DosageBuilder:
    """
    Utility class for building FHIR Dosage objects.
    
    Dosage describes how a medication should be taken including:
    - Dose amount (e.g., 500mg, 2 tablets)
    - Timing (e.g., 3 times a day, every 8 hours)
    - Route (e.g., oral, intravenous)
    - Additional instructions
    
    Example:
        dosage = DosageBuilder.build(
            dose_value=500,
            dose_unit="mg",
            frequency=3,
            period=1,
            period_unit="d",
            route=RouteOfAdministration.ORAL,
            timing_code=EventTiming.AFTER_MEAL,
            text="Take 500mg three times daily after meals"
        )
    """
    
    @staticmethod
    def build(
        dose_value: Optional[float] = None,
        dose_unit: Optional[str] = None,
        dose_quantity: Optional[Union[Quantity, QuantityInput]] = None,
        frequency: Optional[int] = None,
        period: Optional[float] = None,
        period_unit: Optional[str] = None,  # s, min, h, d, wk, mo, a
        duration: Optional[float] = None,
        duration_unit: Optional[str] = None,
        route: Optional[Union[RouteOfAdministration, str, CodeableConcept]] = None,
        timing_code: Optional[Union[EventTiming, str]] = None,
        timing: Optional[Timing] = None,
        as_needed: bool = False,
        as_needed_for: Optional[CodeInput] = None,
        max_dose_per_period: Optional[Quantity] = None,
        text: Optional[str] = None,
        additional_instruction: Optional[str] = None,
        sequence: Optional[int] = None,
    ) -> Dosage:
        """
        Build a FHIR Dosage object.
        
        Args:
            dose_value: Numeric dose value (e.g., 500)
            dose_unit: Unit for dose (e.g., "mg", "tablet")
            dose_quantity: Pre-built Quantity object (alternative to dose_value/unit)
            frequency: How many times per period (e.g., 3 for "three times")
            period: The period length (e.g., 1 for "per day")
            period_unit: Unit for period: s, min, h, d, wk, mo, a
            duration: Total duration of treatment
            duration_unit: Unit for duration
            route: Route of administration
            timing_code: When during day (MORN, EVE, AC, PC, etc.)
            timing: Pre-built Timing object
            as_needed: Whether to take as needed (PRN)
            as_needed_for: Condition for as-needed use
            max_dose_per_period: Maximum dose in a period
            text: Human-readable dosing instructions
            additional_instruction: Extra instructions (e.g., "with food")
            sequence: Order when multiple dosages are given
            
        Returns:
            FHIR Dosage object
        """
        # Build dose quantity
        dose_and_rate = None
        if dose_value is not None and dose_unit is not None:
            dose_qty = create_quantity(dose_value, dose_unit)
            dose_and_rate = [{"doseQuantity": dose_qty}]
        elif dose_quantity is not None:
            if not isinstance(dose_quantity, Quantity):
                dose_quantity = parse_quantity_input(dose_quantity)
            dose_and_rate = [{"doseQuantity": dose_quantity}]
        
        # Build timing
        if timing is None and (frequency is not None or timing_code is not None or duration is not None):
            repeat_kwargs = {}
            
            if frequency is not None:
                repeat_kwargs["frequency"] = frequency
            
            if period is not None:
                repeat_kwargs["period"] = period
                repeat_kwargs["periodUnit"] = period_unit or "d"
            
            if duration is not None:
                repeat_kwargs["duration"] = duration
                repeat_kwargs["durationUnit"] = duration_unit or "d"
            
            if timing_code:
                code = timing_code.value if isinstance(timing_code, EventTiming) else timing_code
                repeat_kwargs["when"] = [code]
            
            timing_repeat = TimingRepeat(**repeat_kwargs) if repeat_kwargs else None
            
            timing = Timing(repeat=timing_repeat) if timing_repeat else None
        
        # Build route
        route_concept = None
        if route is not None:
            if isinstance(route, CodeableConcept):
                route_concept = route
            elif isinstance(route, RouteOfAdministration):
                route_concept = CodeableConcept(
                    coding=[
                        Coding(
                            system=CodingSystem.SNOMED_CT,
                            code=route.snomed_code,
                            display=route.display
                        )
                    ],
                    text=route.display
                )
            elif isinstance(route, str):
                try:
                    route_enum = RouteOfAdministration(route.lower())
                    route_concept = CodeableConcept(
                        coding=[
                            Coding(
                                system=CodingSystem.SNOMED_CT,
                                code=route_enum.snomed_code,
                                display=route_enum.display
                            )
                        ],
                        text=route_enum.display
                    )
                except ValueError:
                    # If not a known route, just use text
                    route_concept = CodeableConcept(text=route)
        
        # Build as-needed
        as_needed_concept = None
        if as_needed_for:
            as_needed_concept = parse_code_input(as_needed_for)
        
        # Build additional instructions
        additional = None
        if additional_instruction:
            additional = [CodeableConcept(text=additional_instruction)]
        
        # Create the Dosage object
        dosage = Dosage(
            sequence=sequence,
            text=text,
            additionalInstruction=additional,
            timing=timing,
            asNeeded=as_needed if not as_needed_for else None,
            asNeededFor=[as_needed_concept] if as_needed_concept else None,
            route=route_concept,
            doseAndRate=dose_and_rate,
            maxDosePerPeriod=max_dose_per_period,
        )
        
        return dosage


class MedicationBuilder:
    """
    Builder for creating FHIR medication resources.
    
    Supports two types of medication resources:
    1. MedicationRequest - For prescribed medications (what the doctor orders)
    2. MedicationStatement - For medication history (what the patient reports taking)
    
    Example:
        builder = MedicationBuilder()
        
        # Prescribed medication
        prescription = builder.build_prescribed(
            medication=("387517004", "http://snomed.info/sct", "Paracetamol"),
            dosage=DosageBuilder.build(
                dose_value=500,
                dose_unit="mg",
                frequency=3,
                period=1,
                period_unit="d",
                route=RouteOfAdministration.ORAL
            ),
            duration_value=7,
            duration_unit="d"
        )
        
        # Medication history
        history = builder.build_history(
            medication=("Aspirin", ("7984", "http://www.nlm.nih.gov/research/umls/rxnorm")),
            dosage=DosageBuilder.build(dose_value=81, dose_unit="mg"),
            notes="Taking daily for heart health"
        )
    """
    
    @staticmethod
    def build_prescribed(
        medication: CodeInput,
        dosage: Optional[Union[Dosage, List[Dosage]]] = None,
        status: Union[MedicationRequestStatus, str] = MedicationRequestStatus.ACTIVE,
        intent: Union[MedicationRequestIntent, str] = MedicationRequestIntent.ORDER,
        duration_value: Optional[float] = None,
        duration_unit: Optional[str] = None,
        quantity_value: Optional[float] = None,
        quantity_unit: Optional[str] = None,
        refills: Optional[int] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        encounter_reference: Optional[Reference] = None,
        requester_reference: Optional[Reference] = None,
        authored_on: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> MedicationRequest:
        """
        Build a FHIR MedicationRequest resource for a prescribed medication.
        
        Args:
            medication: The medication being prescribed
            dosage: Dosing instructions (Dosage object or list)
            status: Status of the prescription (active, completed, etc.)
            intent: Intent (order, plan, proposal, etc.)
            duration_value: Duration of treatment
            duration_unit: Unit for duration (d, wk, mo)
            quantity_value: Amount to dispense
            quantity_unit: Unit for quantity (tablet, mL, etc.)
            refills: Number of refills allowed
            notes: Additional notes/instructions
            reason: Reason for the prescription
            subject_reference: Reference to the patient
            encounter_reference: Reference to the encounter
            requester_reference: Reference to the prescriber
            authored_on: When the prescription was written
            id: Resource ID
            
        Returns:
            FHIR MedicationRequest resource
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse medication code
        medication_code = parse_code_input(medication)
        
        # Handle status enum
        status_value = status.value if isinstance(status, MedicationRequestStatus) else status
        
        # Handle intent enum
        intent_value = intent.value if isinstance(intent, MedicationRequestIntent) else intent
        
        # Build dosage instructions
        dosage_instruction = None
        if dosage is not None:
            if isinstance(dosage, list):
                dosage_instruction = dosage
            else:
                dosage_instruction = [dosage]
        
        # Build dispense request
        dispense_request = None
        if duration_value or quantity_value or refills is not None:
            dispense_request = {}
            
            if duration_value:
                dispense_request["expectedSupplyDuration"] = Duration(
                    value=duration_value,
                    unit=duration_unit or "d",
                    system=CodingSystem.UCUM,
                    code=duration_unit or "d"
                )
            
            if quantity_value:
                dispense_request["quantity"] = Quantity(
                    value=quantity_value,
                    unit=quantity_unit or "unit"
                )
            
            if refills is not None:
                dispense_request["numberOfRepeatsAllowed"] = refills
        
        # Build reason
        reason_code = None
        if reason:
            reason_code = [parse_code_input(reason)]
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Prepare R5 compatible fields
        from fhir.resources.codeablereference import CodeableReference
        
        # medication is CodeableReference in R5
        medication_ref = CodeableReference(concept=medication_code)

        # reason is List[CodeableReference] in R5
        reason_val = None
        if reason_code:
            reason_val = [CodeableReference(concept=rc) for rc in reason_code]

        # Create the MedicationRequest resource
        medication_request = MedicationRequest(
            id=resource_id,
            status=status_value,
            intent=intent_value,
            medication=medication_ref,
            subject=subject_reference,
            encounter=encounter_reference,
            authoredOn=format_datetime(authored_on) if authored_on else None,
            requester=requester_reference,
            reason=reason_val,
            dosageInstruction=dosage_instruction,
            dispenseRequest=dispense_request,
            note=note,
        )
        
        return medication_request
    
    @staticmethod
    def build_history(
        medication: CodeInput,
        dosage: Optional[Union[Dosage, List[Dosage]]] = None,
        status: Union[MedicationStatementStatus, str] = MedicationStatementStatus.ACTIVE,
        effective_start: Optional[DateTimeInput] = None,
        effective_end: Optional[DateTimeInput] = None,
        notes: Optional[str] = None,
        reason: Optional[CodeInput] = None,
        subject_reference: Optional[Reference] = None,
        context_reference: Optional[Reference] = None,
        information_source_reference: Optional[Reference] = None,
        date_asserted: Optional[DateTimeInput] = None,
        id: Optional[str] = None,
    ) -> MedicationStatement:
        """
        Build a FHIR MedicationStatement resource for medication history.
        
        Args:
            medication: The medication being/was taken
            dosage: Dosing information
            status: Status (active, completed, stopped, etc.)
            effective_start: When started taking
            effective_end: When stopped taking
            notes: Additional notes
            reason: Reason for taking the medication
            subject_reference: Reference to the patient
            context_reference: Reference to encounter/episode
            information_source_reference: Who reported this
            date_asserted: When this was recorded
            id: Resource ID
            
        Returns:
            FHIR MedicationStatement resource
        """
        # Generate ID if not provided
        resource_id = id or str(uuid.uuid4())
        
        # Parse medication code
        medication_code = parse_code_input(medication)
        
        # Handle status enum
        status_value = status.value if isinstance(status, MedicationStatementStatus) else status
        
        # Build dosage
        dosage_list = None
        if dosage is not None:
            if isinstance(dosage, list):
                dosage_list = dosage
            else:
                dosage_list = [dosage]
        
        # Build effective period
        effective_period = None
        effective_datetime = None
        if effective_start or effective_end:
            if effective_end:
                effective_period = create_period(effective_start, effective_end)
            else:
                effective_datetime = format_datetime(effective_start)
        
        # Build reason
        reason_code = None
        if reason:
            reason_code = [parse_code_input(reason)]
        
        # Build notes
        note = None
        if notes:
            note = [Annotation(text=notes)]
        
        # Prepare R5 compatible fields
        from fhir.resources.codeablereference import CodeableReference
        
        # medication is CodeableReference in R5
        medication_ref = CodeableReference(concept=medication_code)

        # reason is List[CodeableReference] in R5
        reason_val = None
        if reason_code:
            reason_val = [CodeableReference(concept=rc) for rc in reason_code]

        # Create the MedicationStatement resource
        medication_statement = MedicationStatement(
            id=resource_id,
            status=status_value,
            medication=medication_ref,
            subject=subject_reference,
            # context is removed in R5, mapped to encounter or partOf usually, but we'll try encounter field if appropriate or skip
            encounter=context_reference, # Using encounter field which exists in R5
            effectiveDateTime=effective_datetime,
            effectivePeriod=effective_period,
            dateAsserted=format_datetime(date_asserted) if date_asserted else None,
            informationSource=information_source_reference,
            reason=reason_val,
            dosage=dosage_list,
            note=note,
        )
        
        return medication_statement


