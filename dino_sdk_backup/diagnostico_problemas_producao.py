#!/usr/bin/env python3
"""
Correção crítica para os problemas identificados:
1. AttributeError: save_ingestion_log não existe 
2. 0 registros processados
3. Log bonitinho não aparece mais
"""

print("🔧 CORREÇÃO CRÍTICA: Problemas de Produção")
print("="*60)

problems = [
    "❌ AttributeError: 'IngestionEngine' object has no attribute 'save_ingestion_log'",
    "❌ 0 registros processados (era 100k antes)", 
    "❌ Log bonitinho não aparece mais",
    "❌ Execução não finaliza corretamente"
]

print("🎯 PROBLEMAS IDENTIFICADOS:")
for i, problem in enumerate(problems, 1):
    print(f"   {i}. {problem}")

print(f"\n💡 CAUSAS PROVÁVEIS:")
print(f"   1. Método save_ingestion_log com problema de indentação/encoding")
print(f"   2. Wheel 2.6.4 não foi instalado no ambiente de produção")
print(f"   3. AutoLoader não está processando dados corretamente")
print(f"   4. DataSaver com problema na contagem")

print(f"\n🔧 SOLUÇÕES NECESSÁRIAS:")
solutions = [
    "1. Verificar/corrigir método save_ingestion_log",
    "2. Corrigir contagem de registros no AutoLoader",
    "3. Restaurar log estruturado bonitinho",
    "4. Garantir que wheel 2.6.4 seja usado",
    "5. Testar funcionalidade completa"
]

for solution in solutions:
    print(f"   {solution}")

print(f"\n🚀 IMPLEMENTANDO CORREÇÕES...")

# Verificar se há problemas de encoding/indentação no arquivo
file_path = "c:\\Users\\User\\OneDrive\\Documentos\\Projetos\\Data_Master_2025\\GIT\\dino_2\\dino_sdk\\src\\dino_sdk\\ingestion_engine.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    # Procurar o método save_ingestion_log
    save_log_lines = []
    for i, line in enumerate(lines):
        if "def save_ingestion_log(" in line:
            save_log_lines.append({
                'line_num': i + 1,
                'content': line,
                'indent': len(line) - len(line.lstrip()),
                'starts_with_spaces': line.startswith('    '),
                'starts_with_tabs': line.startswith('\t')
            })
    
    print(f"\n🔍 ANÁLISE DO MÉTODO save_ingestion_log:")
    if save_log_lines:
        for i, info in enumerate(save_log_lines):
            print(f"   {i+1}. Linha {info['line_num']}: {info['content'][:50]}...")
            print(f"       Indentação: {info['indent']} caracteres")
            print(f"       Espaços: {info['starts_with_spaces']}, Tabs: {info['starts_with_tabs']}")
    else:
        print("   ❌ MÉTODO NÃO ENCONTRADO!")
    
    # Procurar chamadas do método
    calls = []
    for i, line in enumerate(lines):
        if "self.save_ingestion_log(" in line:
            calls.append({
                'line_num': i + 1,
                'content': line.strip(),
                'context': f"Linhas {max(1, i-1)}-{min(len(lines), i+3)}"
            })
    
    print(f"\n🔍 CHAMADAS DO MÉTODO:")
    if calls:
        for call in calls:
            print(f"   Linha {call['line_num']}: {call['content']}")
    else:
        print("   ❌ NENHUMA CHAMADA ENCONTRADA!")
    
    # Verificar estrutura de classe
    class_lines = [i+1 for i, line in enumerate(lines) if line.startswith('class ')]
    print(f"\n🔍 CLASSES ENCONTRADAS:")
    for class_line in class_lines[:5]:  # Primeiras 5 classes
        class_name = lines[class_line-1].split('(')[0].replace('class ', '').strip(':')
        print(f"   Linha {class_line}: {class_name}")
    
    # Verificar se método está dentro de alguma classe
    if save_log_lines:
        method_line = save_log_lines[0]['line_num']
        current_class = None
        
        # Encontrar a classe que contém o método
        for i in range(method_line - 1, -1, -1):
            line = lines[i]
            if line.startswith('class '):
                current_class = line.split('(')[0].replace('class ', '').strip(':')
                break
        
        print(f"\n🔍 CONTEXTO DO MÉTODO:")
        print(f"   Método save_ingestion_log na linha {method_line}")
        print(f"   Pertence à classe: {current_class or 'NENHUMA (PROBLEMA!)'}")
        
        if current_class != 'IngestionEngine':
            print(f"   ❌ ERRO: Método deveria estar na classe IngestionEngine!")
    
except Exception as e:
    print(f"❌ Erro na análise: {str(e)}")

print(f"\n" + "="*60)
print("🎯 PRÓXIMOS PASSOS: Aplicar correções identificadas")
print("="*60)
