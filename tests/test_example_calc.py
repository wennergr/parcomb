from tests.common import assert_success
from typing import Tuple
from parcomb.char import char, trim
from parcomb.number import integer
from parcomb.parsing import future
from parcomb.combinator import many, choice, between


def test_calc():
    """
    BNF:
    Expr ::= Term ('+' Term | '-' Term)*
    Term ::= Factor ('*' Factor | '/' Factor)*
    Factor ::= ['-'] (Number | '(' Expr ')')
    Number ::= Digit+
    """

    input1 = "1 + 4 * (5 + 6) + 6"
    input2 = "(1 + 4 + 6) + 5 + (6 + (10 + 11)) + 5"
    input3 = "1 + 2 + 5 * 6 + 6"

    def eval(x: int, xs: list[Tuple[str, int]]) -> int:
        if not xs:
            return x

        current = xs[0]
        next = xs[1:]

        fdict = {
            "+": lambda a, b: eval(x + a, next),
            "-": lambda a, b: eval(x - a, next),
            "*": lambda a, b: eval(x * a, next),
            "/": lambda a, b: eval(x / a, next),
        }

        return fdict[current[0]](current[1], next)

    op_prio1 = [trim(char(x)) for x in ["*", "/"]]
    op_prio2 = [trim(char(x)) for x in ["+", "-"]]

    expr = future()  # Delay the binding of the expression
    factor = trim(integer()) | between(char("("), expr, char(")"))
    term = (factor * many(choice(*op_prio1) * factor)).map_u(eval)
    expr <<= (term * many(choice(*op_prio2) * term)).map_u(eval)

    assert_success(expr.run(input1), 51, "")
    assert_success(expr.run(input2), 48, "")
    assert_success(expr.run(input3), 39, "")
