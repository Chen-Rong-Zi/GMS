#!/usr/bin/python3
"""
this is a template file
"""
import sys
sys.path.append('../..')

from GMS.interpretor import Interpretor
from .gen_expr import gen_expr

def make_test(type):
    def test():
        for i in range(100):
            try:
                expression = gen_expr(type)
                print(expression)
                assert eval(expression) == Interpretor.evaluate(expression)._inner_value
            except ZeroDivisionError:
                pass
            # except AssertionError:
                # print(expression)
    return test

def test_basic():
    make_test(0)()

def test_op():
    make_test(1)()

def test_eval():
    make_test(2)()

def test_unary():
    make_test(3)()
