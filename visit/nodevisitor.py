#!/usr/bin/python3
"""
"""

from operator import add, sub, mul, truediv, lt, gt, le, ge, eq

import tokenize
from tokenize import NUMBER, NAME, STRING, OP, NEWLINE, ENDMARKER, PLUS, MINUS, STAR, SLASH, TokenInfo
from tokenize import LESSEQUAL, LESS, GREATEREQUAL, GREATER, EQEQUAL

from returns.result     import safe,   Success, Failure, Result
from returns.maybe      import Nothing, Some
from returns.converters import flatten
from returns.pipeline   import is_successful
from returns.iterables  import Fold

from node.ast    import Num, BinOp, UnaryOp, Empty, Compound, Assign, Variable, PrintStat, VarDeclaration, Type, FuncDeclaration
from node.symbol import ScopedSymbolTable, VarSymbol

from util import debugFunc


class NodeVisitor:
    BasicOperation = {
        PLUS  : add,
        MINUS : sub,
        STAR  : mul,
        SLASH : truediv,
        LESS : lt,
        GREATER : gt,
        EQEQUAL : eq,
        LESSEQUAL : le,
        GREATEREQUAL : ge,
    }

    @safe
    def take(token):
        match token:
            case TokenInfo(type=tokenize.NUMBER, string=string):
                return int(string)
            case TokenInfo(type=tokenize.NAME, string='True' | 'False' as string):
                return eval(string)
            case TokenInfo(type=tokenize.STRING, string=string):
                return string
            case t:
                raise Exception(f"unkown factor token {t}")

    @safe
    def binary_calc(op, operand1, operand2):
        return NodeVisitor.BasicOperation[op.exact_type](operand1, operand2)

    def visit(self, node):
        """
        reload visit functions
        visit(node: AstNode) -> Result
        """
        # print(node)
        name = type(node).__name__
        visit_method = getattr(self, 'visit_' + name, self.generic_visit)
        return visit_method(node)

    def generic_visit(self, node):
        raise Exception(f'Not Implemented Operand Type: {type(node).__name__}')

######### just for fun ############

class RPNVisitor(NodeVisitor):
    def visit_Num(self, node):
        return str(node)

    def visit_BinOp(self, node):
        return f'{self.visit(node.left)} {self.visit(node.right)} {node.op.string}'

    def visit_UnaryOp(self, node):
        return str(node)

class LispVisitor(NodeVisitor):
    def visit_Num(self, node):
        return str(node)

    def visit_BinOp(self, node):
        return f'({node.op.string} {self.visit(node.left)} {self.visit(node.right)})'

    def visit_UnaryOp(self, node):
        return f'({node.op.string} {self.visit(node.expr)})'

