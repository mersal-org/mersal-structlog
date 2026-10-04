from __future__ import annotations

from structlog.contextvars import bind_contextvars, clear_contextvars, get_contextvars

from mersal.structlog import StructlogLoggingConfig, StructlogLoggingPlugin
from mersal.structlog.plugin import pipeline_context


def test_plugin_property_builds_structlog_plugin() -> None:
    config = StructlogLoggingConfig()

    plugin = config.plugin

    assert isinstance(plugin, StructlogLoggingPlugin)


def test_incoming_pipeline_context_starts_from_a_clean_context() -> None:
    clear_contextvars()
    bind_contextvars(leftover="from a previous unit of work")

    with pipeline_context(pipeline="incoming", message_id="m1"):
        assert get_contextvars() == {"pipeline": "incoming", "message_id": "m1"}

    clear_contextvars()


def test_outgoing_pipeline_context_restores_the_callers_context() -> None:
    clear_contextvars()
    with pipeline_context(pipeline="incoming", message_id="incoming-1", message_type="DoThing"):
        bind_contextvars(gradebook_id="g1")

        with pipeline_context(pipeline="outgoing", message_id="outgoing-1", destinations="q"):
            assert get_contextvars() == {
                "pipeline": "outgoing",
                "message_id": "outgoing-1",
                "message_type": "DoThing",
                "destinations": "q",
                "gradebook_id": "g1",
            }

        assert get_contextvars() == {
            "pipeline": "incoming",
            "message_id": "incoming-1",
            "message_type": "DoThing",
            "gradebook_id": "g1",
        }

    clear_contextvars()


def test_fields_bound_during_an_outgoing_pipeline_do_not_leak_to_the_caller() -> None:
    clear_contextvars()
    with pipeline_context(pipeline="incoming", message_id="incoming-1"):
        with pipeline_context(pipeline="outgoing", message_id="outgoing-1"):
            bind_contextvars(bound_mid_send="x")

        assert get_contextvars() == {"pipeline": "incoming", "message_id": "incoming-1"}

    clear_contextvars()
