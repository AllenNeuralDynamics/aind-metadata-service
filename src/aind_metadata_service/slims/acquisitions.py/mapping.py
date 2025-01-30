"""Module for mapping imaging metadata from SLIMS to acquisitions."""

from aind_data_schema.core.acquisition import (
    Acquisition,
    ImageAxis,
    AnatomicalDirection,
    Immersion,
    ImmersionMedium,
)
from aind_slims_api.models.imaging import (
    SlimsSPIMBrainOrientationRdrc,
)
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class SlimsAnatomicalDirections(Enum):
    """Enum class for Anatomical Directions defined in SLIMS"""

    SUPERIOR_TO_INFERIOR = "Superior to Inferior"
    INFERIOR_TO_SUPERIOR = "Inferior to Superior"
    LEFT_TO_RIGHT = "Left to Right"
    RIGHT_TO_LEFT = "Right to Left"
    ANTERIOR_TO_POSTERIOR = "Anterior to Posterior"
    POSTERIOR_TO_ANTERIOR = "Posterior to Anterior"


class SlimsImmersionMediums(Enum):
    """Enum class for Immersion Mediums defined in SLIMS"""

    DIH2O = "diH2O"
    CARGILLE_OIL_15200 = "Cargille Oil 1.5200"
    CARGILLE_OIL_15300 = "Cargille Oil 1.5300"
    ETHYL_CINNAMATE = "Ethyl Cinnamate"
    OPTIPLEX_AND_DMSO = "Optiplex and DMSO"
    EASYINDEX = "EasyIndex"


class SlimsAcquisitionMapper:
    """Mapper class for Slims imaging acquisitions"""

    def map_imaging_acquisitions(
        self,
        slims_metadata: List[Dict],
        subject_id: str,
        date_performed: Optional[datetime] = None,
        latest: Optional[bool] = False,
    ) -> List[Acquisition]:
        """Map acquisitions from Slims imaging data"""
        if date_performed:
            # Filter metadata acquired at a given time (no seconds/microseconds)
            date_performed = date_performed.replace(second=0, microsecond=0)
            slims_metadata = [
                data
                for data in slims_metadata
                if data.get("date_performed")
                and datetime.fromisoformat(data["date_performed"]).replace(
                    second=0, microsecond=0
                )
                == date_performed
            ]
        elif latest:
            dated_metadata = [
                data for data in slims_metadata if data.get("date_performed")
            ]
            if len(dated_metadata) == len(slims_metadata):
                # Filter metadata by most recent acquisition
                slims_metadata = [
                    max(dated_metadata, key=lambda x: datetime.fromisoformat(x["date_performed"]))
                ]
    
        # Map acquisitions for selected metadata, or all metadata
        return [self._map_acquisition(data, subject_id) for data in slims_metadata]


    def _map_acquisition(self, data: Dict, subject_id: str) -> Acquisition:
        """Map acquisition from data"""
        imaging_metadata = data.get("imaging_metadata")
        brain_orientation = data.get("brain_orientation")
        # TODO: return a simple dictionary instead 
        acquisition = Acquisition.model_construct(
            specimen_id=data.get("specimen_id") if data.get("specimen_id") else subject_id,
            subject_id=subject_id,
            experimenter_full_name=(
                [data.get("surgeon")] if data.get("surgeon") else []
            ),
            instrument_id=data.get("instrument"),
            session_type="SPIM Imaging",
            axes=(
                self._map_brain_orientation(brain_orientation)
                if brain_orientation
                else []
            ),
            chamber_immersion=self._map_immersion(
                medium=getattr(
                    imaging_metadata, "chamber_immersion_medium", None
                ),
                refractive_index=getattr(
                    imaging_metadata, "chamber_refractive_index", None
                ),
            ),
            sample_immersion=self._map_immersion(
                medium=getattr(
                    imaging_metadata, "sample_immersion_medium", None
                ),
                refractive_index=getattr(
                    imaging_metadata, "sample_refractive_index", None
                ),
            ),
        )

        return acquisition

    def _map_immersion(
        self, medium: Optional[str], refractive_index: Optional[float]
    ) -> Optional[Immersion]:
        """Map immersion medium and refractive index"""
        if medium or refractive_index:
            return Immersion.model_construct(
                medium=self._map_immersion_medium(medium) if medium else None,
                refractive_index=(
                    int(refractive_index) if refractive_index else None
                ),
            )
        else:
            return None

    def _map_immersion_medium(self, medium: str) -> ImmersionMedium:
        """Map immersion medium"""
        if medium == SlimsImmersionMediums.DIH2O.value:
            return ImmersionMedium.WATER
        elif medium == SlimsImmersionMediums.CARGILLE_OIL_15200.value:
            return ImmersionMedium.OIL
        elif medium == SlimsImmersionMediums.CARGILLE_OIL_15300.value:
            return ImmersionMedium.OIL
        elif medium == SlimsImmersionMediums.ETHYL_CINNAMATE.value:
            return ImmersionMedium.ECI
        elif medium == SlimsImmersionMediums.OPTIPLEX_AND_DMSO.value:
            # TODO: check what to map this to
            return ImmersionMedium.MULTI
        elif medium == SlimsImmersionMediums.EASYINDEX.value:
            return ImmersionMedium.EASYINDEX
        else:
            return ImmersionMedium.OTHER

    def _map_brain_orientation(
        self, brain_orientation: SlimsSPIMBrainOrientationRdrc
    ) -> List[ImageAxis]:
        """Map brain orientation record to axes"""
        axes = []
        if brain_orientation.x_direction:
            x = ImageAxis(
                name="X",
                dimension=2,
                direction=self._map_direction(brain_orientation.x_direction),
            )
            axes.append(x)
        if brain_orientation.y_direction:
            y = ImageAxis(
                name="Y",
                dimension=1,
                direction=self._map_direction(brain_orientation.y_direction),
            )
            axes.append(y)
        if brain_orientation.z_direction:
            z = ImageAxis(
                name="Z",
                dimension=0,
                direction=self._map_direction(brain_orientation.z_direction),
            )
            axes.append(z)
        return axes

    @staticmethod
    def _map_direction(direction: str) -> AnatomicalDirection:
        """Map anatomical direction"""
        if direction == SlimsAnatomicalDirections.SUPERIOR_TO_INFERIOR.value:
            return AnatomicalDirection.SI
        elif direction == SlimsAnatomicalDirections.INFERIOR_TO_SUPERIOR.value:
            return AnatomicalDirection.IS
        elif direction == SlimsAnatomicalDirections.LEFT_TO_RIGHT.value:
            return AnatomicalDirection.LR
        elif direction == SlimsAnatomicalDirections.RIGHT_TO_LEFT.value:
            return AnatomicalDirection.RL
        elif (
            direction == SlimsAnatomicalDirections.ANTERIOR_TO_POSTERIOR.value
        ):
            return AnatomicalDirection.AP
        elif (
            direction == SlimsAnatomicalDirections.POSTERIOR_TO_ANTERIOR.value
        ):
            return AnatomicalDirection.PA
        else:
            return None
