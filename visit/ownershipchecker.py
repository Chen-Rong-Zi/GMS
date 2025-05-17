from .checker import *
from node.symbol import *
import node.symbol as node_symbol

class OwnerShipChecker(SemanticAnalyzer):

    def __init__(self):
        super().__init__()

    def error(self, error_code, token, message=''):
        return self.curr_scope.error(error_code, token)\
                .alt(lambda _ : SemanticError(error_code=error_code,
                                              token=token,
                                              message=f'{error_code}: {token.string} {message}'))

    def ownership_check(self, symbol, state):
        if symbol.state == state:
            return Success(symbol)
        else:
            return self.error(ErrorCode.MemLeak, symbol.token)

    @staticmethod
    def symbol_check(symbol, _type):
        if type(symbol) == _type:
            return Success(symbol)
        else:
            return Failure(None)

    def deref_check(self, symbol):
        match type(symbol):
            case node_symbol.OwnPtrSymbol:
                return self.ownership_check(symbol, OwnerState.Owned)
            case _:
                return self.error(ErrorCode.CanNotDerefence, symbol.token)

    # @debugFunc
    def visit_Compound(self, node):
        new_scope = ScopedSymbolTable('Compound', self.curr_scope.level + 1, self.curr_scope)
        self.curr_scope = new_scope
        ret = Result.do(
            Compound(list(children))
            for children in Fold.collect(map(self.visit, node.children), Success(()))
            for _ in Success(list(map(lambda x : x.return_ownership(), self.curr_scope.get_all_ref())))
            for _ in Fold.collect(
                map(lambda x : self.ownership_check(x, OwnerState.Freed),
                    self.curr_scope.get_all_owner()), Success(()))
        )
        self.curr_scope = self.curr_scope.enclosing_scope
        return ret


    # @debugFunc
    def visit_NewAlloc(self, node):
        return Result.do(
            node
            for _ in self.visit(node.ownptr)
            for _ in self.curr_scope.define(OwnPtrSymbol(node.ownptr.name, OwnerState.Owned, node.ownptr.token))
        )

    def visit_FullType(self, node):
        return self.visit(node.base_type).map(lambda _ : node)

    def visit_OwnPtrDecl(self, node):
        return self.visit(node.full_type).map(lambda _ : node)

    # @debugFunc
    def visit_Deref(self, node):
        return Result.do(
            node
            for s in self.curr_scope.lookup(node.name)
            for _ in s.move().lash(lambda _ : self.error(ErrorCode.NotMoveable, node.token))
        )

    # @debugFunc
    def visit_Mutation(self, node):
        return Result.do(
            node
            for _ in self.visit_Deref_Left(node.deref)
            for _ in self.visit(node.expr)
        )

    # @debugFunc
    def visit_Deref_Left(self, node):
        return Result.do(
            node
            for s in self.curr_scope.lookup(node.name).map(lambda x : x if isinstance(x, OwnPtrSymbol) else x.owner)
            for _ in s.mutate().lash(lambda msg : self.error(ErrorCode.CanNotDerefence, node.token, msg))
        )

    # @debugFunc
    def visit_Move(self, node):
        return Result.do(
            node
            for ownptr in self.visit(node.ownptr)
            for _      in self.curr_scope.define(OwnPtrSymbol(ownptr.name, OwnerState.Owned, node.token))
            for symbol in self.curr_scope.lookup(node.ownvar)
            for _ in symbol.move().lash(lambda msg : self.error(ErrorCode.NotMoveable, node.token, msg))
        )

    def visit_RefDecl(self, node):
        return Result.do(
            node
            for _ in self.visit(node._type)
            for owner in self.curr_scope.lookup(node.deref.name)
            for _ in (owner if isinstance(owner, OwnPtrSymbol) else owner.owner)\
                        .borrow(node.ref_type.string)\
                        .lash(lambda msg : self.error(ErrorCode.CanNotBorror, node.decl_deref.token, msg))
            for _ in self.curr_scope.define(Reference(node.decl_deref.name, node.ref_type, owner if isinstance(owner, OwnPtrSymbol) else owner.owner))
        )

    # @debugFunc
    def visit_Free(self, node):
        return Result.do(
            node
            for owner in self.curr_scope.lookup(node.name)\
                            .bind(lambda s : Success(s) if isinstance(s, OwnPtrSymbol) else self.error(ErrorCode.CanNotFree, s.token, 'not a own pointer'))
            for _ in owner.free()
        )
