#!/usr/bin/python3
"""
this is a template file
"""
from random import randint, choice

def gen_num(n):
    return randint(0, n - 1)

def gen_oper():
    match randint(0, 3):
        case 0:
            return '+'
        case 1:
            return '-'
        case 2:
            return '*'
        case 3:
            return '/'

def gen_expr(type=0, depth=1):
    """
    type=0: primitive int
    type=1: expression with operator
    type=2: expression with parentheses
    type=3: expression with unary
    """
    if depth > 200:
        return 1
    match randint(0, 3):
        case 0:
            expr = str(randint(0, 9))
        case 1:
            expr = ''
            expr += str(gen_expr(type, depth + 1))
            expr += gen_oper()
            expr += str(gen_expr(type, depth + 1))
        case 2:
            expr = ''
            expr += '('
            expr += str(gen_expr(type, depth + 1))
            expr += ')'
        case 3:
            expr = ''
            expr += choice(['+', '-'])
            expr += str(gen_expr(type, depth + 1))
    return expr
