"""
Timing obfuscation for C2 Phantom.

Provides randomized timing delays to evade network monitoring.
"""

import asyncio
import random
from typing import Optional


class TimingObfuscator:
    """Provides timing obfuscation for network operations."""

    def __init__(
        self,
        jitter_min: int = 500,
        jitter_max: int = 2000,
        enable_random_delays: bool = True,
    ) -> None:
        """
        Initialize timing obfuscator.

        Args:
            jitter_min: Minimum jitter in milliseconds
            jitter_max: Maximum jitter in milliseconds
            enable_random_delays: Enable random delays between operations
        """
        self.jitter_min = jitter_min
        self.jitter_max = jitter_max
        self.enable_random_delays = enable_random_delays

    def calculate_jitter(self) -> float:
        """
        Calculate random jitter delay.

        Returns:
            Jitter delay in seconds
        """
        if not self.enable_random_delays:
            return 0.0

        jitter_ms = random.randint(self.jitter_min, self.jitter_max)
        return jitter_ms / 1000.0

    async def apply_jitter(self) -> None:
        """Apply jitter delay asynchronously."""
        if self.enable_random_delays:
            delay = self.calculate_jitter()
            await asyncio.sleep(delay)

    def apply_jitter_sync(self) -> None:
        """Apply jitter delay synchronously."""
        if self.enable_random_delays:
            import time

            delay = self.calculate_jitter()
            time.sleep(delay)

    def randomize_interval(self, base_interval: float, variance: float = 0.3) -> float:
        """
        Randomize an interval to avoid pattern detection.

        Args:
            base_interval: Base interval in seconds
            variance: Variance factor (0.0 to 1.0)

        Returns:
            Randomized interval in seconds
        """
        if not self.enable_random_delays:
            return base_interval

        # Calculate random variance
        delta = base_interval * variance
        min_interval = base_interval - delta
        max_interval = base_interval + delta

        return random.uniform(min_interval, max_interval)

    async def randomized_sleep(self, base_seconds: float, variance: float = 0.3) -> None:
        """
        Sleep for a randomized duration.

        Args:
            base_seconds: Base sleep duration in seconds
            variance: Variance factor (0.0 to 1.0)
        """
        interval = self.randomize_interval(base_seconds, variance)
        await asyncio.sleep(interval)

    def get_random_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """
        Calculate exponential backoff with jitter.

        Args:
            attempt: Attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Backoff delay in seconds
        """
        # Exponential backoff
        delay = min(base_delay * (2**attempt), max_delay)

        # Add jitter
        if self.enable_random_delays:
            jitter = random.uniform(0, delay * 0.3)
            delay += jitter

        return delay
