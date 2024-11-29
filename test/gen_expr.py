#!/usr/bin/python3
"""
this is a template file
"""
import sys
import subprocess
import time

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
    if depth > 100:
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

def cpp_eval(expr):
    process = subprocess.Popen(['/home/rongzi/Program/bin'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=expr)
    if process.returncode != 0:
        raise ZeroDivisionError
    return stdout

# def main():
    # sum = 0
    # count = int(sys.argv[1])
    # while True:
        # if sum >= count:
            # break
        # try:
            # expression = gen_expr()
            # print(expression, eval(expression), sep='\t')
            # sum += 1
        # except:
            # pass

# if __name__ == '__main__':
    # main()
