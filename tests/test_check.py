#!/usr/bin/python3


from .gen_expr import gen_expr
from typing    import Never

from interpretor import Container, providers
from scan        import StrScanner
from visit       import SemanticAnalyzer
from parse       import Parser

def test_check_assign() -> Never:
    code = f"""{{
        Num a, b, c;
        a = 1;
        b = a + 1;
        c = b + 1;
        print a + b + c;
    }}
    """
    Container.scanner.override(providers.Object(StrScanner(code)))
    gms = Container.checkonly()

    actual_table = {
        'a':  '<a:Num>',
        'b':  '<b:Num>',
        'c':  '<c:Num>'
    }

    checker = SemanticAnalyzer()
    print(checker.curr_scope._symbols)
    gms.execute().value_or(None)
    for key, value in checker.curr_scope._symbols.items():
        if key not in actual_table:
            continue
        assert actual_table[key] == str(value)


def test_check_double_declaration():
    code = """\
        Num a;
        Str a;
        Bool a;
    """
    Container.scanner.override(providers.Object(StrScanner(code)))
    gms = Container.checkonly()

    checker = SemanticAnalyzer()
    print(checker.curr_scope._symbols)
    res = gms.execute()
    assert 'Duplicate id found' in str(res.failure())

def test_check_scope_simple():
    import glob, os
    path = glob.glob('./**/semantics')
    for root, dir, files in os.walk(path[0]):
        print(root, dir, files)
        for file in files:
            with open(path[0] + '/' + file) as f:
                code = f.read()

            Container.scanner.override(providers.Object(StrScanner(code)))
            gms = Container.checkonly()

            checker = SemanticAnalyzer()
            print(checker.curr_scope._symbols)
            gms.execute().unwrap()

