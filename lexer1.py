import ply.lex as lex

class Lexer:
    # Lista de tokens
    tokens = [
        'PROGRAM', 'CONST', 'INT', 'FLOAT', 'BOOL', 'STRING',
        'IF', 'ELSE', 'WHILE', 'PRINT', 'INPUT',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQ', 'NEQ', 
        'LT', 'GT', 'LEQ', 'GEQ', 'NOT', 'ASSIGN',
        'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 
        'SEMICOLON', 'ID','INTEGER_CONST','FLOAT_CONST','STRING_CONST'
    ]

    # Palavras reservadas
    reserved = {
        'program': 'PROGRAM',
        'int': 'INT',
        'float': 'FLOAT',
        'bool': 'BOOL',
        'str': 'STRING',
        'const': 'CONST',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'print': 'PRINT',
        'input': 'INPUT'
    }

    # Regras de expressões regulares para tokens simples
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
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_SEMICOLON = r';'
    t_ASSIGN = r'='
    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_INTEGER_CONST(self, t):
        r'\d+'
        return t

    def t_FLOAT_CONST(self, t):
        r'\d+\.\d+'
        return t

    def t_STRING_CONST(self, t):
        r'\".*?\"'
        return t

    def t_newline(self, t):
        r'\n+'
        pass

    def t_error(self, t):
        print(f"Erro léxico: Caractere inválido '{t.value[0]}'")
        t.lexer.skip(1)
