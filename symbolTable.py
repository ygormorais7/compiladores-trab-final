class SymbolTable:
    def __init__(self):
        self.table = {}

    def declare(self, name, var_type):
        if name in self.table:
            raise Exception(f"Erro semântico: Variável '{name}' já declarada.")
        self.table[name] = {'type': var_type, 'value': None}

    def assign(self, name, value):
        if name not in self.table:
            raise Exception(f"Erro semântico: Variável '{name}' não declarada.")
        self.table[name]['value'] = value

    def lookup(self, name):
        if name not in self.table:
            raise Exception(f"Erro semântico: Variável '{name}' não declarada.")
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
                        raise Exception(f"Erro semântico: Operação inválida entre tipos {left_type} e {right_type}.")
                    return left_type
                elif p[0] == 'relop':  # Operação relacional
                    left_type = self.check_type(p[2])
                    right_type = self.check_type(p[3])
                    if left_type != right_type:
                        raise Exception(f"Erro semântico: Comparação inválida entre tipos {left_type} e {right_type}.")
                    return 'bool'  # Operações relacionais retornam um booleano


    def __str__(self):
        return str(self.table)
