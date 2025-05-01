#!/usr/bin/python3
"""
this is a template file
"""

from scan.scanner import StrScanner
from .gen_expr import gen_expr
from interpretor import GMS
from objprint    import objprint as print


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
        scope = GMS(StrScanner(code)).interpret().value_or(None)
        print(scope)
        for (key, value) in scope.items():
            assert value == answer[key]
