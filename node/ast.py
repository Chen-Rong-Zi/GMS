#!/usr/bin/python3
"""
this is a template file
"""
from returns.maybe import  Nothing
from node.symbol import GMSKeyword, BuiltinTypeSymbol

class AST:
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return f'{type(self).__name__}(token={self.token})'

class Num(AST):
    pass

class Str(AST):
    pass

class Bool(AST):
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left  = left
        self.op    = op
        self.right = right

    def __str__(self):
        return f'BinOp({self.left}, {self.op}, {self.right})'


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op   = op
        self.expr = expr

    def __str__(self):
        return f'UnaryOp({self.op}, {self.expr})'

class Variable(AST):
    def __init__(self, token):
        self.token  = token
        self.string = self.token.string
        self.name   = self.token.string

    def __str__(self):
        return f'Variable({self.token})'

class Empty(AST):
    def __init__(self):
        pass

    def __str__(self):
        return 'Empty'

class Compound(AST):
    def __init__(self, children):
        self.children = children

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return 'Compound({children})'.format(children='{' + '\n'.join(str(c) for c in self.children) + '}')

    def __iter__(self):
        return iter(self.children)

class Assign(AST):
    def __init__(self, lvalue, op, rvalue):
        self.lvalue = lvalue
        self.op     = op
        self.rvalue = rvalue

    def __str__(self):
        return f'Assign({self.lvalue}, {self.op}, {self.rvalue})'

class PrintStat(AST):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f'PrintStat({self.expr})'

class Ret(AST):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f'Ret(expr={self.expr})'

class VarDeclaration(AST):
    def __init__(self, _type, token):
        self._type = _type
        self.token = token
        self.name  = self.token.string

    def __str__(self):
        return f'VarDeclaration({self._type}, {self.token})'

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.name  = self.token.string

    def __str__(self):
        return f'Type(self._type)'

class FuncParam(AST):
    def __init__(self, _type, var):
        self._type = _type
        self.name  = var.name
        self.var = var

    def __str__(self):
        return f'FuncParam({self._type} {self.var})'

class FuncDeclaration(AST):
    def __init__(self, var, paramlist, compound):
        self.name = var.name
        self.func_name = var
        self.paramlist = paramlist
        self.compound = compound

    def __str__(self):
        return f'FuncDeclaration({self.func_name}, {self.paramlist}, {self.compound})'


class FuncCall(AST):
    def __init__(self, var_name, arguments, token, declaration=None):
        self.name = var_name.name
        self.var = var_name
        self.arguments = arguments  # a list of AST nodes
        self.token = token
        self.func_symbol = None # to be set after checker finish traversing this ast
        self.decalration = declaration

    def __str__(self):
        return 'FuncCall({name}({args}))'\
            .format(name=self.var, args=', '.join(map(str, self.arguments)))

class GlobalAst(AST):
    name = 'global'
    def __init__(self, compound):
        self.compound = compound

    def __str__(self):
        return f'GlobalAst(name={self.name}, compound={self.compound})'

class Conditional(AST):
    def __init__(self, cond_term, true_term, false_term):
        self.cond = cond_term
        self.true_term = true_term
        self.false_term = false_term

    def __str__(self):
        return f'Conditional({self.cond}, {self.true_term}, {self.false_term})'

class NewAlloc(AST):
    def __init__(self, ownptr):
        self.ownptr = ownptr

    def __str__(self):
        return f'NewAlloc({self.ownptr})'

class FullType(AST):
    def __init__(self, _type, base_type, level=0, kind=GMSKeyword.OWN):
        self.token = _type
        self.name  = _type.string
        self.level = level
        self.kind = kind
        self.base_type = base_type

    def __str__(self):
        return f'Type(self._type)'

class OwnPtrDecl:

    def __init__(self, full_type, name):
        self.token = name
        self.name = name.string
        self.full_type = full_type

    def __str__(self):
        return f'OwnPtrDecl({self.full_type}, {self.name}, {self.token})'

class Deref(AST):
    def __init__(self, token, level):
        self.name = token.string
        self.token = token
        self.level = level

    def __str__(self):
        return f'Deref({self.name}, {self.token}, {self.level})'

class Mutation(AST):
    def __init__(self, deref, expr):
        self.deref = deref
        self.expr  = expr

    def __str__(self):
        return f'Mutation({self.deref}, {self.expr})'

class Move(AST):
    def __init__(self, ownptr, ownvar):
        self.ownptr = ownptr
        self.token = ownvar
        self.ownvar = ownvar.string

    def __str__(self):
        return f'Move({self.ownptr}, {self.ownvar})'

class RefDecl(AST):
    def __init__(self, _type: BuiltinTypeSymbol, decl_deref, ref_type, deref):
        self._type  = _type
        self.ref_type         = ref_type
        self.decl_deref       = decl_deref
        self.deref            = deref

    def __str__(self):
        return f'RefDecl({self._type}, {self.decl_deref}, {self.ref_type.string}, {self.deref})'

class Free(AST):
    def __init__(self, token):
        self.name = token.string
        self.token = token

    def __str__(self):
        return f'Free({self.name})'
