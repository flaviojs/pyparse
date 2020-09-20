# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)


from __builtin__ import AssertionError
from __builtin__ import True
from __builtin__ import len
from pyparse.parser import ParserSkeleton
from pyparse.util import IndexToAttrMixin
from pyparse.util import println


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    exit(1)
except AssertionError:
    pass


class M3uParser(ParserSkeleton):
    r""" Playlist format of files that end with '.m3u'.

    Created by winamp?
    "It is an ah-hoc standard, with no formal definition, no canonical source, and no owner."

    Extended M3U
    ------------

    Before ID3 tags were supported, resource metadata was placed in the comments.

    Example:
    ```m3u
    #EXTM3U
    #EXTINF:<length of the track in whole seconds>,<name of the tune>
    <resource address>
    #...
    #EXTINF:<length of the track in whole seconds>,<name of the tune>
    <resource address>
    ```

    @see http://gonze.com/playlists/playlist-format-survey.html#M3U
    """

    EXTM3U = '#EXTM3U'
    EXTINF = '#EXTINF:'

    class M3uResource(IndexToAttrMixin): _index_to_attr = ('address','ext',)
    class M3u(IndexToAttrMixin): _index_to_attr = ('resources','ext',)

    def token_NEWLINE(self):
        r"""
        token_NEWLINE = '\n'
                      ;
        """
        assert self[0] == '\n'
        return self.consume(1)

    def rule_Line(self):
        r"""
        rule_Line = ( ! token_NEWLINE )*
                  ;
        """
        _n = 0
        while True:
            _c = self[_n]
            if _c is None or _c == '\n':
                break
            _n += 1
        return self.consume(_n)

    def rule_M3u(self):
        r"""
        rule_M3u = rule_Line +
                 ;; "Each line in a M3U is either a comment, a blank, or a resource to render."
        """
        _exts = (self.EXTM3U,)
        _ext = None
        _ext_m3u = None
        _resources = []
        while True:
            _line = self.rule_Line()
            if _line.strip() == '':
                # blank line
                pass
            elif _line[0] == '#':
                # comment
                if _ext_m3u is None:
                    if _line.strip() in _exts:
                        _ext_m3u = _line
                    else:
                        _ext_m3u = False
                if _ext_m3u == self.EXTM3U and _line.startswith(self.EXTINF):
                    _ext = _line
                else:
                    _ext = None
            else:
                # resource
                _resource = self.M3uResource(address=_line,ext=_ext)
                _resources += [_resource]

            _newline = self.maybe(self.token_NEWLINE)
            if _newline is None:
                break # no more lines

        return self.M3u(resources=_resources,ext=_ext_m3u)
# ssalc M3uParser


def test():
    println('GO pyparse.parser.m3u')

    name = 'M3uParser m3u'
    try:
        s = """one_second.mkv
empty.mkv
"""
        p = M3uParser(s)
        m3u = p.rule_M3u()
        assert m3u.ext is None
        assert len(m3u.resources) == 2, m3u
        assert m3u.resources[0].address == 'one_second.mkv', m3u
        assert m3u.resources[0].ext is None, m3u
        assert m3u.resources[1].address == 'empty.mkv', m3u
        assert m3u.resources[1].ext is None, m3u
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    name = 'M3uParser extm3u'
    try:
        s = """#EXTM3U

#EXTINF:1,One Second
one_second.mkv

#EXTINF:0,Empty
empty.mkv
"""
        p = M3uParser(s)
        m3u = p.rule_M3u()
        assert m3u.ext == '#EXTM3U', m3u
        assert len(m3u.resources) == 2, m3u
        assert m3u.resources[0].address == 'one_second.mkv', m3u
        assert m3u.resources[0].ext == '#EXTINF:1,One Second', m3u
        assert m3u.resources[1].address == 'empty.mkv', m3u
        assert m3u.resources[1].ext == '#EXTINF:0,Empty', m3u
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    println('OG pyparse.parser.m3u')
# fed test


__all__ = []
__builtins__ = {} # enter restricted mode
