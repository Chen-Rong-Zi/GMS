#!/usr/bin/python3

from functools   import reduce
from enum        import Enum
from collections import OrderedDict
from dataclasses import dataclass

from returns.result     import safe,   Success, Failure, Result
from util        import debugFunc, error
from error       import ErrorCode, SemanticError

class BuiltinType:
    NUM = 'Num'
    STR = 'Str'
    BOOL = 'Bool'

class GMSKeyword:
    TYPES = [BuiltinType.NUM, BuiltinType.STR, BuiltinType.BOOL]
    PRINT = 'print'
    FUNC  = 'func'
    FREE  = 'free'
    OWN   = 'own'
    NEW   = 'new'
    UNIQ  = 'uniq'
    SHARE = 'shr'
    IF    = 'if'
    ELSE  = 'else'
    RET   = 'return'

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

class RustEnum(type):
    def __getattr__(cls, name):
        match name:
            case 'ShrBrowered':
                return OwnerState._ShrBrowered(1)
            case other:
                error(f'{other} not in OwnerState')
                assert False

class OwnerState(metaclass=RustEnum):
    Owned    = 'Owned'
    UniqBrowered = 'UniqBrowered'
    Moved    = 'Moved'
    Freed    = 'Freed'

    class _ShrBrowered:
        def __init__(self, refcnt):
            self.refcnt = refcnt

        def getcnt(self):
            return self.refcnt

        def incr(self):
            self.refcnt += 1

        def decr(self):
            self.refcnt -= 1
            assert self.refcnt >= 0



class OwnPtrSymbol(Symbol):

    def __init__(self, name, state, token):
        self.name = name
        self.state = state
        self.token = token

    def set_state(self, state):
        self.state = state

    def move(self):
        if self.state != OwnerState.Owned:
            return Failure(f'{self.name} is {self.state} imposible to move')
        self.set_state(OwnerState.Freed)
        return Success(None)

    def mutate(self):
        if self.state == OwnerState.Moved:
            return Failure(None)
        return Success(None)

    def borrow(self, borrow_type):
        if self.state != OwnerState.Owned and not isinstance(self.state, OwnerState._ShrBrowered):
            return Failure(f'{self.name} is in {self.state} imposible to borrow')

        if borrow_type == 'uniq':
            if self.state == OwnerState.UniqBrowered:
                return Failure(f'{self.name} already have a uniq borrow')
            else:
                self.set_state(OwnerState.UniqBrowered)
        elif borrow_type == 'shr':
            if self.state == OwnerState.Owned:
                self.set_state(OwnerState.ShrBrowered)
            elif isinstance(self.state, OwnerState._ShrBrowered):
                self.state.incr()
        else:
            print(borrow_type)
            assert False
        return Success(None)

    # @debugFunc
    def free(self):
        if self.state != OwnerState.Owned:
            return Failure(f'{self.name} is in {self.state}')
        self.set_state(OwnerState.Freed)
        print(self)
        return Success(None)

    def __str__(self):
        return '<{clsname}({name}, {state})>'\
            .format(clsname='OwnPtrSymbol',
                     name=self.name,
                     state=self.state)

class Reference(Symbol):

    def __init__(self, name, kind, owner):
        self.name = name
        self.kind = kind
        self.owner = owner

    def __str__(self):
        return f'<Reference({self.name}, {self.kind.string}, {str(self.owner)})>'

    def return_ownership(self):
        if self.owner.state == OwnerState.UniqBrowered:
            self.owner.set_state(OwnerState.Owned)
        elif isinstance(self.owner.state, OwnerState._ShrBrowered):
            self.owner.state.decr()
            if self.owner.state.getcnt() == 0:
                self.owner.set_state(OwnerState.Owned)
        else:
            assert False, f'{self.owner.state = }'
