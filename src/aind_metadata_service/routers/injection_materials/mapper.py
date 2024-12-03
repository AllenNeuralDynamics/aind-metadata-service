"""Module to handle mapping TARS responses to AIND ViralMaterial model"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from aind_data_schema.core.procedures import ViralMaterial, VirusPrepType
from pydantic import ValidationError
from pydash import get as get_or_else

from aind_metadata_service.backends.tars.models import Alias, PrepLotData


@dataclass
class ViralPrepAliases:
    """Container for viral aliases"""

    plasmid_name: Optional[str] = None
    material_id: Optional[str] = None
    full_genome_name: Optional[str] = None


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
    """Class to handle mapping data into ViralMaterial model."""

    AIP_PATTERN = re.compile(r"^AiP[a-zA-Z0-9_-]+$")
    AIV_PATTERN = re.compile(r"^AiV[a-zA-Z0-9_-]+$")

    def __init__(
        self,
        prep_lot_data: PrepLotData,
    ):
        """Class constructor."""
        self.prep_lot_data = prep_lot_data

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

    @staticmethod
    def map_virus_aliases(aliases: List[Alias]) -> ViralPrepAliases:
        """
        Maps aliases to ViralPrepAliases
        Parameters
        ----------
        aliases : List[Alias]

        Returns
        -------
        ViralPrepAliases

        """
        AIP_PATTERN = re.compile(r"^AiP[a-zA-Z0-9_-]+$")
        AIV_PATTERN = re.compile(r"^AiV[a-zA-Z0-9_-]+$")
        viral_prep_aliases = ViralPrepAliases()
        for alias in aliases:
            match alias.name:
                case None:
                    pass
                case name if AIP_PATTERN.match(alias.name):
                    viral_prep_aliases.plasmid_name = name
                case name if AIV_PATTERN.match(alias.name):
                    viral_prep_aliases.material_id = name
                case _:
                    viral_prep_aliases.full_genome_name = name
        return viral_prep_aliases

    @staticmethod
    def map_full_genome_name(
        plasmid_name: str,
        genome_name: Optional[str],
        molecule_aliases: List[Alias],
    ) -> Optional[str]:
        """
        Maps genome name from MoleculeData
        Parameters
        ----------
        plasmid_name : str
        genome_name: Optional[str]
        molecule_aliases: List[Alias]

        Returns
        -------
        Optional[str]

        """
        if genome_name is not None:
            return genome_name
        elif len(molecule_aliases) != 2:
            return None
        elif molecule_aliases[0].name != plasmid_name:
            return molecule_aliases[0].name
        elif molecule_aliases[1].name != plasmid_name:
            return molecule_aliases[1].name
        else:
            return None

    def map_to_viral_material(
        self, viral_prep_aliases: ViralPrepAliases
    ) -> ViralMaterial:
        """

        Parameters
        ----------
        viral_prep_aliases : ViralPrepAliases

        Returns
        -------
        ViralMaterial

        """

        prep_date = (
            None
            if self.prep_lot_data.datePrepped is None
            else self.prep_lot_data.datePrepped.date()
        )
        prep_lot_number = self.prep_lot_data.lot
        prep_type, prep_protocol = self._map_prep_type(
            get_or_else(self.prep_lot_data, "viralPrep.viralPrepType.name")
        )
        tars_virus_identifiers = {
            "virus_tars_id": viral_prep_aliases.material_id,
            "plasmid_tars_alias": viral_prep_aliases.plasmid_name,
            "prep_lot_number": prep_lot_number,
            "prep_date": prep_date,
            "prep_type": prep_type,
            "prep_protocol": prep_protocol,
        }
        try:
            return ViralMaterial(
                name=viral_prep_aliases.full_genome_name,
                tars_identifiers=tars_virus_identifiers,
            )
        except ValidationError:
            return ViralMaterial.model_construct(
                name=viral_prep_aliases.full_genome_name,
                tars_identifiers=tars_virus_identifiers,
            )
