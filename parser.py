import ply.yacc as yacc
from lexer import Lexer
from symbolTable import SymbolTable

class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.lexer.build()
        self.symbol_table = SymbolTable()
        self.tokens = self.lexer.tokens
        self.parser = None

    def build(self):
        self.parser = yacc.yacc(module=self)
    
    def parse(self, data):
        return self.parser.parse(data, lexer=self.lexer.lexer)

    # Regras da gramática
    def p_program(self, p):
        '''program : PROGRAM ID LBRACE decl_list stmt_list RBRACE'''
        p[0] = ('program', p[2], p[4], p[5])

    def p_decl_list(self, p):
        '''decl_list : decl decl_list
                     | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []


    def p_decl(self, p):
        '''decl : type ID ASSIGN literal SEMICOLON
                | type id_list SEMICOLON'''
        
        if len(p) == 6:  # Declaração de variável com atribuição
            var_type = p[1]
            value_type = self.symbol_table.check_type(p[4])  # Função que verifica o tipo de literal

            if value_type != var_type:
                raise Exception(f"Erro semântico: Tipo incompatível na declaração de '{p[2]}'. Esperado {var_type}, mas encontrado {value_type}.")
            
            self.symbol_table.declare(p[2], p[1]) 
            self.symbol_table.assign(p[2], p[4])  # Atribui o valor à variável
            p[0] = ('var_decl_with_assignment', p[1], p[2], p[4])

        else:  # Declaração de variável
            for var in p[2]:
                self.symbol_table.declare(var, p[1])
            p[0] = ('var_decl', p[1], p[2])


    def p_type(self, p):
        '''type : INT
                | FLOAT
                | BOOL
                | STRING
                | CONST'''
        p[0] = p[1]


    def p_id_list(self, p):
        '''id_list : ID id_tail'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]


    def p_id_tail(self, p):
        '''id_tail : COLON ID id_tail
                   | empty'''
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = []


    def p_stmt_list(self, p):
        '''stmt_list : stmt stmt_list
                     | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []


    def p_stmt(self, p):
        '''stmt : assign_stmt
                | print_stmt
                | input_stmt
                | if_stmt
                | while_stmt'''
        p[0] = p[1]


    def p_assign_stmt(self, p):
        '''assign_stmt : ID ASSIGN exp SEMICOLON'''
        var_type = self.symbol_table.lookup(p[1])
    
        value_type = self.symbol_table.check_type(p[3])  # Função que verifica o tipo da expressão

        if value_type != var_type:
            raise Exception(f"Erro semântico: Tipo incompatível na atribuição de '{p[1]}'. Esperado {var_type}, mas encontrado {value_type}.")
    
        self.symbol_table.assign(p[1], p[3])
        p[0] = ('assign', p[1], p[3])


    def p_print_stmt(self, p):
        '''print_stmt : PRINT LPAREN exp_list RPAREN SEMICOLON'''
        p[0] = ('print', p[3])


    def p_input_stmt(self, p):
        '''input_stmt : INPUT LPAREN id_list RPAREN SEMICOLON'''
        for var in p[3]:
            self.symbol_table.lookup(var)
        p[0] = ('input', p[3])


    def p_if_stmt(self, p):
        '''if_stmt : IF LPAREN exp RPAREN LBRACE stmt_list RBRACE else_part'''
        condition_type = self.symbol_table.check_type(p[3])

        if condition_type != 'bool':
            raise Exception(f"Erro semântico: Condição 'if' deve ser do tipo 'bool', mas foi encontrado {condition_type}.")
        
        p[0] = ('if', p[3], p[6], p[8])


    def p_else_part(self, p):
        '''else_part : ELSE LBRACE stmt_list RBRACE
                     | empty'''
        if len(p) == 5:
            p[0] = ('else', p[3])
        else:
            p[0] = None


    def p_while_stmt(self, p):
        '''while_stmt : WHILE LPAREN exp RPAREN LBRACE stmt_list RBRACE'''
        condition_type = self.symbol_table.check_type(p[3])

        if condition_type != 'bool':
            raise Exception(f"Erro semântico: Condição 'while' deve ser do tipo 'bool', mas foi encontrado {condition_type}.")
        p[0] = ('while', p[3], p[6])


    def p_exp(self, p):
        '''exp : exp_relational'''

        p[0] = p[1]


    def p_exp_relational(self, p):
        '''exp_relational : exp_arithmetic
                     | exp_arithmetic GT exp_arithmetic
                     | exp_arithmetic LT exp_arithmetic
                     | exp_arithmetic GEQ exp_arithmetic
                     | exp_arithmetic LEQ exp_arithmetic
                     | exp_arithmetic EQ exp_arithmetic
                     | exp_arithmetic NEQ exp_arithmetic'''
       
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ('relop', p[2], p[1], p[3])


    def p_exp_arithmetic(self, p):
        '''exp_arithmetic : exp_arithmetic PLUS term
                     | exp_arithmetic MINUS term
                     | term'''
        if len(p) == 4:
            left_type = self.symbol_table.check_type(p[1])
            right_type = self.symbol_table.check_type(p[3])

            if left_type != right_type or left_type == 'bool' or right_type == 'bool':
                raise Exception(f"Erro semântico: Operação aritmética inválida entre tipos {left_type} e {right_type}.")

            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]


    def p_term(self, p):
        '''term : term TIMES factor
                | term DIVIDE factor
                | factor'''
        if len(p) == 4:
            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]


    def p_bool_const(self, p):
        '''BOOL_CONST : TRUE
                     | FALSE'''
        p[0] = p[1]


    def p_factor(self, p):
        '''factor : ID 
                  | INTEGER_CONST 
                  | FLOAT_CONST 
                  | STRING_CONST 
                  | BOOL_CONST
                  | LPAREN exp RPAREN'''
        if len(p) == 2:
            if p.slice[1].type == 'ID':  # Only lookup if token is ID
                self.symbol_table.lookup(p[1])
            p[0] = p[1]
        else:
            p[0] = p[2]


    def p_empty(self, p):
        '''empty :'''
        p[0] = None


    def p_literal(self, p):
        '''literal : INTEGER_CONST
                   | FLOAT_CONST
                   | STRING_CONST
                   | BOOL_CONST'''
        p[0] = p[1]


    def p_exp_list(self, p):
        '''exp_list : exp exp_tail'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]


    def p_exp_tail(self, p):
        '''exp_tail : COLON exp exp_tail
                    | empty'''
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = []


    def p_error(self, p):
        print(f"Erro de sintaxe: {p.value} na linha {p.lineno}")
