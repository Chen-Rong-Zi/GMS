from .                 import Evaluater
from returns.result    import Success,  Result
from returns.iterables import Fold
# from objprint          import objprint  as     print
from util              import debugFunc
from .nodevisitor       import NodeVisitor

class GraphMaker(NodeVisitor):
    Indent = '    '
    def __init__(self):
        self.id = 0

    def get_id(self):
        self.id += 1
        return f'id{self.id}'

    def visit_Num(self, node):
        id = self.get_id()
        # return Success((id, f'{GraphMaker.Indent}{id}[{node.token.string}]\n'))
        return Success((id, f'{GraphMaker.Indent}{id}[Num]\n'))

    def visit_Str(self, node):
        id = self.get_id()
        # return Success((id, f'{GraphMaker.Indent}{id}[{node.token.string}]\n'))
        return Success((id, f'{GraphMaker.Indent}{id}[Str]\n'))

    def visit_BinOp(self, node):
        binop_id = self.get_id()
        return Result.do(
            (
                binop_id,
                GraphMaker.Indent + f'{binop_id}[{node.op.string}] --> {left_id}\n'
                + GraphMaker.Indent + f'{binop_id}[{node.op.string}] --> {right_id}\n'
                + left
                + right
            )
            for (left_id, left) in self.visit(node.left)
            for (right_id, right) in self.visit(node.right)
        )

    def visit_UnaryOp(self, node):
        op_id = self.get_id()
        return Result.do(
            (
                op_id,
                (
                    GraphMaker.Indent
                    + f'{op_id}[{node.op.string}] --> {id}\n'
                    + expr
                    + '\n'
                )
            )
            for (id, expr) in self.visit(node.expr)
        )

    def visit_Variable(self, node):
        id = self.get_id()
        return Success((id, f'{GraphMaker.Indent}{id}[{node.string}]\n'))

    def visit_Empty(self, _):
        id = self.get_id()
        return Success((id, f'{GraphMaker.Indent}{id}[empty]\n'))

    # @debugFunc
    def visit_Compound(self, node):
        compound_id = self.get_id()

        compound = Fold.collect(map(self.visit, node.children), Success(()))
        return compound.map(lambda children:
            (
                compound_id,
                ''.join(
                    map(lambda child :  f'{GraphMaker.Indent}{compound_id} --> {child[0]}\n' + child[1] + '\n', children)
                )
            )
        )

    def visit_Assign(self, node):
        assign_id = self.get_id()
        return Result.do(
            (
                assign_id,
                GraphMaker.Indent 
                + f'{assign_id}[assgin] --> {l_id}\n'
                + GraphMaker.Indent 
                + f'{assign_id}[assgin] --> {r_id}\n'
                + left
                + right
            )
            for (l_id, left)  in self.visit(node.lvalue)
            for (r_id, right) in self.visit(node.rvalue)
        )


    def visit_PrintStat(self, node):
        print_id = self.get_id()
        return Result.do(
            (
                print_id,
                GraphMaker.Indent
                + f'{print_id}[print] --> {id}\n'
                + expr
            )
            for (id, expr)  in self.visit(node.expr)
        )


    # @debugFunc
    def visit_Ret(self, node):
        ret_id = self.get_id()
        return Result.do(
            (
                ret_id,
                (
                    GraphMaker.Indent
                    + f'{ret_id}[Ret] --> {id}\n'
                    + expr
                )
            )
            for (id, expr)  in self.visit(node.expr)
        )


    def visit_VarDeclaration(self, node):
        vardecl_id = self.get_id()
        return Success(
            (
                vardecl_id,
                (
                    GraphMaker.Indent
                    + f'{vardecl_id}[VarDeclaration] --> {self.get_id()}[{node.name}]'
                )
            )
        )

    def visit_Type(self, node):
        id = self.get_id()
        return Success((id, f'{GraphMaker.Indent}{id}[{node.name}]\n'))

    def visit_FuncParam(self, node):
        id = self.get_id()
        return Success((id, f'{GraphMaker.Indent}{node._type.name} --> {node.name}\n'))

    def visit_FuncDeclaration(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id}[decl_{node.name}]\n'
                + self.Indent + f'{id} --> {name_id}[name-id]\n'
                + self.Indent + f'{id} --> {compound_id}[compound]\n'
                + ''.join(
                    map(lambda child :  f'{GraphMaker.Indent}{id} --> {child[0]}\n' + child[1] + '\n', params)
                )
                + name
                + compound
            )
            for name_id,     name     in self.visit(node.func_name)
            for params   in Fold.collect([print(self.visit(param)) or self.visit(param) for param in node.paramlist], Success(()))
            for compound_id, compound in self.visit(node.compound)
        )

    def visit_FuncCall(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id}[call_{node.name}]\n'
                + self.Indent + rf'{id}[call\ {node.name}]' + '\n' + ''.join (
                    map(lambda child :  f'{GraphMaker.Indent}{id} --> {child[0]}\n' + child[1] + '\n', children)
                )
            )
            for children in Fold.collect(map(self.visit, node.arguments), Success(()))
        )

    def visit_GlobalAst(self, node):
        return self.visit(node.compound).map(lambda x: 'graph TD\n    id1[program]\n' + x[1])

    def visit_Conditional(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id} --> {cond_id}\n'
                + self.Indent + f'{id} --> {true_id}\n'
                + self.Indent + f'{id} --> {false_id}\n'
                + cond + true_term + false_term
            )
            for cond_id, cond      in self.visit(node.cond)
            for true_id, true_term in self.visit(node.true_term)
            for false_id, false_term in self.visit(node.false_term)
        )

    def visit_NewAlloc(self, node):
        id = self.get_id()
        # print(f'newalloc  {id = }')
        return Result.do(
            (
                id,
                self.Indent + f'{id}[newalloc]\n'
                + self.Indent + f'{id} --> {decl_id}\n'
                + decl
            )
            for decl_id, decl in self.visit(node.ownptr)
        )

    def visit_FullType(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id} --> {t_id}\n'
                + t
            )
            for t_id, t in self.visit(node.base_type)
        )

    def visit_OwnPtrDecl(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id}[ownptr {node.name}]\n'
                + self.Indent + f'{id} --> {t_id}[{node.full_type.name} {node.name}]\n'
                + t
            )
            for t_id, t in self.visit(node.full_type)
        )

    def visit_Deref(self, node):
        id = self.get_id()
        return Success(
            (
                id,
                self.Indent + f'{id}[* {node.name}]\n'
            )
        )

    # @debugFunc
    def visit_Mutation(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id}[mutation] --> {l_id}\n'
                + self.Indent + f'{id}[mutation] --> {r_id}\n'
                + deref
                + expr
            )
            for (l_id, deref) in self.visit(node.deref)
            for (r_id, expr)  in self.visit(node.expr)
        )

    def visit_Move(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id} --> {p_id}[move]\n'
                + p
            )
            for p_id, p in self.visit(node.ownptr)
        )

    def visit_RefDecl(self, node):
        id = self.get_id()
        return Result.do(
            (
                id,
                self.Indent + f'{id}[RefDecl] --> {t_id}\n'
                + self.Indent + f'{id}[RefDecl] --> {d_id}\n'
                + self.Indent + f'{id}[RefDecl] --> {r_id}\n'
                + t + decl + rvalue
            )
            for (t_id, t)      in self.visit(node._type)
            for (d_id, decl)   in self.visit(node.decl_deref)
            for (r_id, rvalue) in self.visit(node.deref)
        )

    def visit_Free(self, node):
        id = self.get_id()
        string = GraphMaker.Indent
        return Success((id, string + f'{id}[free {node.name}]\n'))

    def visit_tuple(self, node):
        return super().visit_tuple(node)\
                .map(lambda x : ''.join(x))

    def visit_list(self, node):
        return super().visit_list(node)\
                .map(lambda x : ''.join(x))

