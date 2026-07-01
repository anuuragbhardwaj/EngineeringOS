"""EngineeringOS Knowledge Platform."""

from knowledge.version import KNOWLEDGE_VERSION, __version__

__all__ = ["KNOWLEDGE_VERSION", "__version__", "create_knowledge_platform"]


def create_knowledge_platform(*args, **kwargs):
    from knowledge.factory import create_knowledge_platform as _create

    return _create(*args, **kwargs)
