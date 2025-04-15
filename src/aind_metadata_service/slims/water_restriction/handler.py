"""
Module to handle fetching water restriction data from slims
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


class SlimsWaterRestrictionData(BaseModel):
    """Model for water restriction data."""

    content_event_created_on: Optional[int] = None
    subject_id: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    assigned_by: Optional[str] = None
    target_weight_fraction: Optional[Decimal] = None
    baseline_weight: Optional[Decimal] = None
    weight_unit: Optional[str] = None


class SlimsWaterRestrictionHandler(SlimsTableHandler):
    """Class to handle getting Water Restriction info from SLIMS."""

    @staticmethod
    def _parse_graph(
        g: DiGraph, root_nodes: List[str], subject_id: Optional[str] = None
    ) -> List[SlimsWaterRestrictionData]:
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
        wr_data_list = []
        for node in root_nodes:
            wr_data = SlimsWaterRestrictionData()
            row = g.nodes[node]["row"]
            wr_data.content_event_created_on = get_attr_or_none(
                row, "cnvn_createdOn"
            )
            wr_data.start_date = get_attr_or_none(row, "cnvn_cf_startDate")
            wr_data.end_date = get_attr_or_none(row, "cnvn_cf_endDate")
            wr_data.assigned_by = get_attr_or_none(row, "cnvn_cf_assignedBy")
            target_weight_fraction = get_attr_or_none(
                row, "cnvn_cf_targetWeightFraction"
            )
            wr_data.target_weight_fraction = (
                None
                if target_weight_fraction is None
                else Decimal(str(target_weight_fraction))
            )
            node_des = descendants(g, node)
            for n in node_des:
                table_name = g.nodes[n]["table_name"]
                row = g.nodes[n]["row"]
                if table_name == "Content":
                    wr_data.subject_id = get_attr_or_none(row, "cntn_barCode")
                    baseline_weight = get_attr_or_none(
                        row, "cntn_cf_baselineWeight"
                    )
                    wr_data.baseline_weight = (
                        None
                        if baseline_weight is None
                        else Decimal(str(baseline_weight))
                    )
                    wr_data.weight_unit = get_attr_or_none(
                        row, "cntn_cf_baselineWeight", "unit"
                    )
            if subject_id is None or subject_id == wr_data.subject_id:
                wr_data_list.append(wr_data)
        return wr_data_list

    def _get_graph(
        self,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> Tuple[DiGraph, List[str]]:
        """
        Generate a Graph of the records from SLIMS for water restriction
        content events.
        Parameters
        ----------
        start_date_greater_than_or_equal : datetime | None
          Filter content events that were created on or after this datetime.
        end_date_less_than_or_equal : datetime | None
          Filter content events that were created on or before this datetime.

        Returns
        -------
        Tuple[DiGraph, List[str]]
          A directed graph of the SLIMS records and a list of the root nodes.

        """
        date_criteria = self._get_date_criteria(
            start_date=start_date_greater_than_or_equal,
            end_date=end_date_less_than_or_equal,
            field_name="cnvn_createdOn",
        )
        if date_criteria:
            content_event_rows = self.client.fetch(
                table="ContentEvent",
                criteria=conjunction()
                .add(equals("cnvt_name", "Water Restriction"))
                .add(date_criteria),
            )
        else:
            content_event_rows = self.client.fetch(
                table="ContentEvent",
                criteria=equals("cnvt_name", "Water Restriction"),
            )
        G = DiGraph()
        root_nodes = []
        for row in content_event_rows:
            G.add_node(
                f"{row.table_name()}.{row.pk()}",
                row=row,
                pk=row.pk(),
                table_name=row.table_name(),
            )
            root_nodes.append(f"{row.table_name()}.{row.pk()}")

        _ = self.get_rows_from_foreign_table(
            input_table="ContentEvent",
            input_rows=content_event_rows,
            input_table_cols=["cnvn_fk_content"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )

        return G, root_nodes

    def get_water_restriction_data_from_slims(
        self,
        subject_id: Optional[str] = None,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> List[SlimsWaterRestrictionData]:
        """
        Get Water Restriction data from SLIMS.

        Parameters
        ----------
        subject_id : str | None
          Labtracks ID of mouse.
        start_date_greater_than_or_equal : datetime | None
          Filter content events that were created on or after this datetime.
        end_date_less_than_or_equal : datetime | None
          Filter content events that were created on or before this datetime.
        Returns
        -------
        List[SlimsSlimsWaterRestrictionDataimData]

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
        wr_data = self._parse_graph(
            g=G, root_nodes=root_nodes, subject_id=subject_id
        )
        return wr_data
