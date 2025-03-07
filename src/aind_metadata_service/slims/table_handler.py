"""
Module to handle fetching data from slims
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, List, Optional, Union

from networkx import DiGraph
from slims.criteria import (
    Criterion,
    Junction,
    conjunction,
    greater_than_or_equal,
    is_one_of,
    less_than_or_equal,
)
from slims.internal import Record
from slims.slims import Slims


def parse_html(v: Optional[str]) -> Optional[str]:
    """Parse link from html tag"""
    if v is None:
        return None
    try:
        root = ET.fromstring(v)
        return root.get("href")
    except ET.ParseError:
        return v
    except Exception as e:
        logging.warning(f"An exception occurred parsing link {v}: {e}")
        return None


def get_attr_or_none(
    record: Record, field_name: str, attr_name: str = "value"
) -> Optional[Any]:
    """
    Get a column attribute for a record at the field name. If the record does
    not have the field then return None.
    Parameters
    ----------
    record : Record
    field_name : str
    attr_name : str
      Column attribute. Default is "value." The other common attr_name is
      "displayValue."

    Returns
    -------
    Any | None

    """
    if hasattr(record, field_name):
        obj_field = getattr(record, field_name)
        return getattr(obj_field, attr_name, None)
    else:
        return None


class SlimsTableHandler:
    """Class to handle tables pulled from slims."""

    def __init__(self, client: Slims):
        """
        Class constructor.
        Parameters
        ----------
        client : Slims
        """
        self.client = client

    @staticmethod
    def _get_date_criteria(
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        field_name: str,
    ) -> Optional[Union[Criterion, Junction]]:
        """
        Generate a criteria given start_date and end_date.
        Parameters
        ----------
        start_date : datetime | None
        end_date : datetime | None
        field_name : str

        Returns
        -------
        Criterion | Junction | None

        """
        start_date_criteria = None
        end_date_criteria = None
        if start_date:
            start_date_criteria = greater_than_or_equal(
                field_name,
                int(start_date.timestamp() * 1000),
            )
        if end_date:
            end_date_criteria = less_than_or_equal(
                field_name,
                int(end_date.timestamp() * 1000),
            )
        if start_date_criteria and not end_date_criteria:
            date_criteria = start_date_criteria
        elif not start_date_criteria and end_date_criteria:
            date_criteria = end_date_criteria
        elif start_date_criteria and end_date_criteria:
            date_criteria = (
                conjunction().add(start_date_criteria).add(end_date_criteria)
            )
        else:
            date_criteria = None
        return date_criteria

    # TODO: refactor this to make it simpler
    @staticmethod
    def _update_graph(  # noqa: C901
        foreign_table: str,
        foreign_rows: List[Record],
        foreign_table_col: str,
        input_table: str,
        input_rows: List[Record],
        input_table_cols: List[str],
        g: DiGraph,
    ) -> None:
        """
        Update graph of table relations in place.
        Parameters
        ----------
        foreign_table : str
          Name of the slims table
        foreign_rows : List[Record]
          The records pulled from the foreign table
        foreign_table_col : str
          The column name of the foreign table to match keys against
        input_table : str
          Name of the input table
        input_rows : List[Record]
          The records that were pulled from the input table
        input_table_cols : List[str]
          The name of the columns in the input table to match keys against
        g : DiGraph
          The directed graph to updated with the slims information

        Returns
        -------
        None
          Updates the DiGraph object in place.

        """
        for row in foreign_rows:
            g.add_node(
                f"{foreign_table}.{row.pk()}",
                row=row,
                pk=row.pk(),
                table_name=foreign_table,
            )
        if foreign_table_col.endswith("_pk"):
            for row in input_rows:
                for input_table_col in input_table_cols:
                    foreign_table_pk = get_attr_or_none(row, input_table_col)
                    if (
                        isinstance(foreign_table_pk, int)
                        and g.nodes.get(f"{foreign_table}.{foreign_table_pk}")
                        is not None
                    ):
                        g.add_edge(
                            f"{row.table_name()}.{row.pk()}",
                            f"{foreign_table}.{foreign_table_pk}",
                        )
                    elif isinstance(foreign_table_pk, list):
                        for f_pk in foreign_table_pk:
                            if (
                                g.nodes.get(f"{foreign_table}.{f_pk}")
                                is not None
                            ):
                                g.add_edge(
                                    f"{row.table_name()}.{row.pk()}",
                                    f"{foreign_table}.{f_pk}",
                                )
        else:
            for row in foreign_rows:
                input_table_pk = get_attr_or_none(row, foreign_table_col)
                if (
                    isinstance(input_table_pk, int)
                    and g.nodes.get(f"{input_table}.{input_table_pk}")
                    is not None
                ):
                    g.add_edge(
                        f"{input_table}.{input_table_pk}",
                        f"{row.table_name()}.{row.pk()}",
                    )

    # TODO: Allow for multiple input tables
    def get_rows_from_foreign_table(
        self,
        input_table: str,
        input_rows: List[Record],
        foreign_table: str,
        foreign_table_col: str,
        input_table_cols: List[str],
        extra_criteria: Optional[Union[Criterion, Junction]] = None,
        graph: Optional[DiGraph] = None,
    ) -> List[Record]:
        """
        Pull rows from foreign table
        Parameters
        ----------
        input_table : str
        input_rows :
        input_table_cols :
        foreign_table :
        foreign_table_col :
        extra_criteria: Criterion | Junction | None
        graph : Graph | None

        Returns
        -------

        """
        sets_of_foreign_keys = {r: set() for r in input_table_cols}
        for row in input_rows:
            for fk_name in input_table_cols:
                if get_attr_or_none(row, fk_name) is not None:
                    key_values = get_attr_or_none(row, fk_name)
                    if isinstance(key_values, list):
                        key_values = set(key_values)
                    else:
                        key_values = {key_values}
                    sets_of_foreign_keys[fk_name] = sets_of_foreign_keys[
                        fk_name
                    ].union(key_values)
        total_fks = set()
        for v in sets_of_foreign_keys.values():
            total_fks = total_fks.union(v)
        if len(total_fks) == 0:
            rows = []
        else:
            main_criteria = is_one_of(foreign_table_col, list(total_fks))
            if extra_criteria is not None:
                criteria = conjunction().add(main_criteria).add(extra_criteria)
            else:
                criteria = main_criteria
            rows = self.client.fetch(
                table=foreign_table,
                criteria=criteria,
            )
        if graph is not None and rows:
            self._update_graph(
                input_rows=input_rows,
                input_table=input_table,
                input_table_cols=input_table_cols,
                g=graph,
                foreign_table=foreign_table,
                foreign_table_col=foreign_table_col,
                foreign_rows=rows,
            )

        return rows
