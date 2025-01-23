class TACtoAssembly:
    def __init__(self):
        self.assembly_code = []
        self.label_map = {}

    def translate(self, tac_lines):
        for line in tac_lines:
            self.process_line(line.strip())
        return "\n".join(self.assembly_code)

    def process_line(self, line):
        if "=" in line and "goto" not in line:  # Atribuição ou operação
            self.process_assignment(line)
        elif line.startswith("if"):  # Condicional
            self.process_conditional(line)
        elif line.startswith("goto"):  # Desvio incondicional
            self.process_goto(line)
        elif ":" in line:  # Rótulo
            self.process_label(line)
        elif line.startswith("param"):  # Parâmetro para função
            self.process_param(line)
        elif line.startswith("call"):  # Chamada de função
            self.process_call(line)

    def process_assignment(self, line):
        parts = line.split("=")
        dest = parts[0].strip()
        expr = parts[1].strip()

        if "+" in expr or "-" in expr or "*" in expr or "/" in expr:  # Operação binária
            op, left, right = self.parse_binop(expr)
            self.assembly_code.append(f"mov rax, [{left}]")  # Carrega o operando esquerdo
            if op == "+":
                self.assembly_code.append(f"add rax, [{right}]")
            elif op == "-":
                self.assembly_code.append(f"sub rax, [{right}]")
            elif op == "*":
                self.assembly_code.append(f"imul rax, [{right}]")
            elif op == "/":
                self.assembly_code.append(f"mov rdx, 0")  # Limpa o registrador rdx para divisão
                self.assembly_code.append(f"mov rcx, [{right}]")  # Carrega o divisor em rcx
                self.assembly_code.append(f"idiv rcx")
            self.assembly_code.append(f"mov [{dest}], rax")  # Armazena o resultado no destino

        else:  # Atribuição simples
            if expr.isdigit() or "." in expr:  # Constante numérica
                self.assembly_code.append(f"mov rax, {expr}")
                self.assembly_code.append(f"mov [{dest}], rax")
            else:  # Variável
                self.assembly_code.append(f"mov rax, [{expr}]")
                self.assembly_code.append(f"mov [{dest}], rax")

    def process_conditional(self, line):
        parts = line.split()
        condition = parts[1]   # Exemplo: "t1 > t2"
        target_label = parts[3]  # Exemplo: "L1"

        left, op, right = self.parse_condition(condition)
        self.assembly_code.append(f"mov rax, [{left}]")  # Carrega o operando esquerdo em rax
        self.assembly_code.append(f"cmp rax, [{right}]")  # Compara com o operando direito

        if op == ">":
            self.assembly_code.append(f"jg {target_label}")
        elif op == "<":
            self.assembly_code.append(f"jl {target_label}")
        elif op == "==":
            self.assembly_code.append(f"je {target_label}")
        elif op == "!=":
            self.assembly_code.append(f"jne {target_label}")
        elif op == ">=":
            self.assembly_code.append(f"jge {target_label}")
        elif op == "<=":
            self.assembly_code.append(f"jle {target_label}")

    def process_goto(self, line):
        _, target_label = line.split()
        self.assembly_code.append(f"jmp {target_label}")

    def process_label(self, line):
        label = line.strip(":")
        self.assembly_code.append(f"{label}:")

    def process_param(self, line):
        _, param = line.split()
        if param.startswith('"'):  # String literal
            label = f".L{len(self.label_map)}"
            self.label_map[label] = param.strip('"')
            self.assembly_code.append(f"lea rdi, [{label}]")
        else:  # Variável ou valor numérico
            self.assembly_code.append(f"mov rsi, [{param}]")

    def process_call(self, line):
        _, func_name, _ = line.split()
        if func_name == "print":
            self.assembly_code.append("call printf")
        elif func_name == "input":
            self.assembly_code.append("call scanf")

    def parse_binop(self, expr):
        for op in ["+", "-", "*", "/"]:
            if op in expr:
                left, right = map(str.strip, expr.split(op))
                return op, left, right

    def parse_condition(self, condition):
        for op in [">=", "<=", "!=", "==", ">", "<"]:
            if op in condition:
                left, right = map(str.strip, condition.split(op))
                return left, op, right
