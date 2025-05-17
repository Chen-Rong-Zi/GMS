import sys

from returns.result import safe, Success, Failure, Result
from .debug import debugFunc

global __ENABLE_SCOPE_LOGING
__ENABLE_SCOPE_LOGING = False

# @debugFunc
def log(*args, **kwargs):
    if False:
        print(*args, **kwargs)

def validate(result):
    if result is None:
        return Failure('Invalid Value None')
    else:
        return Success(result)

def error(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def check_same(a, b):
    return Success(()) if a == b else Failure(())
