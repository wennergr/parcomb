from __future__ import annotations
from dataclasses import dataclass
from functools import partial
from typing import Generic, TypeVar, Callable, Union, overload, TypeGuard, Tuple

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class Failure:
    message: str
    next: str

    def success(self):
        return False

    def map(self, f: Callable[[A], B]) -> Failure:
        return self


@dataclass
class Success(Generic[A]):
    value: A
    next: str

    def success(self):
        return True

    def map(self, f: Callable[[A], B]) -> Success[B]:
        return Success(f(self.value), self.next)


Return = Success[A] | Failure


def is_success(ret: Return[A]) -> TypeGuard[Success]:
    return isinstance(ret, Success)


def is_failure(ret: Return[A]) -> TypeGuard[Failure]:
    return isinstance(ret, Failure)


class Parser(Generic[A]):
    def __init__(self, f: Callable[[str], Return[A]]):
        self.f = f

    def rebind(self, pa: Parser[A]) -> None:
        self.f = pa.f

    def __ilshift__(self, pa: Parser[A]) -> Parser[A]:  # type: ignore
        self.rebind(pa)
        return self

    @classmethod
    def pure(cls, a: A) -> Parser[A]:
        return Parser(lambda x: Success(a, x))

    def run(self, data: str) -> Return[A]:
        return self.f(data)

    def map(self, f: Callable[[A], B]) -> Parser[B]:
        def parse(data: str) -> Return:
            ret = self.run(data)

            return ret.map(f)

        return Parser(parse)

    def map_u(self, f: Callable[[A], B]) -> Parser[B]:
        def parse(data: str) -> Return:
            ret = self.run(data)

            return Success(f(*ret.value), ret.next) if is_success(ret) else ret

        return Parser(parse)

    def and_then(self, apb: Callable[[A], Parser[B]]) -> Parser[B]:
        def pb(data: str) -> Return:
            match self.run(data):
                case Success(value, next):
                    return apb(value).run(next)
                case failure:
                    return failure

        return Parser(pb)

    ###
    # Methods to add a "nicer" syntax to parsers.
    #

    def count(self, n: int) -> Parser[list[A]]:
        from .combinator import count

        return count(n, self)

    def __mul__(self, other: Parser[B]) -> Parser[Tuple[A, B]]:
        from .combinator import product

        return product(self, other)

    def skip_left(self, pb: Parser[B]) -> Parser[B]:
        from .combinator import skip_left

        return skip_left(self, pb)

    def __lshift__(self, pb: Parser[B]) -> Parser[B]:
        return self.skip_left(pb)

    def skip_right(self, pb: Parser[B]) -> Parser[A]:
        from .combinator import skip_right

        return skip_right(self, pb)

    def __rshift__(self, pb: Parser[B]) -> Parser[A]:
        return self.skip_right(pb)

    def combine(self, pa: Parser[A]) -> Parser[A]:
        from .combinator import combine

        return combine(self, pa)

    def __add__(self, other: Parser[A]) -> Parser[A]:
        return self.combine(other)

    def end_by(self, sep: Parser[B]) -> Parser[list[A]]:
        from .combinator import end_by

        return end_by(self, sep)

    def __or__(self, pa: Parser[B]) -> Parser[A] | Parser[B]:
        from .combinator import choice

        return choice(self, pa)


###
# Helper functions
#


def future() -> Parser[A]:
    return Parser(partial(Failure, "#Future: Parser is not defined yet"))
