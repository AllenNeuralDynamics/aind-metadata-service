"""Maps information to aind-data-schema Rig or Instrument model."""

from typing import Any, Dict, List

from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.rig import Rig
from pydantic import ValidationError


class RigAndInstrumentMapper:
    """Class to handle mapping of data."""

    def __init__(self, slims_models: List[Dict[str, Any]] = ()):
        """
        Class constructor.
        Parameters
        ----------
        slims_models :  List[Dict[str, Any]] | None
        """
        self.slims_models = list(slims_models)

    def map_to_rigs(self) -> List[Rig]:
        """Map information to Rig models"""
        rigs = []
        for model in self.slims_models:
            try:
                rig = Rig(**model)
            except ValidationError:
                rig = Rig.model_construct(**model)
            rigs.append(rig)
        return rigs

    def map_to_instruments(self) -> List[Instrument]:
        """Map information to Instrument models"""

        instruments = []
        for model in self.slims_models:
            try:
                instrument = Instrument(**model)
            except ValidationError:
                instrument = Instrument.model_construct(**model)
            instruments.append(instrument)
        return instruments
