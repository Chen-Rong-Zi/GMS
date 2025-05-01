from .debug import debugFunc

global __ENABLE_SCOPE_LOGING
__ENABLE_SCOPE_LOGING = False

# @debugFunc
def log(*args, **kwargs):
    if False:
        print(*args, **kwargs)
