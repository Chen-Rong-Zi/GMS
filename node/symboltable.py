#!/usr/bin/python3
from .symbol import *
from tokenize import TokenInfo

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
        def print_symbol(scope):
            if scope is None:
                return
            print_symbol(scope.enclosing_scope)
            error(f"{scope}")
        error(f'Traceback (most recent call last)\n')
        print_symbol(self)
        return Failure(SemanticError(error_code, token, message=f'{error_code} -> {token.string}'))

    # @debugFunc
    def define(self, symbol):
        if symbol.name in self._symbols:
            return self.error(ErrorCode.DUPLICATE_ID, TokenInfo(19, symbol.name, (0, 0), (0, 0), ''))
        self._symbols[symbol.name] = symbol
        return Success(self)

    def get_all_owner(self):
        return filter(lambda s : type(s) == OwnPtrSymbol, self._symbols.values())

    def get_all_ref(self):
        return filter(lambda s : type(s) == Reference, self._symbols.values())


    def lookup(self, name):
        if name in self._symbols:
            return Success(self._symbols[name])
        if self.enclosing_scope is None:
            return self.error(ErrorCode.ID_NOT_FOUND, TokenInfo(0, name, (0, 0), (0, 0), ''))
        return self.enclosing_scope.lookup(name)

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        lines.extend('%-15s: %s' % (name, value)
                     for name, value in (('Scope name', self.name), ('Scope level', self.level),))

        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %s' % (key, str(value)))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        return '\n'.join(lines)

