"""Module to map data in TARS to aind_data_schema InjectionMaterial"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from aind_data_schema.components.injection_procedures import (
    TarsVirusIdentifiers,
    VirusPrepType,
)
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.registries import Registry
from aind_tars_service_async_client import Titers
from aind_tars_service_async_client.models import PrepLotData, VirusData
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

    name: Optional[str] = None
    plasmid_alias: Optional[List[str]] = None
    addgene_id: Optional[str] = None
    rrid: Optional[str] = None


class InjectionMaterialsMapper:
    """Class to handle mapping of injection materials."""

    def __init__(
        self,
        tars_prep_lot_data: PrepLotData,
        tars_virus_data: List[VirusData] = (),
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
        self.prep_lot_data = tars_prep_lot_data
        self.virus_data = list(tars_virus_data)

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
        viral_prep_type_name: Optional[str],
    ) -> Optional[VirusPrepType]:
        """
        Maps tars viral prep type to VirusPrepType

        Parameters
        ----------
        viral_prep_type_name : str | None
            The viral prep type name from TARS

        Returns
        -------
        VirusPrepType | None
        """
        match viral_prep_type_name:
            case (
                ViralPrepTypes.CRUDE_SOP
                | ViralPrepTypes.CRUDE_HGT
                | ViralPrepTypes.CRUDE_HGT1
                | ViralPrepTypes.RABIES_SOP
                | ViralPrepTypes.CRUDE_PHP_SOP
                | ViralPrepTypes.CRUDE_MGT1
                | ViralPrepTypes.CRUDE_MGT2
            ):
                prep_type = VirusPrepType.CRUDE
            case ViralPrepTypes.PURIFIED_SOP | ViralPrepTypes.PURIFIED_MGT1:
                prep_type = VirusPrepType.PURIFIED
            case _:
                prep_type = None
        return prep_type

    @staticmethod
    def _map_to_protocol(
        viral_prep_type_name: Optional[str],
    ) -> Optional[str]:
        """
        Maps tars viral_prep_type to protocol string.

        Parameters
        ----------
        viral_prep_type_name : str | None
            The viral prep type from TARS

        Returns
        -------
        PrepProtocols | None
        """
        match viral_prep_type_name:
            case ViralPrepTypes.CRUDE_MGT1 | ViralPrepTypes.PURIFIED_MGT1:
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
    def _map_plasmid_name(aliases: List[Dict[str, Any]]) -> Optional[str]:
        """
        Maps plasmid name from aliases.

        Parameters
        ----------
        aliases : List[Dict[str, Any]]
            List of alias objects

        Returns
        -------
        str | None
            Preferred plasmid name or None
        """
        for alias in aliases:
            if alias.get("isPreferred"):
                return alias.get("name")
        return None

    @staticmethod
    def _map_stock_titer(titers: Optional[List[Titers]]) -> Optional[int]:
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
        if titers and len(titers) > 0 and titers[0].result is not None:
            return titers[0].result
        return None

    def _map_virus_information(self) -> TarsVirusInformation:
        """
        Maps name, plasmid, and addgene from virus response.

        Returns
        -------
        TarsVirusInformation
            Mapped virus information
        """
        if len(self.virus_data) == 0:
            return TarsVirusInformation()

        first_virus = self.virus_data[0]
        names = []
        plasmid_aliases = []
        addgene_ids = []
        rrids = []
        if first_virus.rr_id is not None:
            rrids.append(first_virus.rr_id)
        virus_molecules: List[Dict[str, Any]] = (
            [] if first_virus.molecules is None else first_virus.molecules
        )
        for molecule in virus_molecules:
            if molecule.get("fullName") is not None:
                names.append(molecule["fullName"])
            plasmid_name = self._map_plasmid_name(molecule.get("aliases", []))
            if plasmid_name:
                plasmid_aliases.append(plasmid_name)
            if molecule.get("addgeneId"):
                addgene_ids.append(molecule["addgeneId"])
            if molecule.get("rrId"):
                rrids.append(molecule.get("rrId"))

        name = "; ".join(names) if names else None
        plasmid_alias = plasmid_aliases if plasmid_aliases else None
        addgene_id = "; ".join(addgene_ids) if addgene_ids else None
        rrid = "; ".join(rrids) if rrids else None

        return TarsVirusInformation(
            name=name,
            plasmid_alias=plasmid_alias,
            addgene_id=addgene_id,
            rrid=rrid,
        )

    @staticmethod
    def _create_addgene_pid_name(
        virus_info: TarsVirusInformation,
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
        if virus_info.name is None:
            return None
        else:
            if virus_info.rrid is None:
                registry = None
            elif "addgene".lower() in virus_info.rrid.lower():
                registry = Registry.ADDGENE
            else:
                registry = virus_info.rrid
            return PIDName(
                name=virus_info.name,
                registry=registry,
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
        viral_prep_type_name = (
            None
            if self.prep_lot_data.viral_prep is None
            or self.prep_lot_data.viral_prep.viral_prep_type is None
            else self.prep_lot_data.viral_prep.viral_prep_type.name
        )
        prep_type = self._map_to_prep_type(
            viral_prep_type_name=viral_prep_type_name
        )
        prep_protocol = self._map_to_protocol(
            viral_prep_type_name=viral_prep_type_name
        )

        virus_info = self._map_virus_information()
        addgene_id_pidname = self._create_addgene_pid_name(virus_info)
        stock_titer = self._map_stock_titer(self.prep_lot_data.titers)
        tars_virus_identifiers = TarsVirusIdentifiers(
            prep_lot_number=prep_lot_number,  # Only required field
            virus_tars_id=self.virus_id,
            plasmid_tars_alias=virus_info.plasmid_alias,
            prep_date=prep_date,
            prep_type=prep_type,
            prep_protocol=prep_protocol,
        )

        try:
            return ViralMaterialInformation(
                name=virus_info.name,
                tars_identifiers=tars_virus_identifiers,
                stock_titer=stock_titer,
                addgene_id=addgene_id_pidname,
            )
        except ValidationError:
            return ViralMaterialInformation.model_construct(
                name=virus_info.name,
                tars_identifiers=tars_virus_identifiers,
                stock_titer=stock_titer,
                addgene_id=addgene_id_pidname,
            )
