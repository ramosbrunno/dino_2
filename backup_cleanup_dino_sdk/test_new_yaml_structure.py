#!/usr/bin/env python3
"""
Demonstração da nova estrutura YAML simplificada
"""

from src.keyvault_config import KeyVaultConfigManager

def test_new_yaml_structure():
    """Testa a nova estrutura YAML simplificada"""
    
    print("🧪 Testando nova estrutura YAML simplificada")
    print("=" * 60)
    
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
    
    # Gerar nova estrutura YAML
    try:
        yaml_content = mgr.generate_config_yaml()
        print("✅ YAML gerado com sucesso!")
        print()
        print("📄 Nova estrutura YAML:")
        print("-" * 40)
        print(yaml_content)
        
        print("\n🎯 Características da nova estrutura:")
        print("   🔐 Apenas secrets específicos incluídos ({{SECRET:spn-client-id}})")
        print("   📁 Paths organizados por projeto: /{project_name}/{schema}/raw/")
        print("   🛡️ Secret scope por projeto: {project_name}-scope")
        print("   📊 Configurações específicas do projeto integradas")
        print("   ⚡ Estrutura simplificada e focada")
        
    except Exception as e:
        print(f"❌ Erro ao gerar YAML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_yaml_structure()
