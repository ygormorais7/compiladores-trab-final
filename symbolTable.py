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
        return self.table[name]

    def __str__(self):
        return str(self.table)
