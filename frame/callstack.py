#!/usr/bin/python3
from typing import Self
from returns.result import safe, Success, Failure, Result

class CallStack:
    def __init__(self):
        self._records = []

    def push(self, ar) -> Self:
        self._records.append(ar)
        return self

    @safe
    def pop(self):
        return self._records.pop()

    @safe
    def peek(self):
        return self._records[-1]

    def __len__(self):
        return len(self._records)

    def __str__(self):
        s = '\n'.join(str(ar) for ar in reversed(self._records))
        return f'CALL STACK\n{s}\n'

