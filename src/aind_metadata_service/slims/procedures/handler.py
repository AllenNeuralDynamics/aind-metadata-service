"""
Module to handle fetching histology data from slims and parsing it to a model
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from networkx import DiGraph, descendants
from pydantic import BaseModel
from slims.criteria import equals, is_one_of

from aind_metadata_service.slims.table_handler import (
    SlimsTableHandler,
    get_attr_or_none,
)
import matplotlib.pyplot as plt
import networkx as nx

class SlimsReagentData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""
    name: Optional[str] = None
    source: Optional[str] = None
    lot_number: Optional[str] = None

class SlimsWashData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""
    wash_name: Optional[str] = None
    wash_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    modified_by: Optional[str] = None
    reagents: Optional[List[SlimsReagentData]] = None

class SlimsHistologyData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    experiment_run_created_on: Optional[int] = None
    specimen_id: Optional[str] = None
    subject_id: Optional[str] = None
    protocol_id: Optional[str] = None
    protocol_name: Optional[str] = None
    washes: Optional[List[SlimsWashData]] = None

class SlimsHistologyHandler(SlimsTableHandler):
    """Class to handle getting SPIM Histology Procedures info from SLIMS."""

    @staticmethod
    def _parse_graph(
        g: DiGraph, root_nodes: List[str], subject_id: str
    ) -> List[SlimsHistologyData]:
        """
        Parses the graph object into a list of pydantic models.
        Parameters
        ----------
        g : DiGraph
          Graph of the SLIMS records.
        root_nodes : List[str]
          List of root nodes to pull descendants from.
        subject_id : Optional[str]
          Labtracks ID of mouse to filter records by.

        Returns
        -------
        List[SlimsHistologyData]
        """

        histology_data_list = []
        for node in root_nodes:
            histology_data = SlimsHistologyData()
            node_des = descendants(g, node)
            exp_run_created_on = get_attr_or_none(
                g.nodes[node]["row"], "xprn_createdOn"
            )
            histology_data.experiment_run_created_on = exp_run_created_on # might not need this 
            for n in node_des:
                table_name = g.nodes[n]["table_name"]
                row = g.nodes[n]["row"]
                if table_name == "SOP":
                    stop_link = get_attr_or_none(row, "stop_link")
                    stop_name = get_attr_or_none(row, "stop_name")
                    histology_data.protocol_id = stop_link # protocol link
                    histology_data.protocol_name = stop_name # procedure name
                if (
                    table_name == "Content"
                    and get_attr_or_none(
                        row, "cntn_fk_category", "displayValue"
                    )
                    == "Samples"
                    ):
                    n_specimen_id = get_attr_or_none(row, "cntn_barCode")
                    n_subject_id = get_attr_or_none(row, "cntn_cf_parentBarcode")
                    histology_data.specimen_id = n_specimen_id
                    histology_data.subject_id = n_subject_id
                if (
                    table_name == "ExperimentRunStep"
                    and get_attr_or_none(
                        row, "xprs_name"
                    ) in [
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
                        ]
                ):
                    # TODO: check prod field names
                    wash_data = SlimsWashData()
                    wash_data.wash_name = get_attr_or_none(row, "xprs_name")
                    wash_data.wash_type = get_attr_or_none(row, "xprs_cf_spimWashType")
                    wash_data.start_time = get_attr_or_none(row, "xprs_cf_startTime")
                    wash_data.end_time = get_attr_or_none(row, "xprs_cf_endTime")
                    wash_data.modified_by = get_attr_or_none(row, "xprs_modifiedBy")
                    reagents = []
                    for c in descendants(g, n):
                        table_name = g.nodes[c]["table_name"]
                        crow = g.nodes[c]["row"]
                        if (
                            table_name == "Content"
                            and get_attr_or_none(
                                crow, "cntn_fk_category", "displayValue"
                            ) in ["Reagents, Externally Manufactured", "Reagents, Internally Produced"]
                        ):
                            n_reagent_lot_number = get_attr_or_none(crow, "cntn_cf_lotNumber")
                            # TODO: check if name and source can be retrieved from display values properly
                            n_reagent_name = get_attr_or_none(crow, "cntn_cf_fk_reagentCatalogNumber", "displayValue")
                            n_reagent_source = get_attr_or_none(crow, "cntn_fk_source", "displayValue")
                            reagent_data = SlimsReagentData(
                                name=n_reagent_name,
                                source=n_reagent_source,
                                lot_number=n_reagent_lot_number,
                            )
                            reagents.append(reagent_data)
                    wash_data.reagents = reagents if reagents else None

                    if histology_data.washes is None:
                        histology_data.washes = []
                    histology_data.washes.append(wash_data)
            
            if subject_id is None or subject_id == histology_data.subject_id:
                histology_data_list.append(histology_data)
            
        return histology_data_list

                

    def _get_graph(self) -> Tuple[DiGraph, List[str]]:
        """
        Generate a Graph of the records from SLIMS for imaging experiment runs.
        Returns
        -------
        Tuple[DiGraph, List[str]]
          A directed graph of the SLIMS records and a list of the root nodes.

        """
        experiment_template_rows = self.client.fetch(
            table="ExperimentTemplate",
            criteria=is_one_of(
                "xptm_name", ["SmartSPIM Labeling", "SmartSPIM Delipidation", "SmartSPIM Refractive Index Matching"]),
        )
        exp_run_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentTemplate",
            input_rows=experiment_template_rows,
            input_table_cols=["xptm_pk"],
            foreign_table="ExperimentRun",
            foreign_table_col="xprn_fk_experimentTemplate",
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
        # connect protocol
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
        # TODO: check if this is necessary 
        _ = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStepContent",
            input_rows=exp_run_step_content_rows,
            input_table_cols=["xrsc_fk_content"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )
        # reagents 
        # TODO: check that get_rows can handle a column with list value
        reagent_content_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_cf_fk_reagent"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )
        # TODO: might not need these extra tables if we can use display values properly
        reference_data_rows = self.get_rows_from_foreign_table(
            input_table="Content",
            input_rows=reagent_content_rows,
            input_table_cols=["cntn_cf_fk_reagentCatalogNumber"],
            foreign_table="ReferenceDataRecord",
            foreign_table_col="rdrc_pk",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="ReferenceDataRecord",
            input_rows=reference_data_rows,
            input_table_cols=["rdrc_cf_fk_manufacturer"],
            foreign_table="Source",
            foreign_table_col="sorc_pk",
            graph=G,
        )
        return G, root_nodes
    
    def get_spim_data_from_slims(
        self,
        subject_id: Optional[str] = None,
    ) -> List[SlimsHistologyData]:
        """

        Parameters
        ----------
        subject_id : str | None
          Labtracks ID of mouse. If None, then no filter will be performed.

        Returns
        -------
        List[SlimsSpimData]

        Raises
        ------
        ValueError
          The subject_id cannot be an empty string.

        """

        if subject_id is not None and len(subject_id) == 0:
            raise ValueError("subject_id must not be empty!")

        G, root_nodes = self._get_graph()
        nx.draw(G, with_labels=True)
        plt.show()
        spim_data = self._parse_graph(
            g=G, root_nodes=root_nodes, subject_id=subject_id
        )
        return spim_data
