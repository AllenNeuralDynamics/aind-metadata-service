"""
Module to handle fetching data from slims and mapping it to a data schema model
"""

from typing import Any, List, Optional, Union

from networkx import Graph
from slims.criteria import Criterion, Junction, conjunction, is_one_of
from slims.internal import Record
from slims.slims import Slims


def get_value_or_none(record: Record, field_name: str) -> Optional[Any]:
    """
    Get a value for a record attribute. If the record does not have the
    attribute then return None. This is useful because a Record object
    does not always contain all the attributes for the table it is pulled
    from.
    Parameters
    ----------
    record : Record
    field_name : str

    Returns
    -------
    Optional[Any]

    """
    if hasattr(record, field_name):
        obj_field = getattr(record, field_name)
        return getattr(obj_field, "value", None)
    else:
        return None


class SlimsHandler:

    def __init__(self, client: Slims):
        self.client = client

    @staticmethod
    def _update_graph(
        foreign_table: str,
        input_table: str,
        input_rows: List[Record],
        input_table_cols: List[str],
        g: Graph,
        foreign_rows: List[Record],
        foreign_table_col: str,
    ) -> None:
        """Update graph of table relations in place"""
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
                    foreign_table_pk = get_value_or_none(row, input_table_col)
                    if (
                        isinstance(foreign_table_pk, int)
                        and g.nodes.get(f"{foreign_table}.{foreign_table_pk}")
                        is not None
                    ):
                        g.add_edge(
                            f"{foreign_table}.{foreign_table_pk}",
                            f"{row.table_name()}.{row.pk()}",
                        )
                        break
        else:
            for row in foreign_rows:
                input_table_pk = get_value_or_none(row, foreign_table_col)
                if (
                    isinstance(input_table_pk, int)
                    and g.nodes.get(f"{input_table}.{input_table_pk}")
                    is not None
                ):
                    g.add_edge(
                        f"{row.table_name()}.{row.pk()}",
                        f"{input_table}.{input_table_pk}",
                    )

    def get_rows_from_foreign_table(
        self,
        input_table: str,
        input_rows: List[Record],
        foreign_table: str,
        foreign_table_col: str,
        input_table_cols: List[str],
        extra_criteria: Optional[Union[Criterion, Junction]] = None,
        graph: Optional[Graph] = None,
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
                if get_value_or_none(row, fk_name) is not None:
                    key_values = get_value_or_none(row, fk_name)
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
                criteria = conjunction().add(main_criteria, extra_criteria)
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
