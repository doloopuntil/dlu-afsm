A(ttrs) Finite State Machine
============================

**A(ttrs) Finite State Machine (afsm)** is a simple decorator-based finite state machine library, compatible with `attrs <https://attrs.org>`_ and
`dataclasses <https://docs.python.org/3/library/dataclasses.html>`_.

Example
-------

.. code-block:: python

    from dataclasses import dataclass
    from enum import auto
    from afsm import State, StateMixin, transition

.. code-block:: python

    class MachineState(State):
        INITIAL = auto()
        FINAL = auto()

.. code-block:: python

    @dataclass  # Or @define if using attrs
    class AFiniteStateMachine(StateMixin, initial_state=MachineState.INITIAL):
        @transition(from_=MachineState.INITIAL, to_=MachineState.FINAL)
        def to_final_state(self):
            print("Transitioning to final state")

.. code-block:: rst

    >>> afsm = AFiniteStateMachine()
    >>> afsm.to_final_state()
    Transitioning to final state

.. code-block:: rst

    >>> afsm.to_final_state()
    Traceback (most recent call last):
        ...
    afsm._state.StateError: Actual state for 'AFiniteStateMachine' does not match expected state(s)
    Expected states: INITIAL
    Actual state: FINAL

Development
-----------

* Run ``git clone``
* Run ``pdm install``
* Run ``pdm run pre-commit install`` to install pre-commit hooks.
