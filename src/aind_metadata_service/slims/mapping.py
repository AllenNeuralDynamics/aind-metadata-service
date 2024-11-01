"""
Module to map data from SLIMS to the Session model.
"""

from enum import Enum
from typing import List, Optional, Tuple

from aind_data_schema.components.coordinates import CcfCoords, Coordinates3d
from aind_data_schema.components.devices import SpoutSide
from aind_data_schema.core.procedures import CoordinateReferenceLocation
from aind_data_schema.core.session import (
    DomeModule,
    LaserConfig,
    LightEmittingDiodeConfig,
    ManipulatorModule,
    RewardDeliveryConfig,
    RewardSolution,
    RewardSpoutConfig,
    Session,
    SpeakerConfig,
    StimulusEpoch,
    StimulusModality,
    Stream,
)
from aind_data_schema_models.modalities import Modality
from aind_slims_api.models.ecephys_session import (
    SlimsBrainStructureRdrc,
    SlimsRewardDeliveryRdrc,
    SlimsRewardSpoutsRdrc,
    SlimsStimulusEpochsResult,
)
from aind_slims_api.operations.ecephys_session import (
    EcephysSession as SlimsEcephysSession,
)
from aind_slims_api.operations.ecephys_session import (
    SlimsRewardDeliveryInfo,
    SlimsStream,
    SlimsStreamModule,
)


class SlimsStreamModalities(Enum):
    """Enum class for stream modalities in SLIMS."""

    ECEPHYS = "Ecephys"
    BEHAVIOR = "Behavior"
    BEHAVIOR_VIDEOS = "Behavior videos"
    CONFOCAL = "Confocal"
    ELECTROMYOGRAPHY = "Electromyography"
    FMOST = "Fmost"
    ICEPHYS = "Icephys"
    FIB = "Fib"
    ISI = "Isi"
    MERFISH = "Merfish"
    MRI = "Mri"
    POPHYS = "POphys"
    SLAP = "Slap"
    SPIM = "Spim"


class SlimsRewardSolution(str, Enum):
    """Enum class for reward solution in SLIMS."""

    WATER = "Water"
    OTHER = "Other, (if Other, specify below)"


class SlimsSessionMapper:
    """Client for interacting with SLIMS and mapping session data."""

    def map_sessions(
        self, sessions: List[SlimsEcephysSession], subject_id: str
    ) -> List[Session]:
        """Maps SLIMS sessions to AIND session models."""
        return [
            self._map_session(session, subject_id=subject_id)
            for session in sessions
        ]

    def _map_session(
        self, session: SlimsEcephysSession, subject_id: str
    ) -> Session:
        """Map a single SLIMS session to the AIND session model."""
        session_type = getattr(session.session_group, "session_type", None)
        mouse_platform_name = getattr(
            session.session_group, "mouse_platform_name", None
        )
        active_mouse_platform = getattr(
            session.session_group, "active_mouse_platform", False
        )

        rig_id = getattr(session.session_instrument, "name", None)

        session_result = (
            session.session_result
            if hasattr(session, "session_result")
            else None
        )

        animal_weight_prior = getattr(session_result, "weight_prior_g", None)
        animal_weight_post = getattr(session_result, "weight_post_g", None)
        reward_consumed_total = getattr(
            session_result, "reward_consumed_vol", None
        )

        streams = [
            self._map_stream(stream)
            for stream in getattr(session, "streams", [])
        ]
        stimulus_epochs = [
            self._map_stimulus_epoch(epoch)
            for epoch in getattr(session, "stimulus_epochs", [])
        ]
        reward_delivery_info = (
            self._map_reward_delivery(getattr(session, "reward_delivery"))
            if getattr(session, "reward_delivery")
            else None
        )

        # model_construct because start and end times are not stored in SLIMS
        return Session.model_construct(
            rig_id=rig_id,
            subject_id=subject_id,
            session_type=session_type,
            mouse_platform_name=mouse_platform_name,
            active_mouse_platform=active_mouse_platform,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            data_streams=streams,
            stimulus_epochs=stimulus_epochs,
            reward_delivery=reward_delivery_info,
            reward_consumed_total=reward_consumed_total,
        )

    def _map_reward_delivery(
        self, reward_info: SlimsRewardDeliveryInfo
    ) -> RewardDeliveryConfig:
        """Map reward info from SLIMS to RewardDeliveryConfig model."""

        slims_reward_delivery = getattr(reward_info, "reward_delivery", None)
        slims_reward_spouts = getattr(reward_info, "reward_spouts", None)

        reward_solution, notes = (
            self._map_reward_solution(slims_reward_delivery)
            if slims_reward_delivery
            else (None, None)
        )

        reward_spouts = (
            [self._map_reward_spouts(slims_reward_spouts)]
            if slims_reward_spouts
            else []
        )

        return RewardDeliveryConfig(
            reward_solution=reward_solution,
            reward_spouts=reward_spouts,
            notes=notes,
        )

    @staticmethod
    def _map_reward_solution(
        reward_delivery: SlimsRewardDeliveryRdrc,
    ) -> tuple[Optional[RewardSolution], Optional[str]]:
        """Map reward solution and notes."""

        slims_reward_solution = getattr(
            reward_delivery, "reward_solution", None
        )

        if slims_reward_solution == SlimsRewardSolution.WATER:
            return RewardSolution.WATER, None
        if slims_reward_solution == SlimsRewardSolution.OTHER:
            notes = getattr(reward_delivery, "other_reward_solution", None)
            return RewardSolution.OTHER, notes

        return None, None

    def _map_reward_spouts(
        self, reward_spout: SlimsRewardSpoutsRdrc
    ) -> RewardSpoutConfig:
        """Map reward spout info to RewardSpoutConfig model"""

        spout_side = getattr(reward_spout, "spout_side", None)
        return RewardSpoutConfig.model_construct(
            side=self._map_spout_side(spout_side) if spout_side else None,
            starting_position=getattr(reward_spout, "starting_position", None),
            variable_position=getattr(reward_spout, "variable_position", None),
        )

    @staticmethod
    def _map_spout_side(spout_side: str) -> SpoutSide:
        """Maps SLIMS input spout side to SpoutSide"""

        spout_side_lower = spout_side.lower()
        if "left" in spout_side_lower:
            return SpoutSide.LEFT
        if "right" in spout_side_lower:
            return SpoutSide.RIGHT
        if "center" in spout_side_lower:
            return SpoutSide.CENTER

        return SpoutSide.OTHER

    def _map_stimulus_epoch(
        self, stimulus_epoch: SlimsStimulusEpochsResult
    ) -> StimulusEpoch:
        """Maps stimulus epoch data from SLIMS to StimulusEpoch model"""
        stimulus_name = getattr(stimulus_epoch, "stimulus_name", None)
        stimulus_device_names = getattr(
            stimulus_epoch, "stimulus_device_names", None
        )
        stimulus_modalities = [
            StimulusModality(modality)
            for modality in getattr(stimulus_epoch, "stimulus_modalities", [])
        ]
        reward_consumed_during_epoch = getattr(
            stimulus_epoch, "reward_consumed_during_epoch", None
        )
        speaker_config = self._map_speaker_config(
            speaker_name=getattr(stimulus_epoch, "speaker_name"),
            speaker_volume=getattr(stimulus_epoch, "speaker_volume"),
        )
        light_source_config = self._map_light_source_config(stimulus_epoch)
        # Using model construct because missing start and end times
        return StimulusEpoch.model_construct(
            stimulus_name=stimulus_name,
            stimulus_device_names=stimulus_device_names,
            stimulus_modalities=stimulus_modalities,
            reward_consumed_during_epoch=reward_consumed_during_epoch,
            speaker_config=speaker_config,
            light_source_config=light_source_config,
        )

    @staticmethod
    def _map_light_source_config(
        stimulus_epoch,
    ) -> List[LaserConfig | LightEmittingDiodeConfig]:
        """Maps light source data from SLIMS to list of configs"""
        light_sources = []
        if getattr(stimulus_epoch, "laser_name", None) and getattr(
            stimulus_epoch, "laser_wavelength", None
        ):
            laser = LaserConfig(
                name=getattr(stimulus_epoch, "laser_name", None),
                wavelength=getattr(stimulus_epoch, "laser_wavelength", None),
                excitation_power=getattr(
                    stimulus_epoch, "laser_excitation_power", None
                ),
            )
            light_sources.append(laser)
        if getattr(stimulus_epoch, "led_name", None):
            led = LightEmittingDiodeConfig(
                name=getattr(stimulus_epoch, "led_name"),
                excitation_power=getattr(
                    stimulus_epoch, "led_excitation_power_mw", None
                ),
            )
            light_sources.append(led)
        return light_sources

    @staticmethod
    def _map_speaker_config(
        speaker_name: Optional[str], speaker_volume: Optional[float]
    ) -> SpeakerConfig:
        """Maps speaker config"""
        return (
            SpeakerConfig(name=speaker_name, volume=speaker_volume)
            if speaker_name
            else None
        )

    def _map_stream(self, stream: SlimsStream) -> Stream:
        """Map stream data from SLIMS to the Stream model."""
        stream_modalities = [
            self._map_stream_modality(modality)
            for modality in getattr(stream, "stream_modalities", [])
        ]
        daq_names = getattr(stream, "daq_names", [])
        camera_names = getattr(stream, "camera_names", [])

        stick_microscopes, ephys_modules = self._map_stream_modules(
            stream.stream_modules
        )

        return Stream.model_construct(
            daq_names=daq_names,
            camera_names=camera_names,
            stream_modalities=stream_modalities,
            stick_microscopes=stick_microscopes,
            ephys_modules=ephys_modules,
        )

    def _map_stream_modules(
        self, stream_modules: Optional[List[SlimsStreamModule]]
    ) -> Tuple[List[DomeModule], List[ManipulatorModule]]:
        """
        Map stream modules to either stick microscopes or manipulators.
        Parameters
        ----------
        stream_modules: List of stream modules from SLIMS
        Returns
        -------
        Tuple containing lists of stick microscopes and ephys modules
        """
        stick_microscopes, ephys_modules = [], []

        for stream_module in stream_modules:
            if self._is_manipulator_module(stream_module):
                ephys_modules.append(
                    self._map_manipulator_module(stream_module)
                )
            else:
                stick_microscopes.append(self._map_dome_module(stream_module))

        return stick_microscopes, ephys_modules

    @staticmethod
    def _is_manipulator_module(stream_module: SlimsStreamModule) -> bool:
        """
        Checks if stream module contains fields for a manipulator module.
        """
        return (
            getattr(stream_module, "primary_targeted_structure", None)
            or getattr(stream_module, "ccf_coordinate_ap", None)
            or getattr(stream_module, "manipulator_x", None)
            or getattr(stream_module, "bregma_target_ap", None)
        )

    def _map_manipulator_module(
        self, stream_module: SlimsStreamModule
    ) -> ManipulatorModule:
        """
        Map a stream module to a ManipulatorModule instance.
        """
        primary_targeted_structure = self._map_targeted_structure(
            getattr(stream_module, "primary_targeted_structure", None)
        )
        other_targeted_structures = [
            self._map_targeted_structure(structure_name)
            for structure_name in getattr(
                stream_module, "secondary_targeted_structures", []
            )
        ]
        return ManipulatorModule.model_construct(
            assembly_name=getattr(stream_module, "assembly_name", None),
            arc_angle=getattr(stream_module, "arc_angle", None),
            module_angle=getattr(stream_module, "module_angle", None),
            rotation_angle=getattr(stream_module, "rotation_angle", None),
            coordinate_transform=getattr(
                stream_module, "coordinate_transform", None
            ),
            primary_targeted_structure=primary_targeted_structure,
            other_targeted_structures=other_targeted_structures,
            targetted_ccf_coordinates=self._map_ccf_coords(
                ap=getattr(stream_module, "ccf_coordinate_ap", None),
                ml=getattr(stream_module, "ccf_coordinate_ml", None),
                dv=getattr(stream_module, "ccf_coordinate_dv", None),
            ),
            manipulator_coordinates=self._map_3d_coords(
                x=getattr(stream_module, "manipulator_x", None),
                y=getattr(stream_module, "manipulator_y", None),
                z=getattr(stream_module, "manipulator_z", None),
            ),
            # TODO: map anatomical coordinates once unit is defined
            # anatomical_coordinates=self._map_3d_coords(
            #     x=getattr(stream_module, "bregma_target_ap", None),
            #     y=getattr(stream_module, "bregma_target_ml", None),
            #     z=getattr(stream_module, "bregma_target_dv", None),
            # ),
            anatomical_reference=(
                CoordinateReferenceLocation.BREGMA
                if getattr(stream_module, "bregma_target_ap", None)
                else None
            ),
            surface_z=getattr(stream_module, "surface_z", None),
            dye=getattr(stream_module, "dye", None),
            implant_hole_number=getattr(stream_module, "implant_hole", None),
            notes="Anatomical Coordinates mapped AP:X, ML:Y, DV:Z",
        )

    @staticmethod
    def _map_dome_module(stream_module: SlimsStreamModule) -> DomeModule:
        """
        Map a stream module to a DomeModule instance.
        """
        return DomeModule.model_construct(
            assembly_name=getattr(stream_module, "assembly_name", None),
            arc_angle=getattr(stream_module, "arc_angle", None),
            module_angle=getattr(stream_module, "module_angle", None),
            rotation_angle=getattr(stream_module, "rotation_angle", None),
            coordinate_transform=getattr(
                stream_module, "coordinate_transform", None
            ),
        )

    @staticmethod
    def _map_targeted_structure(structure_record: SlimsBrainStructureRdrc):
        """Map targeted structure"""
        return getattr(structure_record, "name", None)

    @staticmethod
    def _map_stream_modality(modality: str) -> Optional[Modality]:
        """Map stream modality to the Modality enum."""
        modality_mapping = {
            SlimsStreamModalities.ELECTROMYOGRAPHY.value: Modality.EMG,
            SlimsStreamModalities.SPIM.value: Modality.SPIM,
            SlimsStreamModalities.MRI.value: Modality.MRI,
            SlimsStreamModalities.ISI.value: Modality.ISI,
            SlimsStreamModalities.FMOST.value: Modality.FMOST,
        }
        return modality_mapping.get(
            modality,
            Modality.from_abbreviation(modality.lower().replace(" ", "-")),
        )

    @staticmethod
    def _map_ccf_coords(
        ml: Optional[float], ap: Optional[float], dv: Optional[float]
    ) -> Optional[CcfCoords]:
        """Map coordinates to CcfCoords."""
        return CcfCoords(ml=ml, ap=ap, dv=dv) if ml and ap and dv else None

    @staticmethod
    def _map_3d_coords(
        x: Optional[float], y: Optional[float], z: Optional[float]
    ) -> Optional[Coordinates3d]:
        """Map coordinates to 3D space."""
        return Coordinates3d(x=x, y=y, z=z) if x and y and z else None
