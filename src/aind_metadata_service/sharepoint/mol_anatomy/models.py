from pydantic import BaseModel, Field, Extra, validator
from typing import Optional, List, Union
from datetime import datetime
import re
from dataclasses import dataclass
from enum import Enum
import pytz


@dataclass
class NumberWithNotes:
    """Container to hold a parsed number from a string"""

    raw_input: Optional[str] = None
    number: Optional[float] = None
    notes: Optional[str] = None


class Sex(Enum):
    MALE = "M"
    FEMALE = "F"


class ExcelSheetRow(BaseModel, extra=Extra.allow):
    @staticmethod
    def ignore_excel_sheet(
        excel_sheet_name: str, column_names: List[str]
    ) -> bool:
        """
        Filter the excel sheet from processing
        Parameters
        ----------
        excel_sheet_name : str
          Name of the excel sheet
        column_names : List[str]
          column names in the excel sheet

        Returns
        -------
        bool
          True if the excel sheet should be ignored.
          False if it should be kept.

        """
        pattern_for_sheets_to_filter_out = (
            r"(?:Template and Color codes)|(?:.*-old\s*$)"
        )
        return (
            re.match(pattern_for_sheets_to_filter_out, excel_sheet_name)
            is not None
        ) or ("Mouse ID" not in column_names)

    s_perfusion_date: Optional[datetime] = Field(
        default=None, alias=" Perfusion Date"
    )
    hashtag: Optional[int] = Field(default=None, alias="#")
    actual_perfusion_date: Optional[datetime] = Field(
        default=None, alias="Actual Perfusion Date"
    )
    age_injected: Optional[int] = Field(default=None, alias="Age Injected")
    age_at_perfusion: Optional[int] = Field(
        default=None, alias="Age at perfusion"
    )
    age_of_injection: Optional[int] = Field(
        default=None, alias="Age of Injection"
    )
    age_of_perfusion: Optional[int] = Field(
        default=None, alias="Age of Perfusion"
    )
    dob: Optional[datetime] = Field(default=None, alias="DOB")
    dose: Optional[int] = Field(default=None, alias="Dose")
    gross_anatomical_observations: Optional[str] = Field(
        default=None, alias="Gross Anatomical Observations"
    )
    gross_anatomical_observations_pre_processing: Optional[str] = Field(
        default=None, alias="Gross Anatomical Observations (pre-processing)"
    )
    gross_anatomy_notes_pre_processing: Optional[str] = Field(
        default=None, alias="Gross Anatomy Notes (pre-processing)"
    )
    gross_anatomy_observations_pre_processing: Optional[str] = Field(
        default=None, alias="Gross Anatomy Observations (pre-processing)"
    )
    gross_anatomical_observation: Optional[str] = Field(
        default=None, alias="Gross anatomical observation"
    )
    injection_requested: Optional[str] = Field(
        default=None, alias="Injection Requested?"
    )
    las_notes: Optional[str] = Field(default=None, alias="LAS Notes")
    las_notes_1: Optional[str] = Field(default=None, alias="LAS Notes.1")
    las_perfusion_dissection_notes: Optional[str] = Field(
        default=None, alias="LAS Perfusion/Dissection Notes"
    )
    las_injection_notes: Optional[str] = Field(
        default=None, alias="LAS injection Notes"
    )
    mouse_id: Optional[str] = Field(default=None, alias="Mouse ID")
    my_notes: Optional[str] = Field(default=None, alias="My notes")
    notes: Optional[str] = Field(default=None, alias="Notes")
    pedigree: Optional[str] = Field(default=None, alias="Pedigree")
    perfusion_date: Optional[datetime] = Field(
        default=None, alias="Perfusion Date"
    )
    perfusion_requested: Optional[str] = Field(
        default=None, alias="Perfusion Requested?"
    )
    perfusion_type: Optional[str] = Field(default=None, alias="Perfusion Type")
    ro_injection_date: Optional[datetime] = Field(
        default=None, alias="RO Injection Date"
    )
    sex: Optional[Sex] = Field(default=None, alias="Sex")
    staining: Optional[str] = Field(default=None, alias="Staining")
    status: Optional[str] = Field(default=None, alias="Status")
    tam_injection_first_day: Optional[str] = Field(
        default=None, alias="TAM injection (first day)"
    )
    tam_injection_last_day: Optional[str] = Field(
        default=None, alias="TAM injection (last day)"
    )
    titer: Optional[int] = Field(default=None, alias="Titer")
    unnamed_0: Optional[str] = Field(default=None, alias="Unnamed: 0")
    unnamed_22: Optional[str] = Field(default=None, alias="Unnamed: 22")
    vehicle: Optional[str] = Field(default=None, alias="Vehicle")
    virus: Optional[str] = Field(default=None, alias="Virus")
    virus_id: Optional[str] = Field(default=None, alias="Virus ID")
    volume_injected: Optional[NumberWithNotes] = Field(
        default=None, alias="Volume Injected"
    )

    @validator(
        "volume_injected",
        pre=True,
    )
    def parse_numeric_with_notes(cls, v: Optional[str]) -> NumberWithNotes:
        """Match like '0.25' or '20uL"""
        pattern1 = r"^([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))$"
        pattern2 = r"([-+]?(?:[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?))([,\w].*)"
        if type(v) is str and re.match(pattern1, v):
            return NumberWithNotes(
                raw_input=v, number=re.match(pattern1, v).group(1)
            )
        elif type(v) is str and re.match(pattern2, v):
            return NumberWithNotes(
                raw_input=v,
                number=re.match(pattern2, v).group(1),
                notes=re.match(pattern2, v).group(2),
            )
        else:
            return NumberWithNotes(raw_input=v)

    @validator("sex", pre=True)
    def parse_sex_type(cls, v: Optional[str]) -> Optional[Sex]:
        """Parses string into a Sex model"""
        if type(v) is str and v in [e.value for e in Sex]:
            return Sex(v)
        else:
            return None

    @validator("ro_injection_date", pre=True)
    def parse_datetime(cls, v: Union[str, int, None]) -> Optional[datetime]:
        """Parses string or datetime to datetime. Removes dashes."""
        if type(v) is str and v == '-':
            return None
        elif v is None:
            return None
        else:
            utc_dt = datetime.utcfromtimestamp(v / 1000)
            aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
            return aware_utc_dt
