"""Helper methods to map sharepoint fields to schema format"""
import re
import string
from typing import Optional

from aind_data_schema.procedures import Side


def map_hemisphere(response_hemisphere) -> Optional[Side]:
    """Maps response string to Side object"""
    if response_hemisphere == Side.LEFT.value:
        return Side.LEFT
    else:
        return Side.RIGHT


def convert_str_to_time(time_string):
    """converts duration"""
    return int(re.search(r"\d+", time_string).group())


def parse_str_into_float(input_string):
    """Parses int from string and converts to float"""
    if "," in input_string:
        input_string = input_string.split(",")[0]
    return float(input_string.strip(string.ascii_letters))