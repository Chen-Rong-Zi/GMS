from dataclasses  import dataclass
from typing       import Any
from returns.trampolines import trampoline, Trampoline

from .nodevisitor import NodeVisitor
from .nodevisitor import *
from util         import log, debugFunc
from frame        import CallStack, ActivationRecord, ARType
from objprint     import objprint as print
from .evaluater   import *


class ClosureFlow(Evaluater):
    def __init__(self, checker):
        super().__init__()
        self.checker = checker

    def visit_FuncDeclaration(self, node):
        self.checker.visit(node)
        funcsym = self.checker.curr_scope.lookup(node.name).unwrap()
        funcsym.astnode = node
        node.parent_frame = self.call_stack.peek().unwrap()
        return Success(None)

    def visit_FuncCall(self, node):
        funcsym = self.checker.curr_scope.lookup(node.name).unwrap()
        astnode = funcsym.astnode
        return super().visit_FuncCall(node, astnode.parent_frame)
