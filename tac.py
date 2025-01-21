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


    def process_if(self, stmt):
        _, condition, if_body, else_part = stmt
        code = []

        # Processar condição
        cond_temp = self.process_condition(condition, code)

        true_label = self.new_label()
        false_label = self.new_label()
        end_label = self.new_label()

        code.append(f"if {cond_temp} goto {true_label}")
        code.append(f"goto {false_label}")

        # Bloco if
        code.append(f"{true_label}:")
        for if_stmt in if_body:
            code.extend(self.process_statement(if_stmt))
        code.append(f"goto {end_label}")

        # Bloco else
        code.append(f"{false_label}:")
        if else_part:
            for else_stmt in else_part[1]:
                code.extend(self.process_statement(else_stmt))

        code.append(f"{end_label}:")
        return code

    def process_while(self, stmt):
        _, condition, body = stmt
        code = []

        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()

        code.append(f"{start_label}:")
        cond_temp = self.process_condition(condition, code)
        code.append(f"if {cond_temp} goto {body_label}")
        code.append(f"goto {end_label}")

        code.append(f"{body_label}:")
        for body_stmt in body:
            code.extend(self.process_statement(body_stmt))
        code.append(f"goto {start_label}")

        code.append(f"{end_label}:")
        return code

    def process_condition(self, condition, code):
        if condition[0] == 'relop':
            _, op, left, right = condition
            t1 = self.load_value(left, code)
            t2 = self.load_value(right, code)
            t3 = self.next_temp()
            code.append(f"{t3} = {t1} {op} {t2}")
            return t3
        return None


    def process_print(self, stmt):
        code = []
        for expr in stmt[1]:
            if expr.startswith('"'):
                code.append(f"print({expr})")
            else:
                code.append(f"print({self.var_map.get(expr, expr)})")
        return code


