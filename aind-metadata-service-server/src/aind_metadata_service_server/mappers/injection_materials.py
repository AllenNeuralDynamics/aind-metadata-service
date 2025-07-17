"""Module to map data in TARS to aind_data_schema InjectionMaterial"""

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from aind_data_schema.core.procedures import (
    Injection,
    TarsVirusIdentifiers,
    ViralMaterial,
    VirusPrepType,
)
from aind_data_schema_models.pid_names import BaseName, PIDName
from aind_tars_service_async_client.models import PrepLotData, VirusData, Alias
from pydantic import ValidationError

from aind_metadata_service_server.models import ViralMaterialInformation


# TODO: These classes should be in the TARS microservice library
class ViralPrepTypes(str, Enum):
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


class PrepProtocols(str, Enum):
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


@dataclass
class TarsVirusInformation:
    """Dataclass to store virus information"""

    name: Optional[str]
    plasmid_alias: Optional[str]
    addgene_id: Optional[str]
    rrid: Optional[str]


class TarsMapper:
    """Class to handle mapping of TARS data to aind-data-schema models."""

    def __init__(
        self,
        prep_lot_data: PrepLotData,
        virus_data: List[VirusData] = (),
    ):
        """
        Class constructor.

        Parameters
        ----------
        prep_lot_data : PrepLotData
            The prep lot data from TARS
        virus_data : List[VirusData]
            List of VirusData from TARS
        """
        self.prep_lot_data = prep_lot_data
        self.virus_data = list(virus_data)

    @property
    def virus_id(self) -> Optional[str]:
        """Virus ID associated with prep lot."""
        if (
            self.prep_lot_data.viral_prep
            and self.prep_lot_data.viral_prep.virus
            and self.prep_lot_data.viral_prep.virus.aliases
        ):
            for alias in self.prep_lot_data.viral_prep.virus.aliases:
                if alias.is_preferred:
                    return alias.name
        return None

    @staticmethod
    def _map_to_prep_type(
        viral_prep_type: ViralPrepTypes,
    ) -> Optional[VirusPrepType]:
        """
        Maps tars viral prep type to VirusPrepType

        Parameters
        ----------
        viral_prep_type : ViralPrepTypes
            The viral prep type from TARS

        Returns
        -------
        VirusPrepType | None
        """
        match viral_prep_type:
            case (
                ViralPrepTypes.CRUDE_SOP
                | ViralPrepTypes.CRUDE_HGT
                | ViralPrepTypes.CRUDE_HGT1
                | ViralPrepTypes.RABIES_SOP
                | ViralPrepTypes.CRUDE_PHP_SOP
                | ViralPrepTypes.CRUDE_MGT1 | ViralPrepTypes.CRUDE_MGT2
            ):
                prep_type = VirusPrepType.CRUDE
            case (ViralPrepTypes.PURIFIED_SOP | ViralPrepTypes.PURIFIED_MGT1):
                prep_type = VirusPrepType.PURIFIED
            case _:
                prep_type = None
        return prep_type

    @staticmethod
    def _map_to_protocol(
        viral_prep_type: ViralPrepTypes,
    ) -> Optional[PrepProtocols]:
        """
        Maps tars viral_prep_type to  protocol string.

        Parameters
        ----------
        viral_prep_type : ViralPrepTypes
            The viral prep type from TARS

        Returns
        -------
        PrepProtocols | None
        """
        match viral_prep_type:
            case (
                ViralPrepTypes.CRUDE_MGT1 | ViralPrepTypes.PURIFIED_MGT1
            ):
                prep_protocol = PrepProtocols.MGT1
            case ViralPrepTypes.CRUDE_MGT2:
                prep_protocol = PrepProtocols.MGT2
            case ViralPrepTypes.CRUDE_SOP:
                prep_protocol = PrepProtocols.SOP_VC002
            case ViralPrepTypes.PURIFIED_SOP:
                prep_protocol = PrepProtocols.SOP_VC003
            case ViralPrepTypes.CRUDE_HGT:
                prep_protocol = PrepProtocols.HGT
            case ViralPrepTypes.RABIES_SOP:
                prep_protocol = PrepProtocols.SOP_VC001
            case ViralPrepTypes.CRUDE_PHP_SOP:
                prep_protocol = PrepProtocols.SOP_VC004
            case ViralPrepTypes.CRUDE_HGT1:
                prep_protocol = PrepProtocols.HGT1
            case _:
                prep_protocol = None
        return prep_protocol

    @staticmethod
    def _map_plasmid_name(aliases: List[Alias]) -> Optional[str]:
        """
        Maps plasmid name from aliases.

        Parameters
        ----------
        aliases : List
            List of alias objects

        Returns
        -------
        str | None
            Preferred plasmid name or None
        """
        for alias in aliases:
            if alias.is_preferred:
                return alias.name
        return None

    @staticmethod
    def _map_stock_titer(titers: Optional[List]) -> Optional[int]:
        """
        Maps titer from viral prep lot.

        Parameters
        ----------
        titers : Optional[List]
            List of titer objects

        Returns
        -------
        int | None
            Stock titer value or None
        """
        if titers and len(titers) > 0:
            first_titer = titers[0]
            if first_titer.result
            if (
                hasattr(first_titer, "result")
                and first_titer.result is not None
            ):
                return int(first_titer.result)
        return None

    def _get_virus_tars_id_from_prep_lot(self) -> Optional[str]:
        """
        Extracts virus TARS ID from prep lot data.

        Returns
        -------
        Optional[str]
            Virus TARS ID or None
        """
        if (
            self.prep_lot_data.viral_prep
            and self.prep_lot_data.viral_prep.virus
            and self.prep_lot_data.viral_prep.virus.aliases
        ):
            return next(
                (
                    alias.name
                    for alias in self.prep_lot_data.viral_prep.virus.aliases
                    if alias.is_preferred
                ),
                None,
            )
        return None

    def _map_virus_information(self) -> TarsVirusInformation:
        """
        Maps name, plasmid, and addgene from virus response.

        Returns
        -------
        TarsVirusInformation
            Mapped virus information
        """
        names = []
        plasmid_aliases = []
        addgene_ids = []
        rrids = []

        # Use the rr_id from the virus data if available
        if self.virus_data.rr_id:
            rrids.append(str(self.virus_data.rr_id))

        # Process molecules if they exist
        if self.virus_data.molecules:
            for molecule in self.virus_data.molecules:
                # Extract full name
                if hasattr(molecule, "full_name") and molecule.full_name:
                    names.append(molecule.full_name)

                # Extract plasmid name from aliases
                if hasattr(molecule, "aliases") and molecule.aliases:
                    plasmid_name = self._map_plasmid_name(molecule.aliases)
                    if plasmid_name:
                        plasmid_aliases.append(plasmid_name)

                # Extract addgene ID
                if hasattr(molecule, "addgene_id") and molecule.addgene_id:
                    addgene_ids.append(str(molecule.addgene_id))

                # Extract rr_id from molecule
                if hasattr(molecule, "rr_id") and molecule.rr_id:
                    rrids.append(str(molecule.rr_id))

        name = "; ".join(names) if names else None
        plasmid_alias = "; ".join(plasmid_aliases) if plasmid_aliases else None
        addgene_id = "; ".join(addgene_ids) if addgene_ids else None
        rrid = "; ".join(rrids) if rrids else None

        return TarsVirusInformation(
            name=name,
            plasmid_alias=plasmid_alias,
            addgene_id=addgene_id,
            rrid=rrid,
        )

    def _get_prep_type_name(self) -> str:
        """
        Gets the prep type name from the prep lot data.

        Returns
        -------
        str
            Prep type name or empty string
        """
        if (
            self.prep_lot_data.viral_prep
            and hasattr(self.prep_lot_data.viral_prep, "viral_prep_type")
            and self.prep_lot_data.viral_prep.viral_prep_type
            and hasattr(self.prep_lot_data.viral_prep.viral_prep_type, "name")
        ):
            return self.prep_lot_data.viral_prep.viral_prep_type.name
        return ""

    def _create_addgene_pid_name(
        self, virus_info: TarsVirusInformation
    ) -> Optional[PIDName]:
        """
        Creates PIDName for Addgene information.

        Parameters
        ----------
        virus_info : TarsVirusInformation
            Virus information containing addgene data

        Returns
        -------
        PIDName | None
            PIDName object or None
        """
        if not virus_info.addgene_id:
            return None

        return PIDName(
            name=virus_info.name,
            registry=(
                BaseName(name=virus_info.rrid) if virus_info.rrid else None
            ),
            registry_identifier=virus_info.addgene_id,
        )

    def map_to_viral_material_information(self) -> ViralMaterialInformation:
        """
        Map prep lot data to ViralMaterialInformation.
        Will attempt to return a valid model. If there are any validation
        errors, then an invalid model will be returned using model_construct.

        Returns
        -------
        ViralMaterialInformation
            Mapped viral material information
        """
        prep_lot_number = self.prep_lot_data.lot
        prep_date = (
            None
            if self.prep_lot_data.date_prepped is None
            else self.prep_lot_data.date_prepped.date()
        )
        prep_type_name = self._get_prep_type_name()
        prep_type, prep_protocol = self._map_prep_type_and_protocol(
            prep_type_name
        )
        virus_info = self._map_virus_information()
        addgene_id = self._create_addgene_pid_name(virus_info)
        stock_titer = self._map_stock_titer(self.prep_lot_data.titers)

        try:
            tars_virus_identifiers = TarsVirusIdentifiers(
                virus_tars_id=self.virus_id,
                plasmid_tars_alias=virus_info.plasmid_alias,
                prep_lot_number=prep_lot_number,
                prep_date=prep_date,
                prep_type=prep_type,
                prep_protocol=prep_protocol,
            )
            return ViralMaterialInformation(
                name=virus_info.name,
                tars_identifiers=tars_virus_identifiers,
                stock_titer=stock_titer,
                addgene_id=addgene_id,
            )
        except ValidationError:
            tars_virus_identifiers = TarsVirusIdentifiers.model_construct(
                virus_tars_id=self.virus_id,
                plasmid_tars_alias=virus_info.plasmid_alias,
                prep_lot_number=prep_lot_number,
                prep_date=prep_date,
                prep_type=prep_type,
                prep_protocol=prep_protocol,
            )
            return ViralMaterialInformation.model_construct(
                name=virus_info.name,
                tars_identifiers=tars_virus_identifiers,
                stock_titer=stock_titer,
                addgene_id=addgene_id,
            )
