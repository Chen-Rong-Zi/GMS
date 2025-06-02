#!/usr/bin/python3

from .gen_expr import gen_expr
from scan      import StrScanner
from interpretor import Container, providers

def test_simple():
    code = " a = 1; b = 2; c = 3;"
    Container.scanner.override(providers.Object(StrScanner(code)))
    gms = Container.codeformator()
    res = gms.execute()
    print(res)
    assert res.unwrap() ==\
"""\
a = 1;
b = 2;
c = 3;
"""
