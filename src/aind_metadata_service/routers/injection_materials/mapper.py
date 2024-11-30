from typing import Optional, Tuple

from aind_data_schema.core.procedures import (
    Injection,
    TarsVirusIdentifiers,
    ViralMaterial,
    VirusPrepType,
)
import re
from aind_metadata_service.backends.tars.models import (
    PrepLotData,
    MoleculeData,
)
from enum import Enum
from pydash import get as get_or_none


# TODO: This should probably be in aind-data-schema.
class PrepProtocols(str, Enum):
    """Enum of Prep Protocols."""

    SOP_VC002 = "SOP#VC002"
    SOP_VC003 = "SOP#VC003"
    HGT = "HGT"
    SOP_VC001 = "SOP#VC001"
    SOP_VC004 = "PHPeB-SOP#VC004"
    MGT2 = "MGT#2.0"
    MGT1 = "MGT#1.0"
    PHP_SOP_UW = "PHPeB-SOP-UW"
    HGT1 = "HGT#1.0"


class Mapper:

    AIP_PATTERN = re.compile(r"^AiP[a-zA-Z0-9_-]+$")
    AIV_PATTERN = re.compile(r"^AiV[a-zA-Z0-9_-]+$")

    def __init__(
        self,
        prep_lot_data: PrepLotData,
        molecules_data: Optional[MoleculeData],
    ):
        """Class constructor."""
        self.prep_lot_data = prep_lot_data
        self.molecule_data = molecules_data

    @staticmethod
    def _map_prep_type(
        viral_prep_name: Optional[str],
    ) -> Tuple[Optional[VirusPrepType], Optional[str]]:
        """
        Maps TARS viral prep name to viral prep type and protocol
        Parameters
        ----------
        viral_prep_name : Optional[str]

        Returns
        -------
        Tuple[Optional[VirusPrepType], Optional[str]]

        """

        match viral_prep_name:
            case "Crude-SOP#VC002":
                return VirusPrepType.CRUDE, PrepProtocols.SOP_VC002
            case "Purified-SOP#VC003":
                return VirusPrepType.PURIFIED, PrepProtocols.SOP_VC003
            case "Crude-HGT":
                return VirusPrepType.CRUDE, PrepProtocols.HGT
            case "Rabies-SOP#VC001":
                return None, PrepProtocols.SOP_VC001
            case "CrudePHPeB-SOP#VC004":
                return VirusPrepType.CRUDE, PrepProtocols.SOP_VC004
            case "Crude-MGT#2.0":
                return VirusPrepType.CRUDE, PrepProtocols.MGT2
            case "Crude-MGT#1.0":
                return VirusPrepType.CRUDE, PrepProtocols.MGT1
            case "Purified-MGT#1.0":
                return VirusPrepType.PURIFIED, PrepProtocols.MGT1
            case "PHPeB-SOP-UW":
                return None, None
            case "Crude-HGT#1.0":
                return VirusPrepType.CRUDE, PrepProtocols.HGT1
            case "VTC-AAV1":
                return None, None
            case "Unknown":
                return None, None
            case "Iodixanol gradient purification (large scale preps)":
                return None, None
            case _:
                return None, None

    def map_prep_lot_response_to_viral_material(
        self,
    ) -> Optional[ViralMaterial]:

        prep_date = self.prep_lot_data.datePrepped
        prep_lot_number = self.prep_lot_data.lot
        prep_type, prep_protocol = self._map_prep_type(
            get_or_none(self.prep_lot_data, "viralPrep.viralPrepType.name")
        )
