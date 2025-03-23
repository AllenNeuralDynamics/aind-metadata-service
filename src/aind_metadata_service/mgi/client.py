"""Module to handle retrieving information from MGI"""

import logging
import os
import re
from typing import Any, List, Optional, Union

import requests
from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import SettingsConfigDict

from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.settings import ParameterStoreBaseSettings


class MgiSettings(ParameterStoreBaseSettings):
    """Settings required for endpoint"""

    model_config = SettingsConfigDict(
        env_prefix="MGI_",
        extra="ignore",
        aws_param_store_name=os.getenv("AWS_PARAM_STORE_NAME"),
    )

    url: HttpUrl = Field(
        default="https://www.informatics.jax.org//quicksearch/alleleBucket"
    )


class MgiSummaryRow(BaseModel):
    """Model of Summary Row dictionary returned"""

    detailUri: Optional[str] = Field(default=None)
    featureType: Optional[str] = Field(default=None)
    strand: Optional[str] = Field(default=None)
    chromosome: Optional[str] = Field(default=None)
    stars: Optional[str] = Field(default=None)
    bestMatchText: Optional[str] = Field(default=None)
    bestMatchType: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    symbol: Optional[str] = Field(default=None)


class MgiResponse(BaseModel):
    """Model for response from MGI"""

    summaryRows: List[MgiSummaryRow]
    totalCount: Optional[int] = Field(default=None)
    meta: Optional[Any] = Field(default=None)


class MgiClient:
    """Client to connect to Mgi"""

    def __init__(self, settings: MgiSettings):
        """Class constructor"""

        self.settings = settings

    @staticmethod
    def get_allele_names_from_genotype(genotype: Optional[str]) -> List[str]:
        """
        Maps a genotype to list of allele names
        Parameters
        ----------
        genotype : Optional[str]

        Returns
        -------
        List[str]

        """
        if genotype is None:
            filtered_alleles = []
        else:
            alleles = re.split("[; /]", genotype)
            filtered_alleles = [a for a in alleles if a not in ["", "wt"]]
        return filtered_alleles

    def get_allele_info(
        self, allele_name: str
    ) -> Union[MgiResponse, ModelResponse]:
        """
        Get allele info from mgi endpoint
        Parameters
        ----------
        allele_name : str

        Returns
        -------
        MgiResponse

        """
        try:
            params = {
                "queryType": "exactPhrase",
                "query": allele_name,
                "submit": "Quick+Search",
                "startIndex": "0",
                "results": "1",
            }
            response = requests.get(
                url=self.settings.url.unicode_string(), params=params
            )
            response.raise_for_status()
            response_model = MgiResponse(**response.json())
            return response_model
        except Exception as e:
            logging.exception(e)
            return ModelResponse.internal_server_error_response()
