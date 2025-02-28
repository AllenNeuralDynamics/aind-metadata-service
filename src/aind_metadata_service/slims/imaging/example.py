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

subject_id = "782744"

slims_handler = SlimsTableHandler(client=client)

experiment_template_rows = slims_handler.client.fetch(
    table="ExperimentTemplate",
    criteria=equals("xptm_name", "SPIM Imaging"),
)

start_date = int(datetime(2025, 2, 11).timestamp() * 1000)
date_criteria = greater_than_or_equal("xprn_createdOn", start_date)

exp_run_rows = slims_handler.get_rows_from_foreign_table(
    input_table="ExperimentTemplate",
    input_rows=experiment_template_rows,
    input_table_cols=["xptm_pk"],
    foreign_table="ExperimentRun",
    foreign_table_col="xprn_fk_experimentTemplate",
    extra_criteria=date_criteria,
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

sop_rows = slims_handler.get_rows_from_foreign_table(
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

result_rows = slims_handler.get_rows_from_foreign_table(
    input_table="ExperimentRunStep",
    input_rows=exp_run_step_rows,
    input_table_cols=["xprs_pk"],
    foreign_table="Result",
    foreign_table_col="rslt_fk_experimentRunStep",
    graph=G,
)

nx.draw(G, with_labels=True)
plt.show()

content_rows = slims_handler.get_rows_from_foreign_table(
    input_table="ExperimentRunStepContent",
    input_rows=exp_run_step_content_rows,
    input_table_cols=["xrsc_fk_content"],
    foreign_table="Content",
    foreign_table_col="cntn_pk",
    graph=G,
)

nx.draw(G, with_labels=True)
plt.show()