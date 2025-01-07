import ply.lex as lex

class Lexer:
    # Lista de tokens
    tokens = (
        'PROGRAM', 'INT', 'FLOAT', 'BOOL', 'CONST',
        'IF', 'ELSE', 'WHILE', 'PRINT', 'INPUT',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ', 'NOT',
        'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'SEMICOLON', 'ASSIGN',
        'ID',
        'INTEGER_CONST', 'FLOAT_CONST', 'STRING_CONST'
    )

    # Palavras reservadas
    reserved = {
        'program': 'PROGRAM',
        'int': 'INT',
        'float': 'FLOAT',
        'bool': 'BOOL',
        'const': 'CONST',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'print': 'PRINT',
        'input': 'INPUT'
    }

    # Regras de expressões regulares para tokens simples
    # Operadores
    t_NOT = r'!'
    t_MINUS = r'-'
    t_PLUS = r'\+'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQ = r'=='
    t_NEQ = r'!='
    t_GEQ = r'>='
    t_LEQ = r'<='
    t_GT = r'>'
    t_LT = r'<'

    # Delimitadores
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_SEMICOLON = r';'
    t_ignore = " \t"
    t_ASSIGN = r'='

    def __init__(self):
        self.lexer = None

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_INTEGER_CONST(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_FLOAT_CONST(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    def t_STRING_CONST(self, t):
        r'\".*?\"'
        t.value = t.value[1:-1]
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"Erro léxico: Caractere inválido '{t.value[0]}' na linha {t.lineno}")
        t.lexer.skip(1)
        
    def input(self, data):
        self.lexer.input(data)
        
    def token(self):
        return self.lexer.token()
