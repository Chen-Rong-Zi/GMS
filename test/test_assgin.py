#!/usr/bin/python3
"""
this is a template file
"""
import sys
sys.path.append('../..')

from GMS.interpretor import GMS
from .gen_expr import gen_expr


def test_basic():
    for i in range(100):
        code = f"""{{
            a = {i};
            b = a + 1;
            c = b * a;
            d = a + b + c;
            e = a * b * c * d;
            _e = e;
        }}
        """
        a = i
        b = a + 1
        c = b * a
        d = a + b + c
        e = a * b * c * d
        _e = e
        answer = {
            'a':  i,
            'b':  b,
            'c':  c,
            'd':  d,
            'e':  e,
            '_e':  _e
        }
        for (key, value) in GMS.interpret(code)._inner_value.items():
            assert value == answer[key]
