#!/usr/bin/python3
"""
this is a template file
"""

import sys
import readline
import util

from typing           import Iterable
from tokenize         import TokenInfo

from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

from returns.result   import safe,         Success, Failure, Result
from returns.maybe    import Nothing,      Some
from returns.pipeline import is_successful, pipe
from returns.pointfree  import bind, map_
from returns.iterables  import Fold

from objprint         import objprint as pprint

from scan  import FileScanner, StrScanner, PipeLineScanner, Scanner
from visit import Evaluater,   SemanticAnalyzer, OwnerShipChecker, ClosureFlow, NodeVisitor, PrettyPrinter, GraphMaker
from parse import Parser, ExprParser
from util  import debugFunc
from cli   import args
from bridge import Formator, GMSInterpretor, Check, Interact, FromScanner, Graph
if args.scope:
    util.__ENABLE_SCOPE_LOGING = True


class Container(containers.DeclarativeContainer):
    stdin_reader = providers.Factory(PipeLineScanner)
    file_reader = providers.Factory(FileScanner, args.filepath)

    scanner = providers.Selector(
        lambda: 'stdin' if (not sys.stdin.isatty()) else 'file',
        stdin=stdin_reader,
        file=file_reader,
    )

    interact = providers.Callable(lambda processor : Interact(processor))
    fromscanner = providers.Callable(lambda processor : FromScanner(Container.scanner(), processor))

    astprovider = providers.Selector(
        lambda : 'scanner' if ((not sys.stdin.isatty()) or args.filepath) else 'interact',
        scanner=fromscanner,
        interact=interact,
    )

    # concrete checker and evaluater
    analyzer = providers.Factory(OwnerShipChecker)
    graph_maker = providers.Factory(GraphMaker)
    evaluater = providers.Factory(ClosureFlow, analyzer)

    # concrete ASTProcessor
    interpretor = providers.Factory(GMSInterpretor, analyzer, evaluater)
    formator = providers.Object(Formator())
    checker = providers.Factory(Check, analyzer)
    graphfy = providers.Factory(Graph)

    # concrete ASTService
    codeformator = providers.Factory(astprovider, formator)
    checkonly = providers.Factory(astprovider, checker)
    gms = providers.Factory(astprovider, interpretor)
    interact_gms = providers.Factory(astprovider, interpretor)
    graph = providers.Factory(astprovider, graphfy)

if __name__ == '__main__':
    if args.prettyprint:
        formator = Container.codeformator()
        formator.execute().map(print).alt(print)
    elif args.check:
        checker = Container.checkonly()
        checker.execute().alt(print)
    elif args.graph:
        graph = Container.graph()
        graph.execute().alt(print).map(print)
    elif args.filepath:
        gms = Container.gms()
        gms.execute().alt(print)
    else:
        gms = Container.interact_gms()
        gms.execute().alt(print)

