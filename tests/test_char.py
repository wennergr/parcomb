from parcomb.char import *
from tests.common import assert_success, assert_failure


def test_any():
    assert_success(any().run("abc"), "a", "bc")
    assert_success(ANY.run("abc"), "a", "bc")
    assert_failure(ANY.run(""), "")


def test_eof():
    assert_success(eof().run(""), None, "")
    assert_failure(eof().run("aaa"), "aaa")


def test_char():
    input1 = "12a3"
    input2 = "a2a3"

    expr = char("1") + char("2") + any()

    assert_success(expr.run(input1), "12a", "3")
    assert_failure(expr.run(input2), input2)


def test_one_of():
    input1 = "123a"
    input2 = "a23a"

    expr = one_of(["1", "2"])

    assert_success(expr.run(input1), "1", "23a")
    assert_failure(expr.run(input2), input2)
