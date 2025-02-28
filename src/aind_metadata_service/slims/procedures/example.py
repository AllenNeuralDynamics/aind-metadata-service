import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
from dotenv import load_dotenv
from slims.criteria import (
    Criterion,
    Junction,
    conjunction,
    equals,
    greater_than,
    greater_than_or_equal,
    is_one_of,
    less_than_or_equal,
)
from slims.slims import Slims

from aind_metadata_service.slims.table_handler import SlimsTableHandler, get_attr_or_none

load_dotenv()

client = Slims(
    name="slims",
    url=os.getenv("SLIMS_URL"),
    username=os.getenv("SLIMS_USERNAME"),
    password=os.getenv("SLIMS_PASSWORD"),
)

subject_id = "769884"

slims_handler = SlimsTableHandler(client=client)

# xptm_name can be 3 things: "SmartSPIM Labeling", "SmartSPIM Delipidation", "SmartSPIM Refractive Index Matching"
experiment_template_rows = slims_handler.client.fetch(
            table="ExperimentTemplate",
            criteria=is_one_of(
                "xptm_name", ["SmartSPIM Labeling", "SmartSPIM Delipidation", "SmartSPIM Refractive Index Matching"]),
        )

exp_run_rows = slims_handler.get_rows_from_foreign_table(
            input_table="ExperimentTemplate",
            input_rows=experiment_template_rows,
            input_table_cols=["xptm_pk"],
            foreign_table="ExperimentRun",
            foreign_table_col="xprn_fk_experimentTemplate",
            # extra_criteria=date_criteria,
        )

G = nx.DiGraph()
root_nodes = []
for row in exp_run_rows:
    G.add_node(
            f"{row.table_name()}.{row.pk()}",
            row=row,
            pk=row.pk(),
            table_name=row.table_name(),
        )
    root_nodes.append(f"{row.table_name()}.{row.pk()}")

# include washes 
# TODO: check if there's another column that'll be good for washes
exp_run_step_rows = slims_handler.get_rows_from_foreign_table(
            input_table="ExperimentRun",
            input_rows=exp_run_rows,
            input_table_cols=["xprn_pk"],
            foreign_table="ExperimentRunStep",
            foreign_table_col="xprs_fk_experimentRun",
            graph=G,
        )

nx.draw(G, with_labels=True)
plt.show()

# connect protocol
_ = slims_handler.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_cf_fk_protocol"],
            foreign_table="SOP",
            foreign_table_col="stop_pk",
            graph=G,
        )

nx.draw(G, with_labels=True)
plt.show()
exp_run_step_content_rows = slims_handler.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_pk"],
            foreign_table="ExperimentRunStepContent",
            foreign_table_col="xrsc_fk_experimentRunStep",
            graph=G,
        )

nx.draw(G, with_labels=True)
plt.show()
# reagents 
reagent_content_rows = slims_handler.get_rows_from_foreign_table(
            input_table="ExperimentRunStep",
            input_rows=exp_run_step_rows,
            input_table_cols=["xprs_cf_fk_reagent_multiselect"],
            foreign_table="Content",
            foreign_table_col="cntn_pk",
            graph=G,
        )

nx.draw(G, with_labels=True)
plt.show()
reference_data_rows = slims_handler.get_rows_from_foreign_table(
            input_table="Content",
            input_rows=reagent_content_rows,
            input_table_cols=["cntn_cf_fk_reagentCatalogNumber"],
            foreign_table="ReferenceDataRecord",
            foreign_table_col="rdrc_pk",
            graph=G,
        )

nx.draw(G, with_labels=True)
plt.show()
source_rows = slims_handler.get_rows_from_foreign_table(
            input_table="ReferenceDataRecord",
            input_rows=reference_data_rows,
            input_table_cols=["rdrc_cf_fk_manufacturer"],
            foreign_table="Source",
            foreign_table_col="sorc_pk",
            graph=G,
        )

nx.draw(G, with_labels=True)
plt.show()
