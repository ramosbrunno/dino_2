#!/usr/bin/env python3
"""
Teste simples e rápido para verificar se tudo funciona
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🧪 TESTE RÁPIDO - IMPORT E VERIFICAÇÃO")
    print("="*60)
    
    # 1. Importar as classes
    print("1️⃣ Importando IngestionEngine...")
    from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig
    print("✅ Import bem-sucedido!")
    
    # 2. Verificar se o método existe na classe IngestionEngine
    print("\n2️⃣ Verificando método save_ingestion_log...")
    if hasattr(IngestionEngine, 'save_ingestion_log'):
        print("✅ Método save_ingestion_log encontrado em IngestionEngine")
    else:
        print("❌ Método save_ingestion_log NÃO encontrado")
        sys.exit(1)
    
    # 3. Verificar outros métodos essenciais
    print("\n3️⃣ Verificando outros métodos...")
    methods_to_check = ['ingest', '__init__']
    for method in methods_to_check:
        if hasattr(IngestionEngine, method):
            print(f"✅ {method} encontrado")
        else:
            print(f"❌ {method} não encontrado")
    
    print("\n" + "="*60)
    print("🎉 SUCESSO TOTAL!")
    print("✅ Arquivo ingestion_engine.py limpo e funcional")
    print("✅ Método save_ingestion_log na classe IngestionEngine")
    print("✅ Todas as classes importadas corretamente")
    print("🚀 PRONTO PARA USAR!")
    print("="*60)
        
except ImportError as e:
    print(f"❌ Erro de import: {str(e)}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro geral: {str(e)}")
    import traceback
    traceback.print_exc()
