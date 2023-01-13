from .parsing import Parser, Return, Success, Failure
from .combinator import many, many1
from typing import Callable, TypeVar
from functools import partial

A = TypeVar("A")


def any() -> Parser[str]:
    def parse(data: str) -> Return:
        if not data:
            return Failure("#any: Expected any character but got nothing", data)

        return Success(data[0], data[1:])

    return Parser(parse)


def eof() -> Parser[None]:
    def parse(data: str) -> Return:
        if not data:
            return Success(None, data)

        return Failure(f"#eof: Expected end of input but got [{data}]", data)

    return Parser(parse)


def char(c_check: str) -> Parser[str]:
    return satisfy(lambda c: c == c_check, f"#char: Failed to find [{c_check}]")


def space() -> Parser[str]:
    return char(" ")


def spaces() -> Parser[list[str]]:
    return many(space())


def trim(pa: Parser[A]):
    return spaces() << pa >> spaces()


def whitespace() -> Parser[str]:
    return satisfy(lambda c: c.isspace(), "f#whitespace: Not a whitespace char")


def whitespaces() -> Parser[list[str]]:
    return many(whitespace())


def one_of(cs: list[str]) -> Parser[str]:
    return satisfy(lambda c: c in cs, f"#one_of: Failed to find char in {cs}")


def none_of(cs: list[str]) -> Parser[str]:
    return satisfy(lambda c: c not in cs, f"#none_of: Found char in {cs}")


def satisfy(cond: Callable[[str], bool], desc: str) -> Parser[str]:
    def parse(c: str, data: str) -> Return:
        return (
            Success(c, data)
            if cond(c)
            else Failure(f"{desc}. value: [{c}], next: [{data}]", c + data)
        )

    return any().and_then(lambda x: Parser(partial(parse, x)))


#####
# Alias
ANY = any()
EOF = eof()
