# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)


from __builtin__ import AssertionError
from __builtin__ import exit
from __builtin__ import int
from __builtin__ import ord
from __builtin__ import range
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


class Utf8Parser(ParserSkeleton):
    """ Parse utf8 bytes.

    codepoints - yields codepoints from bytes

    TODO what to do with multiple representions of the same codepoint?
    TODO graphemes?
    """

    HIGH_0 = int('00000000', 2)
    HIGH_1 = int('10000000', 2)
    HIGH_2 = int('11000000', 2)
    HIGH_3 = int('11100000', 2)
    HIGH_4 = int('11110000', 2)
    HIGH_5 = int('11111000', 2)
    HIGH_6 = int('11111100', 2)
    HIGH_7 = int('11111110', 2)
    HIGH_8 = int('11111111', 2)
    LOW_0 = int('00000000', 2)
    LOW_1 = int('00000001', 2)
    LOW_2 = int('00000011', 2)
    LOW_3 = int('00000111', 2)
    LOW_4 = int('00001111', 2)
    LOW_5 = int('00011111', 2)
    LOW_6 = int('00111111', 2)
    LOW_7 = int('01111111', 2)
    LOW_8 = int('11111111', 2)

    class Continuation(IndexToAttrMixin): _index_to_attr = ('b','s',)
    class Leading(IndexToAttrMixin): _index_to_attr = ('b','s',)
    class Codepoint(IndexToAttrMixin): _index_to_attr = ('codepoint','s',)

    def __getitem__(self, item):
        _c = ParserSkeleton.__getitem__(self, item)
        assert _c is not None # never None
        return ord(_c) # byte value instead of character

    def byte_Leading(self):
        _b = self[0]
        assert (_b & self.HIGH_2) != self.HIGH_1
        _s = self.consume(1)
        return self.Leading(b=_b, s=_s)

    def byte_Continuation(self):
        _b = self[0]
        assert (_b & self.HIGH_2) == self.HIGH_1
        _s = self.consume(1)
        return self.Continuation(b=_b, s=_s)

    def rule_Codepoint(self):
        """ rule_Codepoint = byte_Leading byte_Continuation* """
        _sub_rules = [
            # _prefix, _prefix_mask, _data_mask, _n_continuation
            (self.HIGH_0, self.HIGH_1, self.LOW_7, 0,), # 0xxxxxxx
            (self.HIGH_2, self.HIGH_3, self.LOW_5, 1,), # 110xxxxx 10xxxxxx
            (self.HIGH_3, self.HIGH_4, self.LOW_4, 2,), # 1110xxxx 10xxxxxx 10xxxxxx
            (self.HIGH_4, self.HIGH_5, self.LOW_3, 3,), # 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
            (self.HIGH_5, self.HIGH_6, self.LOW_2, 4,), # 111110xx 10xxxxxx 10xxxxxx 10xxxxxx 10xxxxxx
            (self.HIGH_6, self.HIGH_7, self.LOW_1, 5,), # 1111110x 10xxxxxx 10xxxxxx 10xxxxxx 10xxxxxx 10xxxxxx
            # 11111110 is 0xFE, used for the BOM in UTF-16, currently meaningless in utf8
            # 11111111 is 0xFF, used for the BOM in UTF-16, currently meaningless in utf8
        ]
        with self:
            _leading = self.byte_Leading()
            _b = _leading.b
            for _prefix, _prefix_mask, _data_mask, _n_continuations in _sub_rules:
                if _prefix == (_b & _prefix_mask):
                    _codepoint = (_b & _data_mask)
                    break
            else:
                assert False, _b # invalid utf8?
            _s = [_leading.s]
            for _ in range(_n_continuations):
                _continuation = self.byte_Continuation()
                _b = _continuation.b
                _codepoint = (_codepoint << 6) + (_b & self.LOW_6)
                _s += [_continuation.s]
        return self.Codepoint(codepoint=_codepoint, s=tuple(_s))

    def codepoint_generator(self):
        while True:
            _rule = self.maybe(self.rule_Codepoint)
            if _rule is None:
                break
            yield _rule.codepoint
# ssalc Utf8Parser


def test():
    println('GO pyparse.parser.unicode')

    name = 'Utf8Parser codepoint 0'
    try:
        s = '0' # zero (0)
        p = Utf8Parser(s)
        c = p.rule_Codepoint()
        assert c.codepoint == 0x30, c # '0'
        assert c.s == ('0',), c
        c = p.maybe(p.rule_Codepoint)
        assert c is None, c
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    name = 'Utf8Parser codepoint €'
    try:
        s = '\xE2\x82\xAC' # euro (€)
        p = Utf8Parser(s)
        c = p.rule_Codepoint()
        assert c.codepoint == 0x20AC, c # '€'
        assert c.s == ('\xE2','\x82','\xAC',), c
        c = p.maybe(p.rule_Codepoint)
        assert c is None, c
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    println('OG pyparse.parser.unicode')
# fed test


__all__ = []
__builtins__ = {} # enter restricted mode
