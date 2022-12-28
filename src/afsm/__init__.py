"""
**A(ttrs) Finite State Machine**, a.k.a. ``afsm``, is a simple `decorator-based
<https://docs.python.org/3/glossary.html#term-decorator>`_
finite state machine library, compatible with `attrs <https://attrs.org>`_ and `dataclasses
<https://docs.python.org/3/library/dataclasses.html>`_.

Quickstart
----------

First, import the requirements:

    >>> from dataclasses import dataclass
    >>> from enum import auto
    >>> from afsm import State, StateMixin, transition

Second, create a set of states for the machine by implementing :class:`~State`:

    >>> class MachineState(State):
    ...     INITIAL = auto()
    ...     FINAL = auto()

Third, define the finite atate machine. Use :class:`~afsm.StateMixin`. Specify an (optional) initial state and

    >>> @dataclass  # Or @define if using attrs
    ... class AFiniteStateMachine(StateMixin, initial_state=MachineState.INITIAL):
    ...     @transition(from_=MachineState.INITIAL, to_=MachineState.FINAL)
    ...     def to_final_state(self):
    ...         print("Transitioning to final state")

    >>> afsm = AFiniteStateMachine()

    >>> afsm.to_final_state()
    Transitioning to final state

    >>> afsm.to_final_state()
    Traceback (most recent call last):
        ...
    afsm._state.StateError: Actual state for 'AFiniteStateMachine' does not match expected state(s)
    Expected states: INITIAL
    Actual state: FINAL
    >>>
"""

from afsm._fsm import StateMixin, Transition as transition
from afsm._state import State, StateError

__version__ = "1.0.0"
__all__ = ["StateMixin", "State", "StateError", "transition"]
