# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)


from __builtin__ import AssertionError
from __builtin__ import exit
from __builtin__ import tuple
from pyparse.parser import ParserSkeleton
from pyparse.util import IndexToAttrMixin
from pyparse.util import println


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    exit(1)
except AssertionError:
    pass


class Lisp1Parser(ParserSkeleton):
    """ Incomplete parser for Lisp I.

    Based on "LISP I   PROGRAMMER'S MANUAL   March 1, 1960"

    Note that there are several hand-written corrections:
     * cover: something about page 17?
     * page 2: IBM 704 to IBM 709? paragraph removed
     * page 11: 704 to 709?
     * page 16: define pairlis? change pair to pairlis? change assoc to sassoc?
     * page 17: fix sublis, modify translation to S-expression
     * page 18: change apply to evalquote, remove note
     * page 19: define evalquote?
     * page 20: ???
     * page 24: note about end of list, remove (), LISP I.5?, remove p-list, remove ()
     * page 25: change tracklist to ???, change TRACKLIST to ???
     * page 35: remove (), change TRACKLIST to ???, remove (), change (T) to *T*
     * page 36: change (F) to NIL?
     * page 37: replace APPLY with ???
     * there are more...

    WARNING spaces are used in place of commas in page 32-35
    WARNING page 66 says spaces are commas, and redundant commas are ignored
    """

    class Atom(IndexToAttrMixin): _index_to_attr = ('s',)
    class ImplicitNilAtom(IndexToAttrMixin): _index_to_attr = ('s',) # => Atom 'NIL'
    class Comma(IndexToAttrMixin): _index_to_attr = ('s',)
    class SymbolicExpression(IndexToAttrMixin): _index_to_attr = ('s','e1','e2',)
    class MetaExpression(IndexToAttrMixin): _index_to_attr = ('s','func','args',)
    class ConditionalExpressions(IndexToAttrMixin): _index_to_attr = ('s','expressions',)

    def token_ATOM(self):
        """ Atomic symbol. (@see pages 10-11)

        It is ambiguous, maybe originally intended as (A-Z0-9)+ ?
        Handling of whitespace is not specified.

        Uppercase is used for symbolic expression stuff.
        Lowercase is used for meta expression stuff.

        Currently accepting anything that is not considered a delimiter...

        TODO is a space an atom in LISP-SAP? (@see page 54)
        """
        _delimiters = ('(','·',',',' ',')','[',';','\t',']',)
        _n = 0
        while True:
            _c = self[_n]
            if _c is None:
                break
            if _c in _delimiters:
                break
            _n += 1
        assert _n >= 0
        _s = self.cursor.consume(_n)
        return self.Atom(s=_s)

    def token_COMMA(self):
        """ (',' | ' ')+

        @see page 66
        @see page 32  "Note that spaces are used in place of commas."
        """
        _commas = (',',' ')
        _n = 0
        while True:
            _c = self[_n]
            if _c is None:
                break
            if _c not in _commas:
                break
            _n += 1
        assert _n >= 0
        _s = self.consume(_n)
        return self.Comma(s=_s)

    def rule_SymbolicExpression(self, abbreviation=False):
        """ Symbolic expression. (@see pages 11-12)

        Can be:
        ATOM
        (e1·e2)

        Abbreviations:
        (m)           -> (m·NIL)
        (m1,...,mn)   -> (m1·(...·(mn·NIL)))
        (m1,...,mn·x) -> (m1·(...·(mn·x)))
        ((AB,C),D)    -> ((AB·(C·NIL))·(D·NIL))
        ((A,B),C,D·E) -> ((A·(B·NIL))·(C·(D·E)))
        """
        with self:
            _atom = self.maybe(self.token_ATOM)
            if _atom is not None:
                # ATOM
                return _atom

            _s = []
            _e1 = None
            _e2 = None
            if abbreviation:
                _comma = self.token_COMMA()
                _s += [_comma.s]
            else:
                assert self[0] == '('
                _s += [self.consume(1)] # '('

            _e1 = self.rule_S_expression()
            _s += [_e1.s]
            if self[0] == '·':
                # (e1·e2)
                _s += [self.consume(1)] # '·'
                _e2 = self.rule_S_expression()
                _s += [_e2.s]
                assert self[0] == ')'
                _s += [self.consume(1)] # ')'
            elif self[0] == ')':
                # abbreviation  (m)           -> (m·NIL)
                _e2 = self.ImplicitNilAtom(s=self.consume(0))
                _s += [self.consume(1)] # ')'
            else:
                # abbreviation  (m1,...,mn)   -> (m1·(...·(mn·NIL)))
                # abbreviation  (m1,...,mn·x) -> (m1·(...·(mn·x)))
                _e2 = self.rule_S_expression(abreviation=True)
                _s += [_e2.s]

        _s = tuple(_s)
        assert _e1 is not None
        assert _e2 is not None
        return self.SymbolicExpression(s=_s,e1=_e1,e2=_e2)

    def rule_MetaExpression(self):
        """ Meta expression. (@see page 12)

        func
        func[arg]
        func[arg;...;arg]
        """
        with self:
            _s = []
            _func = self.token_ATOM()
            _args = []
            if self[0] == '[':
                _delim = '['
                while self[0] != ']':
                    assert self[0] == _delim
                    _s += [self.consume(1)] # '[' or ';'
                    _delim = ';'
                    _e = self.rule_SymbolicExpression()
                    _s += [_e.s]
                    _args += [_e]

                _s += [self.consume(1)] # ']'

        _s = tuple(_s)
        _args = tuple(_args)
        return self.MetaExpression(s=_s,func=_func,args=_args)

    def rule_ConditionalExpressions(self):
        """ TODO [?→?;...;?→?] (@see page 14)

        → is the tab character?
        """
        pass

    @staticmethod
    def toSymbolicExpression(x):
        """ TODO (@see page 17, 9 rules) """
        pass
# ssalc Lisp1Parser


__all__ = []
__builtins__ = {} # enter restricted mode
