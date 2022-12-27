"""
This module defines the business logic for a finite state machine.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, Iterable, Optional, TypeVar, final, overload

from ._state import State, StateError, StateField

_State = TypeVar("_State", bound="State")
_Result = TypeVar("_Result")
_ErrorResult = TypeVar("_ErrorResult")

try:
    dataclass(eq=False, frozen=True, slots=True)  # type: ignore[call-overload] # pylint: disable=unexpected-keyword-arg
    _is_slotted = {"slots": True}
except TypeError:  # Python < 3.10 does not support slotted dataclasses
    _is_slotted = {}


@final
@dataclass(eq=False, frozen=True, **_is_slotted)  # pylint: disable=unexpected-keyword-arg
class Transition(Generic[_ErrorResult]):
    """
    A decorator that ensures an instance of a class derived from :class:`StateMixin` is in an expected state before
    calling the decorated method. When a new state is given, the instance transitions to the new state if the call to
    the decorated method succeeds.

    Args:
        from_: the :class:`~State` or set of states in which the instance must be before the decorated method gets
               called. If the expected state is ``None``, no check occurs.
        to_: a :class:`~NamedState` to which the instance transitions if the method call succeeds. No transition
             occurs if the call to the decorated method raises an exception. If the instance is already in the new
             state, the decorated method does not get called and its cached return value (if available) is returned
             instead, thus making the call idempotent. If the new state is ``None``, the decorated method gets
             called unconditionally.
        is_idempotent: if ``True``, marks the method as idempotent with respect to the new state. if the new state has
                       already been reached, return the previous result and do not change state.
        on_error: (optional) the :class:`~Callable` to invoke if the decorated method raises an exception. The first
                  argument if the exception, the remaining arguments are the same passed to the decorated method.

    Raises:
        :exc:`~StateError`: if the instance is not in the expected :class:`~State` or in the expected set of states.

    Returns:
        A state-checking method with the same declaration as the decorated method.
    """

    from_: Optional[State] | Iterable[State] = None
    to_: Optional[State] = None
    is_idempotent: bool = False
    on_error: Optional[Callable[..., _ErrorResult]] = None

    @overload
    def __call__(self, method: Callable[..., _ErrorResult]) -> Callable[..., _ErrorResult]:
        ...

    @overload
    def __call__(self, method: Callable[..., _Result]) -> Callable[..., _Result]:
        ...

    def __call__(self, method: Any) -> Any:
        # Cache values and method access calls at the outset for speed.
        state_attr = StateField.STATE.value
        ret_values_attr = StateField.RETURN_VALUES.value
        expected_states = frozenset(
            self.from_ if isinstance(self.from_, Iterable) else [self.from_] if self.from_ else []
        )

        @wraps(method)
        def transitioning_method(instance: Any, *args: Any, **kwargs: Any) -> _Result | _ErrorResult:
            current_state = getattr(instance, state_attr)

            # If the method is marked as idempotent with respect to the new state, and the new state has already
            # been reached, return the previous result and do not change state.
            if self.is_idempotent and self.to_ is not None and current_state is self.to_:
                return getattr(instance, ret_values_attr).get(method, None)  # type: ignore[no-any-return]

            # Raise an exception if the current state is unexpected at this time.
            if expected_states and current_state not in expected_states:
                raise StateError(type(instance), method, current_state, expected_states)

            # Call the decorated method and store the result to be later returned by idempotent methods.
            try:
                result: _Result | _ErrorResult
                result = getattr(instance, ret_values_attr)[method] = method(instance, *args, **kwargs)

            except Exception as exception:  # pylint: disable=broad-except
                if self.on_error is None:
                    raise exception

                result = self.on_error(instance, exception, *args, **kwargs)

            # Set the new state, if specified, otherwise retain the current state.
            # Use `object.__setattr__()` for compatibility with frozen/immutable `attrs` or `dataclass` classes.
            # See https://www.attrs.org/en/stable/init.html#post-init.
            object.__setattr__(instance, state_attr, self.to_ or current_state)
            return result

        return transitioning_method


class StateMixin:
    """
    Mixin class that adds state tracking to a class definition. The mixin expect the argument ``initial_state`` to be
    passed in the class definition statement.
    """

    __slots__ = (StateField.STATE.value, StateField.RETURN_VALUES.value)

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        initial_state_attr = StateField.INITIAL_STATE.value

        # Retrieve the initial state stored in the original class when `attrs` or `dataclass` is replacing the original
        # class with its slotted version, see https://www.attrs.org/en/stable/glossary.html#term-slotted-classes.
        initial_state = getattr(cls, initial_state_attr, None)

        # Store the initial state on the class. The state is either specified in `kwargs` or it is the state originally
        # stored in the class `attrs` or `dataclass` is replacing.
        setattr(cls, initial_state_attr, kwargs.pop("initial_state", initial_state))

        super().__init_subclass__(**kwargs)

    def __new__(cls, *_: Any, **__: Any) -> Any:
        instance = super().__new__(cls)

        # Use `object.__setattr__()` for compatibility with frozen/immutable `attrs` or `dataclass` classes.
        # See https://www.attrs.org/en/stable/init.html#post-init.
        object.__setattr__(instance, StateField.STATE.value, getattr(cls, StateField.INITIAL_STATE.value))
        object.__setattr__(instance, StateField.RETURN_VALUES.value, {})

        return instance
