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

# class AntibodyData(BaseModel):
#     """Consolidated antibody data for immunolabeling procedures."""
#     immunolabel_class: Optional[str] = None  # e.g. "PRIMARY" or "SECONDARY"
#     mass: Optional[float] = None

class SlimsReagentData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""
    name: Optional[str] = None
    source: Optional[str] = None
    lot_number: Optional[str] = None

class SlimsWashData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""
    wash_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    modified_by: Optional[str] = None
    reagents: Optional[List[SlimsReagentData]] = None

class SlimsHistologyData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS."""

    experiment_run_created_on: Optional[int] = None
    specimen_id: Optional[str] = None
    protocol_id: Optional[str] = None
    protocol_name: Optional[str] = None
    washes: Optional[List[SlimsWashData]] = None




    # procedure_type: Optional[str] = None # experiment template name 
    # procedure_name: Optional[str] = None # protocol name
    # start_date: Optional[int] = None # experiment step start time (first step start time)
    # end_date: Optional[int] = None # experiment step end time (last step end time)
    # experimenters: Optional[List[str]] = None # 
    # protocol_ids: List[str] = []
    # reagents: Optional[List[ReagentData]] = None
    # antibodies: Optional[List[AntibodyData]] = None


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
                    wash_data.start_time = get_attr_or_none(row, "xprs_cf_sbipDelipidationWash1Start")
                    wash_data.end_time = get_attr_or_none(row, "xprs_cf_sbipDelipidationWash6End")
                    wash_data.modified_by = get_attr_or_none(row, "modified_by")
                    # histology_data.washes.append(wash_data)
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
                    table_name == "Content"
                    and get_attr_or_none(
                        row, "cntn_fk_category", "displayValue"
                    )
                    == "Reagents, Externally Manufactured"
                    or get_attr_or_none(row, "cntn_fk_category", "displayValue")
                    == "Reagents, Internally Produced"
                ):
                    n_reagent_lot_number = get_attr_or_none(row, "cntn_cf_lotNumber")
                    # TODO: check if name and source can be retrieved from display values properly
                    n_reagent_name = get_attr_or_none(row, "cntn_cf_fk_reagentCatalogNumber", "displayValue")
                    n_reagent_source = get_attr_or_none(row, "cntn_fk_source", "displayValue")
                # TODO: figure out how to go through the different nodes, might need to be nested loop?
                # TODO: OR have some field that links the reagent to the wash, nested loop would defeat purpose of graph
                

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
        _ = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStepContent",
            input_rows=exp_run_step_content_rows,
            input_table_cols=["xrsc_fk_content"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )
        # reagents 
        reagent_content_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_cf_fk_reagent_multiselect"],
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

    # def _parse_graph(self, g: DiGraph, root_nodes: List[str], specimen_id: str) -> List[SlimsHistologyData]:
    #     """
    #     Traverse the graph to extract the necessary values and map them into SlimsHistologyData records.
    #     Handles both immunolabeling (which creates one record per wash) and other procedure types (aggregated per block).
    #     """
    #     procedures: List[SlimsHistologyData] = []
        
    #     # Iterate over each block (each root corresponds to an ExperimentRunStepContent block).
    #     for root in root_nodes:
    #         # Find the associated ExperimentRunStep (child of the content node).
    #         exp_run_step = None
    #         exp_run_step_node = None
    #         for child in g.successors(root):
    #             if g.nodes[child]["table_name"] == "ExperimentRunStep":
    #                 exp_run_step = g.nodes[child]["row"]
    #                 exp_run_step_node = child
    #                 break
    #         if not exp_run_step or not exp_run_step_node:
    #             continue
            
    #         # Extract ExperimentTemplate and ProtocolSOP (if available)
    #         experiment_template = None
    #         protocol = None
    #         for child in g.successors(exp_run_step_node):
    #             node_data = g.nodes[child]
    #             if node_data["table_name"] == "ExperimentTemplate":
    #                 experiment_template = node_data["row"]
    #             elif node_data["table_name"] == "ProtocolRunStep":
    #                 # Look for ProtocolSOP under ProtocolRunStep.
    #                 for pr_child in g.successors(child):
    #                     if g.nodes[pr_child]["table_name"] == "ProtocolSOP":
    #                         protocol = g.nodes[pr_child]["row"]
            
    #         # Gather all WashRunStep nodes from exp_run_step children.
    #         washes = []
    #         for child in g.successors(exp_run_step_node):
    #             if g.nodes[child]["table_name"] == "WashRunStep":
    #                 wash_step = g.nodes[child]["row"]
    #                 # For each wash, collect reagents by checking its successors.
    #                 reagents = []
    #                 # Also capture antibody info if applicable.
    #                 antibody: Optional[AntibodyData] = None
    #                 for wash_child in g.successors(child):
    #                     if g.nodes[wash_child]["table_name"] == "ReagentContent":
    #                         reagent_content = g.nodes[wash_child]["row"]
    #                         # Attempt to fetch details and source from the reagent subtree.
    #                         details = None
    #                         source = None
    #                         for rc_child in g.successors(wash_child):
    #                             if g.nodes[rc_child]["table_name"] == "ReagentDetailsRdrc":
    #                                 details = g.nodes[rc_child]["row"]
    #                                 for det_child in g.successors(rc_child):
    #                                     if g.nodes[det_child]["table_name"] == "Source":
    #                                         source = g.nodes[det_child]["row"]
    #                         reagents.append({
    #                             "content": reagent_content,
    #                             "details": details,
    #                             "source": source
    #                         })
    #                 washes.append({
    #                     "wash_step": wash_step,
    #                     "reagents": reagents
    #                 })
            
    #         # Determine procedure type from the experiment template name.
    #         template_name = getattr(experiment_template, "name", None) if experiment_template else None
    #         procedure_type = _map_procedure_type(template_name) if template_name else None
    #         if not procedure_type:
    #             continue  # Skip if we cannot determine a procedure type.
            
    #         # Extract protocol link if available.
    #         protocol_link = None
    #         if protocol and getattr(protocol, "link", None):
    #             protocol_link = _extract_protocol_link(getattr(protocol, "link"))
            
    #         # Depending on procedure type, map into one or more SlimsHistologyData records.
    #         if procedure_type == "IMMUNOLABELING":
    #             # For immunolabeling, create one record per wash that qualifies.
    #             for wash in washes:
    #                 wash_step = wash.get("wash_step")
    #                 if not wash_step:
    #                     continue
    #                 # Determine if this wash corresponds to an antibody wash based on wash name.
    #                 wash_name = getattr(wash_step, "wash_name", None)
    #                 immunolabel_class = None
    #                 if wash_name == "PRIMARY_ANTIBODY_WASH":
    #                     immunolabel_class = "PRIMARY"
    #                 elif wash_name == "SECONDARY_ANTIBODY_WASH":
    #                     immunolabel_class = "SECONDARY"
    #                 if not immunolabel_class:
    #                     continue  # Skip washes that are not antibody washes.
                    
    #                 # Create antibody data from the wash.
    #                 mass = getattr(wash_step, "mass", None)
    #                 antibody = AntibodyData(
    #                     immunolabel_class=immunolabel_class,
    #                     mass=float(mass) if mass is not None else None
    #                 )
                    
    #                 # Use the wash start and end times.
    #                 start_time: Optional[datetime] = getattr(wash_step, "start_time", None)
    #                 end_time: Optional[datetime] = getattr(wash_step, "end_time", None)
                    
    #                 proc = SlimsHistologyData(
    #                     specimen_id=specimen_id,
    #                     procedure_type=procedure_type,
    #                     procedure_name=getattr(protocol, "name", None) if protocol else None,
    #                     start_date=start_time.date() if start_time else None,
    #                     end_date=end_time.date() if end_time else None,
    #                     experimenters=[getattr(wash_step, "modified_by", None)] if getattr(wash_step, "modified_by", None) else None,
    #                     protocol_ids=[protocol_link] if protocol_link else [],
    #                     antibodies=[antibody],
    #                     reagents=None
    #                 )
    #                 procedures.append(proc)
    #         else:
    #             # For non-immunolabeling procedures, aggregate washes.
    #             wash_start_dates = []
    #             wash_end_dates = []
    #             expers = []
    #             reagent_list = []
    #             for wash in washes:
    #                 wash_step = wash.get("wash_step")
    #                 if not wash_step:
    #                     continue
    #                 start_time: Optional[datetime] = getattr(wash_step, "start_time", None)
    #                 end_time: Optional[datetime] = getattr(wash_step, "end_time", None)
    #                 if start_time:
    #                     wash_start_dates.append(start_time.date())
    #                 if end_time:
    #                     wash_end_dates.append(end_time.date())
    #                 mod_by = getattr(wash_step, "modified_by", None)
    #                 if mod_by:
    #                     expers.append(mod_by)
    #                 # Aggregate reagents from this wash.
    #                 for r in wash.get("reagents", []):
    #                     reagent_content = r.get("content")
    #                     details = r.get("details")
    #                     source = r.get("source")
    #                     reagent_obj = ReagentData(
    #                         name=getattr(details, "name", None) if details else None,
    #                         source=getattr(source, "name", None) if source else None,
    #                         lot_number=getattr(reagent_content, "lot_number", None) if reagent_content else None,
    #                     )
    #                     reagent_list.append(reagent_obj)
    #             start_date = min(wash_start_dates) if wash_start_dates else None
    #             end_date = max(wash_end_dates) if wash_end_dates else None
    #             # Remove duplicates from experimenters.
    #             unique_exps = list({exp for exp in expers if exp})
    #             proc = SlimsHistologyData(
    #                 specimen_id=specimen_id,
    #                 procedure_type=procedure_type,
    #                 procedure_name=getattr(protocol, "name", None) if protocol else None,
    #                 start_date=start_date,
    #                 end_date=end_date,
    #                 experimenters=unique_exps if unique_exps else None,
    #                 protocol_ids=[protocol_link] if protocol_link else [],
    #                 reagents=reagent_list if reagent_list else None,
    #                 antibodies=None
    #             )
    #             procedures.append(proc)
    #     return procedures

    # def get_histology_data(self, specimen_id: str) -> List[SlimsHistologyData]:
    #     """
    #     Public method to retrieve histology procedures for a given specimen_id.
    #     Returns a list of SlimsHistologyData records.
    #     Raises:
    #         ValueError: if specimen_id is empty.
    #     """
    #     if not specimen_id:
    #         raise ValueError("specimen_id must not be empty!")
    #     graph, root_nodes = self._get_graph(specimen_id)
    #     return self._parse_graph(graph, root_nodes, specimen_id)