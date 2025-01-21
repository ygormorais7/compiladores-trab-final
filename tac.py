class tacGen:
    def __init__(self):
        self.temp_vars = ["t1", "t2", "t3"]
        self.temp_index = 0
        self.var_map = {}
        self.label_count = 0

    def next_temp(self):
        temp = self.temp_vars[self.temp_index]
        self.temp_index = (self.temp_index + 1) % len(self.temp_vars)
        return temp

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate_code(self, tree):
        return self.process_program(tree)

    def process_program(self, program):
        _, _, declarations, statements = program
        code = []
        
        for stmt in statements:
            code.extend(self.process_statement(stmt))
        
        return "\n".join(code)

    def process_statement(self, stmt):
        code = []
        if stmt[0] == 'assign':
            code.extend(self.process_assignment(stmt))
        elif stmt[0] == 'if':
            code.extend(self.process_if(stmt))
        elif stmt[0] == 'while':
            code.extend(self.process_while(stmt))
        elif stmt[0] == 'print':
            code.extend(self.process_print(stmt))
        elif stmt[0] == 'input':
            code.extend(self.process_input(stmt))
        return code

    def process_assignment(self, stmt):
        _, var, value = stmt
        code = []
        if isinstance(value, tuple) and value[0] == 'binop':
            _, op, left, right = value
            t1 = self.load_value(left, code)
            t2 = self.load_value(right, code)
            t3 = self.next_temp()
            code.append(f"{t3} = {t1} {op} {t2}")
            self.var_map[var] = t3
        else:
            temp = self.next_temp()
            code.append(f"{temp} = {value}")
            self.var_map[var] = temp
        return code

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

    def load_value(self, value, code):
        if isinstance(value, (int, float)):
            temp = self.next_temp()
            code.append(f"{temp} = {value}")
            return temp
        return self.var_map.get(value, value)

    def process_print(self, stmt):
        code = []
        for expr in stmt[1]:
            if expr.startswith('"'):
                code.append(f"print({expr})")
            else:
                code.append(f"print({self.var_map.get(expr, expr)})")
        return code

    def process_input(self, stmt):
        code = []
        temp = self.next_temp()
        code.append(f"{temp} = input()")
        self.var_map[stmt[1][0]] = temp
        return code
