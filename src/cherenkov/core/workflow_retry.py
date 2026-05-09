"""
Workflow Retry Manager - Smart retry with exponential backoff and jitter.

Provides configurable retry policies for workflow tasks and agent operations.
Integrates with existing AIMD pattern for capacity-aware retries.

Features:
- Exponential backoff with jitter
- Configurable max attempts and delays
- Retry on specific exceptions only
- Callbacks for retry events
- Integration with AIMD capacity control
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

logger = logging.getLogger(__name__)


class RetryOutcome(str, Enum):
    """Outcome of a retry attempt."""

    SUCCESS = "success"
    RETRY = "retry"
    FAIL = "fail"


class BackoffStrategy(str, Enum):
    """Backoff calculation strategies."""

    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class RetryPolicy:
    """
    Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts (including first try)
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries (caps exponential growth)
        backoff_strategy: Strategy for calculating delays
        jitter: Whether to add random jitter to delays
        retry_exceptions: Tuple of exception types to retry on (None = all)
        fail_exceptions: Tuple of exception types to fail immediately on
        timeout: Optional timeout per attempt in seconds
        callback: Optional callback on each retry attempt
    """

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    jitter: bool = True
    retry_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    fail_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    timeout: Optional[float] = None
    callback: Optional[Callable[[int, Exception, float], None]] = None

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.

        Args:
            attempt: 0-based attempt number (first retry is attempt 0)

        Returns:
            Delay in seconds before next retry
        """
        if self.backoff_strategy == BackoffStrategy.FIXED:
            delay = self.initial_delay
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.initial_delay * (attempt + 1)
        elif self.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.initial_delay * (2**attempt)
        else:
            delay = self.initial_delay

        delay = min(delay, self.max_delay)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return max(0.0, delay)

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """
        Determine if we should retry based on exception and attempt count.

        Args:
            attempt: Current attempt number (0-based)
            exception: The exception that occurred

        Returns:
            True if should retry, False if should fail
        """
        if attempt >= self.max_attempts - 1:
            return False

        if self.fail_exceptions and isinstance(exception, self.fail_exceptions):
            return False

        if self.retry_exceptions is not None:
            return isinstance(exception, self.retry_exceptions)

        return True


@dataclass
class RetryResult:
    """
    Result of a retry-managed operation.

    Attributes:
        success: Whether the operation succeeded
        result: The result value (if success)
        exception: The last exception (if failed)
        attempts: Number of attempts made
        total_delay: Total time spent waiting between retries
        last_attempt_at: ISO timestamp of last attempt
    """

    success: bool
    result: Optional[Any] = None
    exception: Optional[Exception] = None
    attempts: int = 0
    total_delay: float = 0.0
    last_attempt_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "result": str(self.result) if self.result is not None else None,
            "exception_type": type(self.exception).__name__ if self.exception else None,
            "exception_msg": str(self.exception) if self.exception else None,
            "attempts": self.attempts,
            "total_delay": self.total_delay,
            "last_attempt_at": self.last_attempt_at,
        }


class WorkflowRetryManager:
    """
    Manager for retry operations in workflow execution.

    Provides both sync and async execution with configurable policies.
    """

    def __init__(self, default_policy: Optional[RetryPolicy] = None):
        self.default_policy = default_policy or RetryPolicy()
        self._stats: Dict[str, Dict[str, Any]] = {
            "total_operations": 0,
            "success_on_first": 0,
            "succeeded_after_retry": 0,
            "failed_permanently": 0,
            "total_retries": 0,
        }

    def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        policy: Optional[RetryPolicy] = None,
        **kwargs: Any,
    ) -> RetryResult:
        """
        Execute a function with retry logic (synchronous).

        Args:
            func: Function to execute
            *args: Positional arguments for func
            policy: Optional custom retry policy
            **kwargs: Keyword arguments for func

        Returns:
            RetryResult with outcome details
        """
        use_policy = policy or self.default_policy
        last_exception: Optional[Exception] = None
        total_delay = 0.0
        attempt = 0

        self._stats["total_operations"] += 1

        while attempt < use_policy.max_attempts:
            try:
                result = func(*args, **kwargs)
                self._stats["success_on_first" if attempt == 0 else "succeeded_after_retry"] += 1
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_delay=total_delay,
                    last_attempt_at=datetime.now(timezone.utc).isoformat(),
                )
            except Exception as e:
                last_exception = e
                logger.debug(f"Attempt {attempt + 1} failed: {e}")

                if not use_policy.should_retry(attempt, e):
                    break

                delay = use_policy.calculate_delay(attempt)
                total_delay += delay
                self._stats["total_retries"] += 1

                if use_policy.callback:
                    try:
                        use_policy.callback(attempt, e, delay)
                    except Exception:
                        pass

                logger.debug(f"Waiting {delay:.2f}s before retry {attempt + 2}")
                time.sleep(delay)
                attempt += 1

        self._stats["failed_permanently"] += 1
        return RetryResult(
            success=False,
            exception=last_exception,
            attempts=attempt + 1,
            total_delay=total_delay,
            last_attempt_at=datetime.now(timezone.utc).isoformat(),
        )

    async def execute_async(
        self,
        func: Callable[..., Any],
        *args: Any,
        policy: Optional[RetryPolicy] = None,
        **kwargs: Any,
    ) -> RetryResult:
        """
        Execute a function with retry logic (asynchronous).

        Args:
            func: Async or sync function to execute
            *args: Positional arguments for func
            policy: Optional custom retry policy
            **kwargs: Keyword arguments for func

        Returns:
            RetryResult with outcome details
        """
        use_policy = policy or self.default_policy
        last_exception: Optional[Exception] = None
        total_delay = 0.0
        attempt = 0

        self._stats["total_operations"] += 1

        while attempt < use_policy.max_attempts:
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                self._stats["success_on_first" if attempt == 0 else "succeeded_after_retry"] += 1
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_delay=total_delay,
                    last_attempt_at=datetime.now(timezone.utc).isoformat(),
                )
            except Exception as e:
                last_exception = e
                logger.debug(f"Attempt {attempt + 1} failed: {e}")

                if not use_policy.should_retry(attempt, e):
                    break

                delay = use_policy.calculate_delay(attempt)
                total_delay += delay
                self._stats["total_retries"] += 1

                if use_policy.callback:
                    try:
                        if asyncio.iscoroutinefunction(use_policy.callback):
                            await use_policy.callback(attempt, e, delay)
                        else:
                            use_policy.callback(attempt, e, delay)
                    except Exception:
                        pass

                logger.debug(f"Waiting {delay:.2f}s before retry {attempt + 2}")
                await asyncio.sleep(delay)
                attempt += 1

        self._stats["failed_permanently"] += 1
        return RetryResult(
            success=False,
            exception=last_exception,
            attempts=attempt + 1,
            total_delay=total_delay,
            last_attempt_at=datetime.now(timezone.utc).isoformat(),
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        stats = dict(self._stats)
        if stats["total_operations"] > 0:
            stats["retry_rate"] = stats["total_retries"] / stats["total_operations"]
            stats["success_rate"] = (
                (stats["success_on_first"] + stats["succeeded_after_retry"])
                / stats["total_operations"]
            )
        return stats

    def reset_stats(self) -> None:
        """Reset statistics to zero."""
        self._stats = {
            "total_operations": 0,
            "success_on_first": 0,
            "succeeded_after_retry": 0,
            "failed_permanently": 0,
            "total_retries": 0,
        }


def create_retry_policy(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: str = "exponential",
    jitter: bool = True,
    retry_on: Optional[List[Type[Exception]]] = None,
    fail_on: Optional[List[Type[Exception]]] = None,
) -> RetryPolicy:
    """
    Convenience function to create a RetryPolicy.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        strategy: "fixed", "linear", or "exponential"
        jitter: Whether to add random jitter
        retry_on: List of exception types to retry on
        fail_on: List of exception types to fail immediately on

    Returns:
        Configured RetryPolicy
    """
    strategy_map = {
        "fixed": BackoffStrategy.FIXED,
        "linear": BackoffStrategy.LINEAR,
        "exponential": BackoffStrategy.EXPONENTIAL,
    }

    return RetryPolicy(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        backoff_strategy=strategy_map.get(strategy.lower(), BackoffStrategy.EXPONENTIAL),
        jitter=jitter,
        retry_exceptions=tuple(retry_on) if retry_on else None,
        fail_exceptions=tuple(fail_on) if fail_on else None,
    )


default_retry_manager = WorkflowRetryManager()


def with_retry(
    policy: Optional[RetryPolicy] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for retry-managed functions.

    Usage:
        @with_retry()
        def my_flaky_function():
            ...

        @with_retry(policy=RetryPolicy(max_attempts=5))
        async def my_async_function():
            ...
    """
    use_policy = policy or RetryPolicy()
    manager = WorkflowRetryManager(use_policy)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):

            async def wrapper_async(*args: Any, **kwargs: Any) -> Any:
                result = await manager.execute_async(func, *args, policy=use_policy, **kwargs)
                if result.success:
                    return result.result
                elif result.exception:
                    raise result.exception
                else:
                    raise RuntimeError("Operation failed without exception")

            return wrapper_async
        else:

            def wrapper_sync(*args: Any, **kwargs: Any) -> Any:
                result = manager.execute(func, *args, policy=use_policy, **kwargs)
                if result.success:
                    return result.result
                elif result.exception:
                    raise result.exception
                else:
                    raise RuntimeError("Operation failed without exception")

            return wrapper_sync

    return decorator
