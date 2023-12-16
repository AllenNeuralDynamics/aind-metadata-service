"""Module to map data in TARS to aind_data_schema InjectionMaterial"""

from enum import Enum
from aind_data_schema.procedures import VirusPrepType, InjectionMaterial
from datetime import datetime
import re


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
    AIP = re.compile(r"^AiP[a-zA-Z0-9_-]+$")
    AIV = re.compile(r"^AiV[a-zA-Z0-9_-]+$")


class TarsResponseHandler:
    """This class will contain methods to handle the response from TARS"""

    @staticmethod
    def _map_prep_type_and_protocol(
        viral_prep_type: str,
    ) -> tuple[VirusPrepType, str]:
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
    def _convert_datetime(date: str):
        """Converts date string to datetime date"""
        # Is it safe to assume it'll always be in this pattern
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        if not date_pattern.match(date):
            print(
                "Invalid date format."
                " Please provide a date in the format: YYYY-MM-DDTHH:MM:SSZ"
            )
            return None

        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _map_virus_aliases(aliases: list):
        """Maps aliases to full_genome_name, material_id, viral prep id"""
        material_id, viral_prep_id, full_genome_name = None, None, None
        for alias in aliases:
            name = alias["name"]
            if VirusAliasPatterns.AIP.value.match(name):
                material_id = name
            elif VirusAliasPatterns.AIV.value.match(name):
                viral_prep_id = name
            else:
                # TODO: check pattern
                full_genome_name = name
        return material_id, viral_prep_id, full_genome_name

    def map_response_to_injection_materials(self, response):
        """Map prep lot dictionary to injection materials"""
        data = response.json()["data"][0]
        prep_lot_number = data["lot"]
        prep_date = self._convert_datetime(data["datePrepped"])
        prep_type, prep_protocol = self._map_prep_type_and_protocol(
            data["viralPrep"]["viralPrepType"]["name"]
        )
        material_id, viral_prep_id, name = self._map_virus_aliases(
            data["viralPrep"]["virus"]["aliases"]
        )
        return InjectionMaterial(
            prep_lot_number=prep_lot_number,
            prep_date=prep_date,
            prep_type=prep_type,
            prep_protocol=prep_protocol,
            material_id=material_id,
            name=name,
        )
