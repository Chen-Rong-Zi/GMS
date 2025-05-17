from dataclasses  import dataclass
from typing       import Any
from returns.trampolines import trampoline, Trampoline
from tokenize     import TokenInfo

from .nodevisitor import NodeVisitor
from .nodevisitor import *
from util         import log, debugFunc, validate
from frame        import CallStack, ActivationRecord, ARType
from error        import *
from heap         import *
from node.ast     import *
from node.symbol  import *


@dataclass
class RetExpr:
    expr: Any

@dataclass
class OtherExpr:
    expr: Any

class Evaluater(NodeVisitor):
    def __init__(self):
        self.call_stack = CallStack()

        ar = ActivationRecord('global_frame', ARType.GLOBAL_FRAME, None)
        self.call_stack.push(ar)

        log(str(self.call_stack))

    def error(self, error_code, token, msg):
        return Failure(RuntimeError(error_code=error_code, token=token, message=msg))

    def visit_Num(self, node):
        return NodeVisitor.take(node.token)

    def visit_Bool(self, node):
        return NodeVisitor.take(node.token)

    # @debugFunc
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
        ret = self.call_stack.peek().bind(lambda f : f.getrval(node.name))
        if not is_successful(ret):
            return ret
        value = ret.unwrap()
        if value is None:
            return self.error(ErrorCode.UNINITIALZIED_ID, node.token, f'{node.name} is uninitialzied')
        match value:
            case HeapUnit(value=value):
                return Success(value)
            case other:
                return Success(other)

    def visit_VariableFrame(self, node):
        return self.call_stack.peek().bind(lambda f : f.getlval(node.name))

    def visit_Empty(self, node):
        return Success(None)

    # @debugFunc
    def visit_Compound(self, node):
        last_expr = None
        ar = ActivationRecord(
                'Coumpound',
                ARType.BLOKL_FRAME,
                self.call_stack.peek().unwrap())
        self.call_stack.push(ar)
        for n in map(self.visit, node.children):
            match n:
                case Success(RetExpr(expr)) as ret:
                    self.call_stack.pop()
                    return ret
                case Success(OtherExpr(expr)):
                    last_expr = expr
                case Success(_):
                    continue
                case Failure(_) as failure:
                    return failure
        self.call_stack.pop()
        return Success(OtherExpr(last_expr))

    def visit_Assign(self, node):
        return Result.do(
            frame.set(node.lvalue.name, value)
            for frame in self.visit_VariableFrame(node.lvalue)
            for value in self.visit(node.rvalue)
        )

        # match self.visit(node.rvalue):
            # case Success([frame, x]):
                # return self.visit(node.rvale)\
                    # .map(lambda val : frame.set())
                # frame.set(node.rvalue.name, x)
                # return Success(())
            # case failure:
                # return failure

    # @debugFunc
    def visit_PrintStat(self, node):
        return self.visit(node.expr)\
            .map(print)

    def visit_Ret(self, node):
        return self.visit(node.expr).map(RetExpr)
        # match debugFunc(self.visit)(node.expr):
            # case Success(RetExpr(expr)) as ret:
                # return ret
            # case Success(OtherExpr(expr)) as ret:
                # return ret
            # case Success(expr) as ret:
                # return Success(RetExpr(expr))
            # case Failure(_) as failure:
                # return failure
        # return expr.map(RetExpr)

    def visit_VarDeclaration(self, node):
        return Result.do(
            node
            for _ in self.call_stack.peek().map(lambda f : f.set(node.name, None))
        )

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
        cond = self.visit(node.cond).unwrap()
        if cond:
            return self.visit(node.true_term)
        else:
            return self.visit(node.false_term)

    # @debugFunc
    def visit_Deref(self, node):
        return self.visit_DerefMem(node)\
                .map(lambda x : x.get_value())

    def visit_DerefMem(self, node):
        return self.call_stack.peek().bind(lambda f : f.getlval(node.name)).map(lambda x : x[node.name])

    def visit_NewAlloc(self, node):
        return Result.do(
            frame.set(node.ownptr.name, HeapUnit(node.ownptr))
            for frame in self.call_stack.peek()
        )

    def visit_FullType(self, node):
        return Success(None)

    def visit_OwnPtrDecl(self, node):
        return Success(None)

    # @debugFunc
    def visit_Mutation(self, node):
        return Result.do(
            deref.mutate(expr)
            for deref in self.visit_DerefMem(node.deref)
            for expr  in self.visit(node.expr)
        )

    def visit_Move(self, node):
        return Result.do(
            None
            for _ in self.visit_NewAlloc(NewAlloc(node.ownptr))
            for frame in self.call_stack.peek()
            for expr  in frame.getrval(node.ownvar).map(lambda x : x.get_value())
            for _ in frame.set(node.ownptr.name, HeapUnit(node.ownptr, expr))\
                        .getlval(node.ownvar)\
                        .map(lambda f : f[node.ownvar].release())
        )

    def visit_RefDecl(self, node):
        return Result.do(
            this_frame.set(node.decl_deref.name, heapunit)
            for this_frame in self.call_stack.peek()
            for heapunit   in this_frame.getrval(node.deref.name)
        )

    def visit_Free(self, node):
        return Success(None)
