"""Testing library"""

import re

from pydantic import __version__ as pyd_version

PYD_VERSION = re.match(r"(\d+.\d+).\d+", pyd_version).group(1)
