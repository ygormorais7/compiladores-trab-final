import sys
from lexer import Lexer
from parser import Parser
from tac import tacGen

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
print("Árvore Sintática:")
print(result)

# Gera o código de três endereços (TAC)
generator = tacGen()
tac = generator.generate_code(result)

# Exibe o código de três endereços gerado
print("\nCódigo de Três Endereços (TAC):")
print(tac)
