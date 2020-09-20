# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)
r""" Package ``pyparse.parser'' with parser infrastructure and parser modules.

@see https://en.wikipedia.org/wiki/Context-free_grammar


Disambiguate
============

A grammars is ambiguous if at least one input can be represented by multiple syntax trees.

By adopting disambiguation rules the grammar can stop being ambiguous.

Examples:
 * leftmost derivation or rightmost derivation
 * rule order
 * rewrite syntax tree


Leftmost derivation
-------------------

Always derive/rewrite the first non-terminal on the left.

Example top-down leftmost derivation:
```python
rule1 = "S = '1'"
rule2 = "S = 'a'"
rule3 = "S = S '+' S"
S = object()

input = "1+1+a"

output = S # start, incomplete
output = (S, '+', S,) # [rule3], incomplete
output = ((S, '+', S,), '+', S,) # [rule3,?], incomplete
output = ((('1',), '+', S,), '+', S,) # [rule1,?,?], incomplete
output = ((('1',), '+', ('1',)), '+', S,) # [rule1,?], incomplete
output = ((('1',), '+', ('1',)), '+', ('a',),) # [rule2], accept
```


Rightmost derivation
-------------------

Always derive/rewrite the first non-terminal on the right.

Example top-down rightmost derivation:
```python
rule1 = "S = '1'"
rule2 = "S = 'a'"
rule3 = "S = S '+' S"
S = object()

input = "1+1+a"

output = S # start, incomplete
output = (S, '+', S,) # [rule3], incomplete
output = (S, '+', (S, '+', S,),) # [?,rule3], incomplete
output = (S, '+', (S, '+', ('a',),),) # [?,?,rule2], incomplete
output = (S, '+', (('1',), '+', ('a',),),) # [?,rule1], incomplete
output = (('1',), '+', (('1',), '+', ('a',),),) # [rule1], accept
```


Rule order
----------

Assign a rule order, sort the syntax trees with the rules order, and choose the first syntax tree.
A simple example is the definition order of the rules.

Example with all top-down paths and all orders:
```python
rule1 = "S = '1'"
rule2 = "S = 'a'"
rule3 = "S = S '+' S"

input = "1+1+a"

# order: [rule1,...] or [rule2,rule1,...]
# [rule3][rule1,?][rule3][rule1,?][rule2], accept
# [rule3][rule1,?][rule3][?,rule2][rule1]
output = (('1',), '+', (('1',), '+', ('a',),),)

# order: [?,...] or [rule2,?,...]
# [rule3][?,rule3][rule1,?,?][rule1,?][rule2]
# [rule3][?,rule3][rule1,?,?][?,rule2][rule1]
# [rule3][?,rule3][?,rule1,?][rule1,?][rule2]
# [rule3][?,rule3][?,rule1,?][?,rule2][rule1]
# [rule3][?,rule3][?,?,rule2][rule1,?][rule1]
# [rule3][?,rule3][?,?,rule2][?,rule1][rule1], accept
output = (('1',), '+', (('1',), '+', ('a',),),)
# [rule3][?,rule2][rule3][rule1,?][rule1]
# [rule3][?,rule2][rule3][?,rule1][rule1]
output = ((('1',), '+', ('1',),), '+', ('a',),)

# order: [rule3,rule1,...] or [rule2,rule3,rule1,?] or [rule3,rule2,rule1,?]
# [rule3][rule3,?][rule1,?,?][rule1,?][rule2], accept
# [rule3][rule3,?][rule1,?,?][?,rule2][rule1]
output = ((('1',), '+', ('1',),), '+', ('a',),)

# order: [rule3,?,...] or [rule2,rule3,?,rule1] or [rule3,rule2,?,rule1]
# [rule3][rule3,?][?,rule1,?][rule1,?][rule2]
# [rule3][rule3,?][?,rule1,?][?,rule2][rule1]
# [rule3][rule3,?][?,?,rule2][rule1,?][rule1]
# [rule3][rule3,?][?,?,rule2][?,rule1][rule1], accept
output = ((('1',), '+', ('1',),), '+', ('a',),)
```


Rewrite syntax tree
-------------------

Rewrite the syntax tree according to formulas.

Example top-down with rewrite formulas:
```python
rule1 = "S = '1'"
rule2 = "S = 'a'"
rule3 = "S = S '+' S"
S = object()

def rewrite(syntax_tree):
    _formulas = [
        # has associative property
        (S, '+', (S, '+', S,),): (S, '+', S, '+', S,),
        ((S, '+', S,), '+', S,): (S, '+', S, '+', S,),
    ]
    _done = False
    while not _done:
        _done = True
        for _from, _to in formulas:
            try:
                _index = syntax_tree.index(_from)
                syntax_tree.replace(_index, _from, _to)
                _done = False
            except:
                pass

input = "1+1+a"

output = S # start, incomplete
output = (S, '+', S,) # [rule3], incomplete
# intermediate steps omitted because they depend on the implementation
output = (S, '+', S, '+', S,) # [rule3,?] or [?,rule3] with rewrite, incomplete
# intermediate steps omitted because they depend on the implementation
output = (('1',), '+', ('1',), '+', ('a',),) # [rule1,rule1,rule2], accept
```


Future
======

TODO LL(n) parser
     top-down parser (goal to tokens?)
     Left-to-right (input order?)
     Leftmost derivation (always derive/rewrite the non-terminal on the left?)
     n (needs to know n characters/codepoints/tokens to work?)
TODO parser for EBNF, ABNF, and other grammar languages
TODO parser for matroska
TODO parser for python (try making a sandbox)
TODO decorator to generate a parser class from a text grammar?
TODO decorator to generate a rule/token function from a text grammar?
TODO auto-change grammar to fit requirements? (need better understanding of grammar properties)
TODO use a single syntax tree representation (normalize parsers)
"""


from __builtin__ import AssertionError
from __builtin__ import False
from __builtin__ import IndexError
from __builtin__ import True
from __builtin__ import ValueError
from __builtin__ import enumerate
from __builtin__ import exit
from __builtin__ import getattr
from __builtin__ import int
from __builtin__ import isinstance
from __builtin__ import len
from __builtin__ import object
from __builtin__ import repr
from __builtin__ import str
from __builtin__ import type
from copy import deepcopy
from pyparse.util import println


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    exit(1)
except AssertionError:
    pass


class ParserSkeleton(object):
    r""" Infrastructure for derived parsers.

    It does not parse by itself.

    TODO several states/paths at the same time?
    """

    class State:
        def __init__(self, data):
            self.data = data
        def __repr__(self):
            _s = ["ParserSkeleton.State(", repr(self.data), ")"]
            return ''.join(_s)
    # ssalc State

    def __init__(self, data=''):
        if not isinstance(data, str):
            raise ValueError, type(data) # expecting str # TODO other types
        object.__init__(self)
        self.data = data
        self.state = self.State(data) # TODO strview or similar in the state
        self.stack = []

    def __getitem__(self, index, *args, **kwargs):
        """ Gets data or ``None''. """
        try:
            return self.state.data[index]
        except IndexError:
            return None # implicit None

    def __getslice__(self, start, stop, *args, **kwargs):
        """ Gets data or ``None''. """
        try:
            return self.state.data[start:stop]
        except IndexError:
            return None # implicit None

    def __enter__(self, *args, **kwargs):
        r""" Save parser state. """
        if not isinstance(self, ParserSkeleton):
            raise RuntimeError, type(self) # expecting ParserSkeleton
        self.stack += [self.state]
        self.state = deepcopy(self.state)

    def __exit__(self, exc_type, exc_value, traceback):
        r""" Keep or revert parser state. """
        if not isinstance(self, ParserSkeleton):
            raise RuntimeError, type(self) # expecting ParserSkeleton
        if not len(self.stack) > 0:
            raise RuntimeError, len(self.stack) # expecting a non-empty stack
        _state = self.stack.pop(-1)
        if exc_type is None and exc_value is None and traceback is None:
            # all ok, forget previous state
            pass
        else:
            # has exception, revert to previous position and propagate exception
            self.state = _state

    def consume(self, n, *args, **kwargs):
        r""" Consumes state data. """
        if not isinstance(n, int):
            raise ValueError, n # expecting int
        if not n >= 0:
            raise ValueError, n # expecting >= 0
        _consumed = self.state.data[:n]
        self.state.data = self.state.data[n:]
        return _consumed

    def starts_with(self, s):
        r""" TODO """
        if not isinstance(s, str):
            raise ValueError, (s,) # expecting str
        for _i, _c in enumerate(s):
            if self[_i] != _c:
                return False # does not match

        return True # matches

    def maybe(self, func, *args, **kwargs):
        r""" Call ``func'' with the provided arguments.

        Return ``None'' on ´´AssertionError''.
        """
        if not isinstance(self, ParserSkeleton):
            raise RuntimeError, type(self) # expecting ParserSkeleton
        if not getattr(self, func.__name__) == func:
            raise ValueError, repr(func) # must belong to self

        try:
            with self: # revert state on error
                return func(*args, **kwargs)
        except AssertionError:
            return None
# ssalc ParserSkeleton


__all__ = []
__builtins__ = {} # enter restricted mode
