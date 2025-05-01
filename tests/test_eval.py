#!/usr/bin/python3
"""
this is a template file
"""


from .gen_expr import gen_expr

from interpretor import GMS
from scan        import StrScanner

def make_test(expr_type):
    def test():
        for _ in range(100):
            try:
                expression = gen_expr(expr_type)
                assert eval(expression) == GMS(StrScanner(expression)).evaluate().value_or(None)
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
