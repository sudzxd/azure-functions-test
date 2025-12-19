"""Context for capturing output bindings during function execution."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
from dataclasses import dataclass, field
from typing import Any, TypeVar

# Third-party
from azure.functions import Out

# Project/Local
from ._internal import get_logger

# =============================================================================
# MODULE-LEVEL LOGGER
# =============================================================================
logger = get_logger(__name__)

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
T = TypeVar("T")

# =============================================================================
# PUBLIC API
# =============================================================================
# (Classes below serve as public API)

# =============================================================================
# CORE CLASSES
# =============================================================================


@dataclass
class CapturedOutput(Out[T]):
    """A captured output binding value.

    This class wraps an output binding to track whether it was set by the
    function under test. This allows assertions to distinguish between
    "output was set to None" and "output was never set".

    Type Parameter:
        T: The type of the output value

    Attributes:
        name: The name of the output binding
        value: The captured output value (None if not set)

    Example:
        >>> output = CapturedOutput(name="result")
        >>> output.set({"status": "completed"})
        >>> output.get()
        {'status': 'completed'}
    """

    name: str
    value: T | None = None
    _set: bool = field(default=False, repr=False, init=False)

    def set(self, val: T) -> None:
        """Set the output binding value.

        This is typically called by the function under test.

        Args:
            val: The output value to capture.

        Example:
            >>> output = ctx.out("result")
            >>> output.set({"status": "completed"})
        """
        logger.debug("Setting output '%s' to: %r", self.name, val)
        self.value = val
        self._set = True

    def get(self) -> T:
        """Get the captured output value.

        Returns:
            The captured value.

        Raises:
            ValueError: If the output was never set.

        Example:
            >>> output = ctx.out("result")
            >>> output.set({"status": "completed"})
            >>> output.get()
            {'status': 'completed'}
        """
        if not self._set:
            msg = f"Output '{self.name}' was never set"
            raise ValueError(msg)
        # Type narrowing: if _set is True, value was assigned via set()
        return self.value  # type: ignore[return-value]

    def is_set(self) -> bool:
        """Check if the output was set.

        Returns:
            True if set() was called, False otherwise.

        Example:
            >>> output = ctx.out("result")
            >>> output.is_set()
            False
            >>> output.set({"status": "completed"})
            >>> output.is_set()
            True
        """
        return self._set


class FunctionTestContext:
    """Captures output bindings during function execution.

    This class provides a context object for testing Azure Functions that
    write to output bindings. It allows tests to capture and assert on
    outputs without requiring the full Functions runtime.

    Design Principle:
        Explicit Over Implicit - Output bindings are captured explicitly
        via ctx.out("name"), not through magic interception.

    Example:
        >>> ctx = FunctionTestContext()
        >>> my_function(input_msg, ctx.out("result"))
        >>> assert ctx.outputs["result"] == {"status": "completed"}

        >>> # Or use the assertion helper
        >>> ctx.assert_output("result", {"status": "completed"})
    """

    def __init__(self) -> None:
        """Initialize a new test context with no outputs."""
        self._outputs: dict[str, CapturedOutput[Any]] = {}

    def out(self, name: str) -> CapturedOutput[Any]:
        """Create a named output binding capture.

        This method should be called when passing output bindings to the
        function under test. The same name should not be reused within
        a single test.

        Args:
            name: The name of the output binding.

        Returns:
            A CapturedOutput object that the function can set.

        Example:
            >>> ctx = FunctionTestContext()
            >>> result_output = ctx.out("result")
            >>> logs_output = ctx.out("logs")
            >>> my_function(input_msg, result_output, logs_output)
        """
        if name in self._outputs:
            logger.debug("Reusing existing output capture for '%s'", name)
            return self._outputs[name]

        logger.debug("Creating new output capture for '%s'", name)
        output: CapturedOutput[Any] = CapturedOutput(name=name)
        self._outputs[name] = output
        return output

    @property
    def outputs(self) -> dict[str, Any]:
        """Get all captured output values.

        Returns:
            Dictionary mapping output names to their values.
            Only includes outputs that were actually set.

        Example:
            >>> ctx = FunctionTestContext()
            >>> my_function(input_msg, ctx.out("result"))
            >>> assert ctx.outputs["result"]["status"] == "completed"
        """
        return {
            name: output.value
            for name, output in self._outputs.items()
            if output.is_set()
        }

    def is_set(self, name: str) -> bool:
        """Check if an output binding was set.

        Args:
            name: The name of the output binding.

        Returns:
            True if the output was set, False if never created or not set.

        Example:
            >>> ctx = FunctionTestContext()
            >>> ctx.is_set("result")
            False
            >>> result_output = ctx.out("result")
            >>> ctx.is_set("result")
            False
            >>> result_output.set({"status": "completed"})
            >>> ctx.is_set("result")
            True
        """
        if name not in self._outputs:
            return False
        return self._outputs[name].is_set()

    def assert_output(self, name: str, expected: Any) -> None:
        """Assert an output binding has a specific value.

        This is a convenience method for common assertion patterns.

        Args:
            name: The name of the output binding.
            expected: The expected value.

        Raises:
            AssertionError: If the output doesn't match the expected value
                or was never created.

        Example:
            >>> ctx = FunctionTestContext()
            >>> my_function(input_msg, ctx.out("result"))
            >>> ctx.assert_output("result", {"status": "completed"})
        """
        if name not in self._outputs:
            msg = f"Output '{name}' was never created"
            raise AssertionError(msg)

        actual = self._outputs[name].value
        if actual != expected:
            msg = (
                f"Output '{name}' mismatch:\n"
                f"  Expected: {expected!r}\n"
                f"  Actual:   {actual!r}"
            )
            raise AssertionError(msg)


# =============================================================================
# PRIVATE HELPERS
# =============================================================================
# (None in this module)
