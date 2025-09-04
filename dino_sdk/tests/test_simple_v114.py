#!/usr/bin/env python3
"""
🧪 Teste Simples - DINO SDK v1.1.4
Verifica apenas importações e inicialização básica
"""

def simple_test():
    """Teste simples e rápido"""
    
    print("🧪 TESTE SIMPLES DINO SDK v1.1.4")
    print("=" * 40)
    
    # Teste 1: Importações básicas
    print("\n1️⃣ Testando importações básicas...")
    try:
        import src.keyvault_config
        import src.databricks_sdk_auth_v114
        print("   ✅ Módulos importados")
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # Teste 2: Funções principais
    print("\n2️⃣ Testando funções principais...")
    try:
        from src.keyvault_config import get_notebook_context
        print("   ✅ get_notebook_context disponível")
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # Teste 3: Classe principal
    print("\n3️⃣ Testando classe principal...")
    try:
        from src.keyvault_config import KeyVaultConfigManager
        print("   ✅ KeyVaultConfigManager disponível")
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return
    
    print("\n✅ TODOS OS TESTES BÁSICOS PASSARAM!")
    print("📝 Para teste completo em Databricks:")
    print("   pip install dist/dino_sdk-1.1.4-py3-none-any.whl --force-reinstall")
    print("\n🎯 v1.1.4 pronta para deploy!")

if __name__ == "__main__":
    simple_test()
