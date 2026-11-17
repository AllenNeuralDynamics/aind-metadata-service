"""Maps Dataverse SmartSPIM imaging data to aind-data-schema Acquisition."""

from typing import List, Optional, Type

from aind_data_schema.components.configs import (
    Channel,
    ImagingConfig,
    Immersion,
    LaserConfig,
    SampleChamberConfig,
)
from aind_data_schema.components.coordinates import Axis, CoordinateSystem
from aind_data_schema.core.acquisition import Acquisition, DataStream
from aind_data_schema_models.coordinates import AxisName, Direction, Origin
from aind_data_schema_models.devices import ImmersionMedium
from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.units import SizeUnit
from aind_dataverse_service_async_client.models import SmartSpimImagingModel
from pydantic import BaseModel, ValidationError

IMMERSION_MEDIUMS = {
    "Cargille oil": ImmersionMedium.OIL,
    "diH2O": ImmersionMedium.WATER,
    "EasyIndex": ImmersionMedium.EASYINDEX,
    "Ethyl cinnamate": ImmersionMedium.ECI,
}
SAMPLE_CHAMBER_NAME = "Sample chamber"
TIME_NOTE = (
    "Acquisition start and end times are the date imaging was performed. "
    "Dataverse does not record the exact times."
)


def _build(model: Type[BaseModel], **fields) -> BaseModel:
    """Validate the model, or construct it unvalidated if data is missing."""
    try:
        return model(**fields)
    except ValidationError:
        return model.model_construct(**fields)


class SmartSpimAcquisitionMapper:
    """Class to handle mapping of SmartSPIM imaging data."""

    def __init__(self, imaging: List[SmartSpimImagingModel]):
        """Constructor for SmartSpimAcquisitionMapper."""
        self.imaging = imaging

    def map_to_acquisitions(self) -> List[Acquisition]:
        """Maps each imaging session to an Acquisition model."""
        return [self._map_acquisition(data) for data in self.imaging]

    @staticmethod
    def _map_immersion(
        medium: Optional[str], refractive_index: Optional[str]
    ) -> Optional[Immersion]:
        """Maps an immersion medium label and refractive index."""
        if medium is None and refractive_index is None:
            return None
        return _build(
            Immersion,
            medium=(
                None
                if medium is None
                else IMMERSION_MEDIUMS.get(medium, ImmersionMedium.OTHER)
            ),
            refractive_index=(
                None if refractive_index is None else float(refractive_index)
            ),
        )

    @staticmethod
    def _map_coordinate_system(
        data: SmartSpimImagingModel,
    ) -> Optional[CoordinateSystem]:
        """Maps the x, y and z directions to a coordinate system. The name
        lists the side each axis points to, in x, y, z order."""
        directions = [data.x_direction, data.y_direction, data.z_direction]
        if None in directions:
            return None
        code = "".join(d.split("_to_")[-1][0].upper() for d in directions)
        return CoordinateSystem(
            name=f"SPIM_{code}",
            origin=Origin.ORIGIN,
            axis_unit=SizeUnit.MM,
            axes=[
                Axis(name=name, direction=Direction(direction))
                for name, direction in zip(
                    [AxisName.X, AxisName.Y, AxisName.Z], directions
                )
            ],
        )

    @staticmethod
    def _map_channel(channel_name: str) -> Channel:
        """Maps an imaging channel. Its name is the excitation wavelength."""
        light_sources = (
            [
                LaserConfig(
                    device_name=f"Laser_{channel_name}",
                    wavelength=int(channel_name),
                    wavelength_unit=SizeUnit.NM,
                )
            ]
            if channel_name.isdigit()
            else []
        )
        return Channel.model_construct(
            channel_name=channel_name, light_sources=light_sources
        )

    def _map_acquisition(self, data: SmartSpimImagingModel) -> Acquisition:
        """Maps an imaging session to an Acquisition model. Dataverse has no
        detector or image tile information, so the channels, imaging config,
        data stream and acquisition are constructed without validation."""
        instrument = data.instrument_id or data.instrument_nickname
        coordinate_system = self._map_coordinate_system(data)
        imaging_config = ImagingConfig.model_construct(
            device_name=instrument,
            channels=[
                self._map_channel(c) for c in (data.imaging_channels or [])
            ],
            coordinate_system=coordinate_system,
        )
        chamber_config = _build(
            SampleChamberConfig,
            device_name=SAMPLE_CHAMBER_NAME,
            chamber_immersion=self._map_immersion(
                data.chamber_immersion_medium, data.chamber_refractive_index
            ),
            sample_immersion=self._map_immersion(
                data.sample_immersion_medium, data.sample_refractive_index
            ),
        )
        data_stream = DataStream.model_construct(
            stream_start_time=data.date_performed,
            stream_end_time=data.date_performed,
            modalities=[Modality.SPIM],
            active_devices=[
                d for d in [instrument, SAMPLE_CHAMBER_NAME] if d is not None
            ],
            configurations=[imaging_config, chamber_config],
        )
        return Acquisition.model_construct(
            subject_id=data.subject_id,
            specimen_id=data.specimen_id,
            acquisition_start_time=data.date_performed,
            acquisition_end_time=data.date_performed,
            experimenters=(
                [data.experimenter_name] if data.experimenter_name else []
            ),
            instrument_id=instrument,
            acquisition_type="SmartSPIM",
            protocol_id=[data.protocol_id] if data.protocol_id else None,
            coordinate_system=coordinate_system,
            data_streams=[data_stream],
            notes=TIME_NOTE,
        )
