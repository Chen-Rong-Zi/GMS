from ..nodevisitor import Evaluater

class PrettyPrinter(Evaluater):
    Indent = '    '
    def __init__(self):
        self.level = 0

    def visit_Num(self, node):
        return str(node)

    def visit_BinOp(self, node):
        return str(node)

    def visit_UnaryOp(self, node):
        return str(node)

    def visit_Variable(self, node):
        return str(node)

    def visit_Empty(self, node):
        return ''

    def visit_Compound(self, node):
        indent = PrettyPrinter.Indent * self.level
        string = indent + '{\n'

        self.level += 1
        string += ''.join(self.visit(child) for child in node.children)
        self.level -= 1

        string += indent + '}\n'
        return string

    def visit_Assign(self, node):
        string = PrettyPrinter.Indent * self.level
        string += self.visit(node.lvalue)
        string += ' '
        string += str(node.op.string)
        string += ' '
        string += self.visit(node.rvalue)
        string += ';\n'
        return string

    def visit_PrintStat(self, node):
        indent = PrettyPrinter.Indent * self.level
        return indent + f'print {self.visit(node.expr)}' + ';\n'

    def visit_Declaration(self, node):
        string = PrettyPrinter.Indent * self.level
        return string + str(node)

    def visit_Type(self, node):
        string = PrettyPrinter.Indent * self.level
        return string + str(node)
