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
    SUCCESSIVE = auto()
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
    def mock_function(self) -> Mock:
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

        # Then  # pylint: disable=no-member,protected-access
        assert afsm._state is initial_state  # type: ignore[attr-defined]

    def test_instance_creation_without_initial_state_succeeds(self, class_decorator: Callable[..., Any]) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin):
            pass

        # When
        afsm = AFSM()

        # Then  # pylint: disable=no-member,protected-access
        assert afsm._state is None  # type: ignore[attr-defined]

    def test_transition_to_successive_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State], mock_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            @transition(from_=initial_state or (), to_=_State.SUCCESSIVE)
            def to_successive(self, value: str) -> str:
                return cast(str, mock_function(value))

        afsm = AFSM()

        # When
        result = afsm.to_successive("value")

        # Then  # pylint: disable=no-member,protected-access
        assert afsm._state is _State.SUCCESSIVE  # type: ignore[attr-defined]
        mock_function.assert_called_once_with("value")
        assert result == "value"

    def test_transition_to_same_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State], mock_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            @transition(from_=initial_state or ())
            def to_same_state(self, value: str) -> str:
                return cast(str, mock_function(value))

        afsm = AFSM()

        # When
        result = afsm.to_same_state("value")

        # Then  # pylint: disable=no-member,protected-access
        assert afsm._state is initial_state  # type: ignore[attr-defined]
        mock_function.assert_called_once_with("value")
        assert result == "value"

    def test_transition_to_successive_and_final_state_succeeds(
        self, class_decorator: Callable[..., Any], initial_state: Optional[State], mock_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=initial_state):
            @transition(from_=initial_state, to_=_State.SUCCESSIVE)
            def to_successive_state(self) -> None:
                pass

            @transition(from_=_State.SUCCESSIVE, to_=_State.FINAL)
            def to_final_state(self, value: str) -> str:
                return cast(str, mock_function(value))

        afsm = AFSM()
        afsm.to_successive_state()

        # When
        result = afsm.to_final_state("value")

        # Then  # pylint: disable=no-member,protected-access
        assert afsm._state is _State.FINAL  # type: ignore[attr-defined]
        mock_function.assert_called_once_with("value")
        assert result == "value"

    def test_transition_from_invalid_state_fails(
        self, class_decorator: Callable[..., Any], mock_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            @transition(from_=_State.INITIAL, to_=_State.SUCCESSIVE)
            def to_successive_state(self, value: str) -> str:
                return cast(str, mock_function(value))

            @transition(from_=_State.INITIAL, to_=_State.FINAL)
            def to_final_state(self, value: str) -> str:
                return cast(str, mock_function(value))

        afsm = AFSM()
        result = afsm.to_successive_state("one-value")

        # Then
        with raises(StateError):
            # When
            result = afsm.to_final_state("another-value")

        mock_function.assert_called_once_with("one-value")
        assert result == "one-value"

    def test_transition_to_idempotent_state_returns_cached_result(
        self, class_decorator: Callable[..., Any], mock_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            @transition(from_=_State.INITIAL, to_=_State.SUCCESSIVE, is_idempotent=True)
            def to_successive_state(self, value: str) -> str:
                return cast(str, mock_function(value))

        afsm = AFSM()

        # When
        first_result = afsm.to_successive_state("one-value")
        second_result = afsm.to_successive_state("another-value")

        # Then
        mock_function.assert_called_once_with("one-value")
        assert first_result == "one-value"
        assert second_result == "one-value"

    def test_exception_on_transition_calls_handler(
        self, class_decorator: Callable[..., Any], mock_function: Mock
    ) -> None:
        # Given
        @class_decorator
        class AFSM(StateMixin, initial_state=_State.INITIAL):
            def handle_exception(self, exception: Exception, value: str) -> str:
                return cast(str, mock_function(f"{exception}-{value}"))

            @transition(from_=_State.INITIAL, to_=_State.SUCCESSIVE, on_error=handle_exception)
            def to_successive_state(self, value: str) -> str:
                raise ValueError(value)

        afsm = AFSM()

        # When
        result = afsm.to_successive_state("one-value")

        # Then
        mock_function.assert_called_once_with("one-value-one-value")
        assert result == "one-value-one-value"
