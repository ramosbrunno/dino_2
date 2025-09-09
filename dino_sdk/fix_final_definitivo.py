#!/usr/bin/env python3
"""
Fix final - remove definitivamente a classe IngestionEngine órfã (linha 1364)
e mantém apenas a legítima (linha 1467+)
"""

import os

file_path = r"c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\src\dino_sdk\ingestion_engine.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar onde termina a classe IngestionLogManager (linha 1361)
end_log_manager = -1
for i, line in enumerate(lines):
    if 'self.logger.error(f"❌ Erro no log local de entrada: {str(e)}")' in line:
        end_log_manager = i
        break

# Encontrar onde começa a classe IngestionEngine legítima (linha 1467)
start_engine_real = -1
for i, line in enumerate(lines):
    if i > 1460 and line.strip() == 'class IngestionEngine:':
        # Verificar se a próxima linha contém a docstring correta
        if i + 1 < len(lines) and 'Motor principal de ingestão de dados' in lines[i + 2]:
            start_engine_real = i
            break

print(f"Fim IngestionLogManager: linha {end_log_manager + 1}")
print(f"Início IngestionEngine real: linha {start_engine_real + 1}")

if end_log_manager != -1 and start_engine_real != -1:
    # Criar arquivo limpo
    clean_lines = []
    
    # Adicionar tudo até o final da classe IngestionLogManager
    clean_lines.extend(lines[:end_log_manager + 1])
    
    # Adicionar separação
    clean_lines.append('\n\n')
    
    # Adicionar a classe IngestionEngine real
    clean_lines.extend(lines[start_engine_real:])
    
    # Escrever arquivo limpo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✅ ARQUIVO LIMPO DEFINITIVAMENTE!")
    print(f"Removidas {start_engine_real - end_log_manager - 1} linhas órfãs")
    print(f"Linhas antes: {len(lines)}")
    print(f"Linhas depois: {len(clean_lines)}")
else:
    print("❌ Não conseguiu encontrar os pontos de referência")
    print(f"end_log_manager: {end_log_manager}")
    print(f"start_engine_real: {start_engine_real}")
