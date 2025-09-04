#!/usr/bin/env python3
"""
Dino SDK - Exemplo de Configuração com Azure Key Vault
Demonstra como configurar o Dino SDK usando Azure Key Vault e Secret Scopes
"""

import os
import sys

# Adicionar o src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.keyvault_config import KeyVaultConfigManager, validate_keyvault_config


def exemplo_configuracao_keyvault():
    """
    Exemplo de configuração completa com Key Vault
    """
    print("🦕 Dino SDK - Exemplo de Configuração Key Vault")
    print("=" * 55)
    
    # Configurações de exemplo
    keyvault_name = "dino-keyvault-dev"
    project_name = "vendas_analytics"
    project_spn_id = "12345678-abcd-1234-efgh-123456789012"
    
    print(f"🔐 Key Vault: {keyvault_name}")
    print(f"📁 Projeto: {project_name}")
    print(f"🔑 SPN Projeto: {project_spn_id}")
    print()
    
    # Modo demo para não precisar de credenciais reais
    os.environ['DINO_DEMO_MODE'] = 'true'
    
    try:
        # 1. Validar configuração do Key Vault
        print("🔍 Etapa 1: Validando configuração Key Vault...")
        validation_result = validate_keyvault_config(keyvault_name, project_name)
        
        if validation_result['success']:
            print("✅ Validação bem-sucedida")
        else:
            print("⚠️ Problemas na validação (continuando em modo demo)")
        
        print()
        
        # 2. Criar gerenciador de configuração
        print("⚙️ Etapa 2: Criando gerenciador de configuração...")
        kv_manager = KeyVaultConfigManager(
            keyvault_name=keyvault_name,
            project_name=project_name,
            project_spn_id=project_spn_id
        )
        print("✅ Gerenciador criado")
        print()
        
        # 3. Configuração completa
        print("🚀 Etapa 3: Executando configuração completa...")
        result = kv_manager.setup_complete_configuration()
        
        if result['success']:
            print("✅ Configuração completa concluída!")
            print("\n📋 Resumo da configuração:")
            for step in result['steps']:
                print(f"   {step}")
            
            if result['config_path']:
                print(f"\n📄 Configuração salva em: {result['config_path']}")
            
            if result['details']:
                print(f"\n📝 Detalhes:")
                for detail in result['details']:
                    print(f"   - {detail}")
        else:
            print("❌ Problemas na configuração:")
            print(f"   {result['message']}")
        
        print()
        
        # 4. Demonstrar uso dos secrets
        print("🔒 Etapa 4: Demonstrando acesso aos secrets...")
        secrets = kv_manager.secrets
        
        print("Secrets disponíveis:")
        for config_key, value in secrets.items():
            if 'secret' in config_key or 'password' in config_key:
                masked_value = '*' * 8
            else:
                masked_value = value[:20] + '...' if len(str(value)) > 20 else value
            print(f"   - {config_key}: {masked_value}")
        
        print()
        
        # 5. Exemplo de configuração YAML gerada
        print("📄 Etapa 5: Configuração YAML gerada:")
        config_yaml = kv_manager.generate_config_yaml()
        
        print("Estrutura da configuração:")
        def print_config_structure(obj, indent=0):
            for key, value in obj.items():
                if isinstance(value, dict):
                    print("  " * indent + f"- {key}:")
                    print_config_structure(value, indent + 1)
                else:
                    print("  " * indent + f"- {key}: {type(value).__name__}")
        
        print_config_structure(config_yaml)
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")
        import traceback
        traceback.print_exc()


def exemplo_secrets_esperados():
    """
    Mostra os secrets que devem estar configurados no Key Vault
    """
    print("\n" + "=" * 60)
    print("🔐 SECRETS NECESSÁRIOS NO AZURE KEY VAULT")
    print("=" * 60)
    
    secrets_info = [
        ("databricks-workspace-id", "ID único da workspace Databricks", "1234567890123456"),
        ("databricks-workspace-url", "URL da workspace Databricks", "https://adb-123456.azuredatabricks.net"),
        ("spn-client-id", "Application ID do Service Principal", "12345678-1234-1234-1234-123456789012"),
        ("spn-client-secret", "Secret do Service Principal", "abc123~xyz789-secretvalue"),
        ("sql-admin-password", "Senha do admin do Azure SQL", "MinhaS3nh@F0rt3!"),
        ("sql-connection-string", "String de conexão completa", "Server=tcp:server.database.windows.net..."),
        ("sql-database-name", "Nome do banco de dados", "dino_analytics_db"),
        ("sql-server-name", "Nome do servidor SQL", "dino-sql-server"),
        ("tenant-id", "Tenant ID do Azure AD", "87654321-4321-4321-4321-210987654321"),
        ("unity-catalog-storage-key", "Chave de acesso do storage", "abc123XYZ789storagekey=="),
        ("unity-catalog-storage-name", "Nome da conta de storage", "dinostorage")
    ]
    
    for secret_name, description, example in secrets_info:
        print(f"🔑 {secret_name}")
        print(f"   📝 {description}")
        print(f"   💡 Exemplo: {example}")
        print()
    
    print("📋 Comandos para criar secrets (exemplo):")
    print("az keyvault secret set --vault-name dino-keyvault-dev --name databricks-workspace-url --value 'https://adb-123456.azuredatabricks.net'")
    print("az keyvault secret set --vault-name dino-keyvault-dev --name spn-client-id --value '12345678-1234-1234-1234-123456789012'")
    print("# ... etc para cada secret")


def exemplo_cli_usage():
    """
    Mostra exemplos de uso da CLI
    """
    print("\n" + "=" * 60)
    print("💻 EXEMPLOS DE USO DA CLI")
    print("=" * 60)
    
    examples = [
        ("Configuração inicial", "dino-config setup --keyvault-name dino-keyvault-dev --project-name vendas --project-spn-id abc-123"),
        ("Configuração interativa", "dino-config setup --keyvault-name dino-keyvault-dev --project-name vendas"),
        ("Validar configuração", "dino-config validate --keyvault-name dino-keyvault-dev --project-name vendas"),
        ("Ver configuração atual", "dino-config show"),
        ("Resetar configuração", "dino-config reset"),
        ("Gerar exemplo", "dino-config generate-example -o minha_config.json")
    ]
    
    for description, command in examples:
        print(f"📋 {description}:")
        print(f"   {command}")
        print()
    
    print("🔧 Fluxo típico de configuração:")
    print("1. Criar Key Vault no Azure e adicionar secrets")
    print("2. Executar: dino-config setup --keyvault-name ... --project-name ...")
    print("3. Validar: dino-config validate --keyvault-name ... --project-name ...")
    print("4. Usar o SDK: dino-ingest --target-schema vendas --table-name pedidos ...")


if __name__ == "__main__":
    exemplo_configuracao_keyvault()
    exemplo_secrets_esperados()
    exemplo_cli_usage()
