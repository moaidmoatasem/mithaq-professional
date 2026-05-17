"""
Circuit Breaker - Prevents cascading failures in distributed systems.

Implements the Circuit Breaker pattern with:
- CLOSED -> OPEN -> HALF_OPEN -> CLOSED state transitions
- Configurable failure thresholds and recovery timeouts
- Fallback support
- Integration with AIMD capacity control
- Event hooks for monitoring

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Circuit is tripped, requests fail fast
- HALF_OPEN: Testing recovery with limited requests
"""

import asyncio
import logging
import platform
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Possible states of a circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors."""

    pass


class CircuitOpenError(CircuitBreakerError):
    """Raised when a circuit is open and request is rejected."""

    pass


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for a circuit breaker.

    Attributes:
        failure_threshold: Number of failures before tripping circuit
        recovery_timeout: Time in seconds to wait before attempting recovery
        half_open_max_requests: Max requests allowed in HALF_OPEN state
        slow_call_duration_threshold: Threshold for considering a call "slow" (seconds)
        slow_call_failure_threshold: Number of slow calls before tripping
        allowed_exceptions: Exceptions that count as failures (None = all)
        ignored_exceptions: Exceptions that don't count as failures
        name: Optional name for identification
    """

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_requests: int = 3
    slow_call_duration_threshold: float = 5.0
    slow_call_failure_threshold: int = 3
    allowed_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    ignored_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    name: str = "default"


@dataclass
class CircuitBreakerMetrics:
    """Metrics tracked by a circuit breaker."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    slow_calls: int = 0
    circuit_openings: int = 0
    circuit_closings: int = 0
    rejected_requests: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "slow_calls": self.slow_calls,
            "circuit_openings": self.circuit_openings,
            "circuit_closings": self.circuit_closings,
            "rejected_requests": self.rejected_requests,
            "success_rate": (
                self.successful_requests / self.total_requests if self.total_requests > 0 else 1.0
            ),
        }


class CircuitBreaker:
    """
    Circuit Breaker implementation for fault tolerance.

    Protects systems from cascading failures by:
    1. Monitoring for failures/slow calls
    2. Tripping circuit when thresholds exceeded
    3. Allowing recovery after timeout
    4. Supporting fallbacks when circuit is open

    Example:
        breaker = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10)
        )

        @breaker
        def risky_operation():
            ...

        # Or with context manager
        with breaker:
            risky_operation()

        # Or with fallback
        result = breaker.execute(risky_fn, fallback=default_fn)
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._metrics = CircuitBreakerMetrics()
        self._last_failure_time: Optional[float] = None
        self._failure_count: int = 0
        self._slow_call_count: int = 0
        self._half_open_success_count: int = 0
        self._half_open_failure_count: int = 0
        self._lock = Lock()

        self._on_open_callbacks: List[Callable[[], None]] = []
        self._on_close_callbacks: List[Callable[[], None]] = []
        self._on_half_open_callbacks: List[Callable[[], None]] = []

    @property
    def state(self) -> CircuitState:
        """Get current circuit state (thread-safe)."""
        with self._lock:
            return self._state

    @property
    def metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics (thread-safe)."""
        with self._lock:
            return CircuitBreakerMetrics(
                total_requests=self._metrics.total_requests,
                successful_requests=self._metrics.successful_requests,
                failed_requests=self._metrics.failed_requests,
                slow_calls=self._metrics.slow_calls,
                circuit_openings=self._metrics.circuit_openings,
                circuit_closings=self._metrics.circuit_closings,
                rejected_requests=self._metrics.rejected_requests,
            )

    def is_available(self) -> bool:
        """Check if circuit is available for requests."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._last_failure_time is not None:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed >= self.config.recovery_timeout:
                        self._transition_to_half_open()
                        return True
                return False
            return True

    def _is_failure_exception(self, exc: Exception) -> bool:
        """Check if an exception should count as a failure."""
        if self.config.ignored_exceptions and isinstance(exc, self.config.ignored_exceptions):
            return False

        if self.config.allowed_exceptions is not None:
            return isinstance(exc, self.config.allowed_exceptions)

        return True

    def _record_success(self, duration: float) -> None:
        """Record a successful call."""
        self._metrics.total_requests += 1
        self._metrics.successful_requests += 1
        self._failure_count = 0

        if self._state == CircuitState.HALF_OPEN:
            self._half_open_success_count += 1
            if self._half_open_success_count >= self.config.half_open_max_requests:
                self._transition_to_closed()

    def _record_failure(self, exc: Exception, duration: float) -> None:
        """Record a failed call."""
        self._metrics.total_requests += 1

        if not self._is_failure_exception(exc):
            self._metrics.successful_requests += 1
            return

        self._metrics.failed_requests += 1
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to_open()
        elif self._state == CircuitState.HALF_OPEN:
            self._half_open_failure_count += 1
            self._transition_to_open()

    def _record_slow_call(self, duration: float) -> None:
        """Record a slow call (may trip circuit if threshold exceeded)."""
        self._metrics.slow_calls += 1
        self._slow_call_count += 1

        if self._state == CircuitState.CLOSED:
            if self._slow_call_count >= self.config.slow_call_failure_threshold:
                self._transition_to_open()

    def _persist(self) -> None:
        """Best-effort SQLite persistence of current state (called outside lock)."""
        if self.config.name == "default":
            return
        try:
            from cherenkov.core.storage.database import init_db, save_cb_state
            init_db()
            save_cb_state(
                self.config.name,
                self._state.value,
                self._failure_count,
                self._last_failure_time,
            )
        except Exception as exc:
            logger.debug("CB state persist skipped: %s", exc)

    def _transition_to_open(self) -> None:
        """Transition from CLOSED/HALF_OPEN to OPEN state."""
        old_state = self._state
        self._state = CircuitState.OPEN
        self._metrics.circuit_openings += 1
        self._slow_call_count = 0
        self._half_open_success_count = 0
        self._half_open_failure_count = 0

        logger.warning(
            f"Circuit '{self.config.name}' transitioned from {old_state.value} to OPEN "
            f"(failures={self._failure_count})"
        )
        self._persist()

        for callback in self._on_open_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in on_open callback: {e}")

    def _transition_to_half_open(self) -> None:
        """Transition from OPEN to HALF_OPEN state."""
        self._state = CircuitState.HALF_OPEN
        self._half_open_success_count = 0
        self._half_open_failure_count = 0
        self._failure_count = 0

        logger.info(f"Circuit '{self.config.name}' transitioned to HALF_OPEN (testing recovery)")
        self._persist()

        for callback in self._on_half_open_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in on_half_open callback: {e}")

    def _transition_to_closed(self) -> None:
        """Transition from HALF_OPEN to CLOSED state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._slow_call_count = 0
        self._half_open_success_count = 0
        self._half_open_failure_count = 0
        self._metrics.circuit_closings += 1

        logger.info(f"Circuit '{self.config.name}' transitioned to CLOSED (recovery successful)")
        self._persist()

        for callback in self._on_close_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in on_close callback: {e}")

    def on_open(self, callback: Callable[[], None]) -> None:
        """Register a callback for when circuit opens."""
        self._on_open_callbacks.append(callback)

    def on_close(self, callback: Callable[[], None]) -> None:
        """Register a callback for when circuit closes."""
        self._on_close_callbacks.append(callback)

    def on_half_open(self, callback: Callable[[], None]) -> None:
        """Register a callback for when circuit enters half-open."""
        self._on_half_open_callbacks.append(callback)

    def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        fallback: Optional[Callable[..., Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            fallback: Optional fallback function to call if circuit is open
            **kwargs: Keyword arguments for func

        Returns:
            Result of func or fallback

        Raises:
            CircuitOpenError: If circuit is open and no fallback provided
            Exception: Any exception from func (if allowed)
        """
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._last_failure_time is not None:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed >= self.config.recovery_timeout:
                        self._transition_to_half_open()
                    else:
                        self._metrics.rejected_requests += 1
                        if fallback:
                            return fallback(*args, **kwargs)
                        raise CircuitOpenError(
                            f"Circuit '{self.config.name}' is OPEN. "
                            f"Try again in {self.config.recovery_timeout - elapsed:.1f}s"
                        )
                else:
                    self._metrics.rejected_requests += 1
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise CircuitOpenError(f"Circuit '{self.config.name}' is OPEN")

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            with self._lock:
                if duration >= self.config.slow_call_duration_threshold:
                    self._record_slow_call(duration)
                self._record_success(duration)

            return result
        except Exception as e:
            duration = time.time() - start_time

            with self._lock:
                self._record_failure(e, duration)

            raise

    async def execute_async(
        self,
        func: Callable[..., Any],
        *args: Any,
        fallback: Optional[Callable[..., Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute an async function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            fallback: Optional fallback function
            **kwargs: Keyword arguments for func

        Returns:
            Result of func or fallback
        """
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._last_failure_time is not None:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed >= self.config.recovery_timeout:
                        self._transition_to_half_open()
                    else:
                        self._metrics.rejected_requests += 1
                        if fallback:
                            if asyncio.iscoroutinefunction(fallback):
                                return await fallback(*args, **kwargs)
                            return fallback(*args, **kwargs)
                        raise CircuitOpenError(
                            f"Circuit '{self.config.name}' is OPEN. "
                            f"Try again in {self.config.recovery_timeout - elapsed:.1f}s"
                        )
                else:
                    self._metrics.rejected_requests += 1
                    if fallback:
                        if asyncio.iscoroutinefunction(fallback):
                            return await fallback(*args, **kwargs)
                        return fallback(*args, **kwargs)
                    raise CircuitOpenError(f"Circuit '{self.config.name}' is OPEN")

        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            duration = time.time() - start_time

            with self._lock:
                if duration >= self.config.slow_call_duration_threshold:
                    self._record_slow_call(duration)
                self._record_success(duration)

            return result
        except Exception as e:
            duration = time.time() - start_time

            with self._lock:
                self._record_failure(e, duration)

            raise

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to wrap a function with circuit breaker protection."""
        if asyncio.iscoroutinefunction(func):

            async def wrapper_async(*args: Any, **kwargs: Any) -> Any:
                return await self.execute_async(func, *args, **kwargs)

            return wrapper_async
        else:

            def wrapper_sync(*args: Any, **kwargs: Any) -> Any:
                return self.execute(func, *args, **kwargs)

            return wrapper_sync

    def __enter__(self) -> "CircuitBreaker":
        """Context manager entry - check if circuit is available."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._last_failure_time is not None:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed >= self.config.recovery_timeout:
                        self._transition_to_half_open()
                    else:
                        self._metrics.rejected_requests += 1
                        raise CircuitOpenError(
                            f"Circuit '{self.config.name}' is OPEN. "
                            f"Try again in {self.config.recovery_timeout - elapsed:.1f}s"
                        )
                else:
                    self._metrics.rejected_requests += 1
                    raise CircuitOpenError(f"Circuit '{self.config.name}' is OPEN")

        self._context_start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit - record success or failure."""
        duration = time.time() - self._context_start_time

        with self._lock:
            if exc_type is None:
                if duration >= self.config.slow_call_duration_threshold:
                    self._record_slow_call(duration)
                self._record_success(duration)
            else:
                self._record_failure(exc_val, duration)

        return False

    def reset(self) -> None:
        """Reset the circuit breaker to CLOSED state with cleared metrics."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._slow_call_count = 0
            self._half_open_success_count = 0
            self._half_open_failure_count = 0
            self._last_failure_time = None
            self._metrics = CircuitBreakerMetrics()

    def force_open(self) -> None:
        """Force the circuit to OPEN state (for testing/maintenance)."""
        with self._lock:
            if self._state != CircuitState.OPEN:
                self._transition_to_open()

    def force_closed(self) -> None:
        """Force the circuit to CLOSED state (for testing/maintenance)."""
        with self._lock:
            self._transition_to_closed()


class Meissner(CircuitBreaker):
    """
    Sovereign implementation of the Circuit Breaker pattern.
    Enforces kernel-level network isolation (Fail-Closed) when tripped.

    Physical-Physics Axiom:
    When a Sovereign Breach is detected (failure threshold exceeded),
    the system must physically drop all egress to prevent data exfiltration.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        super().__init__(config)
        self._isolation_active = False
        self._on_open_callbacks = []

    def on_open(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when the circuit opens."""
        self._on_open_callbacks.append(callback)

    def _transition_to_open(self) -> None:
        """Transition to OPEN and enforce fail-closed isolation."""
        super()._transition_to_open()
        self.fail_closed()
        for callback in self._on_open_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in Meissner on_open callback: {e}")

        # Broadcast the state change
        try:
            from cherenkov.api.main import _broadcast

            loop = asyncio.get_running_loop()
            loop.create_task(
                _broadcast(
                    {"type": "circuit_breaker", "state": "OPEN", "reason": "threshold_exceeded"}
                )
            )
        except (ImportError, RuntimeError):
            # E.g. no event loop running, ignore
            pass

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED and restore network connectivity."""
        super()._transition_to_closed()
        self.fail_open()

    def fail_closed(self) -> None:
        """
        Enforce physical egress isolation using OS-level network drops.
        """
        if self._isolation_active:
            return

        system = platform.system().lower()
        logger.critical(f"MEISSNER FAIL-CLOSED TRIGGERED: Dropping all egress on {system}")

        try:
            if system == "linux":
                # Use iptables to drop all output traffic
                # -I OUTPUT 1 inserts at the top of the chain
                subprocess.run(["iptables", "-I", "OUTPUT", "1", "-j", "DROP"], check=True)
                logger.info("Linux iptables: Egress dropped successfully.")
            elif system == "windows":
                # Use netsh to block all outgoing traffic
                # First ensure firewall is on, then set default to block outbound
                subprocess.run(
                    ["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True
                )
                subprocess.run(
                    [
                        "netsh",
                        "advfirewall",
                        "set",
                        "allprofiles",
                        "firewallpolicy",
                        "blockinbound,blockoutbound",
                    ],
                    check=True,
                )
                logger.info("Windows Firewall: Outbound traffic blocked successfully.")
            else:
                logger.error(f"Unsupported OS for Meissner isolation: {system}")

            self._isolation_active = True
        except subprocess.CalledProcessError as e:
            logger.error(f"Sovereign Breach: Failed to enforce kernel isolation: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Meissner isolation: {e}")

    def fail_open(self) -> None:
        """
        Restore network connectivity after recovery or manual override.
        """
        if not self._isolation_active:
            return

        system = platform.system().lower()
        logger.info(f"MEISSNER RECOVERY: Restoring egress on {system}")

        try:
            if system == "linux":
                # Remove the drop rule
                subprocess.run(["iptables", "-D", "OUTPUT", "-j", "DROP"], check=True)
                logger.info("Linux iptables: Egress restored.")
            elif system == "windows":
                # Restore default outbound behavior (allow)
                subprocess.run(
                    [
                        "netsh",
                        "advfirewall",
                        "set",
                        "allprofiles",
                        "firewallpolicy",
                        "blockinbound,allowoutbound",
                    ],
                    check=True,
                )
                logger.info("Windows Firewall: Outbound traffic allowed.")

            self._isolation_active = False
        except Exception as e:
            logger.error(f"Meissner Recovery Error: Failed to restore connectivity: {e}")


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Provides centralized access to circuit breakers by name.
    """

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = Lock()

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        with self._lock:
            return self._breakers.get(name)

    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Get an existing circuit breaker or create one, restoring persisted state."""
        with self._lock:
            if name not in self._breakers:
                use_config = config or CircuitBreakerConfig(name=name)
                breaker = CircuitBreaker(use_config)
                # Restore state that survived the last process restart
                try:
                    from cherenkov.core.storage.database import load_cb_state
                    saved = load_cb_state(name)
                    if saved and saved["state"] in (s.value for s in CircuitState):
                        breaker._state = CircuitState(saved["state"])
                        breaker._failure_count = saved["failure_count"]
                        breaker._last_failure_time = saved["last_failure_time"]
                        logger.info("CB '%s' restored to %s (failures=%d)", name, saved["state"], saved["failure_count"])
                except Exception as exc:
                    logger.debug("CB state restore skipped for '%s': %s", name, exc)
                self._breakers[name] = breaker
            return self._breakers[name]

    def register(self, name: str, breaker: CircuitBreaker) -> None:
        """Register a circuit breaker."""
        with self._lock:
            self._breakers[name] = breaker

    def get_all(self) -> Dict[str, CircuitBreaker]:
        """Get all registered circuit breakers."""
        with self._lock:
            return dict(self._breakers)

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all registered circuit breakers."""
        with self._lock:
            return {name: breaker.metrics.to_dict() for name, breaker in self._breakers.items()}

    def get_all_states(self) -> Dict[str, str]:
        """Get current state for all registered circuit breakers."""
        with self._lock:
            return {name: breaker.state.value for name, breaker in self._breakers.items()}


default_registry = CircuitBreakerRegistry()
meissner_hub = Meissner(CircuitBreakerConfig(name="meissner_hub", failure_threshold=3))


def circuit_breaker(
    name: str = "default",
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    use_meissner: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory for circuit breaker.

    Args:
        name: Name of the breaker
        failure_threshold: Number of failures before opening
        recovery_timeout: Time to wait before half-open
        use_meissner: If True, uses Meissner (kernel isolation) instead of standard breaker
    """
    config = CircuitBreakerConfig(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
    )

    with default_registry._lock:
        if name not in default_registry._breakers:
            if use_meissner:
                default_registry._breakers[name] = Meissner(config)
            else:
                default_registry._breakers[name] = CircuitBreaker(config)

    return default_registry._breakers[name]


def fail_closed() -> None:
    """Trigger global Meissner fail-closed isolation."""
    meissner_hub.fail_closed()


def fail_open() -> None:
    """Restore global network connectivity."""
    meissner_hub.fail_open()
