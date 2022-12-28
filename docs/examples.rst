State Machine Examples
======================

Idempotency and Result Caching
------------------------------

Some text

.. doctest::

    >>> from dataclasses import dataclass
    >>> from enum import auto
    >>> from tempfile import NamedTemporaryFile
    >>> from afsm import State, StateMixin, transition
    >>> class LoggerState(State):
    ...     NOT_INITIALIZED = auto()
    ...     OPEN = auto()
    ...     CLOSED = auto()
    ...
    >>> @dataclass(init=False)
    ... class FileLogger(StateMixin, initial_state=LoggerState.NOT_INITIALIZED):
    ...     _log_file: str
    ...     @transition(
    ...         from_=LoggerState.NOT_INITIALIZED, to_=LoggerState.OPEN, is_idempotent=True
    ...     )
    ...     def open(self) -> str:
    ...         self._log_file = NamedTemporaryFile(mode="wt")
    ...         print("Created temporary file")
    ...         return self._log_file.name
    ...     @transition(from_=LoggerState.OPEN)
    ...     def write(self, entry: str) -> None:
    ...         print(f"Writing log entry '{entry}'")
    ...         self._log_file.write(entry)
    ...     @transition(to_=LoggerState.CLOSED, is_idempotent=True)
    ...     def close(self) -> None:
    ...         self._log_file.close()
    ...         print("Closed temporary file")
    ...
    >>> logger = FileLogger()

Some text

.. doctest::

    >>> first_filename = logger.open()
    Created temporary file

    >>> second_filename = logger.open()
    >>> print(second_filename is first_filename)
    True

Some text

.. doctest::

    >>> logger.write("a log line")
    Writing log entry 'a log line'

Some text

.. doctest::

    >>> logger.close()
    Closed temporary file

    >>> logger.close()


Error Handling
--------------

Some text

.. doctest::

    >>> from enum import auto
    >>> from afsm import State, StateMixin, transition
    >>> class MachineState(State):
    ...     INITIAL = auto()
    ...     FINAL = auto()
    ...
    >>> class AFiniteStateMachine(StateMixin, initial_state=MachineState.INITIAL):
    ...     def handle_exception(self, exception, arg):
    ...         pass
    ...     @transition(
    ...         from_=MachineState.INITIAL,
    ...         to_=MachineState.FINAL,
    ...         on_exception=handle_exception,
    ...     )
    ...     def to_final_state(self, arg):
    ...         print("Transitioning to final state")
    ...

Some text
