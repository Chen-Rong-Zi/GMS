#!/usr/bin/python3
"""
this is a template file
"""


from returns.result import Success
from interpretor    import Evaluater, SemanticAnalyzer
from scan           import StrScanner
from node           import VarSymbol

def test_basic():
    code = \
"""\
Num a, b, c;
a = 1; b = 2; c = 3;
{
    Bool aa, bb, cc;
    {
        Str dd, ee, ff, gg;
    }
}
"""
