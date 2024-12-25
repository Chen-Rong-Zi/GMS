from ..nodevisitor  import Evaluater
from returns.result import Success, Result
from returns.iterables  import Fold

class PrettyPrinter(Evaluater):
    Indent = '    '
    def __init__(self):
        self.level = 0

    def visit_Num(self, node):
        return Success(str(node))

    def visit_BinOp(self, node):
        return Success(str(node))

    def visit_UnaryOp(self, node):
        return Success(str(node))

    def visit_Variable(self, node):
        return Success(str(node))

    def visit_Empty(self, node):
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

        return Success(indent + f'print {self.visit(node.expr)}' + ';\n')

    def visit_Declaration(self, node):
        string = PrettyPrinter.Indent * self.level
        return Success(string + str(node))

    def visit_Type(self, node):
        string = PrettyPrinter.Indent * self.level
        return Success(string + str(node))
