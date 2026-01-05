"""
Event system for C2 Phantom.

Provides pub/sub event handling for asynchronous operations.
"""

import asyncio
from typing import Any, Callable, Dict, List
from collections import defaultdict
from datetime import datetime


class Event:
    """Represents an event."""

    def __init__(self, name: str, data: Any = None, timestamp: datetime = None) -> None:
        """
        Initialize event.

        Args:
            name: Event name
            data: Event data
            timestamp: Event timestamp
        """
        self.name = name
        self.data = data
        self.timestamp = timestamp or datetime.now()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Event(name='{self.name}', timestamp={self.timestamp})"


class EventBus:
    """Event bus for pub/sub messaging."""

    def __init__(self) -> None:
        """Initialize event bus."""
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_handlers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Callable) -> None:
        """
        Subscribe to an event.

        Args:
            event_name: Event name to subscribe to
            handler: Handler function
        """
        if asyncio.iscoroutinefunction(handler):
            self._async_handlers[event_name].append(handler)
        else:
            self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """
        Unsubscribe from an event.

        Args:
            event_name: Event name
            handler: Handler function to remove
        """
        if handler in self._handlers[event_name]:
            self._handlers[event_name].remove(handler)
        if handler in self._async_handlers[event_name]:
            self._async_handlers[event_name].remove(handler)

    def publish(self, event: Event) -> None:
        """
        Publish an event (synchronous).

        Args:
            event: Event to publish
        """
        for handler in self._handlers[event.name]:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")

    async def publish_async(self, event: Event) -> None:
        """
        Publish an event (asynchronous).

        Args:
            event: Event to publish
        """
        # Handle synchronous handlers
        for handler in self._handlers[event.name]:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")

        # Handle asynchronous handlers
        tasks = []
        for handler in self._async_handlers[event.name]:
            tasks.append(asyncio.create_task(handler(event)))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def clear(self) -> None:
        """Clear all event handlers."""
        self._handlers.clear()
        self._async_handlers.clear()


# Global event bus instance
event_bus = EventBus()
