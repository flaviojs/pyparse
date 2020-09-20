# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)
r""" Test script for ``pyparse''. """


import pyparse
if hasattr(pyparse, 'test'):
    pyparse.test()


import pyparse.util
if hasattr(pyparse.util, 'test'):
    pyparse.util.test()


import pyparse.parser
if hasattr(pyparse.parser, 'test'):
    pyparse.parser.test()


import pyparse.parser.bnf
if hasattr(pyparse.parser.bnf, 'test'):
    pyparse.parser.bnf.test()


import pyparse.parser.endless_sky
if hasattr(pyparse.parser.endless_sky, 'test'):
    pyparse.parser.endless_sky.test()


import pyparse.parser.lisp
if hasattr(pyparse.parser.lisp, 'test'):
    pyparse.parser.lisp.test()


import pyparse.parser.m3u
if hasattr(pyparse.parser.m3u, 'test'):
    pyparse.parser.m3u.test()


import pyparse.parser.papers
if hasattr(pyparse.parser.papers, 'test'):
    pyparse.parser.papers.test()


import pyparse.parser.unicode
if hasattr(pyparse.parser.unicode, 'test'):
    pyparse.parser.unicode.test()
