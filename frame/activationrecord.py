#!/usr/bin/python3
from enum import Enum
from typing import Self
from returns.result     import safe,     Success, Failure, Result

class ARType(Enum):
    GLOBAL_FRAME = 'GLOBAL_FRAME'
    LOCAL_FRAME  = 'LOCAL_FRAME'

class ActivationRecord:
    def __init__(self, name, type, parent):
        self.name = name
        self.type = type
        self.parent = parent
        self.members = {}
        # print(f'frame {name} get parent {str(parent)}')

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def get(self, key):
        if key in self.members:
            return self.members[key]
        return self.parent.get(key)

    def set(self, key, value):
        """used only after static checked, safe!!
        """
        # print(f'set {key} <-> {value}')
        self.members[key] = value

    def __str__(self):
        lines = [
            '{type} {name}'.format(
                type=self.type.value,
                name=self.name,
            )
        ]
        for name, val in self.members.items():
            lines.append(f'   {name}: {val}')

        return '\n'.join(lines)

    def __repr__(self):
        return self.__str__()


