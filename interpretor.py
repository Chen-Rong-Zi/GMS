#!/usr/bin/python3
"""
this is a template file
"""

import readline

from typing   import Iterable
from tokenize import TokenInfo
from tokenize import NUMBER, OP, NEWLINE, ENDMARKER, PLUS, MINUS, STAR, SLASH, TokenInfo
from tokenize import LBRACE, RBRACE, LPAR, RPAR
from operator import add, sub, mul, truediv

from returns.result     import safe,   Success, Failure, Result
from returns.maybe      import Nothing, Some
from returns.converters import flatten
from returns.pipeline   import is_successful

from .scanner import Scanner


class Evaluater:
    Literal  = [NUMBER]
    Operator = [OP, PLUS, MINUS, STAR, SLASH]
    EOF      = [NEWLINE, ENDMARKER]
    ExtentedOP = [LPAR, RPAR, OP, PLUS, MINUS, STAR, SLASH]
    BasicOperation = {
        PLUS  : add,
        MINUS : sub,
        STAR  : mul,
        SLASH : truediv
    }
    OPPriority = {
        PLUS: 0,
        MINUS: 0,
        STAR: 1,
        SLASH: 1,
    }

    def __init__(self, expr_str):
        self.tokens = Scanner.scan_from_str(expr_str)
        self.operator_stack = []
        self.operand_stack = []
        self.rpn = []
        self.encoding = next(self.tokens)
        self.curr_token = next(self.tokens)

    def _priority(self, op, instack):
        match op:
            case lbrace if op.exact_type == LPAR:
                if instack:
                    return -1
                else:
                    return 4
            case op if op.exact_type in Evaluater.OPPriority:
                return Evaluater.OPPriority[op.exact_type]

    def _push_op(self, op):
        match op:
            case rbrace if rbrace.string == ')':
                while self.operator_stack and self.operator_stack[-1].exact_type != LPAR:
                    self.rpn.append(self.operator_stack.pop())
                match self.operator_stack:
                    case [*_, lbrace] if lbrace.exact_type == LPAR:
                        self.operator_stack.pop()
                        return Success(())
                    case _:
                        return Failure(f'invalid bracket at line: {op.start[0]} col: ({op.start[0]}, {op.end[1]})')
            case op:
                # breakpoint()
                # if op.exact_type == LPAR:
                    # breakpoint()
                while self.operator_stack and self._priority(self.operator_stack[-1], True) >= self._priority(op, False):
                    higer_op = self.operator_stack.pop()
                    if higer_op.exact_type != LPAR:
                        self.rpn.append(higer_op)
                self.operator_stack.append(op)
                return Success(())

    @safe
    def binary_calc(op, operand1, operand2):
        return Evaluater.BasicOperation[op.exact_type](operand1, operand2)

    @safe
    def take(token):
        return eval(token.string)

    def read_operator(self):
        if self.rpn == []:
            return Failure('invalid expression expect an operator')
        match self.rpn[-1]:
            case op if op.exact_type in Evaluater.Operator:
                return Success(self.rpn.pop())
            case op if op.exact_type in Evaluater.Literal:
                return Evaluater.take(self.rpn.pop())

    def read_operand(self):
        if self.rpn == []:
            return Failure('invalid expression expect an operand')
        first = self.rpn[-1]
        match first.exact_type:
            case y if y in Evaluater.Operator:
                return self.eval_rpn()
            case x if x in Evaluater.Literal:
                return Evaluater.take(self.rpn.pop())
            case operand:
                return Failure(f'unimplemented operand type {first}')

    def eval_rpn(self):
        match self.read_operator():
            case Success(x) if type(x) in [int]:
                return Success(x)
            case Success(op):
                return flatten(Result.do(
                    self.binary_calc(op, rand1, rand2)
                    for rand1 in self.read_operand()
                    for rand2 in self.read_operand()
                ))
            case failure:
                return failure

    def evaluate(self):
        for token in self.tokens:
            match token:
                case num if num.type in Evaluater.Literal:
                    self.rpn.append(num)
                case op if op.type in Evaluater.ExtentedOP:
                    result = self._push_op(op)
                    if not is_successful(result):
                        return result
                case eof if eof.type in Evaluater.EOF:
                    break
                case unimplemented:
                    return Failure(f'unimplemented token {unimplemented}')

        while self.operator_stack:
            self.rpn.append(self.operator_stack.pop())

        return self.eval_rpn()\
            .bind(lambda x : Success(x) if len(self.rpn) == 0 else Failure(f'invalid expression {self.rpn[-1].string} at line: {self.rpn[-1].start[0]} col: {self.rpn[-1].start[1], self.rpn[-1].end[1]}'))

    def advance(self):
        self.curr_token = next(self.tokens)
        return self.curr_token

    def read_factor(self):
        match self.curr_token:
            case tk if tk.type in Evaluater.Literal:
                self.advance()
                return Success(int(tk.string))
            case error_token:
                return Failure(f'invalid expression {error_token.string} at line: {error_token.start[0]} col: {error_token.start[1], error_token.start[1]}')

    def rule(self, read_next, op_type):
        def defination():
            factor = read_next()
            while True:
                match self.curr_token:
                    case op if op.exact_type in op_type:
                        self.advance()
                        factor = flatten(Result.do(
                            self.binary_calc(op, x, y)
                            for x in factor
                            for y in read_next()
                        ))
                    case end:
                        return factor
        return defination

    def read_term(self):
        return self.rule(lambda : self.read_factor(), [STAR, SLASH])()


    def expr(self):
        return self.rule(lambda : self.read_term(), [PLUS, MINUS])()

class Interpretor:
    def interact():
        while True:
            try:
                input_expr = input('GMS> ')
                # breakpoint()
                print(Evaluater(input_expr).expr()._inner_value)
                # print(Evaluater('1 + 1 - 201 * 10').evaluate().__inner_value)
            except ZeroDivisionError as e:
                print(e)
            # except:
                # print('exit')
                # return

if __name__ == '__main__':
    Interpretor.interact()
