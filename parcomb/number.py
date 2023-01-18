from .parsing import Parser
from .char import satisfy, char
from .combinator import many1, option


def integer() -> Parser[int]:
    isdigit = satisfy(lambda c: c.isdigit(), f"#integer: Failed to parse integer")

    return option("", char("-")).and_then(
        lambda s: many1(isdigit).map(lambda x: int(s + "".join(x)))
    )
