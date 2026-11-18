"""Types for the actions parameters sent to `WebDriver.execute`"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NotRequired, ReadOnly, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence


class Parameters(TypedDict):
    pointerType: str


# TODO: wtf is this id lookin thing... its hardcoded in
# selenium/webdriver/common/actions/pointer_input.py
# so it looks like it will always have the same value
Origin = TypedDict("Origin", {"element-6066-11e4-a52e-4f735466cecf": str})


class PointerMoveSubAction(TypedDict):
    type: ReadOnly[Literal["pointerMove"]]
    x: ReadOnly[int]
    y: ReadOnly[int]
    origin: ReadOnly[str | Origin]
    duration: ReadOnly[int]


class ClickSubAction(TypedDict):
    type: ReadOnly[Literal["pointerDown", "pointerUp"]]
    button: int
    duration: ReadOnly[int]


class PauseSubAction(TypedDict):
    type: ReadOnly[Literal["pause"]]
    duration: ReadOnly[int]


class KeySubAction(TypedDict):
    type: ReadOnly[Literal["keyDown", "keyUp"]]
    value: str


class _BaseAction[T](TypedDict):
    type: ReadOnly[str]
    id: ReadOnly[str]
    actions: ReadOnly[Sequence[T]]


class PointerAction(_BaseAction[ClickSubAction | PointerMoveSubAction]):
    type: ReadOnly[Literal["pointer"]]
    parameters: NotRequired[ReadOnly[Parameters]]


class KeyAction(_BaseAction[PauseSubAction | KeySubAction]):
    type: ReadOnly[Literal["key"]]
    parameters: NotRequired[ReadOnly[Parameters]]


class ActionsParams(TypedDict):
    actions: ReadOnly[Sequence[KeyAction | PointerAction]]
