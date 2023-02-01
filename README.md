# Parcomb - Perser combinator library
[![Build Status](https://github.com/wennergr/parcomb/actions/workflows/tests.yml/badge.svg)](https://github.com/wennergr/parcomb/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/parcomb.svg)](https://badge.fury.io/py/parcomb)
[![Coverage](https://codecov.io/gh/wennergr/parcomb/branch/main/graph/badge.svg)](https://app.codecov.io/gh/wennergr/parcomb/tree/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/parcomb.svg?style=flat-square)](https://pypi.org/project/parcomb/)

Parcomb is a library for writing arbitrary text parsers and interpreters using regular python code. Technically, it's a top down back-tracing parser using [parser combinators](https://en.wikipedia.org/wiki/Parser_combinator). It's heavily influences by the [Parsec](https://hackage.haskell.org/package/parsec) library

## Installation
`pip install parcomb`

## Usage

```python
from typing import Tuple
from parcomb.char import char, trim
from parcomb.combinator import many, choice, between
from parcomb.number import integer
from parcomb.parsing import future

input1 = "(1 + 4 * 6) + 5 + (6 + (10 + 11)) + 5"

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

expr = future()
factor = trim(integer()) | between(char("("), expr, char(")"))
term = (factor * many(choice(*op_prio1) * factor)).map_u(eval)
expr <<= (term * many(choice(*op_prio2) * term)).map_u(eval)

expr.run(input1)  # Success(value=62, next='')
```

### More examples

 * [JSON Parser](https://github.com/wennergr/parcomb/blob/main/tests/test_example_json.py)
 * [CSV Parser](https://github.com/wennergr/parcomb/blob/main/tests/test_example_csv.py)
 * [INI Parser](https://github.com/wennergr/parcomb/blob/main/tests/test_example_ini.py)

## Foundation
A [parser](https://github.com/wennergr/parcomb/blob/6afd2a723b841582f43a198f98eb0536badc7828/parcomb/parsing.py#L40) is
a function `string -> (A, string)` that reads zero or more characters from a string. It then optionally transforms what 
it read and return it as a [tuple](https://github.com/wennergr/parcomb/blob/6afd2a723b841582f43a198f98eb0536badc7828/parcomb/parsing.py#L23) together with the part it didn't read. 

 * Example 1: The string "abc" are applied to the `any` parser. It reads the "a" character and returns ("a", "bc")
 * Example 2: The string "12ab" are applied to the `integer` parser. It reads "12", transforms it to an integer, and returns (12, "ab")

The parser can also return a failure.

Multiple parsers can be combined to create new, more complex, parsers. Finally, a parser is evaluated by calling the 
run method on it

## Value parsers
A value parser reads character(s) (input) and produces values (output). These parsers are the building blocks for 
more complex parsers. Parcomb contain many built in value parsers. They are located in 
submodules that corresponding to the type they produce. Character parsers are in `parcomb.char`, number parsers 
in `parcomb.number`, string parsers in `parcomb.string`, and so forth.

```python
from parcomb.char import any, char, none_of

input = "test string"

# Reads (consumes) first character in the input text and sets it as output
any().run(input) # Success(value='t', next='est string')

# Attempts to read an "a" from input text but fails. Does not consume any characters
char("a").run(input)  # Failure(message='#char: Failed to find [a]. value: [t], ...', next='test string')

# Reads (consumes) any character as long as it is not a " " or a "a". 
none_of([" ", "a"]).run(input)  # Success(value='t', next='est string')
```

For more information, see implementation of the [any](https://github.com/wennergr/parcomb/blob/6afd2a723b841582f43a198f98eb0536badc7828/parcomb/char.py#L9) and [char](https://github.com/wennergr/parcomb/blob/6afd2a723b841582f43a198f98eb0536badc7828/parcomb/char.py#L29) parsers

## Combinator parsers

Value parsers reads single values out of a text, but they are rarely useful by themselves. Instead, they serves
as building blocks for combinator parsers. These parsers combine multiple parsers into more complex once. 

```python
from parcomb.number import integer
from parcomb.char import char, any, none_of
from parcomb.combinator import sep_by, combine, combine_f, many, product3

input1 = "2,3,5,7,11 Prime numbers"
input2 = "123,456"

# Parse zero or more integers, separated by ","
sep_by(integer(), char(",")).run(input1)  # Success(value=[2, 3, 5, 7, 11], next=' # Prime numbers')

# Combine any two characters using the build in "+" operator or custom function
combine(any(), any()).run(input1)  # Success(value='2,', next='3,5,7,11 # Prime numbers')
combine_f(any(), any(), lambda a, b: b + a).run(input1)  # Success(value=',2', next='3,5,7,11 # Prime numbers')

# Consume many non " " characters. The many parser continues to parse until its first failure
many(none_of([" "])).run(input1)  # Success(value=['2', ',', '3', ',', '5', .. ], next=' # Prime numbers')

# ProductN combines n parsers into a tuple
product3(integer(), char(","), integer()).run(input2)  # Success(value=(123, ',', 456), next='')
```

The library contains many useful parser combinators such as `many`, `many1`, `choice`, `end_by`, `peek`, and `product`

## Ignoring data

Parsers often reads characters that should not be in the final output structure. Examples of this is:
 * Whitespace, such as new line characters or spaces
 * Characters that are used to define structure (such as "," in a csv document)
 * Comments to humans that have no impact on the data

The library provides two methods for ignoring data `skip_left` and `skip_right`. They are both parser combinators
that takes two parsers as arguments and ignores one of them.

```python
from parcomb.number import integer
from parcomb.char import char, spaces
from parcomb.combinator import sep_by, many, skip_left

input1 = "   2, 3,  5, 7,   11"

# Ignores 0 or more spaces in front of a number
nr = skip_left(spaces(), integer())
sep_by(nr, char(",")).run(input1)  # Success(value=[2, 3, 5, 7, 11], next='')
```

## Transforming data

Every parser contains a transformation function called `map` and a sister function called `map_u`. The purpose of
these functions are to convert a `Parser[A]` to a `Parser[B]` given a function `A -> B`. Very similar to how
the `map` function converts a `List[A]` to a `List[B]`. The difference is that the `map_u` function first unpacks 
a tuple before applying it to the transformation function. This simplifies the usage with the product parser

```python
from parcomb.number import integer
from parcomb.char import char, eof
from parcomb.combinator import product3, sep_by, end_by, choice

input1 = "2,3,5,7,11"
input2 = "This is a text; Comment"

# Create a tuple of "2", ",", 3 and then multiple the numbers
product3(integer(), char(","), integer()) \
    .map(lambda x: x[0] * x[2]).run(input1)  # Success(value=6, next=',5,7,11')
    # .map_u(lambda l, _, r: l * r).run(input)  # map_u unpacks a tuple to function parameters

# Create a list of the first 5 prime numbers and then sum them together
sep_by(integer(), char(",")).map(sum).run(input1)  # Success(value=28, next='')

# Read input, character by character, until we either get a ';' char or end of file. 
# transformation 1: Join the list of character into a string
# transformation 2: Convert all characters to upper case
end_by(any(), choice([char(";"), eof()])) \
    .map(lambda x: "".join(x)) \
    .map(lambda x: x.upper()) \
    .run(input2)  # Success(value='THIS IS A TEXT', next=' Comment')
```

## Recursive parser

Recursive parsing allows parsing of infinitely nested structures such as JSON, JAML, or lists of lists. Parcomb has
a special parser called "future" that allows us to define a parser, refer it, but define it at a later stage.

```python
from parcomb.char import char
from parcomb.number import integer
from parcomb.parsing import future
from parcomb.combinator import between, sep_by, choice

input1 = "[1,[4,5],453,[4,[]]]"

# We create a future parser "elem" but we can't define it yet as it depend # on the "lst" parser, 
# that depends on the "elem" parser. E.g. we have a parser that depends on itself
elem = future()
lst = between(char("["), elem, char("]"))
elem.rebind(sep_by(choice([integer(), lst]), char(",")))

lst.run(input1)  # Success(value=[1, [4, 5], 453, [4, []]], next='')
```

## Syntax DSL

The library contains an optional syntax that can make large expressions easier to read

```python
from parcomb.char import any, char, spaces
from parcomb.number import integer
from parcomb.parsing import future

any() + any()  # Same as: combine(any(), any())

any() * any()  # Same as: product(any(), any())
any() * 5  # Same as: count(any(), 5)

integer() | char("a")  # Same choice([integer(), char("a")])

spaces() << integer() >> spaces()  # Same as skip_right(skip_left(spaces(), integer()),.spaces())

elem = future() 
elem <<= any()  # Same as elem.rebind(any())
```
