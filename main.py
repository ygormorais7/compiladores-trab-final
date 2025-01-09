from lexer import Lexer

with open('programas.LPMS/code1.txt', 'r') as file:
    data = file.read()

lexer = Lexer()
lexer.build()
lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(f"<{tok.type}, {tok.value}>")
