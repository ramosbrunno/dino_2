#!/usr/bin/env python3
"""
Dino SDK - Configuração Programática
Funções para configurar o SDK diretamente no código Python (ideal para notebooks)
"""

import os
from typing import Dict, Any, Optional

from .config_manager import get_config_manager


def configure_dino_sdk(
    workspace_url: str,
    catalog_name: str = "main",
    checkpoint_base_path: str = "/tmp/checkpoints/dino_sdk",
    volume_base_path: str = "/Volumes",
    azure_sql_server: Optional[str] = None,
    azure_sql_database: str = "dino_logging",
    azure_sql_username: Optional[str] = None,
    azure_sql_password: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Configura o Dino SDK programaticamente
    
    Ideal para uso em notebooks Databricks onde CLI interativo não funciona.
    
    Args:
        workspace_url: URL do workspace Databricks (obrigatório)
        catalog_name: Nome do catálogo Unity Catalog (padrão: "main")
        checkpoint_base_path: Caminho base para checkpoints (padrão: "/tmp/checkpoints/dino_sdk")
        volume_base_path: Caminho base para Volumes (padrão: "/Volumes")
        azure_sql_server: Servidor Azure SQL para logging (opcional)
        azure_sql_database: Nome da database Azure SQL (padrão: "dino_logging")
        azure_sql_username: Username Azure SQL (opcional)
        azure_sql_password: Password Azure SQL (opcional)
        **kwargs: Outras configurações adicionais
    
    Returns:
        Dict com status da configuração
    
    Example:
        # Configuração básica
        configure_dino_sdk(
            workspace_url="https://adb-123456789.0.azuredatabricks.net"
        )
        
        # Configuração completa com Azure SQL
        configure_dino_sdk(
            workspace_url="https://adb-123456789.0.azuredatabricks.net",
            catalog_name="production",
            azure_sql_server="myserver.database.windows.net",
            azure_sql_username="dino_admin",
            azure_sql_password="my_password"
        )
    """
    
    print("🦕 Dino SDK - Configuração Programática")
    print("=" * 45)
    
    # Validar entrada obrigatória
    if not workspace_url:
        raise ValueError("workspace_url é obrigatório")
    
    # Obter gerenciador de configuração
    config_manager = get_config_manager()
    
    # Preparar configurações
    config_updates = {
        'catalog_name': catalog_name,
        'workspace_url': workspace_url,
        'checkpoint_base_path': checkpoint_base_path,
        'volume_base_path': volume_base_path,
        **kwargs
    }
    
    # Adicionar configurações Azure SQL se fornecidas
    azure_config_complete = all([azure_sql_server, azure_sql_username, azure_sql_password])
    
    if azure_config_complete:
        config_updates.update({
            'azure_sql_server': azure_sql_server,
            'azure_sql_database': azure_sql_database,
            'azure_sql_username': azure_sql_username,
            'azure_sql_password': azure_sql_password
        })
        print("✅ Configuração Azure SQL incluída")
    elif any([azure_sql_server, azure_sql_username, azure_sql_password]):
        print("⚠️ Configuração Azure SQL incompleta - ignorando")
        print("💡 Para habilitar logging, forneça: azure_sql_server, azure_sql_username, azure_sql_password")
    
    # Aplicar configuração
    try:
        config_manager.update_config(config_updates)
        
        # Configurar variáveis de ambiente também
        set_environment_variables(config_updates)
        
        result = {
            'success': True,
            'message': 'Configuração aplicada com sucesso',
            'config': {
                'catalog_name': catalog_name,
                'workspace_url': workspace_url,
                'checkpoint_base_path': checkpoint_base_path,
                'azure_sql_enabled': azure_config_complete
            }
        }
        
        print(f"✅ Configuração aplicada com sucesso!")
        print(f"📊 Catálogo: {catalog_name}")
        print(f"🌐 Workspace: {workspace_url}")
        print(f"📁 Checkpoints: {checkpoint_base_path}")
        
        if azure_config_complete:
            print(f"🗃️ Azure SQL: {azure_sql_server}/{azure_sql_database}")
        
        print("\n💡 Execute: validate_dino_config() para testar")
        
        return result
        
    except Exception as e:
        result = {
            'success': False,
            'message': f'Erro na configuração: {e}',
            'error': str(e)
        }
        print(f"❌ Erro na configuração: {e}")
        return result


def set_environment_variables(config: Dict[str, Any]):
    """
    Define variáveis de ambiente baseadas na configuração
    
    Args:
        config: Dicionário com configurações
    """
    
    # Mapeamento de configurações para variáveis de ambiente
    env_mapping = {
        'workspace_url': 'DATABRICKS_WORKSPACE_URL',
        'catalog_name': 'DINO_CATALOG_NAME',
        'checkpoint_base_path': 'DINO_CHECKPOINT_BASE_PATH',
        'volume_base_path': 'DINO_VOLUME_BASE_PATH',
        'azure_sql_server': 'DINO_AZURE_SQL_SERVER',
        'azure_sql_database': 'DINO_AZURE_SQL_DATABASE',
        'azure_sql_username': 'DINO_AZURE_SQL_USERNAME',
        'azure_sql_password': 'DINO_AZURE_SQL_PASSWORD'
    }
    
    # Definir variáveis de ambiente
    env_vars_set = []
    for config_key, env_var in env_mapping.items():
        if config_key in config and config[config_key]:
            os.environ[env_var] = str(config[config_key])
            env_vars_set.append(env_var)
    
    if env_vars_set:
        print(f"🔧 Variáveis de ambiente definidas: {', '.join(env_vars_set)}")


def validate_dino_config() -> Dict[str, Any]:
    """
    Valida a configuração atual do Dino SDK
    
    Returns:
        Dict com resultado da validação
    """
    
    print("🔍 Validando Configuração do Dino SDK")
    print("=" * 40)
    
    config_manager = get_config_manager()
    
    # Verificar configurações obrigatórias
    required_configs = {
        'workspace_url': 'DATABRICKS_WORKSPACE_URL',
        'catalog_name': 'DINO_CATALOG_NAME'
    }
    
    optional_configs = {
        'checkpoint_base_path': 'DINO_CHECKPOINT_BASE_PATH',
        'azure_sql_server': 'DINO_AZURE_SQL_SERVER',
        'azure_sql_database': 'DINO_AZURE_SQL_DATABASE',
        'azure_sql_username': 'DINO_AZURE_SQL_USERNAME'
    }
    
    validation_result = {
        'success': True,
        'errors': [],
        'warnings': [],
        'config_summary': {}
    }
    
    # Validar configurações obrigatórias
    for config_key, env_var in required_configs.items():
        value = config_manager.get(config_key) or os.getenv(env_var)
        
        if not value:
            validation_result['errors'].append(f"Configuração obrigatória ausente: {config_key} (ou {env_var})")
            validation_result['success'] = False
        else:
            validation_result['config_summary'][config_key] = value
            print(f"✅ {config_key}: {value}")
    
    # Verificar configurações opcionais
    for config_key, env_var in optional_configs.items():
        value = config_manager.get(config_key) or os.getenv(env_var)
        
        if value:
            validation_result['config_summary'][config_key] = value
            if config_key.startswith('azure_sql'):
                print(f"🗃️ {config_key}: {value}")
            else:
                print(f"⚙️ {config_key}: {value}")
        else:
            if config_key.startswith('azure_sql'):
                validation_result['warnings'].append(f"Azure SQL não configurado: {config_key}")
    
    # Verificar conectividade Databricks
    databricks_valid = config_manager.validate_databricks_config()
    if databricks_valid:
        print("✅ Configuração Databricks válida")
    else:
        validation_result['errors'].append("Configuração Databricks inválida")
        validation_result['success'] = False
    
    # Verificar Azure SQL se configurado
    azure_sql_configs = [k for k in validation_result['config_summary'].keys() if k.startswith('azure_sql')]
    if len(azure_sql_configs) >= 3:  # server, database, username mínimo
        try:
            from .azure_sql_logger import get_sql_logger
            # Em ambiente real, testaria conexão
            print("🗃️ Configuração Azure SQL presente")
        except Exception as e:
            validation_result['warnings'].append(f"Azure SQL configurado mas pode ter problemas: {e}")
    
    # Resultado final
    if validation_result['success']:
        print("\n🎉 Configuração válida! SDK pronto para uso.")
    else:
        print(f"\n❌ Configuração inválida! {len(validation_result['errors'])} erro(s) encontrado(s)")
        for error in validation_result['errors']:
            print(f"   • {error}")
    
    if validation_result['warnings']:
        print(f"\n⚠️ {len(validation_result['warnings'])} aviso(s):")
        for warning in validation_result['warnings']:
            print(f"   • {warning}")
    
    return validation_result


def show_dino_config() -> Dict[str, Any]:
    """
    Exibe a configuração atual do Dino SDK
    
    Returns:
        Dict com configuração atual
    """
    
    print("📋 Configuração Atual do Dino SDK")
    print("=" * 35)
    
    config_manager = get_config_manager()
    current_config = config_manager.show_config()
    
    # Organizar por categoria
    databricks_config = {k: v for k, v in current_config.items() 
                        if k in ['workspace_url', 'catalog_name', 'checkpoint_base_path', 'volume_base_path']}
    
    azure_sql_config = {k: v for k, v in current_config.items() 
                       if k.startswith('azure_sql')}
    
    other_config = {k: v for k, v in current_config.items() 
                   if k not in databricks_config and k not in azure_sql_config}
    
    if databricks_config:
        print("\n🏢 Configuração Databricks:")
        for key, value in databricks_config.items():
            print(f"   {key}: {value}")
    
    if azure_sql_config:
        print("\n🗃️ Configuração Azure SQL:")
        for key, value in azure_sql_config.items():
            if 'password' in key.lower():
                print(f"   {key}: {'*' * len(str(value)) if value else 'não configurado'}")
            else:
                print(f"   {key}: {value}")
    
    if other_config:
        print("\n⚙️ Outras Configurações:")
        for key, value in other_config.items():
            print(f"   {key}: {value}")
    
    return current_config


# Funções de conveniência para uso em notebooks
def quick_setup(workspace_url: str, catalog_name: str = "main") -> Dict[str, Any]:
    """
    Configuração rápida básica (apenas Databricks)
    
    Args:
        workspace_url: URL do workspace Databricks
        catalog_name: Nome do catálogo (padrão: "main")
    
    Returns:
        Resultado da configuração
    """
    return configure_dino_sdk(
        workspace_url=workspace_url,
        catalog_name=catalog_name
    )


def setup_with_azure_sql(
    workspace_url: str,
    azure_sql_server: str,
    azure_sql_username: str,
    azure_sql_password: str,
    catalog_name: str = "main",
    azure_sql_database: str = "dino_logging"
) -> Dict[str, Any]:
    """
    Configuração completa com Azure SQL para logging
    
    Args:
        workspace_url: URL do workspace Databricks
        azure_sql_server: Servidor Azure SQL
        azure_sql_username: Username Azure SQL
        azure_sql_password: Password Azure SQL
        catalog_name: Nome do catálogo (padrão: "main")
        azure_sql_database: Nome da database (padrão: "dino_logging")
    
    Returns:
        Resultado da configuração
    """
    return configure_dino_sdk(
        workspace_url=workspace_url,
        catalog_name=catalog_name,
        azure_sql_server=azure_sql_server,
        azure_sql_database=azure_sql_database,
        azure_sql_username=azure_sql_username,
        azure_sql_password=azure_sql_password
    )
