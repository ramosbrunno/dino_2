#!/usr/bin/env python3
"""
DINO SDK v1.0.3 - Instalação Incremental no Databricks
Estratégia: começar com dependências mínimas e adicionar conforme necessário
"""

def install_and_test():
    """Instalação incremental do Dino SDK"""
    
    print("🦕 DINO SDK v1.0.3 - INSTALAÇÃO INCREMENTAL")
    print("=" * 60)
    
    print("\n📦 FASE 1: Dependências mínimas (já incluídas no wheel)")
    print("   - click>=8.0.0")
    print("   - pyyaml>=6.0") 
    print("   - loguru>=0.7.0")
    print("   - requests>=2.28.0")
    
    print("\n🔧 FASE 2: Comandos para executar no Databricks")
    print("=" * 40)
    
    print("\n# 1. LIMPEZA COMPLETA")
    print("%pip cache purge")
    print("%pip uninstall dino-sdk -y")
    
    print("\n# 2. INSTALAÇÃO MINIMAL")
    print("%pip install --force-reinstall --no-cache-dir /path/to/dino_sdk-1.0.3-py3-none-any.whl")
    
    print("\n# 3. RESTART OBRIGATÓRIO")
    print("dbutils.library.restartPython()")
    
    print("\n# 4. TESTE INICIAL (deve funcionar)")
    print("%sh dino-config --help")
    
    print("\n# 5. TESTE DE DIAGNÓSTICO")
    print("%run test_deps.py")
    
    print("\n# 6. SE O DIAGNÓSTICO MOSTRAR FALTA DE DATABRICKS-SDK:")
    print("# (No Databricks esse comando deve estar disponível)")
    print("%pip install databricks-sdk")
    
    print("\n# 7. SE O DIAGNÓSTICO MOSTRAR FALTA DE AZURE LIBS:")
    print("# (No Databricks essas libs podem não estar disponíveis)")
    print("%pip install azure-keyvault-secrets azure-identity")
    
    print("\n# 8. RESTART APÓS ADICIONAR DEPENDÊNCIAS")
    print("dbutils.library.restartPython()")
    
    print("\n# 9. TESTE FINAL")
    print("%sh dino-config setup --project-name data-master --keyvault-name data-master-dev-akv-1g67 --catalog-name data_master_dev_dbw --schema-name sandbox --project-spn-id 3cef52b5-c984-4635-9dde-636ca35ad4b3")
    
    print("\n🎯 ESTRATÉGIA:")
    print("   1. Wheel v1.0.3 tem APENAS dependências básicas")
    print("   2. Importações Azure/Databricks são 100% lazy")
    print("   3. Erro aparece só quando tentar usar as funções")
    print("   4. Adicionar dependências específicas só quando necessário")
    
    print("\n💡 BENEFÍCIOS:")
    print("   ✅ Comando dino-config --help sempre funciona")
    print("   ✅ Não há erro de importação no início")
    print("   ✅ Instalação limpa e controlada")
    print("   ✅ Diagnóstico identifica exatamente o que falta")
    
    print("\n" + "=" * 60)
    print("📋 ARQUIVOS NECESSÁRIOS:")
    print("   - dino_sdk-1.0.3-py3-none-any.whl")
    print("   - test_deps.py")
    print("=" * 60)

if __name__ == "__main__":
    install_and_test()
