#!/usr/bin/python3
"""
"""

from operator import add, sub, mul, truediv
from tokenize import NUMBER, OP, NEWLINE, ENDMARKER, PLUS, MINUS, STAR, SLASH, TokenInfo

from returns.result     import safe,   Success, Failure, Result
from returns.maybe      import Nothing, Some
from returns.converters import flatten
from returns.pipeline   import is_successful
from returns.iterables  import Fold

from .ast    import Num, BinOp, UnaryOp, Empty, Compound, Assign, Variable, PrintStat, Declaration, Type
from .symbol import SymbolTable, VarSymbol



class NodeVisitor:
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
        return NodeVisitor.BasicOperation[op.exact_type](operand1, operand2)

    def visit(self, node):
        """
        reload visit functions
        visit(node: AstNode) -> Result
        """
        name = type(node).__name__
        visit_method = getattr(self, 'visit_' + name, self.generic_visit)
        return visit_method(node)

    def generic_visit(self, node):
        raise Exception(f'Not Implemented Operand Type: {type(node).__name__}')

class Evaluater(NodeVisitor):
    def __init__(self):
        self.frame_stack = []
        self.GLOBAL_SCOPE = {}

    def visit_Num(self, node):
        return NodeVisitor.take(node)

    def visit_BinOp(self, node):
        return Result.do(
            result
            for operand1 in self.visit(node.left)
            for operand2 in self.visit(node.right)
            for result   in NodeVisitor.binary_calc(node.op, operand1, operand2)
        )

    def visit_UnaryOp(self, node):
        return Result.do(
            result
            for operand in self.visit(node.expr)
            for result  in NodeVisitor.binary_calc(node.op, 0, operand)
        )

    def visit_Empty(self, node):
        return Success(str(node))

    def visit_Compound(self, node):
        match Fold.collect(map(self.visit, node.children), Success(())):
            case Success(_):
                return Success(self.GLOBAL_SCOPE)
            case failure:
                return failure

    def visit_Assign(self, node):
        match self.visit(node.rvalue):
            case Success(x):
                self.GLOBAL_SCOPE[str(node.lvalue)] = x
                return Success(x)
            case failure:
                return failure

    def visit_Variable(self, node):
        if str(node) in self.GLOBAL_SCOPE:
            return Success(self.GLOBAL_SCOPE[str(node)])
        return Failure(f'no such variable {str(node)}')

    def visit_PrintStat(self, node):
        return self.visit(node.expr)\
            .map(print)

    def visit_Declaration(self, node):
        return Success(str(node))

    def visit_Type(self, node):
        return Success(str(node))


class Checker(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()

    def visit_Num(self, node):
        return Success(node)

    def visit_BinOp(self, node):
        return Result.do(
            BinOp(left, node.op, right)
            for left in self.visit(node.left)
            for right in self.visit(node.right)
        )

    def visit_UnaryOp(self, node):
        return self.visit(node.expr)

    def visit_Empty(self, node):
        return Success(())

    def visit_Compound(self, node):
        return Result.do(
            Compound(list(children))
            for children in Fold.collect(map(self.visit, node.children), Success(()))
        )

    def visit_Assign(self, node):
        return Result.do(
            Assign(node.lvalue, node.op, node.rvalue)
            for lvalue in self.visit(node.lvalue)
            for rvalue in self.visit(node.rvalue)
        )

    def visit_Variable(self, node):
        return self.symtab.lookup(node.name)\
            .map(lambda _ : node)

    def visit_PrintStat(self, node):
        return Result.do(
            PrintStat(expr)
            for expr in self.visit(node.expr)
        )

    def visit_Declaration(self, node):
        return self.symtab.lookup(node._type.name)\
            .bind(lambda x : self.symtab.define(VarSymbol(node.name, x)))\
            .map(lambda _ : node)

    def visit_Type(self, node):
        return Success(node)

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

