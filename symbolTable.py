import sys

class SymbolTable:
    def __init__(self):
        self.table = {}

    def __str__(self):
        return str(self.table)


    def declare(self, p, name, var_type, value=None):
        if value == None:
            if var_type == 'str':
                value = ""
            elif var_type == 'bool':
                value = 'false'
            elif var_type == 'int' or var_type == 'float':
                value = 0

        if name in self.table:
            print(f"Erro semântico na linha {p.lineno(3)}: Variável '{name}' já declarada.")
            sys.exit(1)

        if var_type == 'const':
            self.table[name] = {'type': self.check_type(p, value), 'value': None, 'const': True}
        else:
            self.table[name] = {'type': var_type, 'value': None}


    def assign(self, p, name, value):
        if name not in self.table:
            print(f"Erro semântico na linha {p.lineno(2)}: Variável '{name}' não declarada.")
            sys.exit(1)
        
        if 'const' in self.table[name].keys():
            if self.table[name]['value'] != None:
                print(f"Erro semântico na linha {p.lineno(2)}: Tentativa de reatribuir valor a um tipo const")
                sys.exit(1)
            
        self.table[name]['value'] = value


    def lookup(self, p, name):
        if name not in self.table:
            if type(name).__name__ != 'str' or (type(name).__name__ == 'str' and (name == 'true' or name == 'false')):
                raise Exception(f"Erro semântico na linha {p.lineno(2)}: Variável '{name}' não declarada.")
            else:
                print(f"Erro semântico na linha {p.lineno(2)}: Variável '{name}' não declarada.")
                sys.exit(1)
        return self.table[name]['type']


    def check_type(self, p, op):
        # try:
        #     return self.lookup(op)
        # except:
        if isinstance(op, float):  # FLOAT_CONST
            return 'float'
        
        elif isinstance(op, int):  # INTEGER_CONST
            return 'int'
        
        elif isinstance(op, str):  # STRING_CONST
            if op == 'true' or op == 'false':
                return 'bool'
            return 'str'
        
        elif isinstance(op, tuple):
            if op[0] == 'binop':
                left_type = self.check_type(p, op[2])
                right_type = self.check_type(p, op[3])

                if left_type == 'str':
                    left_type = self.lookup(p, op[2])
                
                if right_type == 'str':
                    right_type = self.lookup(p, op[3])

                if left_type != 'float' and left_type != "int" or right_type != 'float' and right_type != "int":
                     print(f"Erro semântico na linha {p.lineno(2)}: Operação inválida entre tipos {left_type} e {right_type}.")
                     sys.exit(1)
                return left_type
            
            elif op[0] == 'relop':  # Operação relacional
                try:
                    left_type = self.table[op[2]]['type']  # Verifica se é variável
                except:
                    if op[2] == 'false' or op[2] == 'true': 
                        left_type = 'bool'
                    else:
                        left_type = self.check_type(p, op[2]) 
                
                try:
                    right_type = self.table[op[2]]['type']  # Verifica se é variável
                except:
                    if op[2] == 'false' or op[2] == 'true': # Verifica bool
                        right_type = 'bool'
                    else:
                        right_type = self.check_type(p, op[2]) # Verifica outros tipos mais internos

                # if left_type != right_type:
                #     print(f"Erro semântico na linha {p.lineno(2)}: Comparação inválida entre tipos {left_type} e {right_type}.")
                #     sys.exit(1)
                return 'bool'  # Operações relacionais retornam um booleano
