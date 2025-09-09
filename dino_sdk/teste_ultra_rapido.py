#!/usr/bin/env python3
"""
Teste ultra rápido - apenas verificar o método
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔍 Testando import...")

try:
    from dino_sdk.ingestion_engine import IngestionEngine
    print("✅ IngestionEngine importado")
    
    if hasattr(IngestionEngine, 'save_ingestion_log'):
        print("✅ save_ingestion_log ENCONTRADO!")
        
        import inspect
        sig = inspect.signature(IngestionEngine.save_ingestion_log)
        print(f"📋 Assinatura: {sig}")
        
        print("🎉 SUCESSO TOTAL - MÉTODO ADICIONADO CORRETAMENTE!")
    else:
        print("❌ save_ingestion_log ainda não encontrado")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
