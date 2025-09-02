#!/usr/bin/env python3
"""
Dino SDK - Comando de Configuração
Configuração inicial e gerenciamento de variáveis de ambiente
"""

import click
import os
import json
from pathlib import Path
from typing import Dict, Any

from .config_manager import get_config_manager


@click.group()
def config():
    """Comandos de configuração do Dino SDK"""
    pass


@config.command()
@click.option('--keyvault-name', required=True, help='Nome do Azure Key Vault contendo os secrets')
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog (usado no path do Volumes)')
@click.option('--project-spn-id', help='Service Principal ID do projeto (para permissões READ)')
def setup(keyvault_name: str, catalog_name: str, project_spn_id: str = None):
    """
    Configuração inicial do Dino SDK usando Azure Key Vault
    
    Este comando:
    1. Conecta ao Azure Key Vault especificado
    2. Extrai os secrets necessários para o Dino SDK
    3. Cria Secret Scope no Databricks apontando para o Key Vault
    4. Configura permissões (MANAGE para dino SPN, READ para projeto SPN)
    5. Gera arquivo de configuração YAML no Volume
    
    Secrets esperados no Key Vault:
    - databricks-workspace-id
    - databricks-workspace-url  
    - spn-client-id
    - spn-client-secret
    - sql-admin-password
    - sql-connection-string
    - sql-database-name
    - sql-server-name
    - tenant-id
    - unity-catalog-storage-key
    - unity-catalog-storage-name
    
    Example:
        dino-config setup --keyvault-name meu-keyvault --catalog-name vendas --project-spn-id abc-123
    """
    print("🦕 Dino SDK - Configuração com Key Vault")
    print("=" * 45)
    
    try:
        # Executar configuração
        from .keyvault_config import KeyVaultConfigManager
        
        kv_manager = KeyVaultConfigManager(
            keyvault_name=keyvault_name,
            project_name=catalog_name,  # Usando catalog_name como project_name
            project_spn_id=project_spn_id
        )
        
        result = kv_manager.setup_complete_configuration()
        
        if result['success']:
            print(f"✅ Configuração concluída com sucesso!")
            print(f"🔐 Key Vault: {keyvault_name}")
            print(f"📁 Catálogo: {catalog_name}")
            print(f"🔑 Secret Scope: dino-scope")
            print(f"📄 Config YAML: /Volumes/{catalog_name}/default/system_files/dino_config.yaml")
            
            if project_spn_id:
                print(f"🆔 SPN Projeto: {project_spn_id} (read access)")
        else:
            print(f"❌ Erro na configuração: {result['message']}")
            if result.get('details'):
                for detail in result['details']:
                    print(f"   • {detail}")
        
    except ImportError:
        print("❌ Dependências não instaladas:")
        print("pip install azure-keyvault-secrets azure-identity databricks-sdk")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")


@config.command()
def show():
    """Mostra configuração atual"""
    print("🦕 Dino SDK - Configuração Atual")
    print("=" * 50)
    
    config_manager = get_config_manager()
    config_data = config_manager.show_config()
    
    if config_data:
        for key, value in config_data.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    if 'password' in sub_key or 'key' in sub_key:
                        print(f"  {sub_key}: {'*' * 8}")
                    else:
                        print(f"  {sub_key}: {sub_value}")
            else:
                if 'password' in key or 'key' in key:
                    print(f"{key}: {'*' * 8}")
                else:
                    print(f"{key}: {value}")
    else:
        print("⚠️ Nenhuma configuração encontrada")
        print("💡 Execute: dino-config init")


@config.command()
@click.option('--keyvault-name', required=True, help='Nome do Azure Key Vault')
@click.option('--catalog-name', required=True, help='Nome do catálogo Unity Catalog')
def validate_keyvault(keyvault_name: str, catalog_name: str):
    """
    Valida configuração do Key Vault e Secret Scope
    
    Example:
        dino-config validate-keyvault --keyvault-name meu-keyvault --catalog-name vendas
    """
    print("🔍 Dino SDK - Validação de Configuração")
    print("=" * 45)
    
    try:
        from .keyvault_config import validate_keyvault_config
        
        # Validar acesso ao Key Vault
        validation_result = validate_keyvault_config(keyvault_name, catalog_name)
        
        if validation_result['success']:
            print(f"✅ Key Vault '{keyvault_name}' acessível")
            print(f"   📋 Secrets encontrados: {len(validation_result['secrets_found'])}")
            
            if validation_result['secrets_missing']:
                print(f"   ⚠️ Secrets faltando: {', '.join(validation_result['secrets_missing'])}")
        else:
            print(f"❌ Problemas na validação:")
            for error in validation_result['errors']:
                print(f"   - {error}")
                
    except ImportError:
        print("❌ Dependências não instaladas:")
        print("pip install azure-keyvault-secrets azure-identity databricks-sdk")
    except Exception as e:
        print(f"❌ Erro na validação: {e}")


if __name__ == '__main__':
    config()
