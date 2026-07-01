"""EngineeringOS Installation & Lifecycle Platform."""

from company_lifecycle.version import LIFECYCLE_VERSION

__version__ = LIFECYCLE_VERSION

__all__ = ["LIFECYCLE_VERSION", "__version__", "create_lifecycle_platform", "LifecyclePlatform"]


def __getattr__(name: str):
    if name == "create_lifecycle_platform":
        from company_lifecycle.factory import create_lifecycle_platform as _create

        return _create
    if name == "LifecyclePlatform":
        from company_lifecycle.platform import LifecyclePlatform as _Platform

        return _Platform
    raise AttributeError(name)
