"""Company Kernel — Runtime Engine v1."""

from runtime_engine.version import CONTRACT_VERSION, SCHEMA_VERSION

__version__ = "0.1.0"
__all__ = ["CONTRACT_VERSION", "SCHEMA_VERSION", "__version__"]


def create_runtime(*args, **kwargs):
    from runtime_engine.factory import create_runtime as _create

    return _create(*args, **kwargs)


def Runtime():
    from runtime_engine.runtime.facade import Runtime as _Runtime

    return _Runtime
