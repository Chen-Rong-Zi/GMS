from .                 import Evaluater
from returns.result    import Success,  Result
from returns.iterables import Fold
# from objprint          import objprint  as     print
from util              import debugFunc

class PrettyPrinter(Evaluater):
    Indent = '    '
    def __init__(self):
        self.level = 0

    def visit_Num(self, node):
        return Success(node.token.string)

    def visit_Str(self, node):
        return Success(node.token.string)

    def visit_BinOp(self, node):
        return Result.do(
            '(' + left + node.op.string + right + ')'
            for left in self.visit(node.left)
            for right in self.visit(node.right)
        )

    def visit_UnaryOp(self, node):
        return Result.do(
            node.op.string + expr
            for expr in self.visit(node.expr)
        )

    def visit_Variable(self, node):
        return Success(node.string)

    def visit_Empty(self, _):
        return Success('')

    def visit_Compound(self, node):
        indent = PrettyPrinter.Indent * self.level
        string = indent + '{\n'

        self.level += 1
        compound = Fold.collect(map(self.visit, node.children), Success(())).map(lambda s : ''.join(s))
        self.level -= 1

        return compound.map(lambda com : string + com + indent + '}\n')

    def visit_Assign(self, node):
        indent = PrettyPrinter.Indent * self.level
        return Result.do(
            indent + left + ' ' + node.op.string + ' ' + right + ';\n'
            for left  in self.visit(node.lvalue)
            for right in self.visit(node.rvalue)
        )


    def visit_PrintStat(self, node):
        indent = PrettyPrinter.Indent * self.level
        return self.visit(node.expr)\
            .map(lambda n : indent + f'print {n};\n')

        # return Success(indent + f'print {self.visit(node.expr)}' + ';\n')

    # @debugFunc
    def visit_Ret(self, node):
        indent = PrettyPrinter.Indent * self.level
        return Result.do(
            indent + f'return {expr}'
            for expr in self.visit(node.expr)
        )

    def visit_VarDeclaration(self, node):
        indent = PrettyPrinter.Indent * self.level
        return Result.do(
            indent + t + ' ' + node.name + ';\n'
            for t in self.visit(node._type)
        )
        # return Success(indent + f'{str(node._type)} {node.name};\n')

    def visit_Type(self, node):
        return Success(node.name)

    def visit_FuncParam(self, node):
        return Success(f'{node._type.name} {node.name}')

    def visit_FuncDeclaration(self, node):
        string = PrettyPrinter.Indent * self.level
        return Result.do(
            string + 'func '  + name + f'({", ".join(params)})' + compound
            for name   in self.visit(node.func_name)
            for params in Fold.collect([self.visit(param) for param in node.paramlist], Success(()))
            for compound in self.visit(node.compound)
        )

    def visit_FuncCall(self, node):
        return Result.do(
            f'{node.name}({",".join(args)})'
            for args in Fold.collect(map(self.visit, node.arguments), Success(()))
        )
        # return Success(string + '{name}({args})'.format(name=node.name, args=', '.join(map(str, node.arguments))))

    def visit_GlobalAst(self, node):
        return Fold.collect(map(self.visit, node.compound), Success(()))\
            .map(lambda x : ''.join(x))

    def visit_Conditional(self, node):
        return Result.do(
            f'{true_term} if {cond} else {false_term}'
            for cond      in self.visit(node.cond)
            for true_term in self.visit(node.true_term)
            for false_term in self.visit(node.false_term)
        )

    def visit_NewAlloc(self, node):
        return Result.do(
            decl + f' = new {node.ownptr.full_type.name}'
            for decl in self.visit(node.ownptr)
        )

    def visit_FullType(self, node):
        return Result.do(
            f'{t} {node.kind} {node.level * '*'}'
            for t in self.visit(node.base_type)
        )

    def visit_OwnPtrDecl(self, node):
        return Result.do(
            t  + node.name + ';'
            for t in self.visit(node.full_type)
        )

    def visit_Deref(self, node):
        return Success(node.level * '*' + node.name)

    def visit_Mutation(self, node):
        string = PrettyPrinter.Indent * self.level
        return Result.do(
            string + deref + ' = ' + expr
            for deref in self.visit(node.deref)
            for expr  in self.visit(node.expr)
        )

    def visit_Move(self, node):
        return Result.do(
            p + ' = ' + node.ownvar + ';'
            for p in self.visit(node.ownptr)
        )

    def visit_RefDecl(self, node):
        string = PrettyPrinter.Indent * self.level
        return Result.do(
            string + t + ' ' + node.ref_type.string + ' ' + decl + ' = &' + rvalue + ';'
            for t      in self.visit(node._type)
            for decl   in self.visit(node.decl_deref)
            for rvalue in self.visit(node.deref)
        )

    def visit_Free(self, node):
        string = PrettyPrinter.Indent * self.level
        return Result.do(
            string + f'free({name})'
            for name in self.visit(node.variable)
        )

    def visit_tuple(self, node):
        return super().visit_tuple(node)\
                .map(lambda x : ''.join(x))

    def visit_list(self, node):
        return super().visit_list(node)\
                .map(lambda x : ''.join(x))
