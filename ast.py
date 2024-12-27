#!/usr/bin/python3
"""
this is a template file
"""
from functools import reduce

class AST:
    pass

class Num(AST):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return str(self.token.string)

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left  = left
        self.op    = op
        self.right = right

    def __str__(self):
        return '(' + str(self.left) + str(self.op.string) + str(self.right) + ')'


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op   = op
        self.expr = expr

    def __str__(self):
        return f'{self.op.string} {str(self.expr)}'

class Empty(AST):
    def __str__(self):
        return 'Empty'

class Compound(AST):
    def __init__(self, children):
        self.children = children

    def add_child(self, child):
        self.children.append(child)

    def __str__(self, level=0):
        string = '{'
        string += ''.join(str(statement) for statement in self.children)
        string += '}'
        return string

class Assign(AST):
    def __init__(self, lvalue, op, rvalue):
        self.lvalue = lvalue
        self.op     = op
        self.rvalue = rvalue

    def __str__(self):
        return f'{str(self.lvalue)} = {str(self.rvalue)}'

class Variable(AST):
    def __init__(self, token):
        self.token  = token
        self.string = self.token.string
        self.name   = self.token.string

    def __str__(self):
        return self.token.string

class PrintStat(AST):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f'print {str(self.expr)}'

class Declaration(AST):
    def __init__(self, _type, token):
        self._type = _type
        self.token = token
        self.name  = self.token.string

    def __str__(self):
        return f'{str(self._type)} {self.name};\n'

class Type(AST):
    def __init__(self, _type):
        self._type = _type
        self.name  = self._type.string

    def __str__(self):
        return self._type.string
