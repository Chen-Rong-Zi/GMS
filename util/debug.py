#!/usr/bin/python3

from objprint import objprint as print

DEBUG = True

def debugFunc(func):
    def inner(*args):
        if DEBUG:
            print(f'call {func.__name__}', args)
            print()
        res = func(*args)
        if DEBUG:
            print(f'return {func.__name__}', ' = ', res)
            print()
        return res

    return inner
