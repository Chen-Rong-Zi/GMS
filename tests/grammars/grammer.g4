grammar GMS;
// 起始规则
program: statement_list EOF;
// 表达式规则
expr: term ((PLUS | MINUS) term)*;
term: factor ((STAR | SLASH) factor)*;
factor: NUMBER
         | LPAR expr RPAR
         | (PLUS | MINUS) factor
         | NAME;
// 语句规则
statement_list: statement+;
statement: assignment
         | compound_statement
         | declaration
         | print_statement
         | empty;

assignment: NAME EQUAL expr SEMI;
compound_statement: LBRACE statement_list RBRACE;
declaration: TYPE WS NAME (COMMA NAME)* SEMI;
print_statement: PRINT WS expr SEMI;
empty: ;

// 关键字
PRINT: 'print';
TYPE: 'Num';

// 符号
EQUAL: '=';
PLUS: '+';
MINUS: '-';
STAR: '*';
SLASH: '/';
LPAR: '(';
RPAR: ')';
LBRACE: '{';
RBRACE: '}';
SEMI: ';';
COMMA: ',';

// 字面量
NUMBER: [0-9]+;
NAME: [a-zA-Z_][a-zA-Z_0-9]*;

// 忽略空白字符
WS: [ ]+ -> skip;
