from tokenize       import TokenInfo
from tokenize       import NUMBER,   OP,      NEWLINE, ENDMARKER, PLUS,     MINUS,    STAR,  SLASH,     TokenInfo
from tokenize       import LBRACE,   RBRACE,  LPAR,    RPAR
from tokenize       import NAME,     EQUAL,   SEMI,    COMMA

from returns.result import safe,     Success, Failure, Result

from .ast           import BinOp,    Num,     UnaryOp, Assign,    Variable, Compound, Empty, PrintStat, Declaration, Type

class Parser:
    Literal    = [NUMBER]
    UnaryOp    = [PLUS, MINUS]
    Operator   = [OP,      PLUS,      MINUS, STAR, SLASH]
    EOF        = [NEWLINE, ENDMARKER, 4]
    ExtentedOP = [LPAR,    RPAR,      OP,    PLUS, MINUS, STAR, SLASH]
    Keyword = ['print', 'Num', 'string']


    def __init__(self, tokens):
        self.tokens     = tokens
        self.encoding   = next(self.tokens)
        self.curr_token = next(self.tokens)
        """
        assignment: variable = expr SEMI
        compound statement: LBRACE statement list RBRACE
        declaration statement: TYPE variable (COMMA variable)* SEMI
        print statement: PRINT expr

        statement: empty
                    | assignment statement 
                    | compound statement
                    | declaration statement
                    | print statement

        statement list: statement
                    | statement statement list


        expr: term   ((PLUS|MINUS) term)*
        term: factor ([MUL DIV] factor)*
        factor: variable
            | (+ | - ) factor
            | int
            | lpaten expr rparen
        variable: NAME
        """
        self.read_term = self.rule(self.read_factor, [STAR, SLASH])
        self.read_expr = self.rule(self.read_term,   [PLUS, MINUS])
        self.read_name = lambda : self.read_specific([NAME])

    def advance(self):
        self.curr_token = next(self.tokens)
        return self.curr_token

    def read_keyword(self, keywords):
        match self.read_specific([NAME]):
            case Success(tk) if tk.string in keywords:
                return Success(tk)
            case Success(tk):
                return Failure(f'expect keyword {keywords}, got {tk.string}')
            case failure:
                return failure

    def read_specific(self, types):
        match self.curr_token:
            case token if token.exact_type in types:
                self.advance()
                return Success(token)
            case error:
                return Failure(f"expect {types} at line: {error.start[0]} col: {error.start[1], error.end[1]} but got {self.curr_token.exact_type}")

    def read_factor(self):
        match self.curr_token:
            case tk if tk.type in Parser.Literal:
                self.advance()
                return Success(Num(tk))
            case tk if tk.exact_type == LPAR:
                self.advance()
                expr = self.read_expr()
                if self.curr_token.exact_type != RPAR:
                    return Failure("unmatched parentheses at line: {x.start[0]} col: {x.start[1], x.end[1]}")
                self.advance()
                return expr
            case tk if tk.exact_type in Parser.UnaryOp:
                self.advance()
                return self.read_factor().map(lambda expr : UnaryOp(tk, expr))
            case var if var.exact_type == NAME:
                if var.string in Parser.Keyword:
                    return Failure(f'invalid name {var.string} at line: {var.start[0]} col: {var.start[1], var.end[1]}, it is a keyword')
                self.advance()
                return Success(Variable(var))
            case error_token:
                return Failure(f'Unkown Factor Token {error_token.string} at line: {error_token.start[0]} col: {error_token.start[1], error_token.end[1]}')

    def rule(self, read_next, op_type):
        def defination():
            factor = read_next()
            while True:
                match self.curr_token:
                    case op if op.exact_type in op_type:
                        self.advance()
                        factor = Result.do(
                            BinOp(x, op, y)
                            for x in factor
                            for y in read_next()
                        )
                    case op:
                        return factor
        return defination

    def read_print_statement(self):
        self.advance()
        return Result.do(
            PrintStat(expr)
            for expr in self.read_expr()
            for semi in self.read_specific([SEMI])
        )

    def read_statement(self):
        match self.curr_token:
            case op if op.string == 'print':
                return self.read_print_statement()
            case op if op.string in Parser.Keyword:
                return self.read_declaration()
            case op if op.exact_type == NAME:
                return Result.do(
                    Assign(lvalue, equal_sign, rvalue)
                    for lvalue     in self.read_factor()
                    for equal_sign in self.read_specific([EQUAL])
                    for rvalue     in self.read_expr()
                    for semicolumn in self.read_specific([SEMI])
                )
            case op if op.exact_type == LBRACE:
                return Result.do(
                    statement_list
                    for left  in self.read_specific([LBRACE])
                    for statement_list in self.read_statement_list()
                    for right in self.read_specific([RBRACE])
                )
            case other:
                return Success(Empty())

    def read_statement_list(self):
        statement_list = []
        while True:
            match self.read_statement():
                case Success(Empty()):
                    return Success(Compound(statement_list))
                case Success(declares) if type(declares) == list:
                    statement_list.extend(declares)
                case Success(statement):
                    statement_list.append(statement)
                case failure:
                    return failure


    def read_declaration(self):
        _type = self.read_keyword(['Num']).map(Type)

        names = Result.do(
            [Declaration(t, n)]
            for t in _type
            for n in self.read_name()
        )

        while True:
            match self.curr_token:
                case comma if comma.exact_type == COMMA:
                    self.advance()
                    names = Result.do(
                        prev_names + [Declaration(t, next_name)]
                        for next_name in self.read_name()
                        for prev_names in names
                        for t in _type
                    )
                case semi  if semi.exact_type  == SEMI:
                    self.advance()
                    return names
                case other:
                    return Failure(f'fail to read declaration due to {other.string} at line: {other.start[0]}, col: {other.start[1], other.end[1]}')

    def parse(self):
        return self.read_statement_list()\
            .bind(lambda result : Success(result)
                    if self.curr_token.exact_type in Parser.EOF
                    else Failure(f'Expect EOF token {self.curr_token.string} at line: {self.curr_token.start[0]} col: {self.curr_token.start[1], self.curr_token.end[1]}'))

class ExprParser(Parser):
    def parse(self):
        return self.read_expr()\
            .bind(lambda result : Success(result)
                if self.curr_token.exact_type in Parser.EOF
                else Failure(f'Expect Eof Token {self.curr_token.string} at line: {self.curr_token.start[0]} col: {self.curr_token.start[1], self.curr_token.end[1]}'))
