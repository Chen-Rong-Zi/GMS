#!/usr/bin/python3
"""
this is a template file
"""

from scan.scanner import StrScanner
from .gen_expr    import gen_expr
from interpretor  import Container, providers
from objprint     import objprint as print
import io
import sys


def test_basic():
    for i in range(100):
        code = \
        f"""{{
            Num a, b, c, d, e, _e;
            a = {i};
            b = a + 1;
            c = b * a;
            d = a + b + c;
            e = a * b * c * d;
            _e = e;
            print a;
            print b;
            print c;
            print d;
            print e;
            print _e;
        }}
        """
        a = i
        b = a + 1
        c = b * a
        d = a + b + c
        e = a * b * c * d
        _e = e
        answer = [ a, b, c, d, e, _e ]

        # 创建一个 StringIO 对象作为内存缓冲区
        output_buffer = io.StringIO()

        # 保存原始的 sys.stdout
        sys.stdout = output_buffer

        Container.scanner.override(providers.Object(StrScanner(code)))
        gms = Container.gms()
        gms.execute().unwrap()

        output = output_buffer.getvalue()

        assert '\n'.join(str(i) for i in answer) + '\n' == output
