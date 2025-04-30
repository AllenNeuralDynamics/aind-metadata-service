"""
Module to handle fetching viral material data from slims
and parsing it to a model.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from networkx import DiGraph, descendants
from pydantic import BaseModel
from slims.criteria import conjunction, equals

from aind_metadata_service.slims.table_handler import (
    SlimsTableHandler,
    get_attr_or_none,
)


class SlimsViralMaterialData(BaseModel):
    """Model for viral material data."""

    content_category: Optional[str] = "Viral Materials"
    content_type: Optional[str] = None
    content_created_on: Optional[datetime] = None
    content_modified_on: Optional[datetime] = None
    viral_solution_type: Optional[str] = None
    virus_name: Optional[str] = None
    lot_number: Optional[str] = None
    lab_team: Optional[str] = None
    virus_type: Optional[str] = None
    virus_serotype: Optional[str] = None
    virus_plasmid_number: Optional[str] = None
    name: Optional[str] = None
    dose: Optional[Decimal] = None
    dose_unit: Optional[str] = None
    titer: Optional[Decimal] = None
    titer_unit: Optional[str] = "GC/ml"
    volume: Optional[Decimal] = None
    volume_unit: Optional[str] = None
    date_made: Optional[datetime] = None
    intake_date: Optional[datetime] = None
    storage_temperature: Optional[str] = None
    special_storage_guidelines: Optional[List[str]] = []
    special_handling_guidelines: Optional[List[str]] = []
    parent_barcode: Optional[str] = None
    parent_name: Optional[str] = None
    derivation_count: Optional[int] = 0
    ingredient_count: Optional[int] = 0


class SlimsViralMaterialHandler(SlimsTableHandler):
    """Class to handle getting Viral Material info from SLIMS."""

    @staticmethod
    def _parse_graph(
        g: DiGraph, root_nodes: List[str]) -> List[SlimsViralMaterialData]:
        """
        Parses the graph object into a list of pydantic models.
        Parameters
        ----------
        g : DiGraph
          Graph of the SLIMS records.
        root_nodes : List[str]
          List of root nodes to pull descendants from.

        Returns
        -------
        List[SlimsSpimData]

        """
        vm_data_list = []
        for node in root_nodes:
            vm_data = SlimsViralMaterialData()
            row = g.nodes[node]["row"]
            node_des = descendants(g, node)
            for n in node_des:
                table_name = g.nodes[n]["table_name"]
                row = g.nodes[n]["row"]
                if table_name == "Content":
                    print(get_attr_or_none(row, "cntn_cf_lotNumber"))
                    vm_data.content_category = get_attr_or_none(row, "cntn_fk_category", "displayValue")
                    vm_data.content_type = get_attr_or_none(row, "cntn_fk_type")
                    vm_data.content_created_on = get_attr_or_none(row, "cntn_createdOn")
                    vm_data.content_modified_on = get_attr_or_none(row, "cntn_modifiedOn")
                    vm_data.viral_solution_type = get_attr_or_none(row, "cntn_cf_fk_viralSolutionType", "displayValue")
                    vm_data.virus_name = get_attr_or_none(row, " cntn_cf_virusName")
                    vm_data.lot_number = get_attr_or_none(row, "cntn_cf_lotNumber")
                    vm_data.lab_team = get_attr_or_none(row, "cntn_cf_fk_labTeam", "displayValue")
                    vm_data.virus_type = get_attr_or_none(row, "cntn_cf_fk_virusType", "displayValue")
                    vm_data.virus_serotype = get_attr_or_none(row, "cntn_cf_fk_virusSerotype", "displayValue")
                    vm_data.virus_plasmid_number = get_attr_or_none(row, "cntn_cf_virusPlasmidNumber")
                    vm_data.name = get_attr_or_none(row, "cntn_id")
                    vm_data.dose = get_attr_or_none(row, "cntn_cf_dose")
                    vm_data.dose_unit = get_attr_or_none(row, "cntn_cf_doseUnit", "unit")
                    vm_data.titer = get_attr_or_none(row, "cntn_cf_titer")
                    vm_data.titer_unit = get_attr_or_none(row, "cntn_cf_titer", "unit")
                    vm_data.volume = get_attr_or_none(row, "cntn_cf_volumeRequired")
                    vm_data.volume_unit = get_attr_or_none(row, "cntn_cf_volumeRequired", "unit")
                    vm_data.date_made = get_attr_or_none(row, "cntn_cf_dateMade")
                    vm_data.intake_date = get_attr_or_none(row, "cntn_cf_intakeDate_NA")
                    vm_data.storage_temperature = get_attr_or_none(row, "cntn_cf_fk_storageTemp_dynChoice", "displayValue")
                    vm_data.special_storage_guidelines = get_attr_or_none(row, "cntn_cf_fk_specialStorageGuidelines", "displayValues")
                    vm_data.special_handling_guidelines = get_attr_or_none(row, "cntn_cf_fk_specialHandlingGuidelines", "displayValues")
                    vm_data.parent_barcode = get_attr_or_none(row, "cntn_cf_parentBarcode")
                    vm_data.parent_name = get_attr_or_none(row, "cntn_cf_parentName")
                    vm_data.derivation_count = get_attr_or_none(row, "cntn_cf_derivationCount")
                    vm_data.ingredient_count = get_attr_or_none(row, "cntn_cf_ingredientCount")
                vm_data_list.append(vm_data)
        return vm_data_list

    def _get_graph(self) -> Tuple[DiGraph, List[str]]:
        """
        Generate a Graph of the records from SLIMS for viral material
        contents.
        Parameters
        ----------

        Returns
        -------
        Tuple[DiGraph, List[str]]
          A directed graph of the SLIMS records and a list of the root nodes.

        """
        content_type_rows = self.client.fetch(
                table="ContentType",
                criteria=equals("cntp_name", "Viral Materials")
            )
        G = DiGraph()
        root_nodes = []
        for row in content_type_rows:
            G.add_node(
                f"{row.table_name()}.{row.pk()}",
                row=row,
                pk=row.pk(),
                table_name=row.table_name(),
            )
            root_nodes.append(f"{row.table_name()}.{row.pk()}")

        _ = self.get_rows_from_foreign_table(
            input_table="ContentType",
            input_rows=content_type_rows,
            input_table_cols=["cntp_pk"],
            foreign_table="Content",
            foreign_table_col="cntn_fk_category",
            graph=G,
        )

        return G, root_nodes

    def get_viral_material_info_from_slims(self) -> List[SlimsViralMaterialData]:
        """
        Get Viral Material data from SLIMS.

        Parameters
        ----------
        prep_lot_number: str | None
          The lot number of the prep to get data for.
        Returns
        -------
        List[SlimsViralMaterialData]

        Raises
        ------
        ValueError
          The subject_id cannot be an empty string.

        """
        G, root_nodes = self._get_graph()
        wr_data = self._parse_graph(g=G, root_nodes=root_nodes)
        return wr_data
