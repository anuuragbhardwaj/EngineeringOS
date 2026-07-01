"""EngineeringOS Source Control Platform."""

from source_control.version import SOURCE_CONTROL_VERSION, __version__

__all__ = ["SOURCE_CONTROL_VERSION", "__version__", "create_source_control_platform"]


def create_source_control_platform(*args, **kwargs):
    from source_control.factory import create_source_control_platform as _create

    return _create(*args, **kwargs)
