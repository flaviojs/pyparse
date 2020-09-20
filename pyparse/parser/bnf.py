# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)
r""" BNF and derivatives

TODO find original BNF spec
TODO EBNF according to "ISO/IEC 14977 : 1996(E)"
TODO ABNF used in RFCs
"""


from __builtin__ import AssertionError
from __builtin__ import Exception
from __builtin__ import False
from __builtin__ import True
from __builtin__ import ValueError
from __builtin__ import int
from __builtin__ import len
from __builtin__ import list
from __builtin__ import ord
from __builtin__ import repr
from __builtin__ import str
from __builtin__ import tuple
from __builtin__ import type
from pyparse.parser import ParserSkeleton
from pyparse.parser.unicode import Utf8Parser
from pyparse.util import IndexToAttrMixin
from pyparse.util import println


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    exit(1)
except AssertionError:
    pass


class McKeemanFormParser(ParserSkeleton):
    r""" McKeeman Form according to Douglas Crockford's blog (2020-01-09)

    "McKeeman Form is a notation for expressing grammars.
    It was proposed by Bill McKeeman of Dartmouth College.
    It is a simplified Backus-Naur Form with significant whitespace
    and minimal use of metacharacters."

    XXX extension: discard empty lines before each rule

    @see https://www.crockford.com/mckeeman.html
    """

    def _str(self, s):
        assert self.starts_with(s), (s, self.state,) # expecting s
        return self.consume(len(s))

    def _codepoint(self, low, high=None):
        if high is None:
            high = low
        if not low <= high:
            raise ValueError, (low, high,) # expecting low <= high
        _p = Utf8Parser(self.state.data)
        _codepoint = _p.rule_Codepoint()
        _codepoint = _codepoint.codepoint
        _n = len(self.state.data) - len(_p.state.data)
        return (_codepoint, self.consume(_n),)

    def rule_Grammar(self):
        r"""
        grammar
            rules
        """
        _rules = self.rule_Rules()
        return (
            'Grammar',
            '.rules', _rules,
        )

    def token_SPACE(self):
        r"""
        space
            '0020'
        """
        _space = self._str('\x20')
        return _space

    def token_NEWLINE(self):
        r"""
        newline
            '000A'
        """
        _newline = self._str('\x0A')
        return _newline

    def token_NAME(self):
        r"""
        name
            letter
            letter name
        """
        _name = self.token_LETTER() # one or more
        while True:
            try:
                _letter = self.token_LETTER()
                _name += _letter
                continue
            except AssertionError:
                pass
            break # ignore the rest
        return _name

    def token_LETTER(self):
        r"""
        letter
            'a' . 'z'
            'A' . 'Z'
            '_'
        """
        _c = self[0]
        assert _c is not None, (self.state,) # expecting a letter
        if _c >= 'a' and _c <= 'z':
            return self.consume(len(_c))
        if _c >= 'A' and _c <= 'Z':
            return self.consume(len(_c))
        if _c == '_':
            return self.consume(len(_c))
        assert False, (_c,self.state,) # expecting a letter

    def token_INDENTATION(self):
        r"""
        indentation
            space space space space
        """
        with self: # restore state on error
            _indentation = self.token_SPACE()
            _indentation += self.token_SPACE()
            _indentation += self.token_SPACE()
            _indentation += self.token_SPACE()
        return _indentation

    def rule_Rules(self):
        r"""
        rules
            rule
            rule newline rules
        """
        _rules = [self.rule_Rule()] # one or more
        while True:
            try:
                with self: # restore state on error
                    _discard = self.token_NEWLINE()
                    _rule = self.rule_Rule()
                _rules += [_rule]
                continue
            except AssertionError:
                pass
            break # ignore the rest
        return tuple(_rules)

    def rule_Rule(self):
        r"""
        rule
            name newline nothing alternatives
        """
        with self: # restore state on error
            # XXX extension: discard empty lines before each rule
            while True:
                _discard = self.maybe(self.token_NEWLINE)
                if _discard is None:
                    break
            _name = self.token_NAME()
            _newline = self.token_NEWLINE()
            _nothing = self.rule_Nothing()
            _alternatives = self.rule_Alternatives()
        return (
            'Rule',
            '.name', _name,
            '.nothing', _nothing,
            '.alternatives', _alternatives,
        )

    def rule_Nothing(self):
        r"""
        nothing
            ""
            indentation '"' '"' newline
        """
        try:
            with self:
                _discard = self.token_INDENTATION()
                _discard = self._str('"')
                _discard = self._str('"')
                _discard = self.token_NEWLINE()
            return True
        except AssertionError:
            pass
        return False # match nothing

    def rule_Alternatives(self):
        r"""
        alternatives
            alternative
            alternative alternatives
        """
        _alternatives = [self.rule_Alternative()] # one or more
        while True:
            _alternative = self.maybe(self.rule_Alternative)
            if _alternative is None:
                break
            _alternatives += [_alternative]
        return tuple(_alternatives)

    def rule_Alternative(self):
        r"""
        alternative
            indentation items newline
        """
        with self: # restore state on error
            _discard = self.token_INDENTATION()
            _items = self.rule_Items()
            _discard = self.token_NEWLINE()
        return _items

    def rule_Items(self):
        r"""
        items
            item
            item space items
        """
        _items = [self.rule_Item()] # one or more
        while True:
            with self: # restore state on error
                _space = self.maybe(self.token_SPACE)
                if _space is None:
                    break
                _item = self.maybe(self.rule_Item)
                if _item is None:
                    break
            _items += [_item]
        return tuple(_items)

    def rule_Item(self):
        r"""
        item
            literal
            name
        """
        _literal = self.maybe(self.rule_Literal)
        if _literal is not None:
            return _literal
        _name = self.maybe(self.token_NAME)
        if _name is not None:
            return _name
        assert False, (self.state,) # not a rule_Item?

    def rule_Literal(self):
        r"""
        literal
            singleton
            range exclude
            '"' characters '"'
        """
        # NOTE range must come first because it starts with a singleton
        try:
            with self: # restore state on error
                _range = self.rule_Range()
                _exclude = self.rule_Exclude()
            return tuple(list(_range) + ['.exclude', _exclude])
        except AssertionError:
            pass
        try:
            _singleton = self.rule_Singleton()
            return _singleton
        except AssertionError:
            pass
        try:
            with self: # restore state on error
                _discard = self._str('"')
                _characters = self.token_CHARACTERS()
                _discard = self._str('"')
            return (
                'Characters',
                '.str', _characters,
            )
        except AssertionError:
            pass
        assert False, (self.state,) # not a rule_Literal?

    def rule_Singleton(self):
        r"""
        singleton
            ''' codepoint '''
        """
        with self: # restore state on error
            _discard = self._str("'")
            _codepoint = self.rule_Codepoint()
            _discard = self._str("'")
        return _codepoint

    def rule_Codepoint(self):
        r"""
        codepoint
            ' ' . '10FFFF'
            hexcode
        """
        # NOTE hexcode must come first because it is longer
        _hexcode = self.maybe(self.token_HEXCODE)
        if _hexcode is not None:
            _value = int(_hexcode, 16)
            return (
                'Codepoint',
                '.value', _value,
                '.hex', _hexcode,
            )
        _codepoint = self.maybe(self._codepoint, ord(' '), 0x10FFFF)
        if _codepoint is not None:
            _value, _str, = _codepoint
            return (
                'Codepoint',
                '.value', _value,
                '.str', _str,
            )
        assert False, (self.state,) # not a rule_Codepoint?

    def token_HEXCODE(self):
        r"""
        hexcode
            "10" hex hex hex hex
            hex hex hex hex hex
            hex hex hex hex
        """
        try:
            with self: # restore state on error
                _hexcode = self._str('10')
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
            return _hexcode
        except AssertionError:
            pass
        try:
            with self: # restore state on error
                _hexcode = self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
            return _hexcode
        except AssertionError:
            pass
        try:
            with self: # restore state on error
                _hexcode = self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
                _hexcode += self.token_HEX()
            return _hexcode
        except AssertionError:
            pass
        assert False, (self.state,) # not a token_HEXCODE?

    def token_HEX(self):
        r"""
        hex
            '0' . '9'
            'A' . 'F'
        """
        _c = self[0]
        assert _c is not None
        if _c >= '0' and _c <= '9':
            return self.consume(len(_c))
        if _c >= 'A' and _c <= 'F':
            return self.consume(len(_c))
        assert False, (_c,self.state,) # not a token_HEX?

    def rule_Range(self):
        r"""
        range
            singleton space '.' space singleton
        """
        with self: # restore state on error
            _low = self.rule_Singleton()
            _discard = self.token_SPACE()
            _discard = self._str('.')
            _discard = self.token_SPACE()
            _high = self.rule_Singleton()
        return (
            'Range',
            '.low', _low,
            '.high', _high,
        )

    def rule_Exclude(self):
        r"""
        exclude
            ""
            space '-' space singleton exclude
            space '-' space range exclude
        """
        _exclude = [] # zero or more
        while True:
            # NOTE range must come first because it starts with a singleton
            try:
                with self: # restore state on error
                    _discard = self.token_SPACE()
                    _discard = self._str('-')
                    _discard = self.token_SPACE()
                    _range = self.rule_Range()
                _exclude += [_range]
                continue
            except AssertionError:
                pass
            try:
                with self: # restore state on error
                    _discard = self.token_SPACE()
                    _discard = self._str('-')
                    _discard = self.token_SPACE()
                    _singleton = self.rule_Singleton()
                _exclude += [_singleton]
                continue
            except AssertionError:
                pass
            break # ignore the rest
        return tuple(_exclude)

    def token_CHARACTERS(self):
        r"""
        characters
            character
            character characters
        """
        _characters = self.token_CHARACTER() # one or more
        while True:
            try:
                _character = self.token_CHARACTER()
                _characters += _character
                continue
            except AssertionError:
                pass
            break # ignore the rest
        return _characters

    def token_CHARACTER(self):
        r"""
        character
            ' ' . '10FFFF' - '"'
        """
        with self: # restore state on error
            _codepoint, _str = self._codepoint(ord(' '), 0x10FFFF)
            assert _str != '"'
        return _str

# ssalc McKeemanFormParser


def test():
    println('GO pyparse.parser.bnf')

    name = 'McKeemanFormParser'
    try:
        s = """
S
    '1'
    'a'
    S '+' S

test
    ""
    ' ' . '10FFFF' - '"' - '1234' . '56789'
    "characters" '0000'
"""
        syntax_tree = (
            'Grammar',
            '.rules',
            (
                (
                    'Rule',
                    '.name', 'S',
                    '.nothing', False,
                    '.alternatives',
                    (
                        (
                            ('Codepoint', '.value', 49, '.str', '1',),
                        ),
                        (
                            ('Codepoint', '.value', 97, '.str', 'a',),
                        ),
                        (
                            'S',
                            ('Codepoint', '.value', 43, '.str', '+',),
                            'S',
                        ),
                    ),
                ),
                (
                    'Rule',
                    '.name', 'test',
                    '.nothing', True,
                    '.alternatives',
                    (
                        (
                            (
                                'Range',
                                '.low', ('Codepoint', '.value', 32, '.str', ' ',),
                                '.high', ('Codepoint', '.value', 1114111, '.hex', '10FFFF',),
                                '.exclude',
                                (
                                    ('Codepoint', '.value', 34, '.str', '"',),
                                    (
                                        'Range',
                                        '.low', ('Codepoint', '.value', 4660, '.hex', '1234',),
                                        '.high', ('Codepoint', '.value', 354185, '.hex', '56789',),
                                    ),
                                ),
                            ),
                        ),
                        (
                            ('Characters', '.str', 'characters',),
                            ('Codepoint', '.value', 0, '.hex', '0000',),
                        )
                    ),
                ),
            ),
        )
        p = McKeemanFormParser(s)
        grammar = p.rule_Grammar()
        assert grammar == syntax_tree, (grammar, syntax_tree,)
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    println('OG pyparse.parser.bnf')


__all__ = []
__builtins__ = {} # enter restricted mode
