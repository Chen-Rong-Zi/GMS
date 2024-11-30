#!/usr/bin/python3
import sys
sys.path.append('../..')

from GMS.interpretor import Interpretor
from .gen_expr import gen_expr

def test_simple():
    code = " a = 1; b = 2; c = 3;"
    assert Interpretor.prettyprint(code)._inner_value ==\
"""{
    a = 1;
    b = 2;
    c = 3;
}
"""
