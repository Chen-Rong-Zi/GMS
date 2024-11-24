#!/usr/bin/python3
"""
this is a template file
"""

from tokenize import generate_tokens, tokenize
from io import BytesIO

class Scanner:
    def scan_from_str(string, encoding='utf-8'):
        return tokenize(BytesIO(string.encode(encoding)).readline)
