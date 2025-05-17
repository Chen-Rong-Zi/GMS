#!/usr/bin/python3

from objprint import objprint as print
import sys

DEBUG = True

def debugFunc(func):
    def inner(*args):
        if DEBUG:
            print(f'call {func.__name__}', args, file=sys.stderr)
            print(file=sys.stderr)
        res = func(*args)
        if DEBUG:
            print(f'return {func.__name__}', ' = ', res, file=sys.stderr)
            print(file=sys.stderr)
        return res

    return inner
