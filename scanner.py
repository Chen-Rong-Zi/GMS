#!/usr/bin/python3
"""
this is a template file
"""

from tokenize import generate_tokens, tokenize, INDENT
from io import BytesIO

from returns.pipeline import flow

class Scanner:
    def scan_from_str(string, encoding='utf-8'):
        return flow(
            string.encode(encoding),
            lambda bytes : BytesIO(bytes).readline,
            tokenize,
            lambda x : filter(lambda x : x.exact_type != INDENT, x)
        )
