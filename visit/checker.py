from .nodevisitor import NodeVisitor
from .nodevisitor import *
from error        import ErrorCode, SemanticError

from node.symbol import *
from util        import log

class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.curr_scope = ScopedSymbolTable.get_global()

    def error(self, error_code, token):
        return Failure(SemanticError(error_code=error_code, token=token, message=f'{error_code}: {token}'))

    def visit_Num(self, node):
        return Success(node)

    def visit_Str(self, node):
        return Success(node)

    def visit_Bool(self, node):
        return Success(node)

    def visit_BinOp(self, node):
        return Result.do(
            BinOp(left, node.op, right)
            for left in self.visit(node.left)
            for right in self.visit(node.right)
        )

    def visit_UnaryOp(self, node):
        return self.visit(node.expr)

    def visit_Variable(self, node):
        return self.curr_scope.lookup(node.name)\
            .map(lambda _ : node)

    def visit_Empty(self, empty):
        return Success(empty)

    # @debugFunc
    def visit_Compound(self, node):
        # return Fold.collect(map(self.visit, node.children), Success(()))
        # log(self.curr_scope)
        new_scope = ScopedSymbolTable('Compound', self.curr_scope.level + 1, self.curr_scope)
        self.curr_scope = new_scope
        ret = Result.do(
            Compound(list(children))
            for children in Fold.collect(map(self.visit, node.children), Success(()))
        )
        self.curr_scope = self.curr_scope.enclosing_scope
        return ret

    def visit_Assign(self, node):
        return Result.do(
            node
            for _ in self.visit(node.lvalue)
            for _ in self.visit(node.rvalue)
        )

    # @debugFunc
    def visit_PrintStat(self, node):
        return Result.do(
            node
            for _ in self.visit(node.expr)
        )

    def visit_Ret(self, node):
        return self.visit(node.expr)

    # @debugFunc
    def visit_VarDeclaration(self, node):
        return Result.do(
            node
            for t in self.curr_scope.lookup(node._type.name)
            for _ in self.curr_scope.define(VarSymbol(node.name, t))
        )

    def visit_Type(self, node):
        return self.curr_scope.lookup(node.name).map(lambda _ : node)

    def visit_FuncParam(self, node):
        return Result.do(
            node
            for _ in self.curr_scope.define(VarSymbol(node.name, node._type))
        )

    def visit_FuncDeclaration(self, node):
        defination = self.curr_scope.define(FuncSymbol(node.func_name, node.paramlist, node.compound))
        new_scope = ScopedSymbolTable(node.name, self.curr_scope.level + 1, self.curr_scope)
        self.curr_scope = new_scope
        ret = Result.do(
            node
            # for _ in self.visit(node.name)
            for _ in defination
            for _ in Fold.collect(map(self.visit, node.paramlist), Success(()))
            for _ in self.visit(node.compound)
        )
        # log(self.curr_scope)
        self.curr_scope = self.curr_scope.enclosing_scope
        return ret

    # @debugFunc
    def visit_FuncCall(self, node):
        symbol = self.curr_scope.lookup(node.name)
        if not is_successful(symbol):
            return symbol

        node.func_symbol = symbol.unwrap()
        return Result.do(
            node
            for _ in self.curr_scope.lookup(node.name)
            for _ in Fold.collect(map(self.visit, node.arguments), Success(()))
        )

    def visit_GlobalAst(self, node):
        return Result.do(
            node
            for _ in self.visit(node.compound)
        )

    def visit_Conditional(self, node):
        return Result.do(
            node
            for cond       in self.visit(node.cond)
            for true_term  in self.visit(node.true_term)
            for false_term in self.visit(node.false_term)
        )

    def visit_NewAlloc(self, node):
        return Success(node)

    def visit_FullType(self, node):
        return Success(node)

    def visit_OwnPtrDecl(self, node):
        return Success(node)

    def visit_Deref(self, node):
        return Success(node)

    def visit_Mutation(self, node):
        return Success(node)

    def visit_Move(self, node):
        return Success(node)

    def visit_RefDecl(self, node):
        return Success(node)

    def visit_Free(self, node):
        return Success(node)
