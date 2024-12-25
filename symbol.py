#!/usr/bin/python3

from returns.result     import safe,   Success, Failure, Result

class Symbol:
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class BuiltinTypesSymbol(Symbol):
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


class SymbolTable:
    def __init__(self):
        self.dict = {}
        self.define(BuiltinTypesSymbol('Num'))
        self.define(BuiltinTypesSymbol('Str'))
        self.define(BuiltinTypesSymbol('Bool'))

    def __str__(self):
        string = 'symbols: '
        for key, value in self.dict.items():
            string += f'({key}:  {value})' + '\n'
        return string

    __repr__ = __str__

    def define(self, symbol):
        if symbol.name in self.dict:
            return Failure(f'{symbol.name} has already in SymbolTable')
        self.dict[symbol.name] = symbol
        return Success(self)

    def lookup(self, name):
        if name in self.dict:
            return Success(self.dict[name])
        return Failure(f'{name} not in SymbolTable')
