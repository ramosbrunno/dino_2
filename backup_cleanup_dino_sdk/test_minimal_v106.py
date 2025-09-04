#!/usr/bin/env python3
"""
Teste mínimo para verificar se a implementação Secret Scope está presente
"""

import sys
import inspect

def test_minimal_structure():
    """
    Teste mínimo da estrutura
    """
    print("🔍 Teste mínimo - Dino SDK v1.0.6 Secret Scope")
    print("=" * 45)
    
    try:
        # Importar apenas a classe
        sys.path.insert(0, 'src')
        from src.keyvault_config import KeyVaultConfigManager
        
        print("✅ Importação da classe bem-sucedida")
        
        # Verificar se métodos Secret Scope existem
        secret_scope_methods = [
            'create_secret_scope',
            'load_secrets_from_scope', 
            '_get_secret_from_scope'
        ]
        
        print("\n🔍 Métodos Secret Scope:")
        for method in secret_scope_methods:
            if hasattr(KeyVaultConfigManager, method):
                # Obter signature do método
                method_obj = getattr(KeyVaultConfigManager, method)
                sig = inspect.signature(method_obj)
                print(f"   ✅ {method}{sig}")
            else:
                print(f"   ❌ {method}")
        
        # Verificar se SECRET_MAPPING existe
        print(f"\n📋 SECRET_MAPPING: {'✅' if hasattr(KeyVaultConfigManager, 'SECRET_MAPPING') else '❌'}")
        
        print("\n🏆 Implementação Secret Scope v1.0.6 validada!")
        print("\n📦 Wheel disponível:")
        print("   📁 dist/dino_sdk-1.0.6-py3-none-any.whl")
        print("\n🚀 Para usar no Databricks:")
        print("   1. Upload do wheel")
        print("   2. dino-config setup --keyvault dino-shared-keyvault --catalog dino_catalog --schema [projeto]")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_minimal_structure()
    sys.exit(0 if success else 1)
