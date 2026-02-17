from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import structlog
from structlog.dev import RichTracebackFormatter

from mersal.logging.config import GetLogger, LoggingConfig

if TYPE_CHECKING:
    from collections.abc import Callable

    from structlog.types import BindableLogger, Processor, WrappedLogger

    from mersal.logging import Logger
    from mersal_structlog.plugin import StructlogLoggingPlugin

__all__ = ("StructlogLoggingConfig",)


@dataclass(kw_only=True)
class StructlogLoggingConfig(LoggingConfig):
    logger_factory: Callable[..., WrappedLogger] | None = None
    processors: list[Processor] | None = None
    wrapper_class: type[BindableLogger] | None = field(default=None)  # pyright: ignore
    cache_logger_on_first_use: bool = field(default=True)
    enable_canonical_log_lines: bool = False
    canonical_log_on_events: list[str] | None = field(default=None)
    pretty_print_tty: bool = field(default=True)
    json_serializer: Callable[..., str | bytes] | None = None

    def __post_init__(self) -> None:
        if self.processors is None:
            self.processors = self._default_processors(as_json=self._as_json(), json_serializer=self.json_serializer)
        if self.logger_factory is None:
            self.logger_factory = self._default_logger_factory(as_json=self._as_json())

    @property
    def plugin(self) -> StructlogLoggingPlugin:
        from mersal_structlog.plugin import StructlogLoggingPlugin

        return StructlogLoggingPlugin(self)

    def configure(self) -> GetLogger:
        structlog.configure(
            cache_logger_on_first_use=self.cache_logger_on_first_use,
            processors=self.processors,
            logger_factory=self.logger_factory,
            wrapper_class=self.wrapper_class,
        )
        return structlog.get_logger

    @staticmethod
    def set_level(logger: Logger, level: int) -> None:
        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))

    def _as_json(self) -> bool:
        return not (sys.stderr.isatty() and self.pretty_print_tty)

    def _default_logger_factory(self, as_json: bool) -> Callable[..., WrappedLogger] | None:
        if as_json:
            return structlog.BytesLoggerFactory()
        return structlog.WriteLoggerFactory()

    def _default_processors(
        self,
        as_json: bool,
        json_serializer: Callable[..., str | bytes] | None = None,
        serializer_kw: dict[str, Any] | None = None,
    ) -> list[Processor]:  # pyright: ignore
        if as_json:
            json_renderer_kwargs = {}
            if json_serializer:
                json_renderer_kwargs["serializer"] = json_serializer
            if serializer_kw:
                json_renderer_kwargs |= serializer_kw
            return [
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer(**json_renderer_kwargs),
            ]
        return [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(
                colors=True, exception_formatter=RichTracebackFormatter(max_frames=1, show_locals=False, width=80)
            ),
        ]
