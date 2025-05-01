#!/usr/bin/python3
"""
this is a template file
"""


from returns.result import Success
from interpretor    import GMS,       Evaluater, SemanticAnalyzer
from scan           import StrScanner
from node           import VarSymbol

def test_basic():
    code = \
"""\
Str d, e, f;
Num a, b, c;
a = 1; b = 2; c = 3;
{
    Bool aa, bb, cc;
    {
        Str dd, ee, ff, gg;
    }
}
"""
    scanner = StrScanner(code)
    interpretor, checker = Evaluater(), SemanticAnalyzer()
    ast = GMS(scanner).parse()

    ast.bind(interpretor.visit).alt(print).map(print)
    ast.bind(checker.visit).alt(print).map(print)

    symtab = checker.curr_scope
    type_Num = symtab.lookup('Num').unwrap()
    type_Str = symtab.lookup('Str').unwrap()
    type_Bool = symtab.lookup('Bool').unwrap()
    # print(symtab)

    for v in ['a', 'b', 'c']:
        assert symtab.lookup(v) == Success(VarSymbol(v, type_Num))
    for v in ['aa', 'bb', 'cc']:
        assert symtab.lookup(v) == Success(VarSymbol(v, type_Bool))
    for v in ['dd', 'ee', 'ff', 'gg']:
        assert symtab.lookup(v) == Success(VarSymbol(v, type_Str))
