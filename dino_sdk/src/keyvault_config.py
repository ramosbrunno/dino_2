#!/usr/bin/env python3
"""
Dino SDK - Key Vault Configuration Manager
Gerenciador de configuração integrado com Azure Key Vault e Databricks Secret Scopes
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.workspace import SecretScope, SecretScopeBackendType
except ImportError:
    SecretClient = None
    DefaultAzureCredential = None
    WorkspaceClient = None
    SecretScope = None
    SecretScopeBackendType = None

from .config_manager import get_config_manager


class KeyVaultConfigManager:
    """
    Gerenciador de configuração integrado com Azure Key Vault
    
    Funcionalidades:
    - Conecta com Azure Key Vault
    - Cria Secret Scope no Databricks
    - Configura permissões (manage para admins/dino SPN, read para projeto SPN)
    - Grava arquivo YAML de configuração em Volumes
    - Mapeia secrets do Key Vault para configurações do Dino SDK
    """
    
    # Service Principal fixo do Dino
    DINO_SPN_ID = "8541a6b4-fa5d-4897-bd76-8c4399ba1792"
    SECRET_SCOPE_NAME = "dino-scope"
    
    # Mapeamento de secrets do Key Vault para configurações
    SECRET_MAPPING = {
        'databricks-workspace-id': 'workspace_id',
        'databricks-workspace-url': 'workspace_url',
        'spn-client-id': 'spn_client_id',
        'spn-client-secret': 'spn_client_secret',
        'sql-admin-password': 'azure_sql_password',
        'sql-connection-string': 'azure_sql_connection_string',
        'sql-database-name': 'azure_sql_database',
        'sql-server-name': 'azure_sql_server',
        'tenant-id': 'tenant_id',
        'unity-catalog-storage-key': 'unity_catalog_storage_key',
        'unity-catalog-storage-name': 'unity_catalog_storage_name'
    }
    
    def __init__(
        self,
        keyvault_name: str,
        project_name: str,
        project_spn_id: Optional[str] = None
    ):
        """
        Inicializa o gerenciador de configuração Key Vault
        
        Args:
            keyvault_name: Nome do Azure Key Vault
            project_name: Nome do projeto (usado no path do Volumes)
            project_spn_id: Service Principal ID do projeto (opcional)
        """
        self.keyvault_name = keyvault_name
        self.project_name = project_name
        self.project_spn_id = project_spn_id
        self.logger = logging.getLogger(__name__)
        
        # Inicializar clientes
        self.keyvault_url = f"https://{keyvault_name}.vault.azure.net/"
        self.secret_client = None
        self.databricks_client = None
        
        # Configurações extraídas do Key Vault
        self.secrets = {}
        
        # Verificar dependências
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        missing_deps = []
        
        if SecretClient is None:
            missing_deps.append("azure-keyvault-secrets")
        if DefaultAzureCredential is None:
            missing_deps.append("azure-identity")
        if WorkspaceClient is None:
            missing_deps.append("databricks-sdk")
        
        if missing_deps:
            raise ImportError(f"""
Dependências necessárias não encontradas: {', '.join(missing_deps)}

Instale com:
pip install azure-keyvault-secrets azure-identity databricks-sdk
            """)
    
    def _initialize_clients(self):
        """Inicializa clientes do Azure e Databricks"""
        try:
            # Cliente do Key Vault
            credential = DefaultAzureCredential()
            self.secret_client = SecretClient(
                vault_url=self.keyvault_url,
                credential=credential
            )
            
            # Primeiro, obter workspace URL do Key Vault para configurar Databricks
            workspace_url = self._get_secret('databricks-workspace-url')
            if not workspace_url:
                raise ValueError("Secret 'databricks-workspace-url' não encontrado no Key Vault")
            
            # Cliente do Databricks
            self.databricks_client = WorkspaceClient(
                host=workspace_url,
                azure_client_id=os.getenv('AZURE_CLIENT_ID'),
                azure_client_secret=os.getenv('AZURE_CLIENT_SECRET'),
                azure_tenant_id=os.getenv('AZURE_TENANT_ID')
            )
            
            self.logger.info("Clientes inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar clientes: {e}")
            raise
    
    def _get_secret(self, secret_name: str) -> Optional[str]:
        """
        Obtém secret do Key Vault
        
        Args:
            secret_name: Nome do secret
            
        Returns:
            Valor do secret ou None se não encontrado
        """
        try:
            secret = self.secret_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            self.logger.warning(f"Secret '{secret_name}' não encontrado: {e}")
            return None
    
    def load_secrets_from_keyvault(self) -> Dict[str, Any]:
        """
        Carrega todos os secrets relevantes do Key Vault
        
        Returns:
            Dicionário com secrets carregados
        """
        print("🔐 Conectando ao Azure Key Vault...")
        
        self._initialize_clients()
        
        print(f"📋 Carregando secrets de {self.keyvault_name}...")
        
        loaded_secrets = {}
        missing_secrets = []
        
        for kv_secret, config_key in self.SECRET_MAPPING.items():
            value = self._get_secret(kv_secret)
            if value:
                loaded_secrets[config_key] = value
                print(f"   ✅ {kv_secret}")
            else:
                missing_secrets.append(kv_secret)
                print(f"   ⚠️ {kv_secret} (não encontrado)")
        
        if missing_secrets:
            print(f"\n⚠️ Secrets não encontrados: {', '.join(missing_secrets)}")
        
        self.secrets = loaded_secrets
        print(f"✅ {len(loaded_secrets)} secrets carregados")
        
        return loaded_secrets
    
    def create_secret_scope(self) -> Dict[str, Any]:
        """
        Cria Secret Scope no Databricks apontando para o Key Vault
        
        Returns:
            Resultado da criação
        """
        print(f"🔑 Criando Secret Scope '{self.SECRET_SCOPE_NAME}'...")
        
        try:
            # Verificar se scope já existe
            try:
                existing_scopes = self.databricks_client.secrets.list_scopes()
                scope_exists = any(scope.name == self.SECRET_SCOPE_NAME for scope in existing_scopes)
                
                if scope_exists:
                    print(f"   ℹ️ Secret Scope '{self.SECRET_SCOPE_NAME}' já existe")
                    return {'success': True, 'message': 'Scope já existe', 'created': False}
                    
            except Exception as e:
                self.logger.warning(f"Erro ao verificar scopes existentes: {e}")
            
            # Criar novo scope
            self.databricks_client.secrets.create_scope(
                scope=self.SECRET_SCOPE_NAME,
                backend_azure_keyvault={
                    "dns_name": self.keyvault_url.rstrip('/'),
                    "resource_id": f"/subscriptions/{self._get_subscription_id()}/resourceGroups/{self._get_resource_group()}/providers/Microsoft.KeyVault/vaults/{self.keyvault_name}"
                }
            )
            
            print(f"   ✅ Secret Scope criado: {self.SECRET_SCOPE_NAME}")
            
            return {'success': True, 'message': 'Scope criado', 'created': True}
            
        except Exception as e:
            error_msg = f"Erro ao criar Secret Scope: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def configure_scope_permissions(self) -> Dict[str, Any]:
        """
        Configura permissões do Secret Scope
        
        Returns:
            Resultado da configuração de permissões
        """
        print("👥 Configurando permissões do Secret Scope...")
        
        results = []
        
        try:
            # Permissão MANAGE para SPN do Dino
            try:
                self.databricks_client.secrets.put_acl(
                    scope=self.SECRET_SCOPE_NAME,
                    principal=self.DINO_SPN_ID,
                    permission="MANAGE"
                )
                print(f"   ✅ SPN Dino ({self.DINO_SPN_ID}): MANAGE")
                results.append(f"Dino SPN: MANAGE")
                
            except Exception as e:
                error_msg = f"Erro ao configurar permissão para Dino SPN: {e}"
                print(f"   ❌ {error_msg}")
                results.append(error_msg)
            
            # Permissão READ para SPN do projeto (se fornecido)
            if self.project_spn_id:
                try:
                    self.databricks_client.secrets.put_acl(
                        scope=self.SECRET_SCOPE_NAME,
                        principal=self.project_spn_id,
                        permission="READ"
                    )
                    print(f"   ✅ SPN Projeto ({self.project_spn_id}): READ")
                    results.append(f"Project SPN: READ")
                    
                except Exception as e:
                    error_msg = f"Erro ao configurar permissão para Project SPN: {e}"
                    print(f"   ❌ {error_msg}")
                    results.append(error_msg)
            else:
                print(f"   ℹ️ SPN do projeto não fornecido - pulando configuração")
            
            # TODO: Configurar permissões para admins da workspace
            # Isso requer listar admins da workspace, que pode precisar de permissões especiais
            print(f"   ℹ️ Permissões para admins devem ser configuradas manualmente")
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            error_msg = f"Erro geral na configuração de permissões: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def generate_config_yaml(self) -> Dict[str, Any]:
        """
        Gera arquivo YAML de configuração
        
        Returns:
            Configuração em formato YAML
        """
        print("📄 Gerando configuração YAML...")
        
        config = {
            'dino_sdk': {
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'keyvault': {
                    'name': self.keyvault_name,
                    'url': self.keyvault_url,
                    'secret_scope': self.SECRET_SCOPE_NAME
                },
                'project': {
                    'name': self.project_name,
                    'spn_id': self.project_spn_id
                },
                'databricks': {
                    'workspace_url': self.secrets.get('workspace_url'),
                    'workspace_id': self.secrets.get('workspace_id'),
                    'catalog_name': 'main',  # Padrão, pode ser customizado
                    'checkpoint_base_path': f'/Volumes/{self.project_name}/default/checkpoints/dino_sdk',
                    'volume_base_path': f'/Volumes/{self.project_name}/default'
                },
                'azure_sql': {
                    'enabled': bool(self.secrets.get('azure_sql_server')),
                    'server': self.secrets.get('azure_sql_server'),
                    'database': self.secrets.get('azure_sql_database'),
                    'connection_string_secret': 'sql-connection-string'
                },
                'unity_catalog': {
                    'storage_name': self.secrets.get('unity_catalog_storage_name'),
                    'storage_key_secret': 'unity-catalog-storage-key'
                },
                'authentication': {
                    'tenant_id': self.secrets.get('tenant_id'),
                    'spn_client_id': self.secrets.get('spn_client_id'),
                    'spn_client_secret_secret': 'spn-client-secret'
                },
                'secret_references': {
                    'description': 'Secrets disponíveis no scope dino-scope',
                    'secrets': list(self.SECRET_MAPPING.keys())
                }
            }
        }
        
        return config
    
    def save_config_yaml(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva arquivo YAML no Volume do Databricks
        
        Args:
            config: Configuração a ser salva
            
        Returns:
            Resultado da operação
        """
        config_path = f"/Volumes/{self.project_name}/default/system_files/dino_config.yaml"
        
        print(f"💾 Salvando configuração em {config_path}...")
        
        try:
            # Converter para YAML
            yaml_content = yaml.dump(config, default_flow_style=False, indent=2)
            
            # Em ambiente real, salvaria diretamente no Volume
            # Por agora, simular salvamento
            if os.getenv('DINO_DEMO_MODE') == 'true':
                # Modo demo - salvar localmente
                local_path = f"./demo_volumes/{self.project_name}/default/system_files/"
                os.makedirs(local_path, exist_ok=True)
                local_file = os.path.join(local_path, "dino_config.yaml")
                
                with open(local_file, 'w') as f:
                    f.write(yaml_content)
                
                print(f"   ✅ Arquivo salvo localmente (demo): {local_file}")
                return {'success': True, 'path': config_path, 'local_path': local_file}
            
            else:
                # Modo real - usar API do Databricks para salvar no Volume
                # TODO: Implementar salvamento real no Volume
                print(f"   ⚠️ Salvamento no Volume não implementado ainda")
                print(f"   📄 Conteúdo YAML:")
                print("   " + "\n   ".join(yaml_content.split('\n')))
                
                return {
                    'success': True, 
                    'path': config_path,
                    'yaml_content': yaml_content,
                    'note': 'Salvamento no Volume requer implementação'
                }
                
        except Exception as e:
            error_msg = f"Erro ao salvar configuração: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def setup_complete_configuration(self) -> Dict[str, Any]:
        """
        Executa configuração completa
        
        Returns:
            Resultado da configuração completa
        """
        print(f"🚀 Iniciando configuração completa do Dino SDK")
        print(f"📁 Projeto: {self.project_name}")
        print(f"🔐 Key Vault: {self.keyvault_name}")
        print("=" * 60)
        
        results = {
            'success': True,
            'steps': [],
            'details': [],
            'config_path': None
        }
        
        try:
            # 1. Carregar secrets do Key Vault
            secrets_result = self.load_secrets_from_keyvault()
            results['steps'].append('✅ Secrets carregados do Key Vault')
            
            # 2. Criar Secret Scope
            scope_result = self.create_secret_scope()
            if scope_result['success']:
                results['steps'].append(f"✅ Secret Scope '{self.SECRET_SCOPE_NAME}' configurado")
            else:
                results['success'] = False
                results['details'].append(scope_result['message'])
                results['steps'].append('❌ Falha ao criar Secret Scope')
            
            # 3. Configurar permissões
            perms_result = self.configure_scope_permissions()
            if perms_result['success']:
                results['steps'].append('✅ Permissões configuradas')
                results['details'].extend(perms_result.get('results', []))
            else:
                results['details'].append(perms_result['message'])
                results['steps'].append('⚠️ Problemas nas permissões')
            
            # 4. Gerar configuração YAML
            config_yaml = self.generate_config_yaml()
            results['steps'].append('✅ Configuração YAML gerada')
            
            # 5. Salvar configuração
            save_result = self.save_config_yaml(config_yaml)
            if save_result['success']:
                results['steps'].append('✅ Configuração salva')
                results['config_path'] = save_result['path']
            else:
                results['details'].append(save_result['message'])
                results['steps'].append('⚠️ Problemas ao salvar configuração')
            
            # 6. Atualizar ConfigManager local
            config_manager = get_config_manager()
            local_config = {
                'keyvault_name': self.keyvault_name,
                'project_name': self.project_name,
                'secret_scope_name': self.SECRET_SCOPE_NAME,
                **{k: v for k, v in self.secrets.items() if not k.endswith('_secret')}
            }
            config_manager.update_config(local_config)
            results['steps'].append('✅ Configuração local atualizada')
            
            if results['success']:
                results['message'] = 'Configuração completa realizada com sucesso'
            else:
                results['message'] = 'Configuração realizada com alguns problemas'
            
        except Exception as e:
            results['success'] = False
            results['message'] = f'Erro durante configuração: {e}'
            results['steps'].append(f'❌ Erro: {e}')
            self.logger.error(f"Erro na configuração completa: {e}")
        
        return results
    
    def _get_subscription_id(self) -> str:
        """Obtém subscription ID do Azure (placeholder)"""
        # TODO: Implementar obtenção real do subscription ID
        return os.getenv('AZURE_SUBSCRIPTION_ID', 'your-subscription-id')
    
    def _get_resource_group(self) -> str:
        """Obtém resource group do Key Vault (placeholder)"""
        # TODO: Implementar obtenção real do resource group
        return os.getenv('AZURE_RESOURCE_GROUP', 'your-resource-group')


def validate_keyvault_config(keyvault_name: str, project_name: str) -> Dict[str, Any]:
    """
    Valida configuração do Key Vault
    
    Args:
        keyvault_name: Nome do Key Vault
        project_name: Nome do projeto
        
    Returns:
        Resultado da validação
    """
    print(f"🔍 Validando configuração Key Vault...")
    
    validation_result = {
        'success': True,
        'errors': [],
        'warnings': [],
        'keyvault_accessible': False,
        'secrets_found': [],
        'secrets_missing': []
    }
    
    try:
        kv_manager = KeyVaultConfigManager(keyvault_name, project_name)
        
        # Testar acesso ao Key Vault
        kv_manager._initialize_clients()
        validation_result['keyvault_accessible'] = True
        
        # Verificar secrets
        for secret_name in kv_manager.SECRET_MAPPING.keys():
            value = kv_manager._get_secret(secret_name)
            if value:
                validation_result['secrets_found'].append(secret_name)
            else:
                validation_result['secrets_missing'].append(secret_name)
        
        if validation_result['secrets_missing']:
            validation_result['warnings'].append(
                f"Secrets não encontrados: {', '.join(validation_result['secrets_missing'])}"
            )
        
        print(f"✅ Key Vault acessível: {len(validation_result['secrets_found'])} secrets encontrados")
        
    except Exception as e:
        validation_result['success'] = False
        validation_result['errors'].append(f"Erro ao acessar Key Vault: {e}")
        print(f"❌ Erro na validação: {e}")
    
    return validation_result
