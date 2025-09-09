#!/usr/bin/env python3
"""
Teste para verificar detecção do Unity Catalog e correção do logging
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_unity_catalog_detection():
    """
    Testa a detecção do Unity Catalog
    """
    print("🔍 DIAGNÓSTICO: Unity Catalog Detection")
    print("="*60)
    
    # Simular PySpark Session
    class MockSparkSQL:
        def __init__(self, unity_enabled=False):
            self.unity_enabled = unity_enabled
            
        def sql(self, query):
            if "SHOW CATALOGS" in query:
                if self.unity_enabled:
                    return MockResult([["hive_metastore"], ["data_master_dev_dbw"]])
                else:
                    raise Exception("Unity Catalog not enabled")
            return MockResult([])
            
        def collect(self):
            return []
    
    class MockResult:
        def __init__(self, data):
            self.data = data
            
        def collect(self):
            return self.data
    
    class MockSparkSession:
        def __init__(self, unity_enabled=False):
            self.sql = MockSparkSQL(unity_enabled).sql
    
    # Teste com Unity Catalog HABILITADO
    print("\n1️⃣ Teste com Unity Catalog HABILITADO:")
    mock_spark_enabled = MockSparkSession(unity_enabled=True)
    
    try:
        result = mock_spark_enabled.sql("SHOW CATALOGS")
        catalogs = result.collect()
        print(f"   ✅ SHOW CATALOGS funcionou: {len(catalogs)} catálogos encontrados")
        print(f"   📋 Catálogos: {catalogs}")
        unity_enabled = True
    except Exception as e:
        print(f"   ❌ SHOW CATALOGS falhou: {str(e)}")
        unity_enabled = False
        
    print(f"   🎯 Resultado: Unity Catalog = {'HABILITADO' if unity_enabled else 'DESABILITADO'}")
    
    # Teste com Unity Catalog DESABILITADO
    print("\n2️⃣ Teste com Unity Catalog DESABILITADO:")
    mock_spark_disabled = MockSparkSession(unity_enabled=False)
    
    try:
        result = mock_spark_disabled.sql("SHOW CATALOGS")
        catalogs = result.collect()
        print(f"   ✅ SHOW CATALOGS funcionou: {len(catalogs)} catálogos")
        unity_enabled = True
    except Exception as e:
        print(f"   ❌ SHOW CATALOGS falhou: {str(e)}")
        unity_enabled = False
        
    print(f"   🎯 Resultado: Unity Catalog = {'HABILITADO' if unity_enabled else 'DESABILITADO'}")
    
    # Agora testar o método real da IngestionEngine
    print("\n3️⃣ Teste do método _is_unity_catalog_enabled():")
    
    try:
        from dino_sdk.ingestion_engine import IngestionEngine
        
        # Criar engine com mock
        class MockLogger:
            def warning(self, msg): print(f"   ⚠️ Warning: {msg}")
            def info(self, msg): print(f"   ℹ️ Info: {msg}")
            def error(self, msg): print(f"   ❌ Error: {msg}")
        
        engine = IngestionEngine(spark=None, logger=MockLogger())
        
        # Testar com Unity Catalog simulado como habilitado
        engine.spark = mock_spark_enabled
        result_enabled = engine._is_unity_catalog_enabled()
        print(f"   ✅ Com Unity habilitado: {result_enabled}")
        
        # Testar com Unity Catalog simulado como desabilitado  
        engine.spark = mock_spark_disabled
        result_disabled = engine._is_unity_catalog_enabled()
        print(f"   ❌ Com Unity desabilitado: {result_disabled}")
        
        print(f"\n🔧 DIAGNÓSTICO:")
        print(f"   - Se Unity Catalog estiver habilitado → Log vai para TABELA")
        print(f"   - Se Unity Catalog estiver desabilitado → Log vai apenas LOCAL")
        print(f"   - Problema: Unity Catalog pode estar sendo detectado como desabilitado")
        
    except ImportError as e:
        print(f"   ❌ Erro ao importar IngestionEngine: {e}")
        
def test_force_unity_catalog():
    """
    Testa forçar o Unity Catalog para sempre usar tabela de log
    """
    print("\n\n🔧 SOLUÇÃO: Forçar Unity Catalog Habilitado")
    print("="*60)
    
    print("💡 OPÇÕES DE CORREÇÃO:")
    print("   1. Modificar _is_unity_catalog_enabled() para sempre retornar True")
    print("   2. Adicionar parâmetro force_unity_catalog=True no construtor")  
    print("   3. Detectar Unity Catalog por outros meios (ex: variáveis ambiente)")
    print("   4. Sempre tentar salvar na tabela primeiro, fallback para local se falhar")
    
    print("\n🎯 RECOMENDAÇÃO: Opção 4 - Tentar tabela primeiro")
    print("   - Sempre tenta salvar na tabela de log")
    print("   - Se falhar, usa logging local como backup")
    print("   - Mais robusto e funciona em qualquer ambiente")

if __name__ == "__main__":
    test_unity_catalog_detection()
    test_force_unity_catalog()
    
    print("\n" + "="*60)
    print("🎯 PRÓXIMO PASSO: Implementar correção para sempre usar tabela de log")
    print("="*60)
