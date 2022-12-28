"""
This module defines the state elements for a finite state machine.
"""

from enum import Enum, unique
from typing import Iterable


@unique
class State(Enum):
    """
    A base :class:`~Enum` used to define states for a state machine. This class enforces enumeration members uniqueness.

    Example:
        >>> from afsm import State
        ...
        >>> class MachineState(State):
        ...     INITIAL = "begin"
        ...     FINAL = "end"

        This class also supports automatic value setting for its members using :class:`~enum.auto`.

        >>> from enum import auto
        >>> from afsm import State
        ...
        >>> class MachineState(State):
        ...     INITIAL = auto()    # INITIAL.value is set to "INITIAL"
        ...     FINAL = auto()      # FINAL.value is set to "FINAL"
    """

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: Iterable[str]) -> str:
        return name.upper()

    def __str__(self) -> str:
        return str(self.name)


class StateError(Exception):
    """
    An exception raised when in invalid state transition occurs.
    """

    def __init__(self, class_: type, expected_states: Iterable[State], actual_state: State) -> None:
        message = (
            f"Actual state for '{class_.__name__}' does not match expected state(s)"
            f"\nExpected states: {'or '.join(map(str, expected_states))}"
            f"\nActual state: {str(actual_state)}"
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
