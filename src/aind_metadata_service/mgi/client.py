from typing import Optional, Any, List

from pydantic_settings import BaseSettings
from pydantic import Extra, Field, HttpUrl, BaseModel
import requests


class MgiSettings(BaseSettings):

    url: HttpUrl = Field(
        default="https://www.informatics.jax.org//quicksearch/alleleBucket"
    )

    class Config:
        """Set env prefix and forbid extra fields."""

        env_prefix = "MGI_"
        extra = Extra.forbid


class MgiSummaryRow(BaseModel):
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

    summaryRows: List[MgiSummaryRow]
    totalCount: Optional[int] = Field(default=None)
    meta: Optional[Any] = Field(default=None)


class MgiClient:

    def __init__(self, settings: MgiSettings):

        self.settings = settings

    def get_allele_info(self, allele_name: str) -> MgiResponse:

        params = {
            "queryType": "exactPhrase",
            "query": allele_name,
            "submit": "Quick+Search",
            "startIndex": "0",
            "results": "1"
        }
        response = requests.get(
            url=self.settings.url.unicode_string(), params=params
        )
        response.raise_for_status()
        response_model = MgiResponse(**response.json())
        return response_model
