"""
Module to handle fetching histology data from slims and parsing it to a model
"""

from datetime import datetime
from typing import List, Optional, Tuple

from networkx import DiGraph
from pydantic import BaseModel
from slims.criteria import is_one_of
from slims.internal import Record

from aind_metadata_service.slims.table_handler import (
    SlimsTableHandler,
    get_attr_or_none,
)


class SlimsReagentData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    name: Optional[str] = None
    source: Optional[str] = None
    lot_number: Optional[str] = None


class SlimsWashData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    wash_name: Optional[str] = None
    wash_type: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    modified_by: Optional[str] = None
    reagents: List[SlimsReagentData] = []
    mass: Optional[float] = None


class SlimsHistologyData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    procedure_name: Optional[str] = None
    experiment_run_created_on: Optional[int] = None
    specimen_id: Optional[str] = None
    subject_id: Optional[str] = None
    protocol_id: Optional[str] = None
    protocol_name: Optional[str] = None
    washes: List[SlimsWashData] = []


class SlimsHistologyHandler(SlimsTableHandler):
    """Class to handle getting SPIM Histology Procedures info from SLIMS."""

    @staticmethod
    def _get_reagent_data(records: List[Record]) -> List[SlimsReagentData]:
        """
        Get reagent data from records
        Parameters
        ----------
        records : List[Record]

        Returns
        -------
        List[SlimsReagentData]

        """

        reagents = []

        for record in records:
            if record.table_name() == "Content" and get_attr_or_none(
                record, "cntn_fk_category", "displayValue"
            ) in [
                "Reagents, Externally Manufactured",
                "Reagents, Internally Produced",
            ]:
                n_reagent_lot_number = get_attr_or_none(
                    record, "cntn_cf_lotNumber"
                )
                n_reagent_name = get_attr_or_none(
                    record, "cntn_cf_fk_reagentCatalogNumber", "displayValue"
                )
                n_reagent_source = get_attr_or_none(
                    record, "cntn_fk_source", "displayValue"
                )
                reagent_data = SlimsReagentData(
                    name=n_reagent_name,
                    source=n_reagent_source,
                    lot_number=n_reagent_lot_number,
                )
                reagents.append(reagent_data)
        return reagents

    def _get_wash_data(
        self, g: DiGraph, exp_run_step: str, exp_run_step_row: Record
    ) -> SlimsWashData:
        """
        Get wash data from SLIMS records.
        Parameters
        ----------
        g : DiGraph
        exp_run_step : str
          Name of the node for the experiment run step
        exp_run_step_row : Record
          The Record attached to the node.

        Returns
        -------
        SlimsWashData

        """
        wash_data = SlimsWashData()
        wash_data.wash_name = get_attr_or_none(exp_run_step_row, "xprs_name")
        wash_data.wash_type = get_attr_or_none(
            exp_run_step_row, "xprs_cf_spimWashType"
        )
        wash_data.start_time = get_attr_or_none(
            exp_run_step_row, "xprs_cf_startTime"
        )
        wash_data.end_time = get_attr_or_none(
            exp_run_step_row, "xprs_cf_endTime"
        )
        wash_data.modified_by = get_attr_or_none(
            exp_run_step_row, "xprs_modifiedBy"
        )
        wash_data.mass = get_attr_or_none(exp_run_step_row, "xprs_cf_mass")
        wash_data_successors = g.successors(exp_run_step)
        records = [g.nodes[n]["row"] for n in wash_data_successors]
        reagents = self._get_reagent_data(records)
        wash_data.reagents = reagents
        return wash_data

    @staticmethod
    def _get_specimen_data(
        g: DiGraph, exp_run_step_content: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get subject_id and specimen_id from Content record.
        Parameters
        ----------
        g : DiGraph
        exp_run_step_content : str
          Name of the node for the experiment run step content

        Returns
        -------
        tuple
          (subject_id, specimen_id)

        """
        content_nodes = g.successors(exp_run_step_content)
        records = [g.nodes[c]["row"] for c in content_nodes]
        specimen_id = None
        subject_id = None
        for record in records:
            n_subject_id = get_attr_or_none(record, "cntn_id")
            if n_subject_id is not None:
                subject_id = n_subject_id
            n_specimen_id = get_attr_or_none(record, "cntn_barCode")
            if n_specimen_id is not None:
                specimen_id = n_specimen_id
        return subject_id, specimen_id

    def _parse_graph(
        self, g: DiGraph, root_nodes: List[str], subject_id: Optional[str]
    ) -> List[SlimsHistologyData]:
        """
        Parses the graph object into a list of pydantic models.
        Parameters
        ----------
        g : DiGraph
          Graph of the SLIMS records.
        root_nodes : List[str]
          List of root nodes to pull descendants from.
        subject_id : str | None
          Labtracks ID of mouse to filter records by.

        Returns
        -------
        List[SlimsHistologyData]
        """

        histology_data_list = []
        for node in root_nodes:
            histology_data = SlimsHistologyData()
            washes = []
            exp_run_created_on = get_attr_or_none(
                g.nodes[node]["row"], "xprn_createdOn"
            )
            histology_data.experiment_run_created_on = exp_run_created_on
            exp_run_name = get_attr_or_none(g.nodes[node]["row"], "xptm_name")
            histology_data.procedure_name = exp_run_name

            exp_run_steps = g.successors(node)

            for exp_run_step in exp_run_steps:
                exp_run_step_row = g.nodes[exp_run_step]["row"]
                exp_run_step_name = get_attr_or_none(
                    exp_run_step_row, "xprs_name"
                )
                if exp_run_step_name in [
                    "Wash 1",
                    "Wash 2",
                    "Wash 3",
                    "Wash 4",
                    "Refractive Index Matching Wash",
                    "Primary Antibody Wash",
                    "Secondary Antibody Wash",
                    "MBS Wash",
                    "Gelation PBS Wash",
                    "Stock X + VA-044 Equilibration",
                    "Gelation + ProK RT",
                    "Gelation + Add'l ProK 37C",
                    "Final PBS Wash",
                ]:
                    wash_data = self._get_wash_data(
                        g,
                        exp_run_step=exp_run_step,
                        exp_run_step_row=exp_run_step_row,
                    )
                    washes.append(wash_data)

                exp_run_step_children = g.successors(exp_run_step)
                for exp_run_step_child in exp_run_step_children:
                    table_name = g.nodes[exp_run_step_child]["table_name"]
                    row = g.nodes[exp_run_step_child]["row"]
                    if table_name == "SOP":
                        stop_link = get_attr_or_none(row, "stop_link")
                        stop_name = get_attr_or_none(row, "stop_name")
                        histology_data.protocol_id = stop_link
                        histology_data.protocol_name = stop_name
                    if table_name == "ExperimentRunStepContent":
                        n_subject_id, n_specimen_id = self._get_specimen_data(
                            g=g, exp_run_step_content=exp_run_step_child
                        )
                        if n_subject_id is not None:
                            histology_data.subject_id = n_subject_id
                        if n_specimen_id is not None:
                            histology_data.specimen_id = n_specimen_id
            histology_data.washes = washes
            if subject_id is None or subject_id == histology_data.subject_id:
                histology_data_list.append(histology_data)
        return histology_data_list

    def _get_graph(
        self,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> Tuple[DiGraph, List[str]]:
        """
        Generate a Graph of the records from SLIMS for histology.

        Parameters
        ----------
        start_date_greater_than_or_equal : datetime | None
          Filter experiment runs that were created on or after this datetime.
        end_date_less_than_or_equal : datetime | None
          Filter experiment runs that were created on or before this datetime.

        Returns
        -------
        Tuple[DiGraph, List[str]]
          A directed graph of the SLIMS records and a list of the root nodes.

        """
        experiment_template_rows = self.client.fetch(
            table="ExperimentTemplate",
            criteria=is_one_of(
                "xptm_name",
                [
                    "SmartSPIM Labeling",
                    "SmartSPIM Delipidation",
                    "SmartSPIM Refractive Index Matching",
                ],
            ),
        )
        date_criteria = self._get_date_criteria(
            start_date=start_date_greater_than_or_equal,
            end_date=end_date_less_than_or_equal,
            field_name="xprn_createdOn",
        )
        exp_run_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentTemplate",
            input_rows=experiment_template_rows,
            input_table_cols=["xptm_pk"],
            foreign_table="ExperimentRun",
            foreign_table_col="xprn_fk_experimentTemplate",
            extra_criteria=date_criteria,
        )
        G = DiGraph()
        root_nodes = []
        for row in exp_run_rows:
            G.add_node(
                f"{row.table_name()}.{row.pk()}",
                row=row,
                pk=row.pk(),
                table_name=row.table_name(),
            )
            root_nodes.append(f"{row.table_name()}.{row.pk()}")

        exp_run_step_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRun",
            input_rows=exp_run_rows,
            input_table_cols=["xprn_pk"],
            foreign_table="ExperimentRunStep",
            foreign_table_col="xprs_fk_experimentRun",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_cf_fk_protocol"],
            foreign_table="SOP",
            foreign_table_col="stop_pk",
            graph=G,
        )
        exp_run_step_content_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_pk"],
            foreign_table="ExperimentRunStepContent",
            foreign_table_col="xrsc_fk_experimentRunStep",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStepContent",
            input_rows=exp_run_step_content_rows,
            input_table_cols=["xrsc_fk_content"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )
        reagent_content_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_cf_fk_reagent"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="Content",
            input_rows=reagent_content_rows,
            input_table_cols=["cntn_cf_fk_reagentCatalogNumber"],
            foreign_table="ReferenceDataRecord",
            foreign_table_col="rdrc_pk",
            graph=G,
        )
        return G, root_nodes

    def get_hist_data_from_slims(
        self,
        subject_id: Optional[str] = None,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> List[SlimsHistologyData]:
        """
        Get Histology data from SLIMS.

        Parameters
        ----------
        subject_id : str | None
          Labtracks ID of mouse. If None, then no filter will be performed.
        start_date_greater_than_or_equal : datetime | None
          Filter experiment runs that were created on or after this datetime.
        end_date_less_than_or_equal : datetime | None
          Filter experiment runs that were created on or before this datetime.


        Returns
        -------
        List[SlimsHistologyData]

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
        hist_data = self._parse_graph(
            g=G, root_nodes=root_nodes, subject_id=subject_id
        )

        return hist_data
