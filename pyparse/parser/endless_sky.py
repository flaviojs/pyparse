# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)


from __builtin__ import AssertionError
from __builtin__ import True
from __builtin__ import exit
from __builtin__ import tuple
from __builtin__ import len
from __builtin__ import slice
from pyparse.parser import ParserSkeleton
from pyparse.util import IndexToAttrMixin
from pyparse.util import println


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    exit(1)
except AssertionError:
    pass


class EndlessSkyParser(ParserSkeleton):
    r""" Parser for the data files of the game ``endless-sky''.

    @see endless-sky/source/DataFile.{cpp,h}
    @see endless-sky/source/DataNode.{cpp,h}
    """

    class EmptyLine(IndexToAttrMixin): _index_to_attr = ('s','lineNumber',)
    class DataLine(IndexToAttrMixin): _index_to_attr = ('s','indent','tokens','lineNumber',)
    class DataNode(IndexToAttrMixin): _index_to_attr = ('s','indent','tokens','lines','children',)

    class State(ParserSkeleton.State):
        def __init__(self, *args, **kwargs):
            ParserSkeleton.State.__init__(self, *args, **kwargs)
            self.lineNumber = 1

    def token_NEWLINE(self):
        r""" Read a newline character. """
        _c = self[0]
        assert _c == '\n', _c
        self.state.lineNumber += 1
        return self.consume(1)

    def token_WHITESPACE(self):
        r""" Read "whitespace". """
        _n = 0
        while True:
            try:
                _c = self[_n]
                assert _c is not None, _c
                assert _c != '\n', _c
                assert _c <= ' ', _c
                _n += 1
            except AssertionError:
                break

        assert _n > 0, _n
        return self.consume(_n)

    def token_COMMENT(self):
        r""" Read a comment. """
        assert self[0] == '#'
        _n = 1
        while True:
            try:
                _c = self[_n]
                assert _c is not None, _c
                assert _c != '\n', _c
                _n += 1
            except AssertionError:
                break

        assert _n > 0, _n
        return self.consume(_n)

    def token_TOKEN(self):
        r""" Read a quoted or regular token. """
        _quotes = ('"','`',)
        _quote = self[0]
        if _quote in _quotes:
            _n = 1
            while True:
                try:
                    _c = self[_n]
                    assert _c is not None, _c
                    assert _c != '\n', _c
                    _n += 1
                    if _c == _quote:
                        break
                except AssertionError:
                    pass
            assert _c == _quote, (_c, _quote) # must terminate with the same quote
        else:
            assert _quote is not None, _quote # not end of data
            assert _quote != '#', _quote # not line comment
            _n = 0
            while True:
                try:
                    _c = self[_n]
                    assert _c is not None, _c
                    assert _c != '\n', _c
                    assert _c > ' ', _c
                    _n += 1
                except AssertionError:
                    break

        assert _n > 0
        return self.consume(_n)

    def rule_EmptyLine(self):
        r"""
        rule_EmptyLine = token_WHITESPACE? token_COMMENT? token_NEWLINE
                       ;
        """
        with self: # revert state on error
            _s = []
            _whitespace = self.maybe(self.token_WHITESPACE)
            if _whitespace is not None:
                _s += [_whitespace]            
            _comment = self.maybe(self.token_COMMENT)
            if _comment is not None:
                _s += [_comment]
            _newline = self.token_NEWLINE()
            _s += [_newline]

        _s = tuple(_s)
        _lineNumber = self.state.lineNumber
        return self.EmptyLine(s=_s,lineNumber=_lineNumber)

    def rule_DataLine(self):
        r"""
        rule_DataLine = token_WHITESPACE? ( token_DATA token_WHITESPACE? )+ rule_EmptyLine
                      ;; the token_WHITESPACE at the start is the indent
        """
        with self: # revert state on error
            _s = []
            _lineNumber = self.state.lineNumber
            _indent = self.maybe(self.token_WHITESPACE)
            if _indent is None:
                _indent = self.consume(0)
            _s += [_indent]
            _tokens = []
            while True:
                try:
                    _token = self.token_TOKEN()
                    _tokens += [_token]
                    _s += [_token]
                    _whitespace = self.maybe(self.token_WHITESPACE)
                    if _whitespace is not None:
                        _s += [_whitespace]
                except AssertionError:
                    break # no more tokens
            _empty_line = self.rule_EmptyLine()
            _s += [_empty_line.s]

        assert len(_tokens) > 0 # expecting a token
        _s = tuple(_s)
        return self.DataLine(s=_s,indent=_indent,tokens=_tokens,lineNumber=_lineNumber)

    def rule_DataNode(self, parent_indent=None):
        r"""
        rule_DataNode = ( rule_EmptyLine )* rule_DataLine rule_DataNode*
                      ;; the rule_DataNode at the end must be children
        """
        with self: # revert cursor on error
            _s = []
            _lineNumber = self.state.lineNumber
            while True:
                _emptyline = self.maybe(self.rule_EmptyLine)
                if _emptyline is None:
                    break # no more empty lines
                _s += [_emptyline.s]
            _dataline = self.rule_DataLine()
            _indent = _dataline.indent
            if parent_indent is None:
                assert _dataline.indent == '' # must be at line start
            else:
                assert _dataline.indent != parent_indent # must be a child
                assert _dataline.indent.startswith(parent_indent) # must match
            _s += [_dataline.s]
            _children = []
            while True:
                try:
                    with self:
                        _child = self.rule_DataNode(parent_indent=_indent)
                        if _children:
                            assert _children[0].indent == _child.indent, (_children[0].indent, child.indent,) # must be at the same level
                        _children += [_child]
                        _s += [_child.s]
                except AssertionError as err:
                    break # no more children

        _s = tuple(_s)
        _tokens = tuple(_dataline.tokens)
        _lines = slice(_lineNumber, self.state.lineNumber)
        _children = tuple(_children)
        _datanode = self.DataNode(s=_s,indent=_indent,tokens=_tokens,lines=_lines,children=_children)
        return _datanode
# ssalc EndlessSkyParser


def test():
    println('GO pyparse.parser.endless_sky')

    name = 'EndlessSkyParser with valid data'
    try:
        s = """# comment
root1 token1 "token 2" `token 3`
    child1.1 token 1.1
    child1.2

root2

# ignored
"""
        p = EndlessSkyParser(s)
        node = p.maybe(p.rule_DataNode)
        assert node is not None, node
        assert node.indent == '', node
        assert node.tokens == ('root1','token1','"token 2"','`token 3`',), node
        assert node.lines == slice(1, 5), node # includes the comment
        assert len(node.children) == 2, node

        assert node.children[0].indent == '    ', node
        assert node.children[0].tokens == ('child1.1', 'token', '1.1',), node
        assert node.children[0].lines == slice(3, 4), node
        assert len(node.children[0].children) == 0, node

        assert node.children[1].indent == '    ', node
        assert node.children[1].tokens == ('child1.2',), node
        assert node.children[1].lines == slice(4, 5), node
        assert len(node.children[1].children) == 0, node

        node = p.maybe(p.rule_DataNode)
        assert node is not None, node
        assert node.indent == '', node
        assert node.tokens == ('root2',), node
        assert node.lines == slice(5, 7), node # includes the empty line
        assert len(node.children) == 0, node

        node = p.maybe(p.rule_DataNode)
        assert node is None, node # ignores the rest
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print stacktrace

    # TODO test invalid data
    # TODO test s?

    println('OG pyparse.parser.endless_sky')
# fed test


__all__ = []
__builtins__ = {} # enter restricted mode
