import asyncio

import pytest

from cherenkov.core.events import EventBus


def test_subscribe_and_publish():
    bus = EventBus()
    received = []

    def callback(data):
        received.append(data)

    bus.subscribe("test_event", callback)
    bus.publish("test_event", data="hello")

    assert len(received) == 1
    assert received[0] == "hello"


def test_unsubscribe():
    bus = EventBus()
    received = []

    def callback(data):
        received.append(data)

    bus.subscribe("test_event", callback)
    bus.unsubscribe("test_event", callback)
    bus.publish("test_event", data="hello")

    assert len(received) == 0


@pytest.mark.asyncio
async def test_publish_async():
    bus = EventBus()
    received = []

    async def async_callback(data):
        await asyncio.sleep(0.01)
        received.append(data)

    bus.subscribe("test_event", async_callback)
    await bus.publish_async("test_event", data="async_hello")

    assert len(received) == 1
    assert received[0] == "async_hello"
