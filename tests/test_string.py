from .common import assert_success, assert_failure
from parcomb.char import char
from parcomb.string import string


def test_string():
    input1 = "[teststring]"
    input2 = "[test2string]"

    expr = char("[") << string("teststring") >> char("]")

    assert_success(expr.run(input1), "teststring", "")
    assert_failure(expr.run(input2), "test2string]")
