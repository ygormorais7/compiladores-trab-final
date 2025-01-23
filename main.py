import sys
from lexer import Lexer
from parser import Parser
from tac import tacGen
from assembly import TACtoAssembly

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
print("Árvore Sintática:\n",result)

# Gera o código de três endereços (TAC)
generator = tacGen()
tac = generator.process_program(result)
print("\nTAC:")
print(tac)

# Traduz o TAC para Assembly
assembly_generator = TACtoAssembly()
tac_lines = tac.split("\n")  # Divide o TAC em linhas para passar ao tradutor
assembly_code = assembly_generator.translate(tac_lines)

# Exibe o código Assembly gerado
print("\nCódigo Assembly:")
print(assembly_code)
