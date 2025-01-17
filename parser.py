import ply.yacc as yacc
from lexer import Lexer
from symbolTable import SymbolTable
import sys

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
        result = self.parser.parse(data, lexer=self.lexer.lexer)
        formatted_result = self.format_output(result)
        return result
    
    def process_complex_item(self, item):
        if isinstance(item, (list, tuple)):
            result = []
            for sub_item in item:
                processed = self.process_complex_item(sub_item)
                if isinstance(processed, list):
                    result.extend(processed)
                else:
                    result.append(processed)
            return result
        else:
            return str(item)
            
    def process_complex_item(self, item):
        if isinstance(item, tuple):
            items = [item[0]]
            for sub_item in item[1:]:
                if isinstance(sub_item, (list, tuple)):
                    processed = self.process_complex_item(sub_item)
                    items.extend(processed)
                else:
                    items.append(str(sub_item))
            return items
        elif isinstance(item, list):
            result = []
            for sub_item in item:
                if isinstance(sub_item, (list, tuple)):
                    processed = self.process_complex_item(sub_item)
                    result.extend(processed)
                else:
                    result.append(str(sub_item))
            return result
        return [str(item)]


    def format_output(self, node):
        if isinstance(node, tuple):
            if node[0] == 'program':
                return f"('program', '{node[1]}', {self.format_output(node[2])}, {self.format_output(node[3])})"
                
            items = [node[0]]
            for item in node[1:]:
                if isinstance(item, (list, tuple)):
                    processed = self.process_complex_item(item)
                    items.extend(processed)
                else:
                    items.append(str(item))
            return "(" + ", ".join(f"'{item}'" if isinstance(item, str) else str(item) for item in items) + ")"
            
        elif isinstance(node, list):
            if not node:
                return "[]"
            items = [self.format_output(item) for item in node]
            return "[\n" + ",\n".join(items) + "\n]"
        
        else:
            if isinstance(node, str):
                return f"'{node}'"
            return str(node)
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
            try:
                value_type = self.symbol_table.table[p[4]]['type'] # No lugar da função lookup
            except:
                value_type = self.symbol_table.check_type(p, p[4])
            #value_type = self.symbol_table.check_type(p, p[4])  # Função que verifica o tipo de literal

            if value_type != var_type and var_type != 'const':
                print(f"Erro semântico na linha {p.lineno(2)}: Tipo incompatível na declaração de '{p[2]}'. Esperado {var_type}, mas encontrado {value_type}.")
                sys.exit(1)

            self.symbol_table.declare(p, p[2], p[1], p[4])
            self.symbol_table.assign(p, p[2], p[4])  # Atribui o valor à variável
            p[0] = ('var_decl_with_assignment', p[1], p[2], p[4])

        else:  # Declaração de variável
            for var in p[2]:
                self.symbol_table.declare(p, var, p[1])
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

        try:
            var_type = self.symbol_table.table[p[1]]['type'] # No lugar da função lookup
        except:
            var_type = self.symbol_table.check_type(p, p[1])
        try:
            exp_type = self.symbol_table.table[p[3]]['type'] # No lugar da função lookup
        except:
            exp_type = self.symbol_table.check_type(p, p[3])
        
        if var_type == 'int' and exp_type == 'float':
            print(f"Observação truncamento na linha {p.lineno(1)}: Valor float atribuido a variável integer.")
            p[3] = int(p[3])

        if var_type == 'float' and exp_type == 'int':
            print(f"Observação realocamento na linha {p.lineno(1)}: Valor integer atribuido a variável float.")
            p[3] = float(p[3])
        
        if var_type == 'str' and not isinstance(p[3], str):
            print(f"Erro semântico na linha {p.lineno(1)}: Atribuição inválida. Esperado string entre aspas, mas encontrado {p[3]}.")
            sys.exit(1)

        self.symbol_table.assign(p, p[1], p[3])
        p[0] = ('assign', p[1], p[3])


    def p_print_stmt(self, p):
        '''print_stmt : PRINT LPAREN exp_list RPAREN SEMICOLON'''

        p[0] = ('print', p[3])


    def p_input_stmt(self, p):
        '''input_stmt : INPUT LPAREN id_list RPAREN SEMICOLON'''

        for var in p[3]:
            self.symbol_table.lookup(p, var)
        p[0] = ('input', p[3])


    def p_if_stmt(self, p):
        '''if_stmt : IF LPAREN exp RPAREN LBRACE stmt_list RBRACE else_part'''

        try:
            condition_type = self.symbol_table.table[p[3]]['type'] # No lugar da função lookup
        except:
            condition_type = self.symbol_table.check_type(p, p[3])
        #condition_type = self.symbol_table.check_type(p, p[3])

        if condition_type != 'bool':
            print(f"Erro semântico na linha {p.lineno(1)}: Condição 'if' deve ser do tipo 'bool', mas foi encontrado {condition_type}.")
            sys.exit(1)
        
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
        try:
            condition_type = self.symbol_table.table[p[3]]['type'] # No lugar da função lookup
        except:
            condition_type = self.symbol_table.check_type(p, p[3])
        #condition_type =self.symbol_table.check_type(p, p[3])

        if condition_type != 'bool':
            print(f"Erro semântico na linha {p.lineno(1)}: Condição 'while' deve ser do tipo 'bool', mas foi encontrado {condition_type}.")
            sys.exit(1)
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
            try:
                left_type = self.symbol_table.table[p[1]]['type'] # No lugar da função lookup
            except:
                left_type = self.symbol_table.check_type(p, p[1])
            try:
                right_type = self.symbol_table.table[p[3]]['type'] # No lugar da função lookup
            except:
                right_type = self.symbol_table.check_type(p ,p[3])

            if left_type == 'bool' or left_type == 'str' or right_type == 'bool' or right_type == 'str':
                print(f"Erro semântico na linha {p.lineno(2)}: Operação aritmética inválida entre tipos {left_type} e {right_type}.")
                sys.exit(1)

            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]


    def p_term(self, p):
        '''term : term TIMES factor
                | term DIVIDE factor
                | factor
                | unary'''
    
        if len(p) == 4:
            try:
                left_type = self.symbol_table.table[p[1]]['type'] # No lugar da função lookup
            except:
                left_type = self.symbol_table.check_type(p, p[1])
            try:
                right_type = self.symbol_table.table[p[3]]['type'] # No lugar da função lookup
            except:
                right_type = self.symbol_table.check_type(p, p[3])

            if left_type == 'bool' or left_type == 'str' or right_type == 'bool' or right_type == 'str':
                print(f"Erro semântico na linha {p.lineno(2)}: Operação aritmética inválida entre tipos {left_type} e {right_type}.")
                sys.exit(1)

            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]


    def p_unary(self,p):
        '''unary : NOT factor
                 | MINUS factor'''
        
        if len(p) == 3:
            try:
                type_factor = self.symbol_table.table[p[2]]['type'] # No lugar da função lookup
            except:
                type_factor = self.symbol_table.check_type(p, p[2])

            if type_factor != 'bool' and type_factor != 'str' and p[1] == '-':
                p[0] = ('unary', p[1], p[2])

            elif type_factor == 'bool' and p[1] == '!':
                p[0] = ('unary', p[1], p[2])

            else:
                print(f"Erro semântico na linha {p.lineno(1)}: Operação unária inválida. Uso do operador unário {p[1]} com o tipo {type_factor}.")
                sys.exit(1)

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
            if p.slice[1].type == 'ID':
                self.symbol_table.lookup(p, p[1])
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
        if p:
            if p.type == 'SEMICOLON':
                print(f"Erro de sintaxe na linha {p.lineno}: Esperado ';' antes de '{p.value}'")
                sys.exit(1)
            else:
                prev_token = self.parser.symstack[-1]
                if prev_token.type in ['ID', 'INTEGER_CONST', 'FLOAT_CONST', 'STRING_CONST', 'BOOL_CONST']:
                    print(f"Erro de sintaxe na linha {p.lineno}: Esperado ';' antes de '{p.value}'")
                    sys.exit(1)
                else:
                    print(f"Erro de sintaxe na linha {p.lineno}: '{p.value}' inesperado")
                    sys.exit(1)
        else:
            print("Erro de sintaxe: Chaves { } desbalanceadas")
        sys.exit(1)
