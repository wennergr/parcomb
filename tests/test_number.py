from tests.common import assert_success, assert_failure
from parcomb.number import *


def test_integer():
    assert_success(integer().run("12345"), 12345, "")
    assert_success(integer().run("-12345"), -12345, "")
    assert_success(integer().run("12abc"), 12, "abc")
    assert_success(integer().run("-12abc"), -12, "abc")
    assert_failure(integer().run("abc12abc"), "abc12abc")


def test_number():
    assert_success(number().run("123.45"), 123.45, "")
    assert_success(number().run("-123.45"), -123.45, "")
    assert_success(number().run("-1.45e+2"), -145, "")
    assert_success(number().run("-1.45e+2abc123"), -145, "abc123")
    assert_success(number().run("0.45e+2"), 45, "")
