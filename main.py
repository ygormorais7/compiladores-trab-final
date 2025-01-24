import sys
from lexer import Lexer
from parser import Parser
from tac import tacGen
from asm import tac_to_assembly

if len(sys.argv) != 2:
    print("Uso: python main.py <arquivo>")
    sys.exit(1)

# Lê o arquivo de entrada
file_name = sys.argv[1]

with open(file_name, 'r') as file:
    data = file.read()

# Inicializa o analisador léxico e sintático
lexer = Lexer()
lexer.build()

parser = Parser()
parser.build()

# Realiza a análise sintática e gera a árvore sintática
result = parser.parse(data)

# Exibe a saída da análise sintática (opcional)
print(f"Árvore Sintática:\n-=-=-=-=-=-=-=-\n{result}\n-=-=-=-=-=-=-=-\n")

# Gera o código de três endereços (TAC)
generator = tacGen()
visu_tac, tac = generator.process_program(result)
print(f"Código de Três Endereços:\n-=-=-=-=-=-=-=-\n{visu_tac}\n-=-=-=-=-=-=-=-\n")

asm = tac_to_assembly(tac)
print(f"Código Assembly x86_64:\n-=-=-=-=-=-=-=-\n{asm}-=-=-=-=-=-=-=-\n")
with open("output.asm", "w") as f:
    f.write(asm)
