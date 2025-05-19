"""
Module to handle fetching imaging data from slims and parsing it to a model
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


class SlimsSpimData(BaseModel):
    """Expected Model that needs to be extracted from SLIMS"""

    experiment_run_created_on: Optional[int] = None
    specimen_id: Optional[str] = None
    subject_id: Optional[str] = None
    protocol_name: Optional[str] = None
    protocol_id: Optional[str] = None
    date_performed: Optional[int] = None
    chamber_immersion_medium: Optional[str] = None
    sample_immersion_medium: Optional[str] = None
    chamber_refractive_index: Optional[Decimal] = None
    sample_refractive_index: Optional[Decimal] = None
    instrument_id: Optional[str] = None
    experimenter_name: Optional[str] = None
    z_direction: Optional[str] = None
    y_direction: Optional[str] = None
    x_direction: Optional[str] = None
    imaging_channels: Optional[List[str]] = None
    stitching_channels: Optional[str] = None
    ccf_registration_channels: Optional[str] = None
    cell_segmentation_channels: Optional[List[str]] = None


class SlimsImagingHandler(SlimsTableHandler):
    """Class to handle getting SPIM Imaging info from SLIMS."""

    @staticmethod
    def _parse_graph(
        g: DiGraph, root_nodes: List[str], subject_id: Optional[str]
    ) -> List[SlimsSpimData]:
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
        List[SlimsSpimData]

        """

        spim_data_list = []
        for node in root_nodes:
            spim_data = SlimsSpimData()
            node_des = descendants(g, node)
            exp_run_created_on = get_attr_or_none(
                g.nodes[node]["row"], "xprn_createdOn"
            )
            spim_data.experiment_run_created_on = exp_run_created_on
            for n in node_des:
                table_name = g.nodes[n]["table_name"]
                row = g.nodes[n]["row"]
                if table_name == "Content":
                    n_subject_id = get_attr_or_none(row, "cntn_id")
                    n_specimen_id = get_attr_or_none(row, "cntn_barCode")
                    spim_data.subject_id = n_subject_id
                    spim_data.specimen_id = n_specimen_id
                if table_name == "SOP":
                    stop_link = get_attr_or_none(row, "stop_link")
                    stop_name = get_attr_or_none(row, "stop_name")
                    spim_data.protocol_id = stop_link
                    spim_data.protocol_name = stop_name
                if (
                    table_name == "ReferenceDataRecord"
                    and get_attr_or_none(
                        row, "rdrc_fk_referenceDataType", "displayValue"
                    )
                    == "SPIM Brain Orientation"
                ):
                    z_direction = get_attr_or_none(row, "rdrc_cf_zDirection")
                    x_direction = get_attr_or_none(row, "rdrc_cf_xDirection")
                    y_direction = get_attr_or_none(row, "rdrc_cf_yDirection")
                    spim_data.z_direction = z_direction
                    spim_data.x_direction = x_direction
                    spim_data.y_direction = y_direction
                if (
                    table_name == "ReferenceDataRecord"
                    and get_attr_or_none(
                        row, "rdrc_fk_referenceDataType", "displayValue"
                    )
                    == "AIND Instruments"
                ):
                    instrument_name = get_attr_or_none(row, "rdrc_name")
                    spim_data.instrument_id = instrument_name
                if table_name == "Result":
                    user = get_attr_or_none(
                        row, "rslt_cf_fk_operator", "displayValue"
                    )
                    chamber_immersion_medium = get_attr_or_none(
                        row, "rslt_cf_chamberImmersionMedium"
                    )
                    sample_immersion_medium = get_attr_or_none(
                        row, "rslt_cf_sampleImmersionMedium"
                    )
                    chamber_refractive_index = get_attr_or_none(
                        row, "rslt_cf_chamberRefractiveIndex"
                    )
                    sample_refractive_index = get_attr_or_none(
                        row, "rslt_cf_sampleRefractiveIndex"
                    )
                    date_performed = get_attr_or_none(
                        row, "rslt_cf_datePerformed"
                    )
                    spim_data.chamber_immersion_medium = (
                        chamber_immersion_medium
                    )
                    spim_data.chamber_refractive_index = (
                        None
                        if chamber_refractive_index is None
                        else Decimal(str(chamber_refractive_index))
                    )
                    spim_data.sample_immersion_medium = sample_immersion_medium
                    spim_data.sample_refractive_index = (
                        None
                        if sample_refractive_index is None
                        else Decimal(str(sample_refractive_index))
                    )
                    spim_data.date_performed = date_performed
                    spim_data.experimenter_name = user
                if (
                    table_name == "Order"
                    and get_attr_or_none(
                        row, "ordr_fk_orderType", "displayValue"
                    )
                    == "SmartSPIM Histology and Imaging"
                ):
                    spim_data.imaging_channels = get_attr_or_none(
                        row, "ordr_cf_fluorescenceChannels_Imaging"
                    )
                    spim_data.stitching_channels = get_attr_or_none(
                        row, "ordr_cf_fluorescenceChannels_Stitching"
                    )
                    spim_data.ccf_registration_channels = get_attr_or_none(
                        row, "ordr_cf_fluorescenceChannels_CcfRegistration"
                    )
                    spim_data.cell_segmentation_channels = get_attr_or_none(
                        row, "ordr_cf_fluorescenceChannels_CellSegmentation"
                    )
            if subject_id is None or subject_id == spim_data.subject_id:
                spim_data_list.append(spim_data)
        return spim_data_list

    def _get_graph(
        self,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> Tuple[DiGraph, List[str]]:
        """
        Generate a Graph of the records from SLIMS for imaging experiment runs.
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
            criteria=equals("xptm_name", "SPIM Imaging"),
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

        result_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_pk"],
            foreign_table="Result",
            foreign_table_col="rslt_fk_experimentRunStep",
            graph=G,
        )

        content_rows = self.get_rows_from_foreign_table(
            input_table="ExperimentRunStepContent",
            input_rows=exp_run_step_content_rows,
            input_table_cols=["xrsc_fk_content"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )

        _ = self.get_rows_from_foreign_table(
            input_table="Result",
            input_rows=result_rows,
            input_table_cols=[
                "rslt_cf_fk_instrumentJson",
                "rslt_cf_fk_spimBrainOrientation",
            ],
            foreign_table="ReferenceDataRecord",
            foreign_table_col="rdrc_pk",
            graph=G,
        )
        # Add Orders
        order_content_rows = self.get_rows_from_foreign_table(
            input_table="Content",
            input_rows=content_rows,
            input_table_cols=["cntn_pk"],
            foreign_table="OrderContent",
            foreign_table_col="rdcn_fk_content",
            graph=G,
        )
        _ = self.get_rows_from_foreign_table(
            input_table="OrderContent",
            input_rows=order_content_rows,
            input_table_cols=["rdcn_fk_order"],
            foreign_table="Order",
            foreign_table_col="ordr_pk",
            graph=G,
        )

        return G, root_nodes

    def get_spim_data_from_slims(
        self,
        subject_id: Optional[str] = None,
        start_date_greater_than_or_equal: Optional[datetime] = None,
        end_date_less_than_or_equal: Optional[datetime] = None,
    ) -> List[SlimsSpimData]:
        """
        Get SPIM data from SLIMS.

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
        List[SlimsSpimData]

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

        spim_data = self._parse_graph(
            g=G, root_nodes=root_nodes, subject_id=subject_id
        )

        return spim_data
