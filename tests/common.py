from parcomb.parsing import Return, is_success, is_failure
from typing import TypeVar, Callable

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def assert_success(obj: Return[A], value: A, next: str) -> None:
    assert obj.success()

    if is_success(obj):
        assert obj.value == value
        assert obj.next == next


def assert_failure(obj: Return, next: str) -> None:
    assert not obj.success()

    if is_failure(obj):
        assert obj.next == next


def join(xs: list[str]) -> str:
    return "".join(xs)


def to_list(x: A) -> list[A]:
    return [x]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))
