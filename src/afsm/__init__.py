"""
``dlu-afsm`` is a simple decorator-based finite state machine library, compatible with `attrs <https://attrs.org>`_ and
`dataclasses <https://docs.python.org/3/library/dataclasses.html>`_.

>>> from dataclasses import dataclass
>>> from enum import auto
>>> from dataclasses import dataclass
>>>
>>> class MachineState(State):
>>>     INITIAL = auto()
>>>     FINAL = auto()
>>>
>>> @dataclass
>>> class AFiniteStateMachine(StateMixin, initial_state=MachineState.INITIAL):
>>>     @transition(from_=MachineState.INITIAL, to_=MachineState.FINAL)
>>>     def change_state(self):
>>>         print("Changing state")
"""

from afsm._fsm import StateMixin, Transition as transition
from afsm._state import State, StateError

__version__ = "1.0.0"
__all__ = ["StateMixin", "State", "StateError", "transition"]
