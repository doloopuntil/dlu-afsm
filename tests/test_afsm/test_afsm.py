# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,too-few-public-methods
from dataclasses import dataclass
from enum import auto
from typing import Any, Callable, Optional, cast
from unittest.mock import Mock

from attr import frozen, mutable
from pytest import FixtureRequest, fixture, raises

from afsm import State, StateError, StateMixin, transition

try:
    _slotted_dataclasses = [dataclass(slots=True), dataclass(frozen=True, slots=True)]  # type: ignore[call-overload]
    _slotted_dataclasses_ids = ["dataclass:mutable,slots", "dataclass:frozen,slots"]

except TypeError:  # Python < 3.10 does not support slotted dataclasses
    _slotted_dataclasses = []
    _slotted_dataclasses_ids = []


class _State(State):
    INITIAL = auto()
    NEXT = auto()
    FINAL = auto()


class TestFiniteStateMachine:
    @fixture(
        params=(
            lambda cls: cls,
            mutable(slots=False),
            mutable(slots=True),
            frozen(slots=False),
            frozen(slots=True),
            dataclass(frozen=False),
            dataclass(frozen=True),
            *_slotted_dataclasses,
        ),
        ids=(
            "undecorated",
            "attrs:mutable,dict",
            "attrs:mutable,slots",
            "attrs:frozen,dict",
            "attrs:frozen,slots",
            "dataclass:frozen,dict",
            "dataclass:mutable,dict",
            *_slotted_dataclasses_ids,
        ),
    )
    def class_decorator(self, request: FixtureRequest) -> Callable[..., Any]:
        return cast(Callable[..., Any], request.param)

    @fixture(params=(None, _State.INITIAL), ids=("initial_state:None", "initial_state:INITIAL"))
    def initial_state(self, request: FixtureRequest) -> Optional[State]:
        return cast(Optional[State], request.param)

    @fixture
    def identity_function(self) -> Mock:
        return Mock(side_effect=lambda value: value)

    def test_instance_creation_with_initial_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State]
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            pass

        # When
        afsm = AFSM()

        # Then
        assert afsm._state is initial_state  # type: ignore[attr-defined] # pylint: disable=no-member,protected-access

    def test_instance_creation_without_initial_state_succeeds(self, class_decorator: Callable[..., Any]) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin):
            pass

        # When
        afsm = AFSM()

        # Then
        assert afsm._state is None  # type: ignore[attr-defined] # pylint: disable=no-member,protected-access

    def test_transition_to_next_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State], identity_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            @transition(from_=initial_state or (), to_=_State.NEXT)
            def to_next_state(self, value: str) -> str:
                return cast(str, identity_function(value))

        afsm = AFSM()

        # When
        result = afsm.to_next_state("blue")

        # Then
        assert afsm._state is _State.NEXT  # type: ignore[attr-defined] # pylint: disable=no-member,protected-access
        identity_function.assert_called_once_with("blue")
        assert result == "blue"

    def test_transition_to_same_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State], identity_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            @transition(from_=initial_state or ())
            def to_same_state(self, value: str) -> str:
                return cast(str, identity_function(value))

        afsm = AFSM()

        # When
        result = afsm.to_same_state("blue")

        # Then
        assert afsm._state is initial_state  # type: ignore[attr-defined] # pylint: disable=no-member,protected-access
        identity_function.assert_called_once_with("blue")
        assert result == "blue"

    def test_transition_to_next_state_and_final_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State], identity_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            @transition(from_=initial_state, to_=_State.NEXT)
            def to_next_state(self) -> None:
                pass

            @transition(from_=_State.NEXT, to_=_State.FINAL)
            def to_final_state(self, value: str) -> str:
                return cast(str, identity_function(value))

        afsm = AFSM()
        afsm.to_next_state()

        # When
        result = afsm.to_final_state("blue")

        # Then
        assert afsm._state is _State.FINAL  # type: ignore[attr-defined] # pylint: disable=no-member,protected-access
        identity_function.assert_called_once_with("blue")
        assert result == "blue"

    def test_transition_from_invalid_state_fails(
        self, class_decorator: Callable[..., Any], identity_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            @transition(from_=_State.INITIAL, to_=_State.NEXT)
            def to_next_state(self, value: str) -> str:
                return cast(str, identity_function(value))

            @transition(from_=_State.INITIAL, to_=_State.FINAL)
            def to_final_state(self, value: str) -> str:
                return cast(str, identity_function(value))

        afsm = AFSM()
        result = afsm.to_next_state("blue")

        # Then
        with raises(StateError):
            # When
            result = afsm.to_final_state("orange")

        identity_function.assert_called_once_with("blue")
        assert result == "blue"

    def test_transition_to_idempotent_state_returns_cached_result(
        self, class_decorator: Callable[..., Any], identity_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            @transition(from_=_State.INITIAL, to_=_State.NEXT, is_idempotent=True)
            def to_next_state(self, value: str) -> str:
                return cast(str, identity_function(value))

        afsm = AFSM()

        # When
        first_result = afsm.to_next_state("blue")
        second_result = afsm.to_next_state("orange")

        # Then
        identity_function.assert_called_once_with("blue")
        assert first_result == "blue"
        assert second_result == "blue"

    def test_transition_raises_on_unhandled_exception(self, class_decorator: Callable[..., Any]) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            @transition(from_=_State.INITIAL, to_=_State.NEXT)
            def to_next_state(self, value: str) -> str:
                raise ValueError(value)

        afsm = AFSM()

        # Then
        with raises(ValueError, match="red"):
            # When
            afsm.to_next_state("red")

    def test_transition_calls_handler_on_handled_exception(self, class_decorator: Callable[..., Any]) -> None:
        # Given
        exception = ValueError("red")
        handle_exception = Mock(return_value="orange")

        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            @transition(from_=_State.INITIAL, to_=_State.NEXT, on_error=handle_exception)
            def to_next_state(self, *args: str, **kwargs: str) -> str:
                raise exception

        afsm = AFSM()

        # When
        result = afsm.to_next_state("blue", "green", third_colour="yellow")

        # Then
        handle_exception.assert_called_once_with(afsm, exception, "blue", "green", third_colour="yellow")
        assert result == "orange"
