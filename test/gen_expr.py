#!/usr/bin/python3
"""
this is a template file
"""
import sys
import subprocess
import time

from random     import randint

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

def gen_expr(depth=1):
    if depth > 100:
        return 1
    match randint(0, 1):
        case 0:
            expr = str(randint(0, 9))
        case 1:
            expr = ''
            expr += str(gen_expr(depth + 1))
            expr += gen_oper()
            expr += str(gen_expr(depth + 1))
        case 2:
            expr = ''
            expr += '('
            expr += str(gen_expr(depth + 1))
            expr += ')'
    return expr

def cpp_eval(expr):
    process = subprocess.Popen(['/home/rongzi/Program/bin'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=expr)
    if process.returncode != 0:
        raise ZeroDivisionError
    return stdout

def main():
    sum = 0
    count = int(sys.argv[1])
    while True:
        if sum >= count:
            break
        try:
            expression = gen_expr()
            print(expression, eval(expression), sep='\t')
            sum += 1
        except:
            pass
        # try:
            # expr    = gen_expr()
            # py_ans  = myeval(expr)
            # cpp_ans = cpp_eval(expr)
            # print(expr, py_ans, cpp_ans)
            # if py_ans <= 2 ** 31 - 1 and py_ans >= 1:
                # assert py_ans == int(cpp_ans)
                # time.sleep(1)
        # except (ZeroDivisionError, ValueError) as e:
            # continue
        # except KeyboardInterrupt:
            # print('exit')
            # break

if __name__ == '__main__':
    main()

