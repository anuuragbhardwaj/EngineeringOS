"""Company Core — Framework API implementation for EngineeringOS."""

from company_core.api.framework import FrameworkAPI
from company_core.version import FRAMEWORK_API_VERSION, FRAMEWORK_VERSION

__version__ = "0.1.0"

__all__ = [
    "FRAMEWORK_API_VERSION",
    "FRAMEWORK_VERSION",
    "FrameworkAPI",
    "__version__",
]
