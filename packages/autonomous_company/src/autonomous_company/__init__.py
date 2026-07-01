"""EngineeringOS Autonomous Company Platform."""

from autonomous_company.version import AUTONOMOUS_VERSION, __version__

__all__ = ["AUTONOMOUS_VERSION", "__version__", "create_autonomous_company_platform"]


def create_autonomous_company_platform(*args, **kwargs):
    from autonomous_company.factory import create_autonomous_company_platform as _create

    return _create(*args, **kwargs)
