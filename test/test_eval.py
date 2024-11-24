#!/usr/bin/python3
"""
this is a template file
"""
import sys
sys.path.append('../..')

from GMS.interpretor import Evaluater
from .gen_expr import gen_expr

def test_eval():
    for i in range(100):
        try:
            expression = gen_expr()
            assert eval(expression) == Evaluater(expression).expr()._inner_value
        except ZeroDivisionError:
            pass
        # except AssertionError:
            # print(expression)
