from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from mersal.logging.standard_plugin import StandardLoggingPlugin
from mersal.plugins import Plugin
from structlog.contextvars import bind_contextvars, clear_contextvars, get_contextvars

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mersal.configuration import StandardConfigurator
    from mersal.structlog.config import StructlogLoggingConfig

__all__ = ("StructlogLoggingPlugin",)


@contextmanager
def pipeline_context(**kwargs: Any) -> Iterator[None]:
    # Only a received message is a fresh unit of work whose context should start
    # empty. An outgoing pipeline runs *inside* one - a handler sending/publishing,
    # or an HTTP request dispatching a command - so clearing there would wipe the
    # caller's context for the rest of its work.
    #
    # Either way, the caller's whole context is restored on exit - not just the
    # keys passed in here - since `LogContext.bind` (via `bind_contextvars`) may
    # add more during the invocation, which must not leak out of a nested send.
    saved = get_contextvars()
    if kwargs.get("pipeline") == "incoming":
        clear_contextvars()
    bind_contextvars(**kwargs)
    try:
        yield
    finally:
        clear_contextvars()
        bind_contextvars(**saved)


class StructlogLoggingPlugin(Plugin):
    def __init__(self, config: StructlogLoggingConfig) -> None:
        self._config = config
        self._plugin = StandardLoggingPlugin(
            self._config,
            pipeline_context=pipeline_context,
            context_binder=bind_contextvars,
        )

    def __call__(self, configurator: StandardConfigurator) -> None:
        self._plugin(configurator)
