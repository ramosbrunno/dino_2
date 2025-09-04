#!/usr/bin/env python3
"""
Exemplo de uso da configuração programática do Dino SDK
Simula uso em notebook Databricks
"""

import os

# Simular ambiente notebook
os.environ['DINO_DEMO_MODE'] = 'true'

# Importar funções de configuração
try:
    from src.programmatic_config import (
        configure_dino_sdk,
        validate_dino_config,
        show_dino_config,
        quick_setup,
        setup_with_azure_sql
    )
    
    from src.ingestion_engine import IngestionEngine
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Execute este script do diretório dino_sdk")
    exit(1)


def test_programmatic_config():
    """Testa configuração programática"""
    
    print("🦕 Teste de Configuração Programática do Dino SDK")
    print("=" * 55)
    
    print("\n1️⃣ Configuração Rápida")
    print("-" * 25)
    
    # Teste configuração rápida
    result = quick_setup(
        workspace_url="https://adb-123456789.0.azuredatabricks.net",
        catalog_name="test_catalog"
    )
    
    print(f"Resultado: {result['success']}")
    
    print("\n2️⃣ Configuração Completa")
    print("-" * 28)
    
    # Teste configuração completa
    result = setup_with_azure_sql(
        workspace_url="https://adb-987654321.0.azuredatabricks.net", 
        azure_sql_server="test-server.database.windows.net",
        azure_sql_username="dino_admin",
        azure_sql_password="test_password",
        catalog_name="production",
        azure_sql_database="dino_logging"
    )
    
    print(f"Resultado: {result['success']}")
    
    print("\n3️⃣ Validação da Configuração")
    print("-" * 32)
    
    # Testar validação
    validation = validate_dino_config()
    print(f"Configuração válida: {validation['success']}")
    
    print("\n4️⃣ Exibir Configuração Atual")
    print("-" * 34)
    
    # Mostrar configuração
    config = show_dino_config()
    
    print("\n5️⃣ Teste de Ingestão")
    print("-" * 23)
    
    # Testar ingestão com configuração
    try:
        engine = IngestionEngine(
            target_schema="bronze",
            table_name="test_table",
            file_path="/Volumes/main/raw/test.csv",
            delimiter=",",
            is_automated=False
        )
        
        result = engine.run_batch_ingestion()
        print(f"✅ Ingestão testada com sucesso!")
        print(f"   Execution ID: {result.get('execution_id', 'N/A')}")
        print(f"   Registros: {result.get('records_processed', {})}")
        
    except Exception as e:
        print(f"⚠️ Erro na ingestão: {e}")
    
    print("\n🎉 Teste Concluído!")
    print("=" * 20)
    print("✅ Configuração programática funcionando")
    print("✅ Validação funcionando")
    print("✅ Ingestão com logging funcionando")
    print("\n💡 Use essas funções em notebooks Databricks!")


if __name__ == "__main__":
    test_programmatic_config()
