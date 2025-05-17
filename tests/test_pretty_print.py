#!/usr/bin/python3

from .gen_expr import gen_expr
from scan      import StrScanner

from interpretor import GMS
def test_simple():
    code = " a = 1; b = 2; c = 3;"
    res = GMS(StrScanner(code)).prettyprint()
    print(res)
    assert res.unwrap() ==\
"""\
a = 1;
b = 2;
c = 3;
"""
