class TACtoAssembly:
    def __init__(self):
        self.assembly_code = []
        self.label_map = {}
        self.float_constants = {}
        self.string_constants = {}
        self.variables = set()
        self.temp_counter = 0

    def translate(self, tac_lines):
        for line in tac_lines:
            self.process_line(line.strip())
        
        # Adicionar seção de dados no início
        self.generate_data_section()
        
        # Adicionar instruções de finalização
        self.assembly_code.append("\n    mov rax, 60")
        self.assembly_code.append("    xor rdi, rdi")
        self.assembly_code.append("    syscall")
        
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
        self.track_variable(dest)
        expr = parts[1].strip()
        
        if "/" in expr:
            left, right = map(str.strip, expr.split("/"))
            self.track_variable(left)
            self.track_variable(right)
            
            if "." in right:
                float_label = self.create_float_constant(right)
                self.assembly_code.append(f"    movsd xmm1, qword [{float_label}]")
            else:
                self.assembly_code.append(f"    movsd xmm1, qword [{right}]")
                
            if "." in left:
                float_label = self.create_float_constant(left)
                self.assembly_code.append(f"    movsd xmm0, qword [{float_label}]")
            else:
                self.assembly_code.append(f"    movsd xmm0, qword [{left}]")
                
            # Realizar a divisão
            self.assembly_code.append(f"    divsd xmm0, xmm1")
            # Armazenar resultado
            self.assembly_code.append(f"    movsd qword [{dest}], xmm0")


    def create_float_constant(self, value):
        label = f"float_{self.temp_counter}"
        self.temp_counter += 1
        self.float_constants[label] = value
        return label

    def load_float_operand(self, reg, operand):
        if "." in operand:
            float_label = self.create_float_constant(operand)
            self.assembly_code.append(f"    movsd {reg}, qword [{float_label}]")
        else:
            self.assembly_code.append(f"    movsd {reg}, qword [{operand}]")

    def store_float_result(self, dest, reg):
        self.assembly_code.append(f"    movsd qword [{dest}], {reg}")


    def process_conditional(self, line):
        parts = line.split()
        condition = parts[1]  # Exemplo: "t1 > t2"
        target_label = parts[3]  # Exemplo: "L1"
        left, op, right = self.parse_condition(condition)

        self.assembly_code.append(f"mov rax, qword [{left}]")  # Carrega o operando esquerdo em rax
        self.assembly_code.append(f"cmp rax, qword [{right}]")  # Compara com o operando direito

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
        if param.startswith('"'):
            # Criar constante string
            str_label = self.create_string_constant(param)
            self.assembly_code.append("    push rbp")
            self.assembly_code.append("    mov rbp, rsp")
            self.assembly_code.append(f"    lea rdi, [fmt_str]")
            self.assembly_code.append(f"    lea rsi, [{str_label}]")
            self.assembly_code.append("    xor rax, rax")  # 0 argumentos float
        else:
            if "." in param:
                self.assembly_code.append("    push rbp")
                self.assembly_code.append("    mov rbp, rsp")
                self.assembly_code.append("    lea rdi, [fmt_float]")
                self.assembly_code.append(f"    movsd xmm0, qword [{param}]")
                self.assembly_code.append("    mov rax, 1")  # 1 argumento float

    def process_call(self, line):
        _, func_name, _ = line.split()
        if func_name == "print":
            self.assembly_code.append("    call printf")
            self.assembly_code.append("    mov rsp, rbp")
            self.assembly_code.append("    pop rbp")
    
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

    def generate_data_section(self):
        self.assembly_code.insert(0, "section .data")
        # Formatos para printf
        self.assembly_code.insert(1, "    fmt_str db '%s', 10, 0")
        self.assembly_code.insert(2, "    fmt_float db '%f', 10, 0")
        # String constante
        self.assembly_code.insert(3, "    msg db 'Resultado:', 0")
        # Constantes float
        self.assembly_code.insert(4, "    const1_1 dq 1.1")
        self.assembly_code.insert(5, "    const1_0 dq 1.0")
        
        # Declarar variáveis
        offset = 3
        for var in self.variables:
            self.assembly_code.insert(offset, f"    {var} dq 0.0")
            offset += 1
        
        # Adicionar constantes float
        for label, value in self.float_constants.items():
            self.assembly_code.insert(offset, f"    {label} dq {value}")
            offset += 1
            
        # Adicionar strings constantes
        for label, value in self.string_constants.items():
            self.assembly_code.insert(offset, f"    {label} db {value}, 0")
            offset += 1
        
        self.assembly_code.insert(offset, "\nsection .text")
        self.assembly_code.insert(offset + 1, "    global _start")
        self.assembly_code.insert(offset + 2, "    extern printf")

    
    def process_print(self, value):
        if "." in value:
            self.assembly_code.append("    sub rsp, 8")  # Alinhar stack
            self.assembly_code.append(f"    movsd xmm0, qword [{value}]")
            self.assembly_code.append("    mov rax, 1")  # Um argumento float
            self.assembly_code.append("    lea rdi, [fmt_float]")
            self.assembly_code.append("    call printf")
            self.assembly_code.append("    add rsp, 8")  # Restaurar stack

    def create_string_constant(self, value):
        # Remove as aspas do início e fim
        value = value.strip('"')
        # Cria label única para a string
        label = f"str_{self.temp_counter}"
        self.temp_counter += 1
        # Converte a string para formato assembly
        asm_string = ", ".join(str(ord(c)) for c in value)
        self.string_constants[label] = asm_string
        return label
    
    def track_variable(self, var_name):
        if not var_name.startswith('float_') and not var_name.startswith('str_'):
            self.variables.add(var_name)
        
    