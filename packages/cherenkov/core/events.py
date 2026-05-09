"""
Event Bus for decoupled system interactions (Event-Driven Architecture).
Allows components to subscribe to and publish events without tight coupling.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """A lightweight publisher-subscriber event bus for the system."""

    def __init__(self):
        # Maps event_name to a list of subscriber callbacks
        self._subscribers: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_name: str, callback: Callable[..., Any]) -> None:
        """Subscribe a callback to a specific event name."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., Any]) -> None:
        """Unsubscribe a callback from an event name."""
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(callback)
            except ValueError:
                pass

    def publish(self, event_name: str, **kwargs: Any) -> None:
        """Publish an event to all subscribers synchronously."""
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(
                        f"Error executing callback {callback.__name__} for event {event_name}: {e}"
                    )

    async def publish_async(self, event_name: str, **kwargs: Any) -> None:
        """Publish an event to all subscribers asynchronously."""
        if event_name in self._subscribers:
            tasks = []
            for callback in self._subscribers[event_name]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(
                        asyncio.create_task(self._safe_await(callback, event_name, **kwargs))
                    )
                else:
                    # Run sync callback in an executor or just run it synchronously
                    try:
                        callback(**kwargs)
                    except Exception as e:
                        logger.error(
                            f"Error executing sync callback {callback.__name__} for event {event_name}: {e}"
                        )
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_await(
        self, callback: Callable[..., Any], event_name: str, **kwargs: Any
    ) -> None:
        """Helper to safely await async callbacks."""
        try:
            await callback(**kwargs)
        except Exception as e:
            logger.error(
                f"Error executing async callback {callback.__name__} for event {event_name}: {e}"
            )


# Global Event Bus instance
event_bus = EventBus()
