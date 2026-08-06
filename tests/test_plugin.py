from __future__ import annotations

from mersal.structlog import StructlogLoggingConfig, StructlogLoggingPlugin


def test_plugin_property_builds_structlog_plugin() -> None:
    config = StructlogLoggingConfig()

    plugin = config.plugin

    assert isinstance(plugin, StructlogLoggingPlugin)
