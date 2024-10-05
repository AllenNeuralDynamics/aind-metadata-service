"""
Module to map data from SLIMS to the Session model.
"""

from aind_data_schema.components.coordinates import CcfCoords, Coordinates3d
from aind_data_schema.core.session import Session, DomeModule, ManipulatorModule, Stream
from enum import Enum
from aind_slims_api import SlimsClient
from aind_slims_api.operations.ecephys_session import (
    fetch_ecephys_sessions,
    EcephysSession as SlimsEcephysSession
)
from typing import Optional, List
from aind_data_schema_models.modalities import Modality
from aind_data_schema.core.procedures import CoordinateReferenceLocation


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


class SessionSlimsClient:
    """Client for interacting with SLIMS and mapping session data."""

    def __init__(self, slims_client: SlimsClient):
        """Initialize the client."""
        self.client = slims_client

    def get_slims_sessions(self, subject_id: str) -> List[Session]:
        """
        Fetches sessions for a given subject ID from SLIMS.

        :param subject_id: The subject identifier
        :return: List of mapped Session objects
        """
        try:
            sessions = fetch_ecephys_sessions(subject_id=subject_id, client=self.client)
            return [self._map_session(session, subject_id=subject_id) for session in sessions]
        except Exception as e:
            print(f"Error fetching SLIMS sessions: {e}")
            return []

    def _map_session(self, session: SlimsEcephysSession, subject_id: str) -> Session:
        """Map a single SLIMS session to the AIND session model."""
        session_type = getattr(session.session_group, 'session_type', None)
        mouse_platform_name = getattr(session.session_group, 'mouse_platform_name', None)
        active_mouse_platform = getattr(session.session_group, 'active_mouse_platform', None)

        session_result = session.session_result if hasattr(session, 'session_result') else None
        animal_weight_prior = getattr(session_result, 'weight_prior_g', None)
        animal_weight_post = getattr(session_result, 'weight_post_g', None)
        reward_consumed_total = getattr(session_result, 'reward_consumed_vol', None)

        streams = [self._map_stream(stream, session.stream_modules) for stream in session.streams]

        # TODO: map additional fields and return a constructed Session object
        return Session.model_construct(
            subject_id=subject_id,
            session_type=session_type,
            mouse_platform_name=mouse_platform_name,
            active_mouse_platform=active_mouse_platform,
            animal_weight_prior=animal_weight_prior,
            animal_weight_post=animal_weight_post,
            data_streams=streams,
            reward_consumed_total=reward_consumed_total,
        )

    def _map_stream(self, stream, stream_modules) -> Stream:
        """Map stream data from SLIMS to the Stream model."""
        stream_modalities = [self._map_stream_modality(modality) for modality in getattr(stream, 'stream_modalities', [])]
        daq_names = getattr(stream, "daq_names", [])
        camera_names = getattr(stream, "camera_names", [])

        stick_microscopes, ephys_modules = self._map_stream_modules(stream, stream_modules)

        return Stream.model_construct(
            daq_names=daq_names,
            camera_names=camera_names,
            stream_modalities=stream_modalities,
            stick_microscopes=stick_microscopes,
            ephys_modules=ephys_modules
        )

    def _map_stream_modules(self, stream, stream_modules) -> (List[DomeModule], List[ManipulatorModule]):
        """
        Map stream modules to either stick microscopes (DomeModule) or manipulators (ManipulatorModule).

        :param stream: Stream object
        :param stream_modules: List of stream modules from SLIMS
        :return: Tuple containing lists of stick microscopes and ephys modules
        """
        stick_microscopes = []
        ephys_modules = []

        for stream_module in stream_modules:
            if stream_module.pk in stream.stream_modules_pk:
                module = self._map_module(stream_module)
                if isinstance(module, ManipulatorModule):
                    ephys_modules.append(module)
                else:
                    stick_microscopes.append(module)

        return stick_microscopes, ephys_modules

    def _map_module(self, stream_module) -> Optional[DomeModule | ManipulatorModule]:
        """
        Map a single stream module to either a DomeModule or ManipulatorModule.

        :param stream_module: Stream module from SLIMS
        :return: DomeModule or ManipulatorModule instance
        """
        assembly_name = getattr(stream_module, 'assembly_name', None)
        arc_angle = getattr(stream_module, 'arc_angle', None)
        module_angle = getattr(stream_module, 'module_angle', None)
        rotation_angle = getattr(stream_module, 'rotation_angle', None)
        coordinate_transform = getattr(stream_module, 'coordinate_transform', None)

        # TODO: check what the best field is for this
        if getattr(stream_module, 'primary_targeted_structure', None):
            primary_targeted_structure = getattr(stream_module, 'primary_targeted_structure')
            other_targeted_structures = getattr(stream_module, 'secondary_targeted_structures', None)
            targetted_ccf_coordinates = self._map_ccf_coords(
                ap=getattr(stream_module, 'ccf_coordinate_ap', None),
                ml=getattr(stream_module, 'ccf_coordinate_ml', None),
                dv=getattr(stream_module, 'ccf_coordinate_dv', None)
            )
            manipulator_coordinates = self._map_3d_coords(
                x=getattr(stream_module, 'manipulator_x', None),
                y=getattr(stream_module, 'manipulator_y', None),
                z=getattr(stream_module, 'manipulator_z', None)
            )
            anatomical_coordinates = self._map_3d_coords(
                x=getattr(stream_module, 'bregma_target_ap', None),
                y=getattr(stream_module, 'bregma_target_ml', None),
                z=getattr(stream_module, 'bregma_target_dv', None)
            )
            anatomical_reference = CoordinateReferenceLocation.BREGMA if anatomical_coordinates else None
            surface_z = getattr(stream_module, 'surface_z', None)
            dye = getattr(stream_module, 'dye', None)
            implant_hole_number = getattr(stream_module, 'implant_hole', None)

            return ManipulatorModule.model_construct(
                assembly_name=assembly_name,
                arc_angle=arc_angle,
                module_angle=module_angle,
                rotation_angle=rotation_angle,
                coordinate_transform=coordinate_transform,
                primary_targeted_structure=primary_targeted_structure,
                other_targeted_structures=other_targeted_structures,
                targetted_ccf_coordinates=targetted_ccf_coordinates,
                manipulator_coordinates=manipulator_coordinates,
                anatomical_coordinates=anatomical_coordinates,
                anatomical_reference=anatomical_reference,
                surface_z=surface_z,
                dye=dye,
                implant_hole_number=implant_hole_number
            )
        else:
            return DomeModule.model_construct(
                assembly_name=assembly_name,
                arc_angle=arc_angle,
                module_angle=module_angle,
                rotation_angle=rotation_angle,
                coordinate_transform=coordinate_transform
            )

    @staticmethod
    def _map_stream_modality(modality: str) -> Optional[Modality]:
        """Map stream modality to the Modality enum."""
        modality_mapping = {
            SlimsStreamModalities.ELECTROMYOGRAPHY.value: Modality.EMG,
            SlimsStreamModalities.SPIM.value: Modality.SPIM,
            SlimsStreamModalities.MRI.value: Modality.MRI,
            SlimsStreamModalities.ISI.value: Modality.ISI,
            SlimsStreamModalities.FMOST.value: Modality.FMOST
        }
        return modality_mapping.get(modality, Modality.from_abbreviation(modality.lower().replace(" ", "-")))

    @staticmethod
    def _map_ccf_coords(ml: Optional[float], ap: Optional[float], dv: Optional[float]) -> Optional[CcfCoords]:
        """Map coordinates to CcfCoords."""
        return CcfCoords(ML=ml, AP=ap, DV=dv) if ml and ap and dv else None

    @staticmethod
    def _map_3d_coords(x: Optional[float], y: Optional[float], z: Optional[float]) -> Optional[Coordinates3d]:
        """Map coordinates to 3D space."""
        return Coordinates3d(x=x, y=y, z=z) if x and y and z else None

