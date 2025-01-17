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
            self.table[name] = {'type': self.check_type(value), 'value': None, 'const': True}
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
            print(f"Erro semântico na linha {p.lineno(2)}: Variável '{name}' não declarada.")
            sys.exit(1)
        return self.table[name]['type']


    def check_type(self, p):
        try:
            return self.lookup(p)
        except:
            if isinstance(p, int):  # INTEGER_CONST
                return 'int'
            elif isinstance(p, float):  # FLOAT_CONST
                return 'float'
            elif isinstance(p, str):  # STRING_CONST
                if p == 'true' or p == 'false':
                    return 'bool'
                return 'str'
            elif isinstance(p, bool):  # BOOL_CONST
                return 'bool'
            elif isinstance(p, tuple):
                if p[0] == 'binop':
                    left_type = self.check_type(p[2])
                    right_type = self.check_type(p[3])
                    if left_type != right_type:
                        print(f"Erro semântico na linha {p.lineno(2)}: Operação inválida entre tipos {left_type} e {right_type}.")
                        sys.exit(1)
                    return left_type
                elif p[0] == 'relop':  # Operação relacional
                    left_type = self.check_type(p[2])
                    right_type = self.check_type(p[3])
                    if left_type != right_type:
                        print(f"Erro semântico na linha {p.lineno(2)}: Comparação inválida entre tipos {left_type} e {right_type}.")
                        sys.exit(1)
                    return 'bool'  # Operações relacionais retornam um booleano
