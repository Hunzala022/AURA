"""Opt-in per-task inference measurements; no persistent logging by default."""
from contextlib import contextmanager
from contextvars import ContextVar

_trace = ContextVar('aura_planning_trace', default=None)


@contextmanager
def collect_planning_trace():
    calls = []
    token = _trace.set(calls)
    try:
        yield calls
    finally:
        _trace.reset(token)


def record_call(record):
    calls = _trace.get()
    if calls is not None:
        calls.append(record)
