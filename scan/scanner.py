#!/usr/bin/python3
"""
this is a template file
"""
import sys

from abc               import ABC, abstractmethod

from returns.result    import safe
from returns.pipeline  import flow
from returns.pointfree import bind,     map_
from tokenize          import tokenize, INDENT, NL, NEWLINE, DEDENT
from tokenize          import TokenError
from io                import BytesIO


class Scanner(ABC):
    remove_extra = lambda x : filter(lambda x : x.exact_type not in [INDENT, NL, NEWLINE, DEDENT], x)
    @abstractmethod
    @safe
    def scan(self):
        raise Exception('unimplemented scan method')

class StrScanner(Scanner):
    def __init__(self, buffer):
        self.buffer = buffer

    @safe
    def scan(self, encoding='utf-8'):
        return flow(
            self.buffer.encode(encoding),
            lambda bytes : BytesIO(bytes).readline,
            tokenize,
            Scanner.remove_extra
        )

class FileScanner(Scanner):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = None

    @safe
    def scan(self):
        self.file = open(self.filepath, 'rb')
        return Scanner.remove_extra(tokenize(self.file.readline))

    def __del__(self):
        if self.file:
            self.file.close()

class PipeLineScanner(StrScanner):
    def __init__(self):
        self.buffer = sys.stdin.read()

    @safe
    def scan(self, encoding='utf-8'):
        return flow(
            self.buffer.encode(encoding),
            lambda bytes : BytesIO(bytes).readline,
            tokenize,
            Scanner.remove_extra
        )
