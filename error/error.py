from enum import Enum

class ErrorCode(Enum):
    SYNTAXERROR = 'Syntax Error'
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND     = 'Identifier not found'
    DUPLICATE_ID     = 'Duplicate id found'

class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'

    def __str__(self):
        return self.message  # 返回自定义的消息

class LexerError(Error):
    pass

class ParserError(Error):
    pass

class SemanticError(Error):
    pass
