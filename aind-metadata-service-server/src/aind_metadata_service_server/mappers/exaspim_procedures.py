"""Module to map ExaSPIM Smartsheet information to Procedures models."""

import re
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
    Solution,
)
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.components.specimen_procedures import SpecimenProcedure
from aind_data_schema.components.subject_procedures import Surgery
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.species import Species
from aind_data_schema_models.registries import Registry
from aind_data_schema_models.specimen_procedure_types import (
    SpecimenProcedureType,
)
from aind_data_schema_models.units import VolumeUnit
from aind_smartsheet_service_async_client.models import (
    MouseTracker,
    SampleTracking,
    ImagingQueue,
    ExaSPIMInfo,
)


class ExaspimProceduresMapper:
    """Class to handle mapping of ExaSPIM procedures data."""

    EXPERIMENTER_SPLIT_REGEX = re.compile(r"[;,]")
    ANTIBODY_ANTI_PATTERN_REGEX = re.compile(
        r"anti[-\s]*([A-Za-z0-9]+)", re.IGNORECASE
    )

    def __init__(
        self,
        exaspim_info: Optional[ExaSPIMInfo] = None,
    ):
        """
        Class constructor.

        Parameters
        ----------
        exaspim_info : Optional[ExaSPIMInfo]
            ExaSPIM info object from Smartsheet containing mouse_tracker_info,
            sample_tracking_info, imaging_queue_info, and qc_sheet_info
        """
        if exaspim_info is None:
            self.mouse_tracker_info = []
            self.sample_tracking_info = []
            self.imaging_queue_info = []
            self.qc_sheet_info = []
        else:
            self.mouse_tracker_info = getattr(
                exaspim_info, "mouse_tracker_info", []
            )
            self.sample_tracking_info = getattr(
                exaspim_info, "sample_tracking_info", []
            )
            self.imaging_queue_info = getattr(
                exaspim_info, "imaging_queue_info", []
            )
            self.qc_sheet_info = getattr(exaspim_info, "qc_sheet_info", [])

    @staticmethod
    def _parse_date(raw: Optional[str]) -> Optional[date]:
        """
        Parse a raw Smartsheet value to a date.

        Parameters
        ----------
        raw : Optional[str]
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
        if text.endswith("Z"):
            text = text[:-1]

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
    def _is_numeric(value: Any) -> bool:
        """
        Check if a value can be converted to a number.

        Parameters
        ----------
        value : Any
            The value to check

        Returns
        -------
        bool
            True if value is numeric or can be converted to float
        """
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return True
        str_value = str(value).strip().lower()
        try:
            float(str_value)
            return True
        except (ValueError, TypeError):
            return False

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
        raw = sample_tracking_row.processing_lead
        if not raw:
            return []

        raw = raw.strip()
        if not raw:
            return []

        names = ExaspimProceduresMapper.EXPERIMENTER_SPLIT_REGEX.split(raw)
        experimenters: List[str] = []
        for name in names:
            name = name.strip()
            if name:
                experimenters.append(name)
        return experimenters

    @staticmethod
    def _map_antibody_species(antibody_name: str) -> Optional[Species.ONE_OF]:
        """Map the host Species of an antibody from its name."""
        antibody_species_map = {
            "rabbit": Species.EUROPEAN_RABBIT,
            "mouse": Species.HOUSE_MOUSE,
            "rat": Species.NORWAY_RAT,
            "goat": Species.GOAT,
            "chicken": Species.CHICKEN,
            "donkey": Species.DONKEY,
        }
        cleaned = antibody_name.strip()
        if not cleaned:
            return None
        first_token = cleaned.split()[0].lower()
        return antibody_species_map.get(first_token)

    @staticmethod
    def _map_antibody_source(antibody_name: str) -> Organization:
        """Map an antibody name to its source Organization."""
        antibody_source_map = {
            "gfp": Organization.ABCAM,
            "donkey anti-rabbit igg (h+l) af 488": Organization.INVITROGEN,
            "donkey anti-rabbitt igg (h+l) af 488": Organization.INVITROGEN,
            "tdtomato": Organization.SICGEN,
            "goat anti-tdt": Organization.SICGEN,
            "donkey anti-goat igg (h+l) af 568": Organization.INVITROGEN,
        }
        return antibody_source_map.get(
            antibody_name.strip().lower(), Organization.OTHER
        )

    @staticmethod
    def _map_rrid(catalog: str, antibody_name: str) -> Optional[PIDName]:
        """Map a catalog number to a PIDName with the corresponding RRID."""
        catalog_to_rrid = {
            "ab290": "AB_303395",
            "ab8181-200": "AB_2722750",
            "a-21311": "AB_221477",
            "155264": "AB_3661847",
            "gr361051-16": "AB_300798",
            "a21206": "AB_2535792",
            "a-21206": "AB_2535792",
            "a-11057": "AB_2534104",
            "a11057": "AB_2534104",
            "a-21247": "AB_141778",
            "703-545-155": "AB_2340375",
            "165794": "AB_2340375",
        }
        if not catalog:
            return None
        rrid = catalog_to_rrid.get(catalog.strip().lower())
        if not rrid:
            return None
        return PIDName(
            name=antibody_name,
            registry=Registry.RRID,
            registry_identifier=rrid,
        )

    @staticmethod
    def _map_primary_antibody_target(antibody_name: str) -> str:
        """Map the protein target for a primary antibody name."""
        target_canonical_map = {
            "gfp": "GFP",
            "tdt": "tdTomato",
            "tdtomato": "tdTomato",
            "tdtomat": "tdTomato",
            "mtfp": "mTFP",
        }
        protein_full_name_map = {
            "GFP": "Green Fluorescent Protein",
            "tdTomato": "tdTomato",
            "mTFP": "monomeric Teal Fluorescent Protein 1",
        }
        cleaned_name = antibody_name.strip()
        if not cleaned_name:
            return cleaned_name

        anti_match = (
            ExaspimProceduresMapper.ANTIBODY_ANTI_PATTERN_REGEX.search(
                cleaned_name
            )
        )
        target_token = anti_match.group(1) if anti_match else cleaned_name

        canonical = target_canonical_map.get(
            target_token.lower(), target_token
        )
        return protein_full_name_map.get(canonical, canonical)

    @staticmethod
    def _map_secondary_antibody_target(
        secondary_antibody_name: str,
        primary_antibody_name: str,
    ) -> str:
        """Map the protein target for a secondary antibody."""
        antibody_host_canonical_map = {
            "rabbit": "Rabbit",
            "mouse": "Mouse",
            "rat": "Rat",
            "goat": "Goat",
            "chicken": "Chicken",
            "donkey": "Donkey",
        }
        primary_name = primary_antibody_name.strip()
        secondary_name = secondary_antibody_name.strip()

        for host_key, host_name in antibody_host_canonical_map.items():
            if re.search(
                rf"\b{re.escape(host_key)}\b",
                primary_name,
                flags=re.IGNORECASE,
            ):
                return f"{host_name} antibody"

        anti_match = (
            ExaspimProceduresMapper.ANTIBODY_ANTI_PATTERN_REGEX.search(
                secondary_name
            )
        )
        if anti_match:
            secondary_token = anti_match.group(1).lower()
            if secondary_token in antibody_host_canonical_map:
                return (
                    f"{antibody_host_canonical_map[secondary_token]} antibody"
                )

        return secondary_name

    def _get_titer_for_virus(
        self,
        mouse_tracker_row: MouseTracker,
        virus_num: int,
    ) -> Optional[Any]:
        """
        Get viral titer using priority system (effective > working > stock).
        Parameters
        ----------
        mouse_tracker_row : MouseTracker
            Row from Mouse Tracker sheet
        virus_num : int
            Virus number (1-4)

        Returns
        -------
        Optional[Any]
            Titer value or None if unavailable
        """
        prefix = f"virus{virus_num}"

        if virus_num > 1:
            titer_raw = getattr(
                mouse_tracker_row, f"{prefix}_effective_titer_gc_ml", None
            )
            if titer_raw is not None and str(titer_raw).strip():
                return titer_raw

        # Working titer (virus1 has unprefixed field name)
        if virus_num == 1:
            titer_raw = getattr(mouse_tracker_row, "working_titer_gc_ml", None)
        else:
            titer_raw = getattr(
                mouse_tracker_row, f"{prefix}_working_titer_gc_ml", None
            )
        if titer_raw is not None and str(titer_raw).strip():
            return titer_raw

        titer_raw = getattr(
            mouse_tracker_row, f"{prefix}_stock_titer_gc_ml", None
        )
        if titer_raw is not None and str(titer_raw).strip():
            return titer_raw

        return None

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

            if virus_num == 4:
                volume_raw = mouse_tracker_row.stereotaxic_volume_injected_nl
            else:
                volume_raw = getattr(
                    mouse_tracker_row,
                    f"{prefix}_stereotaxic_volume_injected_nl",
                )

            if not volume_raw:
                ro_volume_raw = (
                    mouse_tracker_row.virus_mix_total_volume_injected_ro_ul
                )
            else:
                ro_volume_raw = None

            titer_raw = self._get_titer_for_virus(mouse_tracker_row, virus_num)
            vm_kwargs: Dict[str, Any] = {"name": virus_name}
            if virus_id:
                vm_kwargs["tars_identifiers"] = {
                    "virus_tars_id": virus_id,
                    "prep_lot_number": virus_id,
                }
            if self._is_numeric(titer_raw):
                vm_kwargs["titer"] = int(float(str(titer_raw)))

            viral_material = ViralMaterial(**vm_kwargs)

            dynamics_list: List[InjectionDynamics] = []
            if self._is_numeric(volume_raw):
                vol = float(str(volume_raw))
                if vol > 0:
                    dynamics_list.append(
                        InjectionDynamics(
                            profile=InjectionProfile.BOLUS,
                            volume=vol,
                            volume_unit=VolumeUnit.NL,
                        )
                    )
            elif self._is_numeric(ro_volume_raw):
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

            if not dynamics_list:
                continue

            injection_objects.append(
                Injection(
                    injection_materials=[viral_material],
                    dynamics=dynamics_list,
                )
            )

        if not injection_objects:
            return None

        surgery_date = min(injection_dates) if injection_dates else None

        return Surgery(
            start_date=surgery_date,
            procedures=injection_objects,
        )

    def build_delipidation(
        self,
        sample_tracking_row: SampleTracking,
        specimen_id: str,
        experimenters: List[str] = None,
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
        end_date = self._parse_date(sample_tracking_row.sbip_delipidation_end)

        if not start_date or not end_date:
            return None

        reagents = [
            Solution(
                name="Dichloromethane (DCM)",
            ),
            Solution(
                name="SBiP (Sodium dodecylsulfate, Butanol, isoPropanol)",
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
        self,
        sample_tracking_row: SampleTracking,
        specimen_id: str,
        experimenters: List[str] = None,
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
            ab_name = getattr(
                sample_tracking_row, f"immuno_primary_antibody{i}"
            )
            if not ab_name:
                continue
            ab_name = ab_name.strip()

            catalog = getattr(
                sample_tracking_row, f"primary_antibody{i}_catalog_num"
            )
            catalog = catalog.strip() if catalog else None

            lot = getattr(sample_tracking_row, f"primary_antibody{i}_lot_num")
            lot = lot.strip() if lot else None
            mass_raw = getattr(
                sample_tracking_row,
                f"mass_of_primary_antibody{i}_used_per_brain_ug",
            )
            mass = 0.0
            if mass_raw is not None and self._is_numeric(mass_raw):
                mass = float(str(mass_raw))

            reagent = ProbeReagent(
                name=ab_name,
                source=self._map_antibody_source(ab_name),
                lot_number=lot if lot else None,
                rrid=self._map_rrid(catalog, ab_name) if catalog else None,
                target=ProteinProbe(
                    protein=PIDName(
                        name=self._map_primary_antibody_target(ab_name)
                    ),
                    species=self._map_antibody_species(ab_name),
                    mass=mass,
                ),
            )
            reagents.append(reagent)

        # Build secondary antibody reagents (up to 3)
        for i in range(1, 4):
            ab_name = getattr(
                sample_tracking_row, f"immuno_secondary_antibody{i}"
            )
            primary_ab_name = getattr(
                sample_tracking_row, f"immuno_primary_antibody{i}"
            )
            if not ab_name:
                continue
            ab_name = ab_name.strip()
            if primary_ab_name:
                primary_ab_name = primary_ab_name.strip()
            else:
                primary_ab_name = ""

            catalog = getattr(
                sample_tracking_row, f"secondary_antibody{i}_catalog_num"
            )
            catalog = catalog.strip() if catalog else None

            lot = getattr(
                sample_tracking_row, f"secondary_antibody{i}_lot_num"
            )
            lot = lot.strip() if lot else None
            mass_raw = getattr(
                sample_tracking_row,
                f"mass_of_secondary_antibody{i}_used_per_brain_ug",
            )
            mass = 0.0
            if mass_raw is not None and self._is_numeric(mass_raw):
                mass = float(str(mass_raw))

            reagent = ProbeReagent(
                name=ab_name,
                source=self._map_antibody_source(ab_name),
                lot_number=lot if lot else None,
                rrid=self._map_rrid(catalog, ab_name) if catalog else None,
                target=ProteinProbe(
                    protein=PIDName(
                        name=self._map_secondary_antibody_target(
                            ab_name, primary_ab_name
                        )
                    ),
                    species=self._map_antibody_species(ab_name),
                    mass=mass,
                ),
            )
            reagents.append(reagent)

        primary_rrid = (
            sample_tracking_row.primary_antibody_rrid.strip()
            if sample_tracking_row.primary_antibody_rrid
            else None
        )
        secondary_rrid = (
            sample_tracking_row.secondary_antibody_rrid.strip()
            if sample_tracking_row.secondary_antibody_rrid
            else None
        )

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
        self,
        sample_tracking_row: SampleTracking,
        specimen_id: str,
        experimenters: List[str] = None,
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
        start_date = self._parse_date(sample_tracking_row.gelation_mbs_start)
        if not start_date:
            return None

        storage_date = self._parse_date(
            sample_tracking_row.date_of_storage_in_pbs_az_0_05_4c
        )
        pbs_wash_end = self._parse_date(sample_tracking_row.pbs_wash_end)
        end_date = storage_date or pbs_wash_end or start_date

        reagents = [
            Reagent(
                name="MBS (m-Maleimidobenzoyl-N-hydroxysuccinimide ester)",
                source=Organization.SIGMA_ALDRICH,
            ),
            Reagent(
                name="Acryloyl-X (AcX)",
                source=Organization.INVITROGEN,
            ),
            Solution(
                name="Stock X + VA-044",
            ),
            Solution(
                name="Proteinase K (ProK)",
            ),
            Solution(
                name="PBS",
            ),
        ]

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
            procedure_name=(
                "Gelation (MBS, AcX, StockX+VA-044, ProK digestion)"
            ),
            specimen_id=specimen_id,
            start_date=start_date,
            end_date=end_date,
            experimenters=experimenters or [],
            procedure_details=reagents,
            protocol_parameters=(protocol_params if protocol_params else None),
            notes=qc_notes,
        )

    def build_expansion(
        self,
        sample_tracking_row: SampleTracking,
        specimen_id: str,
        imaging_start_date: Optional[date],
        experimenters: List[str] = None,
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
        status = sample_tracking_row.status
        if not status or status.strip().lower() != "imaged":
            return None

        if not imaging_start_date:
            return None

        # Backtrack 3 days from imaging start
        start_date = imaging_start_date - timedelta(days=3)
        end_date = imaging_start_date

        reagents = [
            Solution(
                name="Saline-Sodium Citrate (SSC)",
            ),
            Solution(
                name="Ascorbic Acid",
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
        self,
        imaging_queue_row: ImagingQueue,
        specimen_id: str,
        experimenters: List[str] = None,
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
        start_date = self._parse_date(imaging_queue_row.imaging_start_date)
        if not start_date:
            return None

        end_date = (
            self._parse_date(imaging_queue_row.imaging_end_date) or start_date
        )

        microscope = (
            imaging_queue_row.microscope.strip()
            if imaging_queue_row.microscope
            else None
        )
        imaging_buffer = (
            imaging_queue_row.imaging_buffer.strip()
            if imaging_queue_row.imaging_buffer
            else None
        )
        channels = (
            imaging_queue_row.signal_channel_s.strip()
            if imaging_queue_row.signal_channel_s
            else None
        )
        notes_col = (
            imaging_queue_row.notes.strip()
            if imaging_queue_row.notes
            else None
        )

        reagents: List[Union[Reagent, Solution]] = []
        if imaging_buffer:
            reagents.append(
                Solution(
                    name=f"Imaging Buffer: {imaging_buffer}",
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

        if self.mouse_tracker_info:
            injection_surgery = self.build_injection_surgery(
                self.mouse_tracker_info[0]
            )
            if injection_surgery:
                subject_procedures.append(injection_surgery)

        imaging_start_date = None
        if self.imaging_queue_info:
            imaging_start_date = self._parse_date(
                self.imaging_queue_info[0].imaging_start_date
            )

        if self.sample_tracking_info:
            st_row = self.sample_tracking_info[0]
            experimenters = self._parse_experimenters(st_row)

            delipidation = self.build_delipidation(
                st_row, specimen_id, experimenters
            )
            if delipidation:
                specimen_procedures.append(delipidation)

            immunolabeling = self.build_immunolabeling(
                st_row, specimen_id, experimenters
            )
            if immunolabeling:
                specimen_procedures.append(immunolabeling)

            gelation = self.build_gelation(st_row, specimen_id, experimenters)
            if gelation:
                specimen_procedures.append(gelation)

            expansion = self.build_expansion(
                st_row, specimen_id, imaging_start_date, experimenters
            )
            if expansion:
                specimen_procedures.append(expansion)

        if self.imaging_queue_info:
            experimenters = []
            if self.sample_tracking_info:
                experimenters = self._parse_experimenters(
                    self.sample_tracking_info[0]
                )

            mounting = self.build_mounting_and_imaging(
                self.imaging_queue_info[0], specimen_id, experimenters
            )
            if mounting:
                specimen_procedures.append(mounting)

        specimen_procedures.sort(key=lambda p: p.start_date)

        return subject_procedures, specimen_procedures

    def map_to_aind_procedures(
        self,
        subject_id: str,
        specimen_procedures: List[SpecimenProcedure],
        subject_procedures: List[Surgery],
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
