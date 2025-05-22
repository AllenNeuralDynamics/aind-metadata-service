"""
Module to handle fetching viral injection data from slims
and parsing it to a model.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from networkx import DiGraph, descendants
from pydantic import BaseModel
from slims.criteria import equals

from aind_metadata_service.slims.table_handler import (
    SlimsTableHandler,
    get_attr_or_none,
)


class SlimsViralMaterialData(BaseModel):
    """Model for viral material data."""

    content_category: Optional[str] = "Viral Materials"
    content_type: Optional[str] = None
    content_created_on: Optional[int] = None
    content_modified_on: Optional[int] = None
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
    date_made: Optional[int] = None
    intake_date: Optional[int] = None
    storage_temperature: Optional[str] = None
    special_storage_guidelines: Optional[List[str]] = []
    special_handling_guidelines: Optional[List[str]] = []
    parent_name: Optional[str] = None
    mix_count: Optional[int] = None
    derivation_count: Optional[int] = None
    ingredient_count: Optional[int] = None


class SlimsViralInjectionData(BaseModel):
    """ "Model for viral injection data."""

    content_category: Optional[str] = "Viral Materials"
    content_type: Optional[str] = "Viral Injection"
    content_created_on: Optional[int] = None
    content_modified_on: Optional[int] = None
    name: Optional[str] = None
    viral_injection_buffer: Optional[str] = None
    volume: Optional[Decimal] = None
    volume_unit: Optional[str] = None
    labeling_protein: Optional[str] = None
    date_made: Optional[int] = None
    intake_date: Optional[int] = None
    storage_temperature: Optional[str] = None
    special_storage_guidelines: Optional[List[str]] = []
    special_handling_guidelines: Optional[List[str]] = []
    mix_count: Optional[int] = None
    derivation_count: Optional[int] = None
    ingredient_count: Optional[int] = None

    # From ORDER table
    assigned_mice: Optional[List[str]] = []
    requested_for_date: Optional[int] = None
    planned_injection_date: Optional[int] = None
    planned_injection_time: Optional[int] = None
    order_created_on: Optional[int] = None

    viral_materials: Optional[List[SlimsViralMaterialData]] = []


class SlimsViralInjectionHandler(SlimsTableHandler):
    """Class to handle getting Viral Injection info from SLIMS."""

    @staticmethod
    def _parse_graph(
        g: DiGraph, root_nodes: List[str], subject_id: Optional[str]
    ) -> List[SlimsViralInjectionData]:
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
        List[SlimsViralInjectionData]

        """
        vi_data_list = []
        for node in root_nodes:
            vi_data = SlimsViralInjectionData()
            node_des = descendants(g, node)
            root_row = g.nodes[node]["row"]
            vi_data.content_created_on = get_attr_or_none(
                root_row, "cntn_createdOn"
            )
            vi_data.content_category = get_attr_or_none(
                root_row, "cntn_fk_category", "displayValue"
            )
            vi_data.content_type = get_attr_or_none(
                root_row, "cntn_fk_contentType", "displayValue"
            )
            vi_data.content_created_on = get_attr_or_none(
                root_row, "cntn_createdOn"
            )
            vi_data.content_modified_on = get_attr_or_none(
                root_row, "cntn_modifiedOn"
            )
            vi_data.viral_injection_buffer = get_attr_or_none(
                root_row, "cntn_cf_fk_viralInjectionBuffer", "displayValue"
            )
            volume = get_attr_or_none(root_row, "cntn_cf_volumeRequired")
            vi_data.volume = None if volume is None else Decimal(str(volume))
            vi_data.volume_unit = get_attr_or_none(
                root_row, "cntn_cf_volumeRequired", "unit"
            )
            vi_data.labeling_protein = get_attr_or_none(
                root_row,
                "cntn_cf_fk_viralInjectionFluorescentLabelingP",
                "displayValue",
            )
            vi_data.name = get_attr_or_none(root_row, "cntn_id")
            vi_data.date_made = get_attr_or_none(root_row, "cntn_cf_dateMade")
            vi_data.intake_date = get_attr_or_none(
                root_row, "cntn_cf_intakeDate_NA"
            )
            vi_data.storage_temperature = get_attr_or_none(
                root_row, "cntn_cf_fk_storageTemp_dynChoice", "displayValue"
            )
            vi_data.special_storage_guidelines = get_attr_or_none(
                root_row,
                "cntn_cf_fk_specialStorageGuidelines",
                "displayValues",
            )
            vi_data.special_handling_guidelines = get_attr_or_none(
                root_row,
                "cntn_cf_fk_specialHandlingGuidelines",
                "displayValues",
            )
            for n in node_des:
                table_name = g.nodes[n]["table_name"]
                row = g.nodes[n]["row"]
                if table_name == "Order":
                    vi_data.assigned_mice = get_attr_or_none(
                        row, "ordr_cf_fk_assignedMice", "displayValues"
                    )
                    vi_data.requested_for_date = get_attr_or_none(
                        row, "ordr_cf_requestedForDate"
                    )
                    vi_data.planned_injection_date = get_attr_or_none(
                        row, "ordr_plannedOnDate"
                    )
                    vi_data.planned_injection_time = get_attr_or_none(
                        row, "ordr_plannedOnTime"
                    )
                    vi_data.order_created_on = get_attr_or_none(
                        row, "ordr_createdOn"
                    )
                    vi_data.derivation_count = get_attr_or_none(
                        row, "derivedCount"
                    )
                    vi_data.ingredient_count = get_attr_or_none(
                        row, "ingredientCount"
                    )
                    vi_data.mix_count = get_attr_or_none(row, "mixCount")
                if (
                    table_name == "Content"
                    and get_attr_or_none(
                        row, "cntn_fk_contentType", "displayValue"
                    )
                    == "Viral solution"
                ):
                    vm_data = SlimsViralMaterialData()
                    vm_data.content_category = get_attr_or_none(
                        row, "cntn_fk_category", "displayValue"
                    )
                    vm_data.content_type = get_attr_or_none(
                        row, "cntn_fk_contentType", "displayValue"
                    )
                    vm_data.content_created_on = get_attr_or_none(
                        row, "cntn_createdOn"
                    )
                    vm_data.content_modified_on = get_attr_or_none(
                        row, "cntn_modifiedOn"
                    )
                    vm_data.viral_solution_type = get_attr_or_none(
                        row, "cntn_cf_fk_viralSolutionType", "displayValue"
                    )
                    vm_data.virus_name = get_attr_or_none(
                        row, "cntn_cf_virusName"
                    )
                    vm_data.lot_number = get_attr_or_none(
                        row, "cntn_cf_lotNumber"
                    )
                    vm_data.lab_team = get_attr_or_none(
                        row, "cntn_cf_fk_labTeam", "displayValue"
                    )
                    vm_data.virus_type = get_attr_or_none(
                        row, "cntn_cf_fk_virusType", "displayValue"
                    )
                    vm_data.virus_serotype = get_attr_or_none(
                        row, "cntn_cf_fk_virusSerotype", "displayValue"
                    )
                    vm_data.virus_plasmid_number = get_attr_or_none(
                        row, "cntn_cf_virusPlasmidNumber"
                    )
                    vm_data.name = get_attr_or_none(row, "cntn_id")
                    dose = get_attr_or_none(row, "cntn_cf_dose")
                    vm_data.dose = None if dose is None else Decimal(str(dose))
                    vm_data.dose_unit = get_attr_or_none(
                        row, "cntn_cf_doseUnit", "unit"
                    )
                    titer = get_attr_or_none(row, "cntn_cf_titer")
                    vm_data.titer = (
                        None if titer is None else Decimal(str(titer))
                    )
                    vm_data.titer_unit = get_attr_or_none(
                        row, "cntn_cf_titer", "unit"
                    )
                    volume = get_attr_or_none(row, "cntn_cf_volumeRequired")
                    vm_data.volume = (
                        None if volume is None else Decimal(str(volume))
                    )
                    vm_data.volume_unit = get_attr_or_none(
                        row, "cntn_cf_volumeRequired", "unit"
                    )
                    vm_data.date_made = get_attr_or_none(
                        row, "cntn_cf_dateMade"
                    )
                    vm_data.intake_date = get_attr_or_none(
                        row, "cntn_cf_intakeDate_NA"
                    )
                    vm_data.storage_temperature = get_attr_or_none(
                        row, "cntn_cf_fk_storageTemp_dynChoice", "displayValue"
                    )
                    vm_data.special_storage_guidelines = get_attr_or_none(
                        row,
                        "cntn_cf_fk_specialStorageGuidelines",
                        "displayValues",
                    )
                    vm_data.special_handling_guidelines = get_attr_or_none(
                        row,
                        "cntn_cf_fk_specialHandlingGuidelines",
                        "displayValues",
                    )
                    vm_data.derivation_count = get_attr_or_none(
                        row, "derivedCount"
                    )
                    vm_data.ingredient_count = get_attr_or_none(
                        row, "ingredientCount"
                    )
                    vm_data.mix_count = get_attr_or_none(row, "mixCount")
                    vi_data.viral_materials.append(vm_data)
            if subject_id is None or subject_id in vi_data.assigned_mice:
                vi_data_list.append(vi_data)
        return vi_data_list

    def _get_graph(
        self,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> Tuple[DiGraph, List[str]]:
        """
        Generate a Graph of the records from SLIMS for viral injection
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
            criteria=equals("cntp_name", "Viral Injection"),
        )
        date_criteria = self._get_date_criteria(
            start_date=start_date_greater_than_or_equal,
            end_date=end_date_less_than_or_equal,
            field_name="cntn_createdOn",
        )
        viral_injection_content_rows = self.get_rows_from_foreign_table(
            input_table="ContentType",
            input_rows=content_type_rows,
            input_table_cols=["cntp_pk"],
            foreign_table="Content",
            foreign_table_col="cntn_fk_contentType",
            extra_criteria=date_criteria,
        )
        G = DiGraph()
        root_nodes = []
        for row in viral_injection_content_rows:
            G.add_node(
                f"{row.table_name()}.{row.pk()}",
                row=row,
                pk=row.pk(),
                table_name=row.table_name(),
            )
            root_nodes.append(f"{row.table_name()}.{row.pk()}")

        # content relation: viral injection -> viral materials
        content_relation_rows = self.get_rows_from_foreign_table(
            input_table="Content",
            input_rows=viral_injection_content_rows,
            input_table_cols=["cntn_pk"],
            foreign_table="ContentRelation",
            foreign_table_col="corl_fk_to",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="ContentRelation",
            input_rows=content_relation_rows,
            input_table_cols=["corl_fk_from"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="Content",
            input_rows=viral_injection_content_rows,
            input_table_cols=["cntn_pk"],
            foreign_table="Order",
            foreign_table_col="ordr_cf_fk_viralInjection",
            graph=G,
        )

        return G, root_nodes

    def get_viral_injection_info_from_slims(
        self,
        subject_id: Optional[str] = None,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> List[SlimsViralInjectionData]:
        """
        Get Viral injection data from SLIMS.

        Parameters
        ----------
        prep_lot_number: str | None
          The lot number of the prep to get data for.
        Returns
        -------
        List[SlimsViralInjectionData]

        Raises
        ------
        ValueError
          The subject_id cannot be an empty string.

        """
        if subject_id is not None and len(subject_id) == 0:
            raise ValueError("subject_id must not be empty!")

        G, root_nodes = self._get_graph(
            start_date_greater_than_or_equal=start_date_greater_than_or_equal,
            end_date_less_than_or_equal=end_date_less_than_or_equal,
        )
        vm_data = self._parse_graph(
            g=G, root_nodes=root_nodes, subject_id=subject_id
        )
        return vm_data
