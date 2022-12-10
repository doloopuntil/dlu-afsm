Attrs Finite State Machine
==========================

**dlu-afsm** is a simple decorator-based finite state machine library, compatible with `attrs <https://attrs.org>`_ and
`dataclasses <https://docs.python.org/3/library/dataclasses.html>`_.

Example
-------
.. code-block:: python

    from dataclasses import dataclass
    from enum import auto
    from dataclasses import dataclass


    class MachineState(State):
        INITIAL = auto()
        FINAL = auto()


    @dataclass
    class AFiniteStateMachine(StateMixin, initial_state=MachineState.INITIAL):
        @transition(from_=MachineState.INITIAL, to_=MachineState.FINAL)
        def change_state(self):
            print("Changing state")

Development
-----------

* Run ``git clone``
* Run ``poetry install``
* Run ``poetry run pre-commit install -t pre-commit -t pre-push`` to install pre-commit hooks.
