"""Helper methods to map sharepoint fields to schema format"""
import datetime
import re
from typing import Optional

from aind_data_schema.procedures import Side
from dateutil import parser


def map_choice(response):
    """Maps choice response when it wasn't selected"""
    if response == "Select..." or response == "N/A":
        return None
    return response


def map_hemisphere(response_hemisphere) -> Optional[Side]:
    """Maps response string to Side object"""
    if response_hemisphere == Side.LEFT.value:
        return Side.LEFT
    elif response_hemisphere == Side.RIGHT.value:
        return Side.RIGHT
    else:
        return None


def convert_str_to_time(time_string) -> Optional[int]:
    """converts duration"""
    try:
        return int(re.search(r"\d+", time_string).group())
    except AttributeError:
        return None
    except TypeError:
        return None


def parse_str_into_float(input_string) -> Optional[float]:
    """Parses int from string and converts to float"""
    if input_string:
        if "," in input_string:
            input_string = input_string.split(",")[0]
        stripped_response = re.sub(r"[^0-9.-]", "", input_string)
        if re.search("[0-9]", stripped_response):
            return float(stripped_response)
    return None


def convert_str_to_bool(input_string) -> Optional[bool]:
    """converts yes/no"""
    if input_string == "Yes":
        return True
    elif input_string == "No":
        return False
    else:
        return None


def map_date_to_datetime(date) -> Optional[datetime.date]:
    """maps sharepoint date to datetime.date object"""
    if date:
        return parser.isoparse(date).date()
    else:
        return None
