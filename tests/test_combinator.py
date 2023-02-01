from parcomb.combinator import *
from parcomb.char import any, char
from parcomb.string import literal
from parcomb.number import integer
from tests.common import assert_success, assert_failure, join


def test_const():
    input1 = "abc 123"
    input2 = "123"

    expr = any().and_then(
        lambda x: any().and_then(
            lambda y: any().and_then(
                lambda z: any().and_then(lambda p: const((x + y, z + p)))
            )
        )
    )

    assert_success(expr.run(input1), ("ab", "c "), "123")
    assert_failure(expr.run(input2), "")


def test_count():
    input1 = "aaaaabbb"
    input2 = "aaabb"

    expr = count(4, char("a")).map(join)

    assert_success(expr.run(input1), "aaaa", "abbb")
    assert_failure(expr.run(input2), input2)

    assert_success(count(0, char("a")).run(input1), [], input1)


def test_debug():
    input = "abc"

    result = []

    def p(s: str):
        result.append(s)

    many(debug(any(), "test", p)).run(input)

    assert len(result) == 4


def test_many():
    input1 = "aaaaabb"

    assert_success(many(char("a")).map(join).run(input1), "aaaaa", "bb")
    assert_success(many(char("b")).run(input1), [], input1)


def test_many1():
    input1 = "aaaaabb"

    assert_success(many1(char("a")).map(join).run(input1), "aaaaa", "bb")
    assert_success(many1(count(3, char("a"))).run(input1), [["a", "a", "a"]], "aabb")
    assert_failure(many1(char("b")).run(input1), input1)


def test_choice():
    input1 = "abcdef"
    input2 = "123456"
    input3 = "end"

    start1 = literal("abcdef")
    start2 = integer().map(str)

    expr = choice(start1, start2)

    assert_success(expr.run(input1), "abcdef", "")
    assert_success(expr.run(input2), "123456", "")
    assert_failure(expr.run(input3), "end")


def test_sep():
    input1 = "1,2123,12,56"
    input2 = "1,2123a,12,56"
    input3 = "abc"

    expr1 = sep_by1(integer(), char(","))

    assert_success(expr1.run(input1), [1, 2123, 12, 56], "")
    assert_success(expr1.run(input2), [1, 2123], "a,12,56")
    assert_failure(expr1.run(input3), "abc")


def test_between():
    input1 = "[a]"
    input2 = "abc1234cba"
    input3 = "abc1234cb"

    expr1 = between(char("["), any(), char("]"))
    expr2 = between(literal("abc"), integer(), literal("cba"))

    assert_success(expr1.run(input1), "a", "")
    assert_success(expr2.run(input2), 1234, "")
    assert_failure(expr2.run(input3), "cb")


def test_combine():
    input1 = "abbbbbc"
    input2 = "acccbbb"

    expr1 = combine(char("a"), char("b"))
    expr2 = char("a") + char("b") + char("b")
    expr3 = combine(many(char("a")).map(join), many(char("b")).map(join))
    expr4 = combine_f(char("a"), char("b"), lambda a, b: b + a)

    assert_success(expr1.run(input1), "ab", "bbbbc")
    assert_success(expr2.run(input1), "abb", "bbbc")
    assert_success(expr3.run(input1), "abbbbb", "c")
    assert_success(expr4.run(input1), "ba", "bbbbc")
    assert_failure(expr1.run(input2), input2)


def test_end_by():
    input1 = "abcdefghijkl;aa"
    input2 = ";abc"
    input3 = "abc123"

    expr = any().end_by(char(";")).map(join)

    assert_success(expr.run(input1), "abcdefghijkl", ";aa")
    assert_success(expr.run(input2), "", ";abc")
    assert_failure(expr.run(input3), input3)


def test_product_sum():
    input1 = "abcdef"

    expr1 = any() * any()
    expr1_1 = product(any(), any())

    expr2 = any() * (any() + any())
    expr2_1 = product(any(), (combine(any(), any())))

    expr3 = product3(any(), any(), any())
    expr4 = product4(any(), any(), any(), any())
    expr5 = product5(any(), any(), any(), any(), any())

    assert_success(expr1.run(input1), ("a", "b"), "cdef")
    assert expr1.run(input1) == expr1_1.run(input1)

    assert_success(expr2.run(input1), ("a", "bc"), "def")
    assert expr2.run(input1) == expr2_1.run(input1)

    assert_success(expr3.run(input1), ("a", "b", "c"), "def")
    assert_success(expr4.run(input1), ("a", "b", "c", "d"), "ef")
    assert_success(expr5.run(input1), ("a", "b", "c", "d", "e"), "f")


def test_peak():
    input = "abc"

    assert_success((peek(any()) + any()).run(input), "aa", "bc")
