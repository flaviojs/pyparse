# -*- coding: utf8 -*-
# license: WTFPL version 2, or whatever is closest to "no license" and "public domain" (like Unlicense or CC0)
r""" Module with utility stuff.

Module ``pyparse.util''.

NOTE:
    class objects = old-style classes = classic classes
    class types   = new-style classes (@since python 2.2?)

Future
======

TODO explore cpython stuff (lots of stuff there, @see cpython/Misc/cheatsheet)
TODO protect execution from the debugger?
TODO __members__ and __methods__?
TODO config defaults?
TODO protect private stuff of modules?
TODO remove globals from functions and other stuff?
TODO study https://github.com/tav/scripts/blob/master/safelite.py
     @see http://tav.espians.com/a-challenge-to-break-python-security.html
     @see http://tav.espians.com/paving-the-way-to-securing-the-python-interpreter.html
     @see http://tav.espians.com/update-on-securing-the-python-interpreter.html
TODO make a strview or similar, memoryview is not satisfactory
"""


import __builtin__
from __builtin__ import AssertionError as _builtin_AssertionError
from __builtin__ import IndexError     as _builtin_IndexError
from __builtin__ import KeyError       as _builtin_KeyError
from __builtin__ import basestring     as _builtin_basestring
from __builtin__ import enumerate      as _builtin_enumerate
from __builtin__ import getattr        as _builtin_getattr
from __builtin__ import int            as _builtin_int
from __builtin__ import isinstance     as _builtin_isinstance
from __builtin__ import len            as _builtin_len
from __builtin__ import setattr        as _builtin_setattr
from sys import exc_info               as _sys_exc_info


# function executed by the print statement
println = _builtin_getattr(__builtin__, 'print')


try:
    assert False # assert must work
    println('the assert statement does not work, disable optimizations to fix this')
    _builtin_exit(1)
except _builtin_AssertionError:
    pass


class IndexToAttrMixin:
    r""" Class object that redirects indexes to attributes.

    Expects ``self._index_to_attr'' to be a sequence of index names.
    """

    def __init__(self, *args, **kw):
        _index_to_attr = self._index_to_attr
        _n_args = _builtin_len(args)
        if _n_args > _builtin_len(_index_to_attr):
            raise _builtin_IndexError, args # too many unnamed args
        for _i, _k in _builtin_enumerate(_index_to_attr):
            if _i < _n_args:
                if _k in kw:
                    raise _builtin_KeyError, _k # too many values (unnamed arg and named arg)
                _v = args[_i]
            else:
                _v = None
            _builtin_setattr(self, _k, _v)
        for _k, _v in kw.items():
            _builtin_setattr(self, _k, _v)

    def __getitem__(self, index, *args, **kw):
        _name = self._index_to_attr[index]
        return _builtin_getattr(self, _name)

# ssalc IndexToAttrMixin


def caller_source(nth=1, *args, **kw):
    """ Returns the file name and line number of the ``nth'' caller of this function or ``None''.

    The code that calls this functions is the ``nth=1'' caller.
    ``nth'' must be > 0
    """
    assert nth > 0, nth # only callers of this function
    try:
        raise _builtin_Exception
    except:
        _exc_info = _sys_exc_info()
        _traceback = _exc_info[2]
        _frame = _traceback.tb_frame
        while _frame and nth > 0:
            _frame = _frame.f_back
            nth -= 1
        if _frame:
            return (_frame.f_code.co_filename, _frame.f_lineno,)
        else:
            return None
# fed caller_source


def test():
    println('GO pyparse.util')

    name = 'caller_source'
    try:
        _source = caller_source()
        assert _builtin_len(_source) == 2, _source
        assert _builtin_isinstance(_source[0], _builtin_basestring), _source
        assert _builtin_isinstance(_source[1], _builtin_int), _source
        println('PASS', name)
    except:
        println('FAIL', name)
        raise # print traceback

    println('OG pyparse.util')
# fed test


__all__ = []
__builtins__ = {} # enter restricted mode
