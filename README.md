# Configuração inicial (Linux)

- Ferramentas de uso: python, venv e PLY
- sudo apt update
- sudo apt install nasm

# Iniciar o ambiente virtual:

- python venv -m compilas
- source compilas/bin/activate (ativar a venv)
- pip install ply
- deactivate (desativar a venv)

# Como executar:

- Iniciar a venv com o PLY e o nasm instalados
- No prompt de comando executar: python main.py `<archive>`
- No lugar de `<archive>` coloque um arquivo (sugestão: algum code.txt dentro de LPMS/)
- Após, para rodar o código assembly x86_64 com o nasm use no terminal os seguintes comandos:
  - nasm -f elf64 -o assmbl.o output.asm; ld assmbl.o -o assmbl; ./assmbl
  - echo $? (apenas caso o código seja para impressão de inteiros, por exemplo, LPMS/code-asm3.txt)

### Observações:

- A geração de código assembly foi testada com os arquivos com o padrão: LPMS/code-asm.txt
