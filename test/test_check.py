#!/usr/bin/python3

import sys
sys.path.append('../..')

from GMS.interpretor import GMS
from .gen_expr import gen_expr


def test_check_assign():
    gms = GMS()
    code = f"""{{
        Num a, b, c;
        a = 1;
        b = a + 1;
        c = b + 1;
        print a + b + c;
    }}
    """

    actual_table = {
        'a':  '<a:Num>',
        'b':  '<b:Num>',
        'c':  '<c:Num>'
    }

    print(gms.checker.symtab.dict)
    gms.check(code)
    for key, value in gms.checker.symtab.dict.items():
        if key not in actual_table:
            continue
        assert actual_table[key] == str(value)
