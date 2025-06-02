#!/usr/bin/python3
"""
this is a template file
"""


import io, sys

from .gen_expr import gen_expr
from interpretor import Container, providers
from scan        import StrScanner

def make_test(expr_type):
    def test():
        for _ in range(100):
            try:
                expression = gen_expr(expr_type)
                code = f'print {expression};'
                print(f'{expression = }', f'{code = }')

                iobuffer = io.StringIO()
                # 保存原始的 sys.stdout
                oldstdout = sys.stdout
                sys.stdout = iobuffer
                Container.scanner.override(providers.Object(StrScanner(code)))
                gms = Container.gms()
                gms.execute()
                output = iobuffer.getvalue()

                assert eval(expression) == eval(output.strip())
                # print(f'\rpass {count} tests', end='')
            except ZeroDivisionError:
                pass
            # count += 1
        print()
    return test

def test_basic():
    make_test(0)()

def test_op():
    make_test(1)()

def test_eval():
    make_test(2)()

def test_unary():
    make_test(3)()

test_eval()
