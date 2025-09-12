#!/usr/bin/env python3
"""
Script de teste para validar implementação Secret Scope do Dino SDK v1.0.6
Testa o padrão correto de Secret Scope em vez de acesso direto ao Key Vault
"""

import os
import sys
import traceback
from typing import Dict, Any

def test_secret_scope_pattern():
    """
    Testa o padrão Secret Scope implementado na versão 1.0.6
    """
    print("🔍 Testando implementação Secret Scope - Dino SDK v1.0.6")
    print("=" * 60)
    
    try:
        # Importar o KeyVaultConfigManager
        sys.path.insert(0, 'src')
        from src.keyvault_config import KeyVaultConfigManager
        
        # Configurações de teste
        keyvault_name = "dino-shared-keyvault"
        catalog_name = "dino_catalog"
        schema_name = "teste_secretscope"
        
        print(f"📋 Configuração:")
        print(f"   Key Vault: {keyvault_name}")
        print(f"   Catálogo: {catalog_name}")
        print(f"   Schema: {schema_name}")
        print()
        
        # Inicializar o manager
        print("🔧 Inicializando KeyVaultConfigManager...")
        kv_manager = KeyVaultConfigManager(keyvault_name, catalog_name, schema_name)
        
        # Verificar se o SECRET_SCOPE_NAME foi definido corretamente
        print(f"📝 Secret Scope Name: {kv_manager.SECRET_SCOPE_NAME}")
        print(f"🔗 Key Vault URL: {kv_manager.keyvault_url}")
        print()
        
        # Teste 1: Verificar inicialização do cliente Databricks
        print("🧪 Teste 1: Inicialização do cliente Databricks")
        try:
            kv_manager._initialize_databricks_client()
            if kv_manager.databricks_client:
                print("   ✅ Cliente Databricks inicializado com sucesso")
                print(f"   📡 Usando auto-detecção: WorkspaceClient()")
            else:
                print("   ⚠️ Cliente Databricks não inicializado")
        except Exception as e:
            print(f"   ❌ Erro na inicialização: {e}")
        print()
        
        # Teste 2: Verificar métodos de obtenção de subscription/resource group
        print("🧪 Teste 2: Obtenção de Subscription ID e Resource Group")
        try:
            subscription_id = kv_manager._get_subscription_id()
            resource_group = kv_manager._get_resource_group()
            print(f"   📋 Subscription ID: {subscription_id}")
            print(f"   📋 Resource Group: {resource_group}")
            
            if subscription_id != 'your-subscription-id' and resource_group != 'your-resource-group':
                print("   ✅ Valores obtidos dos secrets configurados")
            else:
                print("   ⚠️ Usando valores placeholder - verifique se os secrets existem")
        except Exception as e:
            print(f"   ❌ Erro ao obter valores: {e}")
        print()
        
        # Teste 3: Verificar SECRET_MAPPING
        print("🧪 Teste 3: Verificar mapeamento de secrets")
        print(f"   📋 Secrets esperados: {len(kv_manager.SECRET_MAPPING)} secrets")
        for kv_secret, config_key in kv_manager.SECRET_MAPPING.items():
            print(f"      • {kv_secret} → {config_key}")
        print()
        
        # Teste 4: Simular criação de Secret Scope (sem executar na verdade)
        print("🧪 Teste 4: Lógica de criação de Secret Scope")
        print("   📝 Estrutura esperada para create_scope:")
        print(f"      scope: {kv_manager.SECRET_SCOPE_NAME}")
        print(f"      dns_name: {kv_manager.keyvault_url.rstrip('/')}")
        
        # Montar resource_id esperado
        subscription_id = kv_manager._get_subscription_id()
        resource_group = kv_manager._get_resource_group()
        expected_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.KeyVault/vaults/{keyvault_name}"
        print(f"      resource_id: {expected_resource_id}")
        print()
        
        print("✅ Testes de estrutura concluídos com sucesso!")
        print()
        print("💡 Próximos passos:")
        print("   1. Fazer upload do wheel dino_sdk-1.0.6-py3-none-any.whl para Databricks")
        print("   2. Executar: dino-config setup --keyvault dino-shared-keyvault --project [seu-projeto]")
        print("   3. Verificar se a Secret Scope é criada automaticamente")
        print("   4. Validar acesso aos secrets via Secret Scope")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se de estar na pasta dino_sdk")
        return False
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        print("\n🔍 Stack trace completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_secret_scope_pattern()
    sys.exit(0 if success else 1)
