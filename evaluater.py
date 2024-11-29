#!/usr/bin/python3
"""
"""

from operator import add, sub, mul, truediv
from tokenize import NUMBER, OP, NEWLINE, ENDMARKER, PLUS, MINUS, STAR, SLASH, TokenInfo

from returns.result     import safe,   Success, Failure, Result
from returns.maybe      import Nothing, Some
from returns.converters import flatten
from returns.pipeline   import is_successful


class Evaluater:
    BasicOperation = {
        PLUS  : add,
        MINUS : sub,
        STAR  : mul,
        SLASH : truediv
    }

    @safe
    def take(token):
        return eval(str(token))

    @safe
    def binary_calc(op, operand1, operand2):
        return Evaluater.BasicOperation[op.exact_type](operand1, operand2)

    def visit(self, node):
        """
        reload visit functions
        visit(node: BinOp) -> Result
        visit(node: Num) -> Result
        """
        name = type(node).__name__
        visit_method = getattr(self, 'visit_' + name, self.generic_visit)
        return visit_method(node)

    def generic_visit(self, node):
        raise Exception(f'Not Implemented Operand Type: {type(node).__name__}')

class NodeVisitor(Evaluater):
    def visit_Num(self, node):
        return Evaluater.take(node)

    def visit_BinOp(self, node):
        return Result.do(
            result
            for operand1 in self.visit(node.left)
            for operand2 in self.visit(node.right)
            for result   in Evaluater.binary_calc(node.op, operand1, operand2)
        )

    def visit_UnaryOp(self, node):
        return Result.do(
            result
            for operand in self.visit(node.expr)
            for result  in Evaluater.binary_calc(node.op, 0, operand)
        )

    def visit_Empty(self, node):
        return Success(str(node))

    def visit_Compound(self, node):
        return Success(str(node))

    def visit_Assign(self, node):
        return Success(str(node))

    def visit_Variable(self, node):
        return Success(str(node))





######### just for fun ############

class RPNVisitor(Evaluater):
    def visit_Num(self, node):
        return str(node)

    def visit_BinOp(self, node):
        return f'{self.visit(node.left)} {self.visit(node.right)} {node.op.string}'

    def visit_UnaryOp(self, node):
        return str(node)

class LispVisitor(Evaluater):
    def visit_Num(self, node):
        return str(node)

    def visit_BinOp(self, node):
        return f'({node.op.string} {self.visit(node.left)} {self.visit(node.right)})'

    def visit_UnaryOp(self, node):
        return f'({node.op.string} {self.visit(node.expr)})'

