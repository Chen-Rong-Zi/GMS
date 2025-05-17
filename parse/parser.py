from token import GREATER
import tokenize
from tokenize       import TokenInfo
from tokenize       import NUMBER,  STRING, OP,  NEWLINE, ENDMARKER, PLUS,     MINUS,    STAR,  SLASH,     TokenInfo
from tokenize       import LBRACE,   RBRACE,  LPAR,    RPAR, AMPER
from tokenize       import NAME,     EQUAL,   SEMI,    COMMA, LESSEQUAL, GREATEREQUAL, LESS, GREATER, EQEQUAL

from returns.result     import safe,     Success, Failure, Result
from returns.iterables  import Fold
from returns.pipeline   import is_successful

from node.ast       import BinOp,    Num, Str, Bool, UnaryOp, Assign,    Variable, Compound, Empty, PrintStat, VarDeclaration, Type, RefDecl, Free
from node.ast       import FuncParam, FuncDeclaration, FuncCall, Ret, GlobalAst, Conditional, NewAlloc, FullType, Deref, Mutation, OwnPtrDecl, Move
from node.symbol    import BuiltinType, GMSKeyword, FuncSymbol
from util           import debugFunc, check_same
from error          import ParserError, ErrorCode

class Parser:
    Literal    = [NUMBER]
    UnaryOp    = [PLUS, MINUS]
    Operator   = [OP,      PLUS,      MINUS, STAR, SLASH]
    EOF        = [NEWLINE, ENDMARKER, 4]
    ExtentedOP = [LPAR,    RPAR,      OP,    PLUS, MINUS, STAR, SLASH]
    BuiltinTypes = [BuiltinType.NUM, BuiltinType.BOOL, BuiltinType.STR]
    Keyword = [GMSKeyword.FREE, GMSKeyword.NEW, GMSKeyword.SHARE, GMSKeyword.UNIQ, GMSKeyword.OWN, GMSKeyword.ELSE, GMSKeyword.IF, GMSKeyword.PRINT, GMSKeyword.FUNC, GMSKeyword.RET] + GMSKeyword.TYPES

    @staticmethod
    def token_to_literal(token_type):
        assert token_type in tokenize.tok_name, "unkown token type {}".format(token_type)
        return tokenize.tok_name[token_type]

    def __init__(self, tokens):
        self.tokens     = tokens
        self.encoding   = next(self.tokens)
        self.curr_token = next(self.tokens)
        self.in_func_block = 0
        """
        assignment: ID = expr SEMI
        mutate: DEREF = expr SEMI
        compound statement: LBRACE statement list RBRACE
        print statement: PRINT expr SEMI
        variable declaration statement: TYPE ID (COMMA ID)* SEMI
        function declaration statement: FUNC ID paramlist  RETARR ID compound_statement
        own-pointer declaration statement: TYPE name EQUAL new TYPE SEMI

        paramlist: LPAR (ID: TYPE)* RPAR

        statement: empty
                    | assignment statement 
                    | compound statement
                    | declaration statement
                    | own pointer declaration
                    | borrow pointer declaration
                    | free statement:
                    | print statement
                    | return statement

        statement list: statement
                    | statement statement list

        expr: term2
            | term2 if expr else expr
        term2: term1  ((> | < | == | >= | <=) term1)*
        term1: term0  ((PLUS|MINUS) term0)*
        term0: factor ([MUL DIV] factor)*
        factor: ID
            | ID LPAREN (expr (COMMA expr)*)? RPAREN
            | + factor
            | - factor
            | int
            | lpaten expr rparen
            | DEREF
        TYPE: BASETYPE own (STAR)*
            | BASETYPE uniq (STAR)*
            | BASETYPE share (STAR)*
            | BASETYPE
        DEREF: (STAR)+ ID
        BASETYPE: Num | Str | 
        ID: NAME
        LPAR: '('
        RPAR: ')'
        FUNC: 'func'
        RETARR: '->'
        """
        self.read_term0 = self.rule(self.read_factor, [STAR, SLASH])
        self.read_term1 = self.rule(self.read_term0,   [PLUS, MINUS])
        self.read_term2 = self.rule(self.read_term1,   [LESS, LESSEQUAL, GREATER, GREATEREQUAL, EQEQUAL])
        self.read_name = lambda : self.read_specific([NAME])
        self.read_base_type = lambda : self.read_keyword(Parser.BuiltinTypes).map(Type)

    def error(self, error_code, token, origin):
        return Failure(ParserError(error_code=error_code,
                                   token=token,
                                   message=f'{error_code} -> {token.string, Parser.token_to_literal(token.type)} at line: {token[2][0]}, expect {origin}'))

    # @debugFunc
    def advance(self):
        self.curr_token = next(self.tokens)
        return self.curr_token

    # @debugFunc
    def read_expr(self):
        term = self.read_term2()
        if self.curr_token.string == 'if':
            return term.bind(self.read_conditional)
        else:
            return term

    def read_conditional(self, term):
        return Result.do(
            Conditional(cond, term, else_term)
            for _         in self.read_keyword([GMSKeyword.IF])
            for cond      in self.read_expr()
            for _         in self.read_keyword([GMSKeyword.ELSE])
            for else_term in self.read_expr()
        )

#  @debugFunc
    def read_keyword(self, keywords):
        match self.read_name():
            case Success(tk) if tk.string in keywords:
                return Success(tk)
            case Success(tk):
                return self.error(ErrorCode.UNEXPECTED_TOKEN, tk, keywords)
            case failure:
                return failure

#  @debugFunc
    def read_specific(self, types):
        match self.curr_token:
            case token if token.exact_type in types:
                self.advance()
                return Success(token)
            case tk:
                # print(self.curr_token, types)
                #  return Result.do("expect {} at line: {} col: {} but got {}".format(_types, error.start[0], (error.start[1], error.end[1]), t)
                #              for _types in Fold.collect([Parser.token_to_literal(type) for type in types], Success(()))
                #              # for _types in (i for i in range(1))
                #              for t      in Parser.token_to_literal(self.curr_token.exact_type))\
                #          .bind(Failure)
                return self.error(ErrorCode.UNEXPECTED_TOKEN, tk, f'{[Parser.token_to_literal(type) for type in types]}')

    def read_deref(self):
        level = 0
        while self.curr_token.exact_type == STAR:
            level += 1
            self.advance()
        if level == 0:
            return self.error(ErrorCode.UNEXPECTED_TOKEN, self.curr_token, '*')
        return self.read_name().map(lambda tk : Deref(tk, level))

#  @debugFunc
    def read_factor(self):
        match self.curr_token:
            case TokenInfo(type=tokenize.NUMBER) as tk:
                self.advance()
                return Success(Num(tk))
            case TokenInfo(type=tokenize.STRING) as tk:
                self.advance()
                return Success(Str(tk))
            case TokenInfo(string='True' | 'False') as tk:
                self.advance()
                return Success(Bool(tk))
            case TokenInfo(string='('):
                self.advance()
                expr = self.read_expr()
                if self.curr_token.exact_type != RPAR:
                    return self.error(ErrorCode.UNEXPECTED_TOKEN, self.curr_token, f')')
                self.advance()
                return expr
            case TokenInfo(string=('+' | '-')) as tk:
                self.advance()
                return self.read_factor().map(lambda expr : UnaryOp(tk, expr))
            case TokenInfo(string='*') as tk:
                return self.read_deref()
            case var if var.exact_type == NAME:
                if var.string in Parser.Keyword:
                    return self.error(ErrorCode.UNEXPECTED_TOKEN, var, 'NAME')
                self.advance()
                if self.curr_token.exact_type == LPAR:
                    return self.read_funccall(var)
                else:
                    return Success(Variable(var))
            case error_token:
                return self.error(ErrorCode.UNEXPECTED_TOKEN, error_token, '+ factor | - factor | int | lpaten expr rparen')

#  @debugFunc
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

#  @debugFunc
    def read_print_statement(self):
        self.advance()
        return Result.do(
            PrintStat(expr)
            for expr in self.read_expr()
            for _ in self.read_specific([SEMI])
        )

    # @debugFunc
    def read_assign(self):
        return Result.do(
            Assign(lvalue, equal_sign, rvalue)
            for lvalue     in self.read_factor()
            for equal_sign in self.read_specific([EQUAL])
            for rvalue     in self.read_expr()
            for _ in self.read_specific([SEMI])
        )

    def read_compound(self):
        return Result.do(
            Compound(statement_list)
            for _  in self.read_specific([LBRACE])
            for statement_list in self.read_statement_list()
            for _ in self.read_specific([RBRACE])
        )

    def read_ret_statement(self):
        return Result.do(
            Ret(expr)
            for _ in self.read_keyword([GMSKeyword.RET])
            for expr in self.read_expr()
            for _ in self.read_specific([SEMI])
        )

    # @debugFunc
    def read_mutation(self):
        return Result.do(
            Mutation(deref, expr)
            for deref in self.read_deref()
            for _ in self.read_specific([EQUAL])
            for expr in self.read_expr()
            for _  in self.read_specific([SEMI])
        )

    def read_reference_declaration(self, type_token):
        return Result.do(
            RefDecl(Type(type_token), decl_deref, keyword, deref)
            for keyword in self.read_keyword([GMSKeyword.UNIQ, GMSKeyword.SHARE])
            for decl_deref in self.read_deref()
            for _ in self.read_specific([EQUAL])
            for _ in self.read_specific([AMPER])
            for _ in self.read_keyword([keyword.string])
            for deref in self.read_factor()
            for _ in self.read_specific([SEMI])
        )

    def read_free(self):
        return Result.do(
            Free(name)
            for _ in self.read_keyword([GMSKeyword.FREE])
            for _ in self.read_specific([LPAR])
            for name in self.read_name()
            for _ in self.read_specific([RPAR])
            for _ in self.read_specific([SEMI])
        )

    # @debugFunc
    def read_statement(self):
        match self.curr_token:
            case TokenInfo(string=GMSKeyword.RET):
                if self.in_func_block > 0:
                    return self.read_ret_statement()
                return self.error(ErrorCode.SYNTAXERROR, self.curr_token, f'STATEMENT {self.in_func_block}')
            case TokenInfo(string=GMSKeyword.PRINT):
                return self.read_print_statement()
            case TokenInfo(string=GMSKeyword.FUNC):
                return self.read_funcdeclaration()
            case TokenInfo(string=GMSKeyword.FREE):
                return self.read_free()
            case op if op.string in Parser.BuiltinTypes:
                self.advance()
                match self.curr_token:
                    case TokenInfo(string=GMSKeyword.OWN):
                        return self.read_own_declaration(op)
                    case TokenInfo(string=GMSKeyword.UNIQ |  GMSKeyword.SHARE):
                        return self.read_reference_declaration(op)
                    case _:
                        return self.read_vardeclara(op)
            case TokenInfo(string='*'):
                return self.read_mutation()
            case op if op.exact_type == NAME:
                return self.read_assign()
            case TokenInfo(string='{'):
                return self.read_compound()
            case _:
                return Success(Empty())

    # @debugFunc
    def read_statement_list(self):
        statement_list = []
        while True:
            match self.read_statement():
                case Success(Empty() as e):
                    return Success(statement_list + [e])
                case Success([*declares]):
                    statement_list.extend([*declares])
                case Success(statement):
                    statement_list.append(statement)
                case failure:
                    return failure

    def read_own_pointer(self, type_token):
        return Result.do(
            OwnPtrDecl(ftype, name)
            for ftype in self.read_full_type(type_token)
            for name in self.read_name()
        )


    def read_own_declaration(self, type_token):
        ownptrdecl = self.read_own_pointer(type_token)
        equal = self.read_specific([EQUAL])
        if not is_successful(equal):
           return equal
        if self.curr_token.string == GMSKeyword.NEW:
            return Result.do(
                NewAlloc(ownptr)
                for ownptr in ownptrdecl
                for _    in self.read_keyword([GMSKeyword.NEW])
                for t    in self.read_base_type()
                for _    in check_same(type_token.string, t.token.string).lash(lambda _ : self.error(ErrorCode.UnmatchedType, type_token, [t.token]))
                for _    in self.read_specific([SEMI])
            )
        else:
            return Result.do(
                Move(own_pointer, deref)
                for own_pointer  in ownptrdecl
                for deref in self.read_name()
                for _    in self.read_specific([SEMI])
            )

    def read_full_type(self, base_type_token):
        match self.curr_token:
            case TokenInfo(string=GMSKeyword.OWN):
                self.advance()
                level = 0
                while self.curr_token.exact_type == STAR:
                    level += 1
                    self.advance()
                return Success(FullType(base_type_token, Type(base_type_token), level, GMSKeyword.OWN))
            case _:
                return self.error(ErrorCode.SYNTAXERROR, self.curr_token, [GMSKeyword.OWN])

#  @debugFunc
    def read_vardeclara(self, type_token):
        _type = Type(type_token)

        names = Result.do(
            [VarDeclaration(_type, n)]
            for n in self.read_name()
        )
        if not is_successful(names):
           return names

        while True:
            match self.curr_token:
                # case comma if comma.exact_type == COMMA:
                case TokenInfo(string=','):
                    self.advance()
                    names = Result.do(
                        prev_names + [VarDeclaration(_type, next_name)]
                        for next_name in self.read_name()
                        for prev_names in names
                    )
                case semi  if semi.exact_type  == SEMI:
                    self.advance()
                    return names
                case other:
                    return self.error(ErrorCode.UNEXPECTED_TOKEN, other, ',')

    def read_funcdeclaration(self):
        self.in_func_block += 1
        ret = Result.do(
            FuncDeclaration(Variable(funcname), paramlist, compound)
            for _  in self.read_keyword([GMSKeyword.FUNC])
            for funcname  in self.read_name()
            for paramlist in self.read_paramlist()
            for compound  in self.read_statement()
        )
        self.in_func_block -= 1
        return ret

    def read_param(self):
        return Result.do(
            FuncParam(_type, Variable(name))
            for _type in self.read_base_type()
            for name  in self.read_name()
        )

    def read_paramlist(self):
        def read_params():
            params = []
            while True:
                match self.curr_token:
                    case TokenInfo(string=','):
                        self.advance()
                    case TokenInfo(string=')'):
                        return Success(params)
                    case _:
                        param = self.read_param().map(params.append)
                        if not is_successful(param):
                            return param
                        else:
                            continue
        return Result.do(
            params
            for _ in self.read_specific([LPAR])
            for params in read_params()
            for _ in self.read_specific([RPAR])
        )

    # @debugFunc
    def read_funccall(self, tk):
        return Result.do(
            FuncCall(Variable(tk), args, tk)
            for lpar in self.read_specific([LPAR])
            for args in self.read_arguments()
            for rpar in self.read_specific([RPAR])
        )

    # @debugFunc
    def read_arguments(self):
        arguments = []
        while True:
            match self.curr_token:
                case TokenInfo(string=')'):
                    return Success(arguments)
                case TokenInfo(string=','):
                    self.advance()
                case _:
                    args = self.read_expr().map(arguments.append)
                    if not is_successful(args):
                        return args
                    else:
                        continue

    # @debugFunc
    def parse(self):
        return self.read_statement_list()\
            .bind(lambda result : Success(result)
                    if self.curr_token.exact_type in Parser.EOF
                    else self.error(ErrorCode.UNEXPECTED_TOKEN, self.curr_token, 'EOF'))\
            .map(Compound)\
            .map(GlobalAst)

    def parse_list(self):
        return self.read_statement_list()\
            .bind(lambda result : Success(result)
                    if self.curr_token.exact_type in Parser.EOF
                    else self.error(ErrorCode.UNEXPECTED_TOKEN, self.curr_token, 'EOF'))


class ExprParser(Parser):
    def parse(self):
        return self.read_expr()\
            .bind(lambda result : Success(result)
                if self.curr_token.exact_type in Parser.EOF
                else self.error(ErrorCode.UNEXPECTED_TOKEN, self.curr_token, 'EOF'))
