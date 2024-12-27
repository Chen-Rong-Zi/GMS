#!/usr/bin/python3
"""
this is a template file
"""
import sys
sys.path.append('../..')

from GMS.interpretor import GMS
from .gen_expr import gen_expr

def make_test(type):
    def test():
        interpretor = GMS()
        # count = 0
        for i in range(100):
            try:
                expression = gen_expr(type)
                assert eval(expression) == GMS.evaluate(expression)._inner_value
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
