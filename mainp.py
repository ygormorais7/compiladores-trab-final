import sys
from lexer import Lexer
from parser import Parser

if len(sys.argv) != 2:
    sys.exit(1)

dados = sys.argv[1]
with open(f'{dados}', 'r') as file:
    data = file.read()

lexer = Lexer()
lexer.build()
lexer.input(data)

parser = Parser()
parser.build()

result = parser.parse(data)
print(result)
print(parser.lexer.symbolTable)
