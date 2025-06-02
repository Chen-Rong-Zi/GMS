#!/usr/bin/env python3
from node.ast import AST
from abc import ABC, abstractmethod
from parse import Parser
from scan  import StrScanner, FileScanner, PipeLineScanner
from visit import PrettyPrinter, GraphMaker

from returns.result import Result, ResultE, Success
from typing import Any, Iterator

class ASTProcessor(ABC):
    def process(self, ast) -> ResultE[Any]:
        pass

class GMSInterpretor(ASTProcessor):
    def __init__(self, analyzer, interpretor):
        self._analyzer    = analyzer
        self._interpretor = interpretor

    def process(self, ast):
        return Result.do(
            second
            for first in self._analyzer.visit(ast)
            for second in self._interpretor.visit(first)
        )

class Check(ASTProcessor):
    def __init__(self, analyzer):
        self._analyzer = analyzer
        self.process     = self._analyzer.visit

class Formator(ASTProcessor):
    def process(self, ast):
        return PrettyPrinter().visit(ast)

class Graph(ASTProcessor):
    def __init__(self):
        self._analyzer = GraphMaker()

    def process(self, ast):
        return self._analyzer.visit(ast)


class ASTService(ABC):
    @abstractmethod
    def scan(self) -> ResultE[Iterator['Token']]:
        pass

    @property
    @abstractmethod
    def processor(self) -> ASTProcessor:
        pass

    def execute(self):
        return Result.do(
            n
            for token in self.scan()
            for ast in Parser(token).parse()
            for n   in self.processor.process(ast)
        )

class Interact(ASTService):
    def __init__(self, processor):
        self._processor = processor

    def scan(self):
        string = input('gms> ')
        return StrScanner(string).scan()

    @property
    def processor(self):
        return self._processor


    def execute(self) -> ResultE[Any]:
        while True:
            try:
                super().execute().map(print).alt(print)
            except KeyboardInterrupt:
                print('\nKeyboardInterrupt, press CTRL-D to exit')
            except EOFError:
                print()
                break
        return Success(None)

class FromScanner(ASTService):
    def __init__(self, scanner, processor):
        self._processor = processor
        self._scanner = scanner

    def scan(self):
        return self._scanner.scan()

    @property
    def processor(self):
        return self._processor
