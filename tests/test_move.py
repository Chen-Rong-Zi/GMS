#!/usr/bin/python3


import sys
import io
from typing    import Never

from returns.result import Success
from .gen_expr import gen_expr
from interpretor import Container, providers
from scan        import StrScanner
from visit       import SemanticAnalyzer, ClosureFlow
from parse       import Parser

def test_basic() -> Never:
    code = r"""
    Num own *p = new Num;
    *p = 123;
    print *p;
    """
    Container.scanner.override(providers.Object(StrScanner(code)))
    gms = Container.gms()

    iobuffer = io.StringIO()
    # 保存原始的 sys.stdout
    oldstdout = sys.stdout
    sys.stdout = iobuffer
    checker = SemanticAnalyzer()
    print(checker.curr_scope._symbols)
    gms.execute().alt(print)
    output = iobuffer.getvalue()
    print(output, file=oldstdout)

    assert '123' in output


def test_basic_move():
    code = """\
    Num own *p = new Num;
    *p = 123;
    Num own *q = p;
    print *q;
    """
    checker = SemanticAnalyzer()
    Container.scanner.override(providers.Object(StrScanner(code)))
    gms = Container.gms()

    iobuffer = io.StringIO()
    # 保存原始的 sys.stdout
    oldstdout = sys.stdout
    sys.stdout = iobuffer
    gms.execute().alt(print)
    output = iobuffer.getvalue()
    print(output, file=oldstdout)

    assert '123' in output
