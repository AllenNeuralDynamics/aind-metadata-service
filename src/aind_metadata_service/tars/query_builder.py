"""Module that returns appropriate URL query strings"""
from enum import Enum


class APICalls(Enum):
    """Enum of different API calls for TARS"""

    REFERENCE_GENOMES = "api/v1/ReferenceGenomes"
    TITER_IMPORTS = "/api/v1/TiterImports"
    TITER_TYPES = "/api/v1/TiterTypes"
    VIRAL_PREP_IMPORTS = "/api/v1/ViralPrepImports"
    VIRAL_PREP_LOTS = "/api/v1/ViralPrepLots"
    VIRAL_PREPS = "/api/v1/ViralPreps"
    VIRAL_PREP_TYPES = "/api/v1/ViralPrepTypes"


class URLQueries(Enum):
    """Enum of queries"""

    DEFAULT_ORDER = "order=1&orderBy=id"
    SEARCH = "search"
    SEARCH_FIELDS = "searchFields"


class QuerySearchFieldValues(Enum):
    """Enum of Search Field Values"""

    LOT = "lot"


class TarsQueries:
    """Class to hold url query strings for TARS"""

    @staticmethod
    def prep_lot_from_number(resource: str, prep_lot_number: str) -> str:
        """Retrieves information to populate injection materials metadata"""
        query = (
            f"{resource}{APICalls.VIRAL_PREP_LOTS.value}"
            f"?{URLQueries.DEFAULT_ORDER.value}"
            f"&{URLQueries.SEARCH_FIELDS.value}="
            f"{QuerySearchFieldValues.LOT.value}"
            f"&{URLQueries.SEARCH.value}={prep_lot_number}"
        )
        return query
