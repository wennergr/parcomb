from parcomb.parsing import *
from parcomb.combinator import const
from tests.common import assert_success, assert_failure

a1 = "abc"
a2 = "next"


def test_pure():
    assert_success(const(a1).run(a2), "abc", a2)


def test_map():
    assert_success(const(10).map(lambda x: x * 2).run(a2), 20, a2)


def test_map_u():
    assert_success(const((2, 5)).map_u(lambda a, b: a + b).run(a2), 7, a2)


def test_future():
    expr = future()
    assert_failure(expr.run(a1), a1)

    expr <<= const(a1)
    assert_success(expr.run(a2), a1, a2)
