#!/usr/bin/env python3
"""
Fix definitivo - reconstrói a estrutura correta do arquivo
"""

import os

file_path = r"c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\src\dino_sdk\ingestion_engine.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar onde começa a classe IngestionEngine legítima
# Vamos procurar por uma assinatura única que sabemos estar correta
target = '''class IngestionEngine:
    """
    Motor principal de ingestão de dados.
    """
    
    def __init__(self, spark: SparkSession = None):'''

start_pos = content.find(target)
if start_pos == -1:
    print("❌ Não encontrou o início da classe IngestionEngine")
    exit(1)

# Encontrar onde termina a classe IngestionLogManager
# Vamos procurar pela linha de fechamento do último método
log_manager_end = 'self.logger.error(f"❌ Erro no log local de entrada: {str(e)}")'
end_pos = content.find(log_manager_end)
if end_pos == -1:
    print("❌ Não encontrou o final da classe IngestionLogManager") 
    exit(1)

# Encontrar o final da linha
end_line_pos = content.find('\n', end_pos)
if end_line_pos == -1:
    end_line_pos = end_pos + len(log_manager_end)

# Criar conteúdo limpo
clean_content = content[:end_line_pos] + '\n\n\n' + content[start_pos:]

# Escrever arquivo limpo
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("✅ Arquivo limpo definitivamente!")
print(f"Posição fim IngestionLogManager: {end_line_pos}")
print(f"Posição início IngestionEngine: {start_pos}")
print(f"Removidos {start_pos - end_line_pos - 3} caracteres de lixo")
