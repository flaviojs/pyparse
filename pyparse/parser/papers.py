# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)
r""" Module with miscelaneus stuff related to papers.

-----(paper 1)

"PROPERTIES OF INFINITE LANGUAGES AND GRAMMARS, Matthew Scott Estes, May 2005"
@see http://metanotion.net/misc/thesis.pdf

SsAnBnCnParser -> O(n)? LL(1)?

"2.3 The Halting Problem"
TODO conceptually coverity is like the 'halt' function if it detects cycles? (@see https://scan.coverity.com/)
TODO in python, 'halt' would disassemble function 'f' and prove that it always returns or raises an exception?

"5.3 Undecidability Of Van Wijngaarden Grammars"
TODO maybe it's like a programming language?

"5.4 Infinite Grammars"
"5.5 Infinite Languages"
TODO a token that can have infinite length implies an infinite grammar/language?
     or is it a single symbol in the grammar/language?
"""


from __builtin__ import AssertionError
from __builtin__ import True
from __builtin__ import exit
from pyparse.parser import ParserSkeleton
from pyparse.util import IndexToAttrMixin
from pyparse.util import println


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    exit(1)
except AssertionError:
    pass


class SsAnBnCnParser(ParserSkeleton):
    """
    ```latex
    $ S_s = A^n B^n C^n, n \in \N^0 $
    ```
    """

    class An(IndexToAttrMixin): _index_to_attr = ('n',)
    class Bn(IndexToAttrMixin): _index_to_attr = ('n',)
    class Cn(IndexToAttrMixin): _index_to_attr = ('n',)
    class Ss(IndexToAttrMixin): _index_to_attr = ('n',)

    def rule_An(self):
        _n = 0
        while True:
            try:
                if self[_n] == 'a':
                    _n += 1
                    continue
            except:
                pass
            break
        _slice = self.consume(_n)
        return self.An(n=_n)

    def rule_Bn(self):
        _n = 0
        while True:
            try:
                if self[_n] == 'b':
                    _n += 1
                    continue
            except:
                pass
            break
        _slice = self.consume(_n)
        return self.Bn(n=_n)

    def rule_Cn(self):
        _n = 0
        while True:
            try:
                if self[_n] == 'c':
                    _n += 1
                    continue
            except:
                pass
            break
        _slice = self.consume(_n)
        return self.Cn(n=_n)

    def rule_Ss(self):
        _a = self.rule_An()
        assert _a.n >= 0, _a.n # not negative
        _n = _a.n
        _b = self.rule_Bn()
        assert _b.n == _n, (_b.n,_n) # n must match
        _c = self.rule_Cn()
        assert _c.n == _n, (_c.n,_n) # n must match
        return self.Ss(n=_n)
# ssalc SsAnBnCnParser


def test():
    println('GO pyparse.parser.papers')

    name = 'SsAnBnCnParser n=4'
    try:
        s = "aaaabbbbcccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        assert ss.n == 4, ss
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    name = 'SsAnBnCnParser -a'
    try:
        s = "aaabbbbcccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        println('FAIL', name, ss)
    except AssertionError:
        println('PASS', name)
    except:
        println('ERR', name)
        raise # print traceback

    name = 'SsAnBnCnParser +a'
    try:
        s = "aaaaabbbbcccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        println('FAIL', name, ss)
    except AssertionError:
        println('PASS', name)
    except:
        println('ERR', name)
        raise # print traceback

    name = 'SsAnBnCnParser -b'
    try:
        s = "aaaabbbcccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        println('FAIL', name, ss)
    except AssertionError:
        println('PASS', name)
    except:
        println('ERR', name)
        raise # print traceback

    name = 'SsAnBnCnParser +b'
    try:
        s = "aaaabbbbbcccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        println('FAIL', name, ss)
    except AssertionError:
        println('PASS', name)
    except:
        println('ERR', name)
        raise # print traceback

    name = 'SsAnBnCnParser -c'
    try:
        s = "aaaabbbbccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        println('FAIL', name, ss)
    except AssertionError:
        println('PASS', name)
    except:
        println('ERR', name)
        raise # print traceback

    name = 'SsAnBnCnParser +c'
    try:
        s = "aaaabbbbccccc"
        p = SsAnBnCnParser(s)
        ss = p.rule_Ss()
        println('FAIL', name, ss)
    except AssertionError:
        println('PASS', name)
    except:
        println('ERR', name)
        raise # print traceback

    println('OG pyparse.parser.papers')
# fed test


__all__ = []
__builtins__ = {} # enter restricted mode
