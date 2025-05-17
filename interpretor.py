#!/usr/bin/python3
"""
this is a template file
"""

import sys
import readline
import argparse

from typing           import Iterable
from tokenize         import TokenInfo

from returns.result   import safe,         Success, Failure, Result
from returns.maybe    import Nothing,      Some
from returns.pipeline import is_successful, pipe
from returns.pointfree  import bind, map_
from returns.iterables  import Fold

from objprint         import objprint as pprint

from scan  import FileScanner, StrScanner, Scanner
from visit import Evaluater,   SemanticAnalyzer, OwnerShipChecker, ClosureFlow,  LispVisitor, RPNVisitor, NodeVisitor, PrettyPrinter
from parse import Parser, ExprParser
import util
from util  import debugFunc

class GMS:

    def __init__(self, scanner: Scanner):
        self.scanner = scanner
                # if not is_successful(res):

    def evaluate(self):
        return self.parse_and_visit(ExprParser, Evaluater())

    def interpret(self):
        return self.parse_and_visit(Parser, Evaluater())

    def prettyprint(self):
        return self.parse_and_visit(Parser, PrettyPrinter())

    def check(self):
        return self.parse_and_visit(Parser, SemanticAnalyzer())

    def parse(self, parser_type=Parser):
        return self.scanner.scan().bind(lambda tokens : parser_type(tokens).parse())

    def parse_list(self, parser_type=Parser):
        return self.scanner.scan().bind(lambda tokens : parser_type(tokens).parse_list())

    def parse_and_visit(self, parser_type, visitor):
        return self.scanner.scan()\
            .bind(lambda tokens : parser_type(tokens).parse())\
            .bind(visitor.visit)


class InteractGMS(GMS):
    @staticmethod
    def interact():
        interpretor = Evaluater()
        checker = SemanticAnalyzer()
        while True:
            try:
                gms = Success(GMS(StrScanner(input('GMS> '))))
                # .map(StrScanner).map(GMS)
                # gms = Success(GMS(StrScanner(input('GMS> '))))

                # gms.bind(GMS.evaluate).map(print)
                # gms.bind(Lisp_evaluate).map(print)
                # gms.bind(RPNVisitor().visit).map(print)
                first    = gms.bind(lambda g : g.parse_list(Parser))
                first.bind(PrettyPrinter().visit).map(print)
                second = first.bind(checker.visit)
                third = second.bind(interpretor.visit)

                # Result.do(1 for _ in first for _ in second).alt(print)
                # Result.do(1 for _ in second for _ in third).alt(print)
                Result.do(1 for _ in first for _ in second for _ in third).alt(print)

            except KeyboardInterrupt:
                print('\nKeyboardInterrupt, press CTRL-D to exit')
            except EOFError:
                print()
                break

def parse_args(args, parser):
    if args.filepath:
        gms = Success(GMS(FileScanner(args.filepath)))
    elif not sys.stdin.isatty():
        gms = safe(sys.stdin.read)().map(StrScanner).map(GMS)
    else:
        gms = Failure("error useage")
        # parser.print_help()
    return gms

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GMS: an interpretor')
    parser.add_argument('-i', help='交互模式', required=False, nargs='?')
    parser.add_argument('filepath', default=None, help='文件路径', nargs='?')
    parser.add_argument('-p', '--prettyprint', action='store_true', default=False, help='仅打印代码')
    parser.add_argument('-c', '--check', action='store_true', default=False, help='仅静态检查')
    parser.add_argument('--scope', default=False, action='store_true', help='打印出名字作用域')
    args = parser.parse_args()

    # from viztracer import VizTracer
    # with VizTracer(output_file="optional.json") as tracer:
        # Something happens here

    gms = parse_args(args, parser)
    if args.scope:
        util.__ENABLE_SCOPE_LOGING = True

    if args.prettyprint:
        gms.bind(lambda g : g.prettyprint()).map(print).alt(print)
    elif args.check:
        gms.bind(lambda g : g.check()).bind(lambda g : g.prettyprint()).alt(print).map(print)
    elif is_successful(gms):
        checker = OwnerShipChecker()
        gms.bind(lambda g: g.parse_and_visit(Parser, checker)).bind(ClosureFlow(checker).visit).alt(print)
        # gms.bind(lambda g : g.parse()).bind(ClosureFlow(Evaluater(), SemanticAnalyzer()).visit).alt(print)
    else:
        InteractGMS.interact()

