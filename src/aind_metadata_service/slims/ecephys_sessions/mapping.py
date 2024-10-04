"""Module to map data from slims to Session model"""
from Demos.win32console_demo import coord
from aind_data_schema.core.session import Session, DomeModule
from enum import Enum
from aind_slims_api import SlimsClient
from aind_slims_api.operations.ecephys_session import (
    fetch_ecephys_sessions,
    EcephysSession as SlimsEcephysSession
)
from typing import Optional
from aind_data_schema_models.modalities import Modality

class SlimsStreamModalities(Enum):
    """Enum class for stream modalities in SLIMS"""
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
    """Client to connect to slims db"""

    def __init__(self, slims_client: SlimsClient):
        """Class constructor for slims client"""
        self.client = slims_client


    def get_slims_sessions(self, subject_id: str):
        # TODO: don't use getattr for required fields?
        try:
            sessions = fetch_ecephys_sessions(subject_id=subject_id, client=self.client)
            for session in sessions:
                # map session group
                session_type = getattr(session.session_group, 'session_type', None)
                mouse_platform_name = getattr(session.session_group, 'mouse_platform_name', None)
                active_mouse_platform = getattr(session.session_group, 'active_mouse_platform', None)
                # TODO: get rig id and experimenter name from SLIMS

                # map session result
                session_result = getattr(session, 'session_result', None)
                animal_weight_prior = getattr(session.session_result, 'weight_prior_g', None) if session_result else None
                animal_weight_post = getattr(session.session_result, 'weight_post_g', None) if session_result else None
                reward_consumed_total = getattr(session.session_result, 'reward_consumed_vol', None) if session_result else None

                # map streams
                streams = []
                for stream in session.streams:
                    # TODO: get stream_start_time and end_time from SLIMS (ask Lisa)
                    stream_modalities = [self._map_stream_modality(modality) for modality in getattr(stream, 'stream_modalities', [])]
                    daq_names = getattr(stream, "daq_names", [])
                    camera_names = getattr(stream, "camera_names", [])

                    if getattr(stream, 'stream_modules_pk', None):
                        #  maybe change logic in slims api to have Stream object with stream result and linked modules
                        for stream_module in session.stream_modules:
                            if stream_module.pk in stream.stream_modules_pk:
                                assembly_name = getattr(stream_module, 'assembly_name', None)
                                arc_angle = getattr(stream_module, 'arc_angle', None)
                                module_angle = getattr(stream_module, 'module_angle', None)
                                rotation_angle = getattr(stream_module, 'rotation_angle', None)
                                coordinate_transform = getattr(stream_module, 'coordinate_transform', None)
                                # TODO: what is distinguishing data point for manipulator vs stick microscope
                                if getattr(stream_module, 'primary_targeted_structure', None):
                                    # map manipulator module
                                    primary_targeted_structure = getattr(stream_module, 'primary_targeted_structure')
                                    other_targeted_structures = getattr(stream_module, 'secondary_targeted_structures', None)
                                    # TODO: map coords
                                else:
                                    dome_module = DomeModule(
                                        assembly_name=assembly_name,
                                        arc_angle=arc_angle,
                                        module_angle=module_angle,
                                        rotation_angle=rotation_angle,
                                        coordinate_transform=coordinate_transform,
                                    )





        except Exception as e:
            print(e)


    @staticmethod
    def _map_stream_modality(modality: str) -> Optional[Modality]:
        """Maps stream modality"""
        if modality == SlimsStreamModalities.ELECTROMYOGRAPHY:
            return Modality.EMG
        elif modality == SlimsStreamModalities.SPIM or modality == SlimsStreamModalities.MRI or modality == SlimsStreamModalities.ISI:
            return Modality.from_abbreviation(modality.upper())
        elif modality == SlimsStreamModalities.FMOST:
            return Modality.FMOST
        else:
            modality_abbreviation = modality.lower().replace(" ", "-")
            mapped_modality = Modality.from_abbreviation(modality_abbreviation)
            return mapped_modality
