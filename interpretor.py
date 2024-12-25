#!/usr/bin/python3
"""
this is a template file
"""

import sys
import readline
import argparse

from typing                import Iterable

from returns.result        import safe,         Success,   Failure,     Result
from returns.maybe         import Nothing,      Some
from returns.pipeline      import is_successful

from .scanner              import FileScanner,  StrScanner
from .nodevisitor          import Evaluater,    Checker,   LispVisitor, RPNVisitor, NodeVisitor
from .parser               import Parser, ExprParser
from .pretty.prettyprinter import PrettyPrinter



class Interpretor:
    def _select_scanner(arg, is_file=False):
        if is_file:
            return FileScanner(arg)
        return StrScanner(arg)

    def _select_visitor(visitor):
        if isinstance(visitor, NodeVisitor):
            return visitor
        return visitor()

    def _interpret(parser=Parser, visitor=Evaluater()):
        def run(arg, is_file=False):
            scanner = Interpretor._select_scanner(arg, is_file)
            _visitor = Interpretor._select_visitor(visitor)
            return scanner\
                .scan()\
                .bind(lambda tokens : parser(tokens).parse())\
                .bind(_visitor.visit)
        return run

def debug(func):
    def inner(*args, **kwargs):
        breakpoint()
        return func(*args, **kwargs)
    return inner

class GMS:
    prettyprint = Interpretor._interpret(visitor=PrettyPrinter)
    interpret   = Interpretor._interpret(visitor=Evaluater)
    evaluate    = Interpretor._interpret(parser=ExprParser, visitor=Evaluater())

    def __init__(self):
        self.interpretor = Evaluater()
        self.checker      = Checker()
        self.check       = Interpretor._interpret(visitor=self.checker)

    def interact(self):
        while True:
            try:
                input_expr = safe(input)('GMS> ').alt(lambda _ : exit(0))
                # input_expr.bind(GMS.evaluate).map(print)
                # input_expr.bind(Lisp_evaluate).map(print)
                # input_expr.bind(RPNVisitor).map(print)
                input_expr.bind(GMS.prettyprint).map(print)
                input_expr\
                    .bind(self.check)\
                    .bind(self.interpretor.visit)\
                    .alt(print)

            except KeyboardInterrupt:
                print('\nKeyboardInterrupt')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GMS: an interpretor')
    parser.add_argument('-i', help='交互模式', required=False, nargs='?')
    parser.add_argument('filepath', default=None, help='gms文件路径', nargs='?')
    args = parser.parse_args()

    if not sys.stdin.isatty():
        GMS.interpret(sys.stdin.read())
    elif args.filepath:
        GMS.interpret(args.filepath, is_file=True)
    else:
        gms = GMS()
        gms.interact()

