"""Hermes plugin registration for the rp-compute LCD."""

import atexit
from functools import partial
import os

from .bridge import HOOKS, Publisher, SOCKET_PATH


_publisher = None


def register(ctx):
    global _publisher
    if _publisher is not None:
        _publisher.close()
    _publisher = Publisher(os.environ.get("RP_COMPUTE_ACTIVITY_SOCKET", SOCKET_PATH))
    for event in HOOKS:
        ctx.register_hook(event, partial(_publisher.event, event))
    _publisher.start()
    atexit.register(_publisher.close)
