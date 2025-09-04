#!/usr/bin/env python3
"""
Teste da geração de YAML multi-projeto
"""

from src.keyvault_config import KeyVaultConfigManager
import json

def test_yaml_generation():
    """Testa a geração do YAML para múltiplos projetos"""
    
    print("🧪 Testando geração de YAML multi-projeto")
    print("=" * 50)
    
    # Criar instância do manager
    mgr = KeyVaultConfigManager(
        keyvault_name='data-master-dev-akv-1g67',
        catalog_name='data_master_dev_dbw',
        schema_name='bronze',
        project_spn_id='3cef52b5-c984-4635-9dde-636ca35ad4b3'
    )
    
    print(f"📊 Schema: {mgr.schema_name}")
    print(f"🏢 Projeto: {mgr.project_name}")
    print(f"🔐 Key Vault: {mgr.keyvault_name}")
    print()
    
    # Gerar configuração YAML
    try:
        config_yaml = mgr.generate_config_yaml()
        print("✅ YAML gerado com sucesso!")
        print()
        print("📄 Conteúdo do YAML:")
        print("-" * 30)
        print(config_yaml)
        
    except Exception as e:
        print(f"❌ Erro ao gerar YAML: {e}")

if __name__ == "__main__":
    test_yaml_generation()
