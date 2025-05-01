from dataclasses  import dataclass
from typing       import Any
from returns.trampolines import trampoline, Trampoline

from .nodevisitor import NodeVisitor
from .nodevisitor import *
from util         import log, debugFunc
from frame        import CallStack, ActivationRecord, ARType
from objprint     import objprint as print


@dataclass
class RetExpr:
    expr: Any

@dataclass
class OtherExpr:
    expr: Any

class Evaluater(NodeVisitor):
    def __init__(self):
        self.call_stack = CallStack()

        ar = ActivationRecord('global_frame', ARType.GLOBAL_FRAME, 1)
        self.call_stack.push(ar)

        log(str(self.call_stack))


    def visit_Num(self, node):
        return NodeVisitor.take(node.token)

    def visit_Bool(self, node):
        return NodeVisitor.take(node.token)

    def visit_Str(self, node):
        return NodeVisitor.take(node.token)

    # @debugFunc
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

    # @debugFunc
    def visit_Variable(self, node):
        return self.call_stack.peek().map(lambda f : f.get(node.name))

    def visit_Empty(self, node):
        return Success(None)

    def visit_Compound(self, node):
        last_expr = None
        for n in map(self.visit, node.children):
            match n:
                case Success(RetExpr(expr)) as ret:
                    return ret
                case Success(OtherExpr(expr)):
                    last_expr = expr
                case Success(_):
                    continue
                case Failure(_) as failure:
                    return failure
        return Success(OtherExpr(last_expr))

    def visit_Assign(self, node):
        match self.visit(node.rvalue):
            case Success(x):
                return self.call_stack.peek()\
                    .map(lambda f : f.set(node.lvalue.name, x))\
                    .map(lambda _: None)
            case failure:
                return failure

    def visit_PrintStat(self, node):
        return self.visit(node.expr)\
            .map(print)

    def visit_Ret(self, node):
        return self.visit(node.expr).map(RetExpr)

    def visit_VarDeclaration(self, _):
        return Success(None)

    def visit_Type(self, _):
        return Success(None)

    # @debugFunc
    def visit_FuncParam(self, _):
        return Success(None)

    # @debugFunc
    def visit_FuncDeclaration(self, _):
        return Success(None)

    # @debugFunc
    # @trampoline
    def visit_FuncCall(self, node, parent_frame=None):
        if parent_frame is None:
            parent_frame = self.call_stack.peek().unwrap()

        ar = ActivationRecord(node.name, ARType.LOCAL_FRAME, parent_frame)
        func_sym = node.func_symbol
        if len(node.arguments) != len(func_sym.params):
            return Failure(f"{func_sym.name} need {len(func_sym.params)} but got {len(node.arguments)}")

        for param, arg in zip(map(lambda v : v.name, func_sym.params), node.arguments):
            self.visit(arg).map(lambda value : ar.set(param, value))

        self.call_stack.push(ar)
        ret = self.visit(func_sym.compound)
        self.call_stack.pop()

        match ret:
            case Success(RetExpr(expr)):
                return Success(expr)
            case Success(OtherExpr(expr)):
                return Success(expr)
            case other:
                return other

    def visit_GlobalAst(self, node):
        match self.visit(node.compound):
            case Success(RetExpr(expr)):
                return Success(expr)
            case Success(OtherExpr(expr)):
                return Success(expr)
            case Success(expr) as ret:
                return ret
            case other:
                return other

    def visit_Conditional(self, node):
        # cond = self.visit(node.cond).unwrap()
        # if cond:
            # return self.visit(node.true_term)
        # else:
            # return self.visit(node.false_term)
        return Result.do(
            expr
            for cond in self.visit(node.cond)
            for expr in (self.visit(node.true_term) if cond else self.visit(node.false_term))
        )
