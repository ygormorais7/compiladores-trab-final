class tacGen:
    def __init__(self):
        self.temp_counter = 0
        self.var_map = {}
        self.label_count = 0

    def next_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate_code(self, tree):
        return self.process_program(tree)

    def process_program(self, program):
        _, _, declarations, statements = program
        code = []

        for decl in declarations:
            if decl[0] == 'var_decl_with_assignment':
                _, dtype, var, value = decl
                temp = self.load_value(value, code)
                self.var_map[var] = temp
            elif decl[0] == 'var_decl':
                _, dtype, vars_list = decl
                for var in vars_list:
                    self.var_map[var] = None

        for stmt in statements:
            code.extend(self.process_statement(stmt))

        return "\n".join(code)

    def process_statement(self, stmt):
        code = []
        if stmt[0] == 'assign':
            code.extend(self.process_assignment(stmt))
        elif stmt[0] == 'print':
            code.extend(self.process_print(stmt))
        return code

    def process_assignment(self, stmt):
        _, var, value = stmt
        code = []
        if isinstance(value, tuple):
            if value[0] == 'relop':
                _, op, left, right = value
                t1 = self.load_value(left, code)
                t2 = self.load_value(right, code)
                t3 = self.next_temp()
                code.append(f"{t3} = {t1} {op} {t2}")
                self.var_map[var] = t3
            elif value[0] == 'unary':
                _, op, operand = value
                t1 = self.load_value(operand, code)
                t2 = self.next_temp()
                code.append(f"{t2} = {op} {t1}")
                self.var_map[var] = t2
            elif value[0] == 'binop':
                _, op, left, right = value
                t1 = self.load_value(left, code)
                t2 = self.load_value(right, code)
                t3 = self.next_temp()
                code.append(f"{t3} = {t1} {op} {t2}")
                self.var_map[var] = t3
        else:
            temp = self.load_value(value, code)
            self.var_map[var] = temp
        return code

    def load_value(self, value, code):
        if isinstance(value, tuple):
            if value[0] == 'relop':
                _, op, left, right = value
                t1 = self.load_value(left, code)
                t2 = self.load_value(right, code)
                temp = self.next_temp()
                code.append(f"{temp} = {t1} {op} {t2}")
                return temp
            elif value[0] == 'unary':
                _, op, operand = value
                t1 = self.load_value(operand, code)
                temp = self.next_temp()
                code.append(f"{temp} = {op} {t1}")
                return temp
            elif value[0] == 'binop':
                _, op, left, right = value
                t1 = self.load_value(left, code)
                t2 = self.load_value(right, code)
                temp = self.next_temp()
                code.append(f"{temp} = {t1} {op} {t2}")
                return temp
        elif isinstance(value, str) and value in self.var_map:
            return self.var_map[value]
        elif isinstance(value, str) and value in ('true', 'false'):
            temp = self.next_temp()
            code.append(f"{temp} = {value}")
            return temp
        else:
            temp = self.next_temp()
            code.append(f"{temp} = {value}")
            return temp

    def process_print(self, stmt):
        code = []
        for expr in stmt[1]:
            if expr.startswith('"'):
                code.append(f"print({expr})")
            else:
                code.append(f"print({self.var_map.get(expr, expr)})")
        return code


