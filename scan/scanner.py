#!/usr/bin/python3
"""
this is a template file
"""

from returns.result   import safe
from returns.pipeline import flow
from tokenize         import tokenize, INDENT, NL, NEWLINE, DEDENT
from io               import BytesIO


class Scanner:
    remove_extra = lambda x : filter(lambda x : x.exact_type not in [INDENT, NL, NEWLINE, DEDENT], x)
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
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

    @safe
    def scan(self):
        self.file = open(self.filepath, 'rb')
        return Scanner.remove_extra(tokenize(self.file.readline))

    def __del__(self):
        if self.file:
            self.file.close()
