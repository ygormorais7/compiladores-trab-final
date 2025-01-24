def tac_to_assembly(tac_code):
    data_section = "section .data\n"
    data_section += f"    ; Adicionando mensagens padroes do sistema:\n"
    data_section += f"    msg_true db 'true', 10\n    tam_msg_true equ $-msg_true\n"
    data_section += f"    msg_false db 'false', 10\n    tam_msg_false equ $-msg_false\n\n"
    data_section += f"    ; Adicionando variaveis do em codigo especifico:\n"

    bss_section = "section .bss\n"

    text_section = "section .text\nglobal _start\n\n_start:\n"

    exit_label = ".exit:\n    mov rax, 60\n    syscall\n"
    
    operacoes = ["+", "-", "=="]
    
    temp_vars = {}
    labels = {}

    for line in tac_code:
        line = line.strip()
        if not line:
            continue
            
        if any(op in line for op in operacoes):
            value_op = None
            if "+" in line:
                var, expr = map(str.strip, line.split("="))
                op1, op2 = map(str.strip, expr.split("+"))

                bss_section += f"    {var} resq 1\n"

                if op1.isdigit():
                    text_section += f"    mov rax, {op1}\n"
                else:
                    text_section += f"    mov rax, [{op1}]\n"
                    value_op1 = int(temp_vars[op2])

                if op2.isdigit():
                    text_section += f"    add rax, {op2}\n"
                else:
                    text_section += f"    add rax, [{op2}]\n"
                    value_op2 = int(temp_vars[op2])
                    value_op = value_op1 + value_op2

                text_section += f"    mov [{var}], rax\n"
            
            elif "-" in line:
                var, expr = map(str.strip, line.split("="))
                op1, op2 = map(str.strip, expr.split("-"))

                bss_section += f"    {var} resq 1\n"

                if op1.isdigit():
                    text_section += f"    mov rax, {op1}\n"
                else:
                    text_section += f"    mov rax, [{op1}]\n"
                    value_op1 = int(temp_vars[op1])

                if op2.isdigit():
                    text_section += f"    sub rax, {op2}\n"
                else:
                    text_section += f"    sub rax, [{op2}]\n"
                    value_op2 = int(temp_vars[op2])
                    value_op = value_op1 - value_op2

                text_section += f"    mov [{var}], rax\n"

            elif "==" in line:
                var_op1, op2 = map(str.strip, line.split("=="))
                var, op1 = map(str.strip, var_op1.split("="))

                bss_section += f"    {var} resq 1\n"
                
                if op1.isdigit():
                    text_section += f"    mov rax, {op1}\n"
                else:
                    text_section += f"    mov rax, [{op1}]\n"
                    value_op1 = temp_vars[op1]

                if op2.isdigit():
                    text_section += f"    cmp rax, {op2}\n"
                    value_op = op1 == op2
                else:
                    text_section += f"    cmp rax, [{op2}]\n"
                    value_op2 = temp_vars[op2]
                    value_op = value_op1 == value_op2

            temp_vars[var] = value_op
            text_section += f"\n"

        elif "=" in line:
            var, value = map(str.strip, line.split("="))
            if value.isdigit():
                data_section += f"    {var} dq {value}\n"
                temp_vars[var] = value
            elif isinstance(value, str):
                temp_vars[var] = value
            else:
                raise ValueError(f"Operação não suportada: {line}")
        
        elif line.startswith("while"):
            _, condition, _

        elif line.startswith("if"):
            _, condition, _, label = line.split()
            text_section += f"    je .{label}\n"

        elif line.startswith("goto"):
            _, label = line.split()
            text_section += f"    jmp .{label}\n"

        elif line.startswith("L") and ":" in line:
            label = line.replace(":", "")
            labels[label] = True
            text_section += f".{label}:\n"

        elif line.startswith("param"):
            _, param = line.split(maxsplit=1)

            if param not in list(temp_vars.keys()):
                param_name = param.strip('"')

                msg_label = f"msg{len(temp_vars) + len(labels)}"
                data_section += f"    {msg_label} db '{param_name}', 10\n"
                data_section += f"    tam_{msg_label} equ $-{msg_label}\n"

            elif type(temp_vars[param]) == str:
                msg_label = f"msg{len(temp_vars) + len(labels)}"
                data_section += f"    {msg_label} db {temp_vars[param]}, 10\n"
                data_section += f"    tam_{msg_label} equ $-{msg_label}\n"
            
            elif type(temp_vars[param]) == bool and temp_vars[param] == True:
                msg_label = "msg_true"
            else:
                msg_label = "msg_false"
            
        elif line.startswith("call"):
            _, func_name, _ = line.split()
            if func_name == "print":
                
                print()
                if (param in list(temp_vars.keys())) and type(temp_vars[param]) == int:
                    text_section += f"    mov rdi, [{param}]\n"

                elif param not in list(temp_vars.keys()) or type(temp_vars[param]) == str or type(temp_vars[param]) == bool:
                    text_section += f"    mov rax, 1\n"
                    text_section += f"    mov rdi, 1\n"
                    text_section += f"    mov rsi, {msg_label}\n"
                    text_section += f"    mov rdx, tam_{msg_label}\n"
                    text_section += f"    syscall\n\n"

    text_section += "    jmp .exit\n"
    assembly_code = data_section + "\n" + bss_section + "\n" + text_section + "\n" + exit_label
    return assembly_code
