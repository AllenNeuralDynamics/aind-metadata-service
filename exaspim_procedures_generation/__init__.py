"""ExaSPIM Procedures Generation.

Generates procedures.json files compliant with aind-data-schema>=2.0
from ExaSPIM Smartsheet metadata.
"""

__version__ = "0.1.0"

from exaspim_procedures_generation.main import generate_procedures

__all__ = ["generate_procedures", "__version__"]
