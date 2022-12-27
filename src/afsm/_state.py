"""
This module defines the state elements for a finite state machine.
"""

from enum import Enum, unique
from pprint import pformat
from typing import Any, Iterable


@unique
class State(Enum):
    """
    A base :class:`~Enum` that defines states for a finite state machine. This class supports automatic value setting
    for members using :class:`~auto` and enforces enumeration members uniqueness.

    >>> from enum import auto
    >>>
    >>> class MachineState(State):
    >>>     INITIAL = auto()  # INITIAL.value is set to "initial"
    >>>     ...
    """

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: Iterable[str]) -> str:
        return name.lower()

    def __str__(self) -> str:
        return str(self.value)


class StateError(Exception):
    """
    An exception raised when in invalid state transition occurs.
    """

    def __init__(self, class_: type, method: Any, actual_state: State, expected_state: Iterable[State]) -> None:
        message = (
            f"Current state for '{class_.__name__}.{method.__name__}()' does not match expected state(s): "
            f"\nExpected state in:\n{pformat(sorted(map(str, expected_state)))}"
            f"\nActual state:\n{pformat(actual_state)}"
        )

        super().__init__(message)


@unique
class StateField(Enum):
    """
    An :class:`~Enum` that defines utility field names for a finite state machine. These fields should not be accessed
    directly, they are used internally to manage the machine state.
    """

    STATE = "_state"
    INITIAL_STATE = "_initial_state"
    RETURN_VALUES = "_return_values"
