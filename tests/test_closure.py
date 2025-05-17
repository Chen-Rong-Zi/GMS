#!/usr/bin/python3


import sys
import io
from typing    import Never

from returns.result import Success
from .gen_expr import gen_expr
from interpretor import GMS
from scan        import StrScanner
from visit       import SemanticAnalyzer, ClosureFlow
from parse       import Parser

def test_check_depth() -> Never:
    code = r"""
    func outer() {
        Num a;
        a = 111;
        func inner() {
            a = 222;
            func inner0() {
                a = 333;
                func inner1() {
                    a = 444;
                    return a;
                }
                return inner1();
            }
            return inner0();
        }
        return inner();
    }

    print outer();
    """
    gms = Success(GMS(StrScanner(code)))

    iobuffer = io.StringIO()
    # 保存原始的 sys.stdout
    oldstdout = sys.stdout
    sys.stdout = iobuffer
    checker = SemanticAnalyzer()
    print(checker.curr_scope._symbols)
    # gms.parse_and_visit(Parser, ClosureFlow(checker)).unwrap()
    gms.bind(lambda g: g.parse_and_visit(Parser, checker)).bind(ClosureFlow(checker).visit).alt(print)
    output = iobuffer.getvalue()
    print(output, file=oldstdout)

    assert '444' in output


def test_recursion():
    code = """\
    func fib(Num a) {
        return 0 if a <= 0 else 1 if a == 1 else fib(a - 1) + fib(a - 2);
    }

    func fact(Num a) {
        return 1 if a <= 1 else a * fact(a - 1);
    }
    print fib(10);
    print fib(4);
    print fact(10);
    print fact(4);
    """
    checker = SemanticAnalyzer()
    gms = Success(GMS(StrScanner(code)))

    iobuffer = io.StringIO()
    # 保存原始的 sys.stdout
    oldstdout = sys.stdout
    sys.stdout = iobuffer
    gms.bind(lambda g: g.parse_and_visit(Parser, checker)).bind(ClosureFlow(checker).visit).alt(print)
    output = iobuffer.getvalue()
    print(output, file=oldstdout)

    assert output == ('\n'.join(['55', '3', '3628800', '24']) + '\n')
