#!/usr/bin/env python3
"""
Diagnóstico completo do ingestion_engine.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def analyze_ingestion_engine():
    """
    Analisa o arquivo ingestion_engine.py para identificar problemas
    """
    print("🔍 DIAGNÓSTICO COMPLETO: ingestion_engine.py")
    print("="*60)
    
    file_path = "c:\\Users\\User\\OneDrive\\Documentos\\Projetos\\Data_Master_2025\\GIT\\dino_2\\dino_sdk\\src\\dino_sdk\\ingestion_engine.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Contar linhas
        lines = content.split('\n')
        total_lines = len(lines)
        print(f"📊 Total de linhas: {total_lines}")
        
        # Procurar métodos duplicados
        save_log_occurrences = []
        create_table_occurrences = []
        
        for i, line in enumerate(lines):
            if "def save_ingestion_log(" in line:
                save_log_occurrences.append(i + 1)
            if "def _create_log_table_if_not_exists(" in line:
                create_table_occurrences.append(i + 1)
        
        print(f"\n🔍 MÉTODOS ENCONTRADOS:")
        print(f"   save_ingestion_log: {len(save_log_occurrences)} ocorrências nas linhas: {save_log_occurrences}")
        print(f"   _create_log_table_if_not_exists: {len(create_table_occurrences)} ocorrências nas linhas: {create_table_occurrences}")
        
        # Verificar se há problema de duplicação
        if len(save_log_occurrences) > 1:
            print(f"\n❌ PROBLEMA CRÍTICO: Método save_ingestion_log DUPLICADO!")
            for i, line_num in enumerate(save_log_occurrences):
                print(f"   {i+1}. Linha {line_num}")
                # Mostrar algumas linhas do contexto
                start_line = max(0, line_num - 2)
                end_line = min(len(lines), line_num + 5)
                for j in range(start_line, end_line):
                    marker = ">>>" if j == line_num - 1 else "   "
                    print(f"   {marker} {j+1:4d}: {lines[j][:80]}...")
                print()
        
        # Verificar importações Unity Catalog
        unity_imports = [i+1 for i, line in enumerate(lines) if "unity" in line.lower()]
        print(f"\n🔍 UNITY CATALOG REFERENCIAS: {len(unity_imports)} linhas")
        
        # Verificar métodos críticos
        critical_methods = [
            "_is_unity_catalog_enabled",
            "_get_log_table_name",
            "_create_log_table_if_not_exists",
            "_save_log_locally",
            "save_ingestion_log"
        ]
        
        print(f"\n🔍 MÉTODOS CRÍTICOS:")
        for method in critical_methods:
            occurrences = [i+1 for i, line in enumerate(lines) if f"def {method}(" in line]
            status = "✅" if len(occurrences) == 1 else ("❌ DUPLICADO" if len(occurrences) > 1 else "❌ MISSING")
            print(f"   {method}: {status} - Linhas: {occurrences}")
        
        # Verificar calls problemáticos
        print(f"\n🔍 CHAMADAS PROBLEMÁTICAS:")
        
        # Verificar _is_unity_catalog_enabled calls
        unity_calls = [i+1 for i, line in enumerate(lines) if "_is_unity_catalog_enabled()" in line]
        print(f"   _is_unity_catalog_enabled() chamado {len(unity_calls)} vezes nas linhas: {unity_calls}")
        
        # Verificar se o método que não deveria usar Unity Catalog está sendo usado
        for i, line_num in enumerate(save_log_occurrences):
            print(f"\n🔍 ANALISANDO save_ingestion_log #{i+1} (linha {line_num}):")
            
            # Pegar o método completo
            method_start = line_num - 1
            method_end = method_start
            indent_level = len(lines[method_start]) - len(lines[method_start].lstrip())
            
            # Encontrar o fim do método
            for j in range(method_start + 1, len(lines)):
                current_line = lines[j].strip()
                if current_line and not current_line.startswith('#'):
                    current_indent = len(lines[j]) - len(lines[j].lstrip())
                    if current_indent <= indent_level and (current_line.startswith('def ') or current_line.startswith('class ')):
                        method_end = j
                        break
            else:
                method_end = len(lines)
            
            method_lines = lines[method_start:method_end]
            method_content = '\n'.join(method_lines)
            
            # Analisar o conteúdo do método
            if "_create_log_table_if_not_exists" in method_content:
                print(f"   ✅ Tenta criar tabela Unity Catalog")
            else:
                print(f"   ❌ NÃO tenta criar tabela Unity Catalog")
                
            if "saveAsTable" in method_content:
                print(f"   ✅ Tenta salvar na tabela Delta")
            else:
                print(f"   ❌ NÃO tenta salvar na tabela Delta")
                
            if "_save_log_locally" in method_content:
                print(f"   ✅ Tem fallback para logging local")
            else:
                print(f"   ❌ NÃO tem fallback para logging local")
        
        return {
            'total_lines': total_lines,
            'save_log_duplicated': len(save_log_occurrences) > 1,
            'save_log_lines': save_log_occurrences,
            'has_unity_methods': len(create_table_occurrences) > 0
        }
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {str(e)}")
        return None

def generate_fix_plan(analysis):
    """
    Gera plano de correção baseado na análise
    """
    print(f"\n" + "="*60)
    print("🔧 PLANO DE CORREÇÃO")
    print("="*60)
    
    if analysis and analysis['save_log_duplicated']:
        print("🎯 PROBLEMA IDENTIFICADO: Métodos save_ingestion_log duplicados")
        print("   - O segundo método só faz logging local")
        print("   - O primeiro método tenta Unity Catalog mas tem bugs")
        print("   - Python usa a ÚLTIMA definição do método")
        
        print(f"\n💡 SOLUÇÃO RECOMENDADA:")
        print(f"   1. Remover o método duplicado (linha {analysis['save_log_lines'][1]})")
        print(f"   2. Corrigir o primeiro método para funcionar corretamente")
        print(f"   3. Garantir que _create_log_table_if_not_exists seja robusto")
        print(f"   4. Implementar fallback funcional")
        
        print(f"\n🔄 ESTRATÉGIA:")
        print(f"   - Remover completamente método duplicado")
        print(f"   - Simplificar lógica Unity Catalog")
        print(f"   - Sempre tentar tabela primeiro, fallback depois")
        print(f"   - Logs detalhados para debug")
    
    return True

if __name__ == "__main__":
    analysis = analyze_ingestion_engine()
    generate_fix_plan(analysis)
    
    print(f"\n" + "="*60)
    print("🎯 PRÓXIMO PASSO: Implementar correção")
    print("="*60)
