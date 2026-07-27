from importlib.metadata import version

from .config import StructlogLoggingConfig
from .plugin import StructlogLoggingPlugin

__all__ = [
    "StructlogLoggingConfig",
    "StructlogLoggingPlugin",
]


def __getattr__(name: str) -> str:
    if name != "__version__":
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    return version("mersal_structlog")
