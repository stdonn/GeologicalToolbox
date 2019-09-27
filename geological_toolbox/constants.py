# -*- coding: UTF-8 -*-
"""
Definition of package wide constants.
"""

from ._version import __version__

project_version = __version__.split('.')
"""
Current project version
"""

float_precision = 0.001  # 1 mm
"""
precision for float comparison
"""
