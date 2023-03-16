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


def parse_str_into_float(input_string: str) -> Optional[float]:
    """Parses int from string and converts to float"""
    if isinstance(input_string, float) or isinstance(input_string, int):
        return input_string
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


def convert_hour_to_datetime(hours) -> Optional[datetime.time]:
    """maps hour to datetime.time object"""
    if hours:
        hours = float(hours)
        mins = (hours % 1) * 60
        hours = hours / 1
        secs = (mins % 1) * 60
        mins = mins / 1
        return datetime.time(int(hours), int(mins), int(secs))


def convert_min_to_datetime(mins) -> Optional[datetime.time]:
    """maps mins to datetime.time object"""
    if mins:
        mins = parse_str_into_float(mins)
        return datetime.time(0, int(mins), 0)
    return None
