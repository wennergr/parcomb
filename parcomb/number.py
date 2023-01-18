from .parsing import Parser
from .char import satisfy, char, one_of
from .combinator import many1, option
from .common import join

_isdigit = satisfy(lambda c: c.isdigit(), f"#number: Failed to parse integer")
_numeric = many1(_isdigit).map(join)
_sign = option("", char("-"))


def integer() -> Parser[int]:
    return (_sign + _numeric).map(int)


def number() -> Parser[float]:
    """
    Numeric parser that supports:
    1. Can be negative (starting with "-")
    2. Can be a fraction (0.5, 12.2)
    3. Can have an exponent of 10, prefixed by "e" or "E". (10e+5)

    :return: A float parser
    """
    exponent = one_of(["e", "E"]) + char("+") + _numeric

    return (
        _sign + _numeric + option("", char(".") + _numeric) + option("", exponent)
    ).map(float)
