#!/usr/bin/python3

from functools   import reduce
from enum        import Enum
from collections import OrderedDict
from returns.result     import safe,   Success, Failure, Result
from util        import debugFunc
from error       import ErrorCode, SemanticError

class BuiltinType:
    NUM = 'Num'
    STR = 'Str'
    BOOL = 'Bool'

class GMSKeyword:
    TYPES = [BuiltinType.NUM, BuiltinType.STR, BuiltinType.BOOL]
    PRINT = 'print'
    FUNC  = 'func'
    IF  = 'if'
    ELSE  = 'else'
    RET  = 'return'

class Symbol:
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__

class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return f'<{self.name}:{self.type}>'

    __repr__ = __str__

class FuncSymbol(Symbol):
    def __init__(self, funcname, params=None, compound=None, astnode=None):
        super(FuncSymbol, self).__init__(funcname.name)
        self.params = params if params is not None else []
        self.compound = compound
        self.astnode = astnode

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params,
        )

    __repr__ = __str__

class ScopedSymbolTable:
    GLOBAL = None

    @staticmethod
    def get_global():
        if ScopedSymbolTable.GLOBAL is None:
            GLOBAL = ScopedSymbolTable('GLOBAL', 0, True)
            GLOBAL.enclosing_scope = None
            GLOBAL._init_builtins()
            ScopedSymbolTable.GLOBAL = GLOBAL
        return ScopedSymbolTable.GLOBAL

    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = OrderedDict()
        self.name = scope_name
        self.level = scope_level
        self.enclosing_scope = enclosing_scope if enclosing_scope else ScopedSymbolTable.get_global()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol('Num'))
        self.define(BuiltinTypeSymbol('Str'))
        self.define(BuiltinTypeSymbol('Bool'))

    def error(self, error_code, token):
        return Failure(SemanticError(error_code, token, message=f'{error_code.value} -> {token}'))

    # @debugFunc
    def define(self, symbol):
        if symbol.name in self._symbols:
            return self.error(ErrorCode.DUPLICATE_ID, symbol.name)
        self._symbols[symbol.name] = symbol
        return Success(self)

    def lookup(self, name):
        if name in self._symbols:
            return Success(self._symbols[name])
        if self.enclosing_scope is None:
            return self.error(ErrorCode.ID_NOT_FOUND, name)
        return self.enclosing_scope.lookup(name)

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        lines.extend('%-15s: %s' % (name, value)
                     for name, value in (('Scope name', self.name), ('Scope level', self.level),))

        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        return '\n'.join(lines)

    __repr__ = __str__
