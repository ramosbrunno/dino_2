#!/usr/bin/env python3
"""
Script de emergência para limpar o arquivo ingestion_engine.py
Remove todo código órfão entre o final da classe IngestionLogManager e o início da classe IngestionEngine
"""

import os

# Caminho do arquivo
file_path = r"c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\src\dino_sdk\ingestion_engine.py"

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar onde termina a classe IngestionLogManager (última linha válida)
end_log_manager = -1
for i, line in enumerate(lines):
    if 'self.logger.error(f"❌ Erro no log local de entrada: {str(e)}")' in line:
        end_log_manager = i
        break

# Encontrar onde começa a classe IngestionEngine (primeira linha válida)
start_engine = -1
for i, line in enumerate(lines):
    if line.strip() == 'class IngestionEngine:' and i > end_log_manager:
        start_engine = i
        break

print(f"End IngestionLogManager: linha {end_log_manager}")
print(f"Start IngestionEngine: linha {start_engine}")

if end_log_manager != -1 and start_engine != -1:
    # Criar arquivo limpo
    clean_lines = []
    
    # Adicionar tudo até o final da classe IngestionLogManager
    clean_lines.extend(lines[:end_log_manager + 1])
    
    # Adicionar linhas em branco para separação
    clean_lines.append('\n\n')
    
    # Adicionar tudo a partir da classe IngestionEngine
    clean_lines.extend(lines[start_engine:])
    
    # Escrever arquivo limpo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✅ Arquivo limpo! Removidas {start_engine - end_log_manager - 1} linhas órfãs")
    print(f"Linhas antes: {len(lines)}")
    print(f"Linhas depois: {len(clean_lines)}")
else:
    print("❌ Não conseguiu encontrar os pontos de referência")
