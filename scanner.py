#!/usr/bin/python3
"""
this is a template file
"""

from returns.result import safe
from tokenize       import tokenize, INDENT, NL
from io             import BytesIO

from returns.pipeline import flow

class Scanner:
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
            lambda x : filter(lambda x : x.exact_type != INDENT and x.exact_type != NL, x)
        )

class FileScanner(Scanner):
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

    @safe
    def scan(self, encoding='utf-8'):
        self.file = open(self.filepath, 'rb')
        return filter(lambda x : x.exact_type != INDENT and x.exact_type != NL, tokenize(self.file.readline))

    def __del__(self):
        if self.file:
            self.file.close()
