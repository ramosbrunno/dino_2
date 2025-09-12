#!/usr/bin/env python3
"""
Teste de importações do DINO SDK v1.2.0
Testa todas as classes principais após a refatoração
"""

def test_imports():
    """Testa todas as importações principais do DINO SDK"""
    
    print("🧪 DINO SDK v1.2.0 - Teste de Importações")
    print("=" * 50)
    
    # Testes de importação
    tests = []
    
    # Teste 1: Importações principais do __init__.py
    try:
        from src import (
            configure_dino_sdk,
            validate_dino_config, 
            show_dino_config,
            quick_setup,
            setup_with_azure_sql
        )
        print("✅ Funções de configuração programática importadas")
        tests.append(("Configuração Programática", True))
    except Exception as e:
        print(f"❌ Erro nas funções de configuração: {e}")
        tests.append(("Configuração Programática", False))
    
    # Teste 2: Função de criação de schema
    try:
        from src import create_unity_catalog_schema
        print("✅ Função create_unity_catalog_schema importada")
        tests.append(("Criação de Schema", True))
    except Exception as e:
        print(f"❌ Erro na função de criação de schema: {e}")
        tests.append(("Criação de Schema", False))
    
    # Teste 3: Engines principais
    try:
        from src import get_ingestion_engine
        IngestionEngine = get_ingestion_engine()
        print("✅ IngestionEngine importado")
        tests.append(("IngestionEngine", True))
    except Exception as e:
        print(f"❌ Erro no IngestionEngine: {e}")
        tests.append(("IngestionEngine", False))
    
    try:
        from src import get_genie_assistant
        GenieAssistant = get_genie_assistant()
        print("✅ GenieAssistant importado")
        tests.append(("GenieAssistant", True))
    except Exception as e:
        print(f"❌ Erro no GenieAssistant: {e}")
        tests.append(("GenieAssistant", False))
    
    try:
        from src import get_workflow_manager
        WorkflowManager = get_workflow_manager()
        print("✅ WorkflowManager importado")
        tests.append(("WorkflowManager", True))
    except Exception as e:
        print(f"❌ Erro no WorkflowManager: {e}")
        tests.append(("WorkflowManager", False))
    
    try:
        from src import get_job_manager
        JobManager = get_job_manager()
        print("✅ JobManager importado")
        tests.append(("JobManager", True))
    except Exception as e:
        print(f"❌ Erro no JobManager: {e}")
        tests.append(("JobManager", False))
    
    # Teste 4: Módulos diretos
    try:
        from src.config_manager import get_config_manager
        print("✅ ConfigManager importado")
        tests.append(("ConfigManager", True))
    except Exception as e:
        print(f"❌ Erro no ConfigManager: {e}")
        tests.append(("ConfigManager", False))
    
    # Teste 5: Verificar se KeyVault foi removido
    try:
        from src import DinoKeyVaultConfig
        print("❌ DinoKeyVaultConfig ainda existe (deveria ter sido removido)")
        tests.append(("Remoção KeyVault", False))
    except ImportError:
        print("✅ DinoKeyVaultConfig removido corretamente")
        tests.append(("Remoção KeyVault", True))
    except Exception as e:
        print(f"❌ Erro inesperado ao verificar KeyVault: {e}")
        tests.append(("Remoção KeyVault", False))
    
    # Resultados
    print("\n📊 RESULTADOS DOS TESTES:")
    print("-" * 30)
    
    success_count = 0
    total_count = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:<25} {status}")
        if success:
            success_count += 1
    
    print("-" * 30)
    print(f"Total: {success_count}/{total_count} testes passaram")
    
    if success_count == total_count:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ DINO SDK v1.2.0 está pronto para uso!")
    else:
        print("⚠️  Alguns testes falharam")
        print("🔧 Verifique os erros acima")
    
    return success_count == total_count


if __name__ == "__main__":
    test_imports()
