from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from structlog.contextvars import bound_contextvars, clear_contextvars

from mersal.logging.standard_plugin import StandardLoggingPlugin
from mersal.plugins import Plugin

if TYPE_CHECKING:
    from mersal.configuration import StandardConfigurator
    from mersal_structlog.config import StructlogLoggingConfig

__all__ = ("StructlogLoggingPlugin",)


@contextmanager
def pipeline_context(**kwargs):
    clear_contextvars()
    with bound_contextvars(**kwargs):
        yield


class StructlogLoggingPlugin(Plugin):
    def __init__(self, config: StructlogLoggingConfig) -> None:
        self._config = config
        self._plugin = StandardLoggingPlugin(self._config, pipeline_context=pipeline_context)

    def __call__(self, configurator: StandardConfigurator) -> None:
        self._plugin(configurator)
