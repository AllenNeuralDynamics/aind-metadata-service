"""Module to map data in TARS to aind_data_schema InjectionMaterial"""

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional

from aind_data_schema.core.procedures import (
    TarsVirusIdentifiers,
    ViralMaterial,
    VirusPrepType,
)
from pydantic import ValidationError


class ViralPrepTypes(Enum):
    """Enum of Viral Prep Type options in TARS"""

    CRUDE_SOP = "Crude-SOP#VC002"
    PURIFIED_SOP = "Purified-SOP#VC003"
    CRUDE_HGT = "Crude-HGT"
    RABIES_SOP = "Rabies-SOP#VC001"
    CRUDE_PHP_SOP = "CrudePHPeB-SOP#VC004"
    CRUDE_MGT2 = "Crude-MGT#2.0"
    CRUDE_MGT1 = "Crude-MGT#1.0"
    PURIFIED_MGT1 = "Purified-MGT#1.0"
    PHP_SOP_UW = "PHPeB-SOP-UW"
    CRUDE_HGT1 = "Crude-HGT#1.0"
    VTC_AAV1 = "VTC-AAV1"
    UNKNOWN = "Unknown"
    IODIXANOL = "Iodixanol gradient purification (large scale preps)"


class PrepProtocols(Enum):
    """Enum of Prep Protocols"""

    SOP_VC002 = "SOP#VC002"
    SOP_VC003 = "SOP#VC003"
    HGT = "HGT"
    SOP_VC001 = "SOP#VC001"
    SOP_VC004 = "PHPeB-SOP#VC004"
    MGT2 = "MGT#2.0"
    MGT1 = "MGT#1.0"
    PHP_SOP_UW = "PHPeB-SOP-UW"
    HGT1 = "HGT#1.0"


class VirusAliasPatterns(Enum):
    """Virus Alias Patterns"""

    # TODO: add pattern for genome_name once confirmed
    AIP = re.compile(r"^AiP[a-zA-Z0-9_-]+$")
    AIV = re.compile(r"^AiV[a-zA-Z0-9_-]+$")


@dataclass
class ViralPrepAliases:
    """Model for mapping viral prep aliases"""

    plasmid_name: Optional[str]
    material_id: Optional[str]
    full_genome_name: Optional[str]


class TarsResponseHandler:
    """This class will contain methods to handle the response from TARS"""

    @staticmethod
    def _map_prep_type_and_protocol(
        viral_prep_type: str,
    ) -> tuple[Optional[VirusPrepType], Optional[str]]:
        """Maps TARS viral prep type to prep_type and prep_protocol"""
        if viral_prep_type == ViralPrepTypes.CRUDE_SOP.value:
            prep_type = VirusPrepType.CRUDE
            prep_protocol = PrepProtocols.SOP_VC002.value
        elif viral_prep_type == ViralPrepTypes.PURIFIED_SOP.value:
            prep_type = VirusPrepType.PURIFIED
            prep_protocol = PrepProtocols.SOP_VC003.value
        elif viral_prep_type == ViralPrepTypes.CRUDE_HGT.value:
            prep_type = VirusPrepType.CRUDE
            prep_protocol = PrepProtocols.HGT.value
        elif viral_prep_type == ViralPrepTypes.RABIES_SOP.value:
            prep_type = None
            prep_protocol = PrepProtocols.SOP_VC001.value
        elif viral_prep_type == ViralPrepTypes.CRUDE_PHP_SOP.value:
            prep_type = VirusPrepType.CRUDE
            prep_protocol = PrepProtocols.SOP_VC004.value
        elif viral_prep_type == ViralPrepTypes.CRUDE_MGT2.value:
            prep_type = VirusPrepType.CRUDE
            prep_protocol = PrepProtocols.MGT2.value
        elif viral_prep_type == ViralPrepTypes.CRUDE_MGT1.value:
            prep_type = VirusPrepType.CRUDE
            prep_protocol = PrepProtocols.MGT1.value
        elif viral_prep_type == ViralPrepTypes.PURIFIED_MGT1.value:
            prep_type = VirusPrepType.PURIFIED
            prep_protocol = PrepProtocols.MGT1.value
        elif viral_prep_type == ViralPrepTypes.CRUDE_HGT1.value:
            prep_type = VirusPrepType.CRUDE
            prep_protocol = PrepProtocols.HGT1.value
        else:
            # TODO: figure out how we want to handle the rest
            #  PHP_SOP_UW, VTC_AAV1, UNKNOWN, and IODIXANOL
            prep_type = None
            prep_protocol = None
        return prep_type, prep_protocol

    @staticmethod
    def _convert_datetime(date: str) -> Optional[date]:
        """Converts date string to datetime date"""
        # Is it safe to assume it'll always be in this pattern
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        if not date_pattern.match(date):
            logging.warning(
                "Invalid date format."
                " Please provide a date in the format: YYYY-MM-DDTHH:MM:SSZ"
            )
            return None
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()

    @staticmethod
    def map_virus_aliases(aliases: list) -> ViralPrepAliases:
        """Maps aliases to full_genome_name, material_id, viral prep id"""
        plasmid_name, material_id, full_genome_name = None, None, None
        for alias in aliases:
            name = alias["name"]
            if VirusAliasPatterns.AIP.value.match(name):
                plasmid_name = name
            elif VirusAliasPatterns.AIV.value.match(name):
                material_id = name
            else:
                full_genome_name = name
        viral_prep_aliases = ViralPrepAliases(
            plasmid_name=plasmid_name,
            material_id=material_id,
            full_genome_name=full_genome_name,
        )
        return viral_prep_aliases

    @staticmethod
    def map_full_genome_name(response, plasmid_name) -> Optional[str]:
        """Maps genome name from molecular response"""
        full_genome_name = None
        data = response.json()["data"][0]
        aliases = data["aliases"]
        if len(aliases) == 2:
            if aliases[0]["name"] != plasmid_name:
                full_genome_name = aliases[0]["name"]
            elif aliases[1]["name"] != plasmid_name:
                full_genome_name = aliases[1]["name"]
        return full_genome_name

    def map_lot_to_injection_material(
        self, viral_prep_lot: dict, viral_prep_aliases: ViralPrepAliases
    ) -> ViralMaterial:
        """
        Map prep lot dictionary to injection materials
        Parameters
        ----------
        viral_prep_lot: dict
            Dictionary of raw viral prep lot data from TARS response.
        viral_prep_aliases: ViralPrepAliases
            Prep aliases mapped from TARS viral prep and molecular endpoints.
        """
        prep_lot_number = viral_prep_lot["lot"]
        prep_date = self._convert_datetime(viral_prep_lot["datePrepped"])
        prep_type, prep_protocol = self._map_prep_type_and_protocol(
            viral_prep_lot["viralPrep"]["viralPrepType"]["name"]
        )
        try:
            tars_virus_identifiers = TarsVirusIdentifiers(
                virus_tars_id=viral_prep_aliases.material_id,
                plasmid_tars_alias=viral_prep_aliases.plasmid_name,
                prep_lot_number=prep_lot_number,
                prep_date=prep_date,
                prep_type=prep_type,
                prep_protocol=prep_protocol,
            )
            return ViralMaterial(
                name=viral_prep_aliases.full_genome_name,
                tars_identifiers=tars_virus_identifiers,
            )
        except ValidationError:
            tars_virus_identifiers = TarsVirusIdentifiers.model_construct(
                virus_tars_id=viral_prep_aliases.material_id,
                plasmid_tars_alias=viral_prep_aliases.plasmid_name,
                prep_lot_number=prep_lot_number,
                prep_date=prep_date,
                prep_type=prep_type,
                prep_protocol=prep_protocol,
            )
            return ViralMaterial.model_construct(
                name=viral_prep_aliases.full_genome_name,
                tars_identifiers=tars_virus_identifiers,
            )
