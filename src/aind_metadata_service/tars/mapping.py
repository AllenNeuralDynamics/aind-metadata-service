"""Module to map data in TARS to aind_data_schema InjectionMaterial"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional

from aind_data_schema.core.procedures import (
    Injection,
    TarsVirusIdentifiers,
    ViralMaterial,
    VirusPrepType,
)
from aind_data_schema_models.pid_names import BaseName, PIDName
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import ViralMaterialInformation
from aind_metadata_service.response_handler import ModelResponse


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


@dataclass
class TarsVirusInformation:
    """Dataclass to store virus information"""

    name: Optional[str]
    plasmid_alias: Optional[str]
    addgene_id: Optional[str]
    rrid: Optional[str]


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
    def map_plasmid_name(aliases: List[Dict]) -> Optional[str]:
        """Maps plasmid name from aliases"""
        return next(
            (
                alias.get("name")
                for alias in aliases
                if alias.get("isPreferred")
            ),
            None,
        )

    @staticmethod
    def map_stock_titer(titers: List[dict]) -> Optional[int]:
        """Maps titer from viral prep lot"""
        if titers and titers[0].get("result") is not None:
            return int(titers[0]["result"])
        return None

    def map_info_from_virus_response(
        self, virus: dict
    ) -> TarsVirusInformation:
        """Maps name, plasmid, and addgene from virus response"""
        names = []
        plasmid_aliases = []
        addgene_ids = []
        rrids = []
        for molecule in virus.get("molecules", []):
            if molecule.get("fullName"):
                names.append(molecule["fullName"])
            plasmid_name = self.map_plasmid_name(molecule.get("aliases", []))
            if plasmid_name:
                plasmid_aliases.append(plasmid_name)
            if molecule.get("addgeneId"):
                addgene_ids.append(molecule["addgeneId"])
            if molecule.get("rrId"):
                rrids.append(molecule["rrId"])
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

    def map_lot_to_injection_material(
        self, viral_prep_lot: dict, virus: dict, virus_tars_id: str
    ) -> ViralMaterial:
        """
        Map prep lot dictionary to injection materials
        Parameters
        ----------
        viral_prep_lot: dict
            Dictionary of raw viral prep lot data from TARS response.
        virus: dict
            Dictionary of raw virus data from TARS response.
        """
        prep_lot_number = viral_prep_lot.get("lot")
        prep_date = self._convert_datetime(
            viral_prep_lot.get("datePrepped", "")
        )
        prep_type, prep_protocol = self._map_prep_type_and_protocol(
            viral_prep_lot.get("viralPrep", {})
            .get("viralPrepType", {})
            .get("name", "")
        )
        virus_info = self.map_info_from_virus_response(virus)
        addgene_id = None
        if virus_info.addgene_id:
            addgene_id = PIDName(
                name=virus_info.name,
                registry=(
                    BaseName(name=virus_info.rrid) if virus_info.rrid else None
                ),
                registry_identifier=virus_info.addgene_id,
            )
        try:
            tars_virus_identifiers = TarsVirusIdentifiers(
                virus_tars_id=virus_tars_id,
                plasmid_tars_alias=virus_info.plasmid_alias,
                prep_lot_number=prep_lot_number,
                prep_date=prep_date,
                prep_type=prep_type,
                prep_protocol=prep_protocol,
            )
            return ViralMaterialInformation(
                name=virus_info.name,
                tars_identifiers=tars_virus_identifiers,
                stock_titer=self.map_stock_titer(
                    viral_prep_lot.get("titers", None)
                ),
                addgene_id=addgene_id,
            )
        except ValidationError:
            tars_virus_identifiers = TarsVirusIdentifiers.model_construct(
                virus_tars_id=virus_tars_id,
                plasmid_tars_alias=virus_info.plasmid_alias,
                prep_lot_number=prep_lot_number,
                prep_date=prep_date,
                prep_type=prep_type,
                prep_protocol=prep_protocol,
            )
            return ViralMaterialInformation.model_construct(
                name=virus_info.name,
                tars_identifiers=tars_virus_identifiers,
                stock_titer=self.map_stock_titer(
                    viral_prep_lot.get("titers", None)
                ),
                addgene_id=addgene_id,
            )

    @staticmethod
    def get_virus_strains(response: ModelResponse) -> List:
        """
        Iterates through procedures response and creates list of
        virus strains.
        Parameters
        ---------
        response : ModelResponse
        """
        viruses = []
        if len(response.aind_models) > 0:
            procedures = response.aind_models[0]
            for subject_procedure in procedures.subject_procedures:
                if not hasattr(subject_procedure, "procedures"):
                    continue
                for procedure in subject_procedure.procedures:
                    if (
                        isinstance(procedure, Injection)
                        and hasattr(procedure, "injection_materials")
                        and isinstance(procedure.injection_materials, list)
                        and procedure.injection_materials
                    ):
                        virus_strains = [
                            getattr(material, "name").strip()
                            for material in procedure.injection_materials
                            if getattr(material, "name", None)
                        ]
                        viruses.extend(virus_strains)
        return viruses

    # TODO: Refactor this method
    @staticmethod
    def integrate_injection_materials(  # noqa: C901
        response: ModelResponse, tars_mapping: Dict[str, JSONResponse]
    ) -> ModelResponse:
        """
        Merges tars_response with procedures_response.
        Parameters
        ----------
        """
        output_aind_models = []
        status_code = response.status_code
        if len(response.aind_models) > 0:
            pre_procedures = response.aind_models[0]
            for subject_procedure in pre_procedures.subject_procedures:
                if not hasattr(subject_procedure, "procedures"):
                    output_aind_models = [pre_procedures]
                    continue
                for procedure in subject_procedure.procedures:
                    if isinstance(procedure, Injection) and hasattr(
                        procedure, "injection_materials"
                    ):
                        for idx, injection_material in enumerate(
                            procedure.injection_materials
                        ):
                            if isinstance(
                                injection_material, ViralMaterial
                            ) and getattr(injection_material, "name", None):
                                virus_strain = injection_material.name.strip()
                                tars_response = tars_mapping.get(virus_strain)
                                if (
                                    tars_response
                                    and tars_response.status_code
                                    == StatusCodes.DB_RESPONDED.value
                                    or tars_response.status_code
                                    == StatusCodes.VALID_DATA.value
                                    or tars_response.status_code
                                    == StatusCodes.INVALID_DATA.value
                                ):
                                    data = json.loads(tars_response.body)[
                                        "data"
                                    ]
                                    try:
                                        data.pop(
                                            "stock_titer", None
                                        )  # Remove extra field
                                        new_material = ViralMaterial(**data)
                                        new_material.titer = (
                                            injection_material.titer
                                        )
                                    except ValidationError as e:
                                        logging.error(f"{e}")
                                        new_material = (
                                            ViralMaterial.model_construct(
                                                **data
                                            )
                                        )
                                        new_material.titer = (
                                            injection_material.titer
                                        )
                                    procedure.injection_materials[idx] = (
                                        new_material
                                    )
                                elif (
                                    tars_response.status_code
                                    == StatusCodes.NO_DATA_FOUND.value
                                ):
                                    pass
                                else:
                                    status_code = StatusCodes.MULTI_STATUS
                output_aind_models = [pre_procedures]
        return ModelResponse(
            aind_models=output_aind_models, status_code=status_code
        )
