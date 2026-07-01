"""EngineeringOS Orchestrator — operational intelligence layer."""

from orchestrator.version import ORCHESTRATOR_VERSION

__version__ = ORCHESTRATOR_VERSION

__all__ = ["ORCHESTRATOR_VERSION", "__version__", "create_orchestrator"]


def create_orchestrator(*args, **kwargs):
    from orchestrator.factory import create_orchestrator as _create

    return _create(*args, **kwargs)
