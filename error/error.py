from enum import Enum

class ErrorCode:
    SYNTAXERROR      = 'Syntax     Error'
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND     = 'Identifier not found'
    DUPLICATE_ID     = 'Duplicate id found'
    UNINITIALZIED_ID = 'Uninitialzied'
    UnmatchedType = 'UnmatchedType'
    NotMoveable  = 'can not move out'
    CanNotDerefence = 'can not derefernce'
    MemLeak = 'not free! memory leak'
    CanNotBorror = 'can not borrow'
    CanNotFree = 'can not free'

class Error(Exception):
    def __init__(self, error_code, token, message):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'

    def __str__(self):
        message = [
            self.message,
            self.token.line,
            ' ' * self.token.start[1] + '^' * (self.token.end[1] - self.token.start[1]),
        ]
        return '\n'.join(message)   # 返回自定义的消息

class LexerError(Error):
    pass

class ParserError(Error):
    pass

class SemanticError(Error):
    pass

class RuntimeError(Error):
    pass
