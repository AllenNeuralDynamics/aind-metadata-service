"""Maps ExaSPIM Smartsheet information to aind-data-schema Procedures models."""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from aind_data_schema.components.injection_procedures import (
    Injection,
    InjectionDynamics,
    InjectionProfile,
    ViralMaterial,
)
from aind_data_schema.components.reagent import (
    ProbeReagent,
    ProteinProbe,
    Reagent,
)
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.components.specimen_procedures import SpecimenProcedure
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)
from aind_data_schema_models.units import VolumeUnit

from aind_smartsheet_service_async_client.models import (
    MouseTracker,
    SampleTracking,
    ImagingQueue,
    QcSheet,

)


class ExaspimProceduresMapper:
    """Class to handle mapping of ExaSPIM procedures data."""

    def __init__(
        self,
        mouse_tracker_info: List[MouseTracker] = None,
        sample_tracking_info: List[SampleTracking] = None,
        imaging_queue_info: List[ImagingQueue] = None,
        qc_sheet_info: List[QcSheet] = None,
    ):
        """
        Class constructor.

        Parameters
        ----------
        mouse_tracker_info : List[MouseTracker]
            Mouse tracker data from Smartsheet
        sample_tracking_info : List[SampleTracking]
            Sample tracking data from Smartsheet
        imaging_queue_info : List[ImagingQueue]
            Imaging queue data from Smartsheet
        qc_sheet_info : List[QcSheet]
            QC sheet data from Smartsheet
        """
        self.mouse_tracker_info = mouse_tracker_info or []
        self.sample_tracking_info = sample_tracking_info or []
        self.imaging_queue_info = imaging_queue_info or []
        self.qc_sheet_info = qc_sheet_info or []

    @staticmethod
    def _parse_date(raw: Any) -> Optional[date]:
        """
        Parse a raw Smartsheet value to a date.

        Parameters
        ----------
        raw : Any
            The cell value

        Returns
        -------
        Optional[date]
            Parsed date, or None if empty or unparseable
        """
        if raw is None:
            return None
        if isinstance(raw, date):
            return raw
        text = str(raw).strip()
        if not text:
            return None
        for fmt in (
            "%m/%d/%y",
            "%m/%d/%Y",
            "%m/%d/%y %I:%M %p",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
        ):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_experimenters(sample_tracking_row: SampleTracking) -> List[str]:
        """
        Parse the processing_lead field into a list of experimenter names.

        Handles comma- or semicolon-separated lists of experimenter names.

        Parameters
        ----------
        sample_tracking_row : SampleTracking
            Row from Sample Tracking sheet

        Returns
        -------
        List[str]
            List of experimenter name strings (may be empty)
        """
        import re
        
        raw = sample_tracking_row.processing_lead
        if not raw:
            return []
        
        raw = raw.strip()
        if not raw:
            return []
        
        # Split on comma or semicolon
        names = re.split(r"[;,]", raw)
        experimenters: List[str] = []
        for name in names:
            name = name.strip()
            if name:
                experimenters.append(name)
        return experimenters

    def build_injection_surgery(
        self, mouse_tracker_row: MouseTracker
    ) -> Optional[Surgery]:
        """
        Build a Surgery model containing Injection(s) from Mouse Tracker data.

        Supports up to 4 independent viral injections (Virus1-Virus4).

        Parameters
        ----------
        mouse_tracker_row : MouseTracker
            Row from the Mouse Tracker sheet

        Returns
        -------
        Optional[Surgery]
            Surgery model instance or None if no injections found
        """
        injection_objects: List[Injection] = []
        injection_dates: List[date] = []

        for virus_num in range(1, 5):
            prefix = f"virus{virus_num}"
            virus_name = getattr(mouse_tracker_row, prefix)
            if not virus_name:
                continue
            virus_name = virus_name.strip()

            injection_date = self._parse_date(
                getattr(mouse_tracker_row, f"{prefix}_injection_date")
            )
            if injection_date:
                injection_dates.append(injection_date)

            virus_id = getattr(mouse_tracker_row, f"{prefix}_id")
            if virus_id:
                virus_id = virus_id.strip()

            titer_raw = getattr(mouse_tracker_row, f"{prefix}_stock_titer_gc_ml")

            # Volume — check stereotaxic first
            if virus_num == 4:
                volume_raw = mouse_tracker_row.stereotaxic_volume_injected_nl
            else:
                volume_raw = getattr(
                    mouse_tracker_row, f"{prefix}_stereotaxic_volume_injected_nl"
                )

            # Fall back to retro-orbital volume (stored in µL)
            if not volume_raw:
                ro_volume_raw = mouse_tracker_row.virus_mix_total_volume_injected_ro_ul
            else:
                ro_volume_raw = None

            # Build injection material
            vm_kwargs: Dict[str, Any] = {"name": virus_name}
            if virus_id:
                vm_kwargs["tars_identifiers"] = {
                    "virus_tars_id": virus_id,
                    "prep_lot_number": virus_id,
                }
            if titer_raw is not None:
                vm_kwargs["titer"] = int(float(str(titer_raw)))

            viral_material = ViralMaterial(**vm_kwargs)

            # Build injection dynamics
            dynamics_list: List[InjectionDynamics] = []
            if volume_raw:
                vol = float(str(volume_raw))
                if vol > 0:
                    dynamics_list.append(
                        InjectionDynamics(
                            profile=InjectionProfile.BOLUS,
                            volume=vol,
                            volume_unit=VolumeUnit.NL,
                        )
                    )
            elif ro_volume_raw:
                # RO volume is in µL — convert to nL
                vol_ul = float(str(ro_volume_raw))
                if vol_ul > 0:
                    vol_nl = vol_ul * 1000.0
                    dynamics_list.append(
                        InjectionDynamics(
                            profile=InjectionProfile.BOLUS,
                            volume=vol_nl,
                            volume_unit=VolumeUnit.NL,
                        )
                    )

            # Skip injection if no volume data
            if not dynamics_list:
                continue

            # Build injection object
            injection_objects.append(
                Injection(
                    injection_materials=[viral_material],
                    dynamics=dynamics_list,
                )
            )

        if not injection_objects:
            return None

        # Use the earliest injection date as the surgery date
        surgery_date = min(injection_dates) if injection_dates else None

        return Surgery(
            start_date=surgery_date,
            procedures=injection_objects,
        )

    def build_delipidation(
        self, sample_tracking_row: SampleTracking, specimen_id: str, experimenters: List[str] = None
    ) -> Optional[SpecimenProcedure]:
        """
        Build a Delipidation SpecimenProcedure.

        Two phases: DCM (dichloromethane) and SBiP.

        Parameters
        ----------
        sample_tracking_row : SampleTracking
            Row from Sample Tracking sheet
        specimen_id : str
            The specimen identifier

        Returns
        -------
        Optional[SpecimenProcedure]
            The delipidation procedure or None if dates missing
        """
        start_date = self._parse_date(
            sample_tracking_row.dcm_delipidation_start
        )
        end_date = self._parse_date(
            sample_tracking_row.sbip_delipidation_end
        )

        if not start_date or not end_date:
            # logger.info(
            #     "Delipidation dates not available — skipping delipidation."
            # )
            return None

        reagents = [
            Reagent(
                name="Dichloromethane (DCM)",
                source=Organization.OTHER,
            ),
            Reagent(
                name="SBiP (Sodium dodecylsulfate, Butanol, isoPropanol)",
                source=Organization.OTHER,
            ),
        ]

        qc_notes = self._extract_qc_notes("special")

        return SpecimenProcedure(
            procedure_type=SpecimenProcedureType.DELIPIDATION,
            procedure_name="Delipidation (DCM + SBiP)",
            specimen_id=specimen_id,
            start_date=start_date,
            end_date=end_date,
            experimenters=experimenters or [],
            procedure_details=reagents,
            notes=qc_notes,
        )

    def build_immunolabeling(
        self, sample_tracking_row: SampleTracking, specimen_id: str, experimenters: List[str] = None
    ) -> Optional[SpecimenProcedure]:
        """
        Build an Immunolabeling SpecimenProcedure.

        Parameters
        ----------
        sample_tracking_row : SampleTracking
            Row from Sample Tracking sheet
        specimen_id : str
            The specimen identifier

        Returns
        -------
        Optional[SpecimenProcedure]
            The immunolabeling procedure or None if dates missing
        """
        start_date = self._parse_date(
            sample_tracking_row.immuno_primary_ab_start_date
        )
        if not start_date:
            return None

        secondary_start = self._parse_date(
            sample_tracking_row.immuno_secondary_ab_start_date
        )
        end_date = secondary_start or start_date

        reagents: List[ProbeReagent] = []

        # Build primary antibody reagents (up to 3)
        for i in range(1, 4):
            ab_name = getattr(sample_tracking_row, f"immuno_primary_antibody{i}")
            if not ab_name:
                continue
            ab_name = ab_name.strip()

            catalog = getattr(sample_tracking_row, f"primary_antibody{i}_catalog_num")
            if catalog:
                catalog = catalog.strip()
            
            lot = getattr(sample_tracking_row, f"primary_antibody{i}_lot_num")
            if lot:
                lot = lot.strip()
            mass_raw = getattr(
                sample_tracking_row, f"mass_of_primary_antibody{i}_used_per_brain_ug"
            )
            mass = float(str(mass_raw)) if mass_raw is not None else 0.0

            reagent = ProbeReagent(
                name=f"Primary Antibody: {ab_name}",
                source=Organization.OTHER,
                lot_number=lot,
                target=ProteinProbe(
                    protein=PIDName(name=ab_name),
                    mass=mass,
                ),
            )
            reagents.append(reagent)

        # Build secondary antibody reagents (up to 3)
        for i in range(1, 4):
            ab_name = getattr(sample_tracking_row, f"immuno_secondary_antibody{i}")
            if not ab_name:
                continue
            ab_name = ab_name.strip()

            catalog = getattr(sample_tracking_row, f"secondary_antibody{i}_catalog_num")
            if catalog:
                catalog = catalog.strip()
            
            lot = getattr(sample_tracking_row, f"secondary_antibody{i}_lot_num")
            if lot:
                lot = lot.strip()
            mass_raw = getattr(
                sample_tracking_row, f"mass_of_secondary_antibody{i}_used_per_brain_ug"
            )
            mass = float(str(mass_raw)) if mass_raw is not None else 0.0

            reagent = ProbeReagent(
                name=f"Secondary Antibody: {ab_name}",
                source=Organization.OTHER,
                lot_number=lot,
                target=ProteinProbe(
                    protein=PIDName(name=ab_name),
                    mass=mass,
                ),
            )
            reagents.append(reagent)

        # Build notes about RRID if available
        primary_rrid = sample_tracking_row.primary_antibody_rrid
        if primary_rrid:
            primary_rrid = primary_rrid.strip()
        secondary_rrid = sample_tracking_row.secondary_antibody_rrid
        if secondary_rrid:
            secondary_rrid = secondary_rrid.strip()
        
        rrid_notes = []
        if primary_rrid:
            rrid_notes.append(f"Primary RRID: {primary_rrid}")
        if secondary_rrid:
            rrid_notes.append(f"Secondary RRID: {secondary_rrid}")

        qc_notes = self._extract_qc_notes("immunolabeling")
        notes_parts = []
        if rrid_notes:
            notes_parts.append("; ".join(rrid_notes))
        if qc_notes:
            notes_parts.append(qc_notes)

        return SpecimenProcedure(
            procedure_type=SpecimenProcedureType.IMMUNOLABELING,
            procedure_name="Primary + Secondary Immunolabelling",
            specimen_id=specimen_id,
            start_date=start_date,
            end_date=end_date,
            experimenters=experimenters or [],
            procedure_details=reagents,
            notes="; ".join(notes_parts) if notes_parts else None,
        )

    def build_gelation(
        self, sample_tracking_row: SampleTracking, specimen_id: str, experimenters: List[str] = None
    ) -> Optional[SpecimenProcedure]:
        """
        Build a Gelation SpecimenProcedure.

        Parameters
        ----------
        sample_tracking_row : SampleTracking
            Row from Sample Tracking sheet
        specimen_id : str
            The specimen identifier

        Returns
        -------
        Optional[SpecimenProcedure]
            The gelation procedure or None if dates missing
        """
        start_date = self._parse_date(
            sample_tracking_row.gelation_mbs_start
        )
        if not start_date:
            return None

        # End date: storage date or PBS Wash End
        storage_date = self._parse_date(
            sample_tracking_row.date_of_storage_in_pbs_az_0_05_4c
        )
        pbs_wash_end = self._parse_date(
            sample_tracking_row.pbs_wash_end
        )
        end_date = storage_date or pbs_wash_end or start_date

        reagents = [
            Reagent(
                name="MBS (m-Maleimidobenzoyl-N-hydroxysuccinimide ester)",
                source=Organization.OTHER,
            ),
            Reagent(
                name="Acryloyl-X (AcX)", source=Organization.OTHER
            ),
            Reagent(
                name="Stock X + VA-044", source=Organization.OTHER
            ),
            Reagent(
                name="Proteinase K (ProK)", source=Organization.OTHER
            ),
            Reagent(
                name="PBS", source=Organization.OTHER
            ),
        ]

        # Build protocol parameters with sub-step timing
        protocol_params: Dict[str, str] = {}
        substep_mapping = [
            ("MBS Start", "gelation_mbs_start"),
            ("MBS End", "gelation_mbs_end"),
            ("AcX Start", "gelation_ac_x_start"),
            ("AcX End", "gelation_ac_x_end"),
            ("PBS Wash Start", "gelation_pbs_wash_start"),
            ("PBS Wash End", "gelation_pbs_wash_end"),
            (
                "StockX Equilibration Start",
                "gelation_stock_xva_044_equilibration_start",
            ),
            (
                "StockX Equilibration End",
                "gelation_stock_xva_044_equilibration_end",
            ),
            ("ProK RT Start", "gelation_prok_rt_start"),
            ("ProK RT End", "gelation_prok_rt_end"),
            ("ProK 37C Start", "gelation_add_l_prok_37c_start"),
            ("ProK 37C End", "gelation_add_l_prok_37c_end"),
            ("PBS Wash Start (post-gel)", "pbs_wash_start"),
            ("PBS Wash End (post-gel)", "pbs_wash_end"),
            ("4C Storage Date", "date_of_storage_in_pbs_az_0_05_4c"),
        ]
        for param_key, col_name in substep_mapping:
            val = getattr(sample_tracking_row, col_name)
            if val is not None:
                protocol_params[param_key] = str(val)

        qc_notes = self._extract_qc_notes("digestion")

        return SpecimenProcedure(
            procedure_type=SpecimenProcedureType.GELATION,
            procedure_name="Gelation (MBS, AcX, StockX+VA-044, ProK digestion)",
            specimen_id=specimen_id,
            start_date=start_date,
            end_date=end_date,
            experimenters=experimenters or [],
            procedure_details=reagents,
            protocol_parameters=(
                protocol_params if protocol_params else None
            ),
            notes=qc_notes,
        )

    def build_expansion(
        self, sample_tracking_row: SampleTracking, specimen_id: str, 
        imaging_start_date: Optional[date], experimenters: List[str] = None
    ) -> Optional[SpecimenProcedure]:
        """
        Build an Expansion SpecimenProcedure.

        Expansion is only performed if the Status column is "Imaged".
        Dates are inferred by backtracking from the imaging start date:
        - SSC: 2 days (imaging_start - 3 days to imaging_start - 1 day)
        - Ascorbic acid: 1 day (imaging_start - 1 day to imaging_start)
        - Overall: imaging_start - 3 days to imaging_start

        Parameters
        ----------
        sample_tracking_row : SampleTracking
            Row from Sample Tracking sheet
        specimen_id : str
            The specimen identifier
        imaging_start_date : Optional[date]
            Imaging start date to backtrack from
        experimenters : List[str]
            List of experimenters

        Returns
        -------
        Optional[SpecimenProcedure]
            The expansion procedure or None if not applicable
        """
        from datetime import timedelta
        
        # Check if expansion has occurred (status must be "Imaged")
        status = sample_tracking_row.status
        if not status:
            return None
        status = status.strip().lower()
        if status != "imaged":
            return None
        
        # Need imaging start date to calculate expansion dates
        if not imaging_start_date:
            return None
        
        # Backtrack 3 days from imaging start
        start_date = imaging_start_date - timedelta(days=3)
        end_date = imaging_start_date
        
        reagents = [
            Reagent(
                name="Saline-Sodium Citrate (SSC)",
                source=Organization.OTHER,
            ),
            Reagent(
                name="Ascorbic Acid",
                source=Organization.OTHER,
            ),
        ]
        
        # Protocol parameters with sub-step timing
        protocol_params = {
            "ssc_duration": "2 days",
            "ssc_start": str(imaging_start_date - timedelta(days=3)),
            "ssc_end": str(imaging_start_date - timedelta(days=1)),
            "ascorbic_acid_duration": "1 day",
            "ascorbic_acid_start": str(imaging_start_date - timedelta(days=1)),
            "ascorbic_acid_end": str(imaging_start_date),
        }

        return SpecimenProcedure(
            procedure_type=SpecimenProcedureType.EXPANSION,
            procedure_name="Expansion",
            specimen_id=specimen_id,
            start_date=start_date,
            end_date=end_date,
            experimenters=experimenters or [],
            procedure_details=reagents,
            protocol_parameters=protocol_params,
        )

    def build_mounting_and_imaging(
        self, imaging_queue_row: ImagingQueue, specimen_id: str, experimenters: List[str] = None
    ) -> Optional[SpecimenProcedure]:
        """
        Build a Mounting SpecimenProcedure for the final imaging step.

        Parameters
        ----------
        imaging_queue_row : ImagingQueue
            Row from the Imaging Queue sheet
        specimen_id : str
            The specimen identifier

        Returns
        -------
        Optional[SpecimenProcedure]
            The mounting + imaging procedure or None if dates missing
        """
        start_date = self._parse_date(
            imaging_queue_row.imaging_start_date
        )
        if not start_date:
            return None

        end_date = self._parse_date(
            imaging_queue_row.imaging_end_date
        ) or start_date

        microscope = imaging_queue_row.microscope
        if microscope:
            microscope = microscope.strip()
        imaging_buffer = imaging_queue_row.imaging_buffer
        if imaging_buffer:
            imaging_buffer = imaging_buffer.strip()
        channels = imaging_queue_row.signal_channel_s
        if channels:
            channels = channels.strip()
        notes_col = imaging_queue_row.notes
        if notes_col:
            notes_col = notes_col.strip()

        reagents: List[Reagent] = []
        if imaging_buffer:
            reagents.append(
                Reagent(
                    name=f"Imaging Buffer: {imaging_buffer}",
                    source=Organization.OTHER,
                )
            )

        notes_parts = []
        if microscope:
            notes_parts.append(f"Microscope: {microscope}")
        if channels:
            notes_parts.append(f"Signal channels: {channels}")
        if notes_col:
            notes_parts.append(f"Imaging notes: {notes_col}")

        return SpecimenProcedure(
            procedure_type=SpecimenProcedureType.MOUNTING,
            procedure_name="Mounting and ExaSPIM Imaging",
            specimen_id=specimen_id,
            start_date=start_date,
            end_date=end_date,
            experimenters=experimenters or [],
            procedure_details=reagents if reagents else [],
            notes="; ".join(notes_parts) if notes_parts else None,
        )

    def _extract_qc_notes(self, category: str) -> Optional[str]:
        """
        Extract QC notes for a specific category from QC sheet.

        Parameters
        ----------
        category : str
            The category key to look for

        Returns
        -------
        Optional[str]
            Combined notes, or None if empty
        """
        column_mapping = {
            "perfusion": "perfusion_dissection_quality_notes",
            "immunolabeling": "immuno_gross_anatomy_notes",
            "digestion": "digestion_notes",
            "special": "special_notes",
        }
        col = column_mapping.get(category)
        if not col:
            return None

        notes_parts = []
        for row in self.qc_sheet_info:
            value = getattr(row, col)
            if value:
                notes_parts.append(value.strip())

        return "; ".join(notes_parts) if notes_parts else None

    def map_to_exaspim_procedures(
        self, specimen_id: str
    ) -> tuple[List[Surgery], List[SpecimenProcedure]]:
        """
        Map ExaSPIM data to subject and specimen procedures.

        Parameters
        ----------
        specimen_id : str
            The specimen identifier

        Returns
        -------
        tuple[List[Surgery], List[SpecimenProcedure]]
            Subject procedures and specimen procedures
        """
        subject_procedures: List[Surgery] = []
        specimen_procedures: List[SpecimenProcedure] = []

        # Build injection surgery from Mouse Tracker
        if self.mouse_tracker_info:
            injection_surgery = self.build_injection_surgery(
                self.mouse_tracker_info[0]
            )
            if injection_surgery:
                subject_procedures.append(injection_surgery)

        # Get imaging start date for expansion calculation
        imaging_start_date = None
        if self.imaging_queue_info:
            imaging_start_date = self._parse_date(
                self.imaging_queue_info[0].imaging_start_date
            )
        
        # Build specimen procedures from Sample Tracking
        if self.sample_tracking_info:
            st_row = self.sample_tracking_info[0]
            experimenters = self._parse_experimenters(st_row)

            # Delipidation
            delipidation = self.build_delipidation(st_row, specimen_id, experimenters)
            if delipidation:
                specimen_procedures.append(delipidation)

            # Immunolabeling
            immunolabeling = self.build_immunolabeling(st_row, specimen_id, experimenters)
            if immunolabeling:
                specimen_procedures.append(immunolabeling)

            # Gelation
            gelation = self.build_gelation(st_row, specimen_id, experimenters)
            if gelation:
                specimen_procedures.append(gelation)

            # Expansion (requires imaging_start_date and status="Imaged")
            expansion = self.build_expansion(st_row, specimen_id, imaging_start_date, experimenters)
            if expansion:
                specimen_procedures.append(expansion)

        # Build mounting and imaging from Imaging Queue
        if self.imaging_queue_info:
            # Try to get experimenters from sample tracking if available
            experimenters = []
            if self.sample_tracking_info:
                experimenters = self._parse_experimenters(self.sample_tracking_info[0])
            
            mounting = self.build_mounting_and_imaging(
                self.imaging_queue_info[0], specimen_id, experimenters
            )
            if mounting:
                specimen_procedures.append(mounting)

        # Sort specimen_procedures by start_date
        specimen_procedures.sort(key=lambda p: p.start_date)

        return subject_procedures, specimen_procedures

    def map_to_aind_procedures(
            self, subject_id: str, specimen_procedures: List[SpecimenProcedure], subject_procedures: List[Surgery]
    ):
        """
        Map ExaSPIM procedures to AIND procedures.

        Parameters
        ----------
        subject_id : str
            The subject identifier
        specimen_procedures : List[SpecimenProcedure]
            List of specimen procedures
        subject_procedures : List[Surgery]
            List of subject procedures

        Returns
        -------
        Dict[str, Any]
            Mapped AIND procedures data
        """
        procedures = Procedures(
                subject_id=subject_id,
                subject_procedures=subject_procedures,
                specimen_procedures=specimen_procedures,
        )
        return procedures
