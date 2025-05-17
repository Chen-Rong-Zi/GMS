#!/usr/bin/python3
from enum import Enum
from typing import Self
from tokenize import TokenInfo
from returns.result     import safe,     Success, Failure, Result
from returns.pipeline   import is_successful
from error import RuntimeError, ErrorCode
from util  import debugFunc

class ARType(Enum):
    GLOBAL_FRAME = 'GLOBAL_FRAME'
    LOCAL_FRAME  = 'LOCAL_FRAME'
    BLOKL_FRAME  = 'BLOKL_FRAME'

class ActivationRecord:
    def __init__(self, name, type, parent):
        self.name = name
        self.type = type
        self.parent = parent
        self.members = {}

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def print_frame(self, frame):
        if frame is None:
            return
        self.print_frame(frame.parent)
        print(frame)

    def error(self, error_code, token):
        print(token)
        self.print_frame(self)
        return Failure(RuntimeError(error_code, token, message=f'{error_code} -> {token}'))

    # @debugFunc
    def getrval(self, key):
        # print(f'looking {key} in {self}')
        if key in self.members:
            return Success(self.members[key])
        if self.parent is None:
            return self.error(ErrorCode.ID_NOT_FOUND, TokenInfo(19, key, (0, 0), (0, 0), ''))
        return self.parent.getrval(key)

    def getlval(self, key):
        # print(f'looking {key} in {self}')
        if key in self.members:
            return Success(self)
        if self.parent is None:
            return self.error(ErrorCode.ID_NOT_FOUND, TokenInfo(19, key, (0, 0), (0, 0), ''))

        return self.parent.getlval(key)

    def set(self, key, value):
        """used only after static checked, safe!!
        """
        # print(f'set {key} <-> {value}')
        self.members[key] = value
        return self

    def __str__(self):
        title = 'Frame (Frame Stack)'
        lines = [title,
            '{type} {name}'.format(
                type=self.type.value,
                name=self.name,
            ),
            '============\n'
        ]
        for name, val in self.members.items():
            lines.append(f'   {name}: {val}')

        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()


