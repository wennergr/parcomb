from .common import assert_success, assert_failure
from parcomb.number import *


def test_integer():
    assert_success(integer().run("12345"), 12345, "")
    assert_success(integer().run("12abc"), 12, "abc")
    assert_failure(integer().run("abc12abc"), "abc12abc")
