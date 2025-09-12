"""
🔐 DINO SDK v1.1.6 - Criador de Secret Scope
Cria Secret Scope apontando para Azure Key Vault
"""

import logging
from typing import Dict, Any, Optional

# Import local
from .dino_keyvault import DinoKeyVaultConfig

class DinoSecretScopeManager:
    """
    Gerenciador de Secret Scopes para o DINO SDK
    """
    
    def __init__(self, force_databricks: bool = True):
        """
        Inicializa o gerenciador de Secret Scope
        """
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Usar configuração DINO existente
        self.dino_config = DinoKeyVaultConfig(force_databricks=force_databricks)
        
        # Configurações padrão
        self.scope_name = "dino-keyvault-scope"
        self.keyvault_name = "dino-keyvault-dev"
        
        print("🔐 DINO Secret Scope Manager v1.1.6")
        print("=" * 45)
        
    def _setup_logging(self):
        """Configura logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def get_databricks_client(self):
        """
        Obtém cliente Databricks usando configuração DINO
        """
        try:
            # Extrair contexto
            context = self.dino_config.get_databricks_context(force=True)
            
            # Criar cliente
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.core import Config
            
            # Configuração do cliente
            config = Config(
                host=context['workspace_url'],
                token=context['admin_token']
            )
            
            client = WorkspaceClient(config=config)
            print(f"✅ Cliente Databricks conectado: {context['workspace_url']}")
            
            return client
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar cliente Databricks: {e}")
            raise
    
    def create_keyvault_scope(self, scope_name: str = None, keyvault_name: str = None) -> Dict[str, Any]:
        """
        Cria secret scope apontando para Azure Key Vault
        """
        try:
            # Usar valores padrão se não fornecidos
            scope_name = scope_name or self.scope_name
            keyvault_name = keyvault_name or self.keyvault_name
            
            print(f"🔧 Criando Secret Scope: {scope_name}")
            print(f"🗂️  Key Vault: {keyvault_name}")
            
            # Obter cliente Databricks
            client = self.get_databricks_client()
            
            # Obter contexto para Key Vault
            context = self.dino_config.get_databricks_context(force=True)
            
            # Extrair informações do Key Vault
            subscription_id = context.get('subscription_id', '46c8ee51-8493-4e0e-8da5-de84c7a4b88a')
            resource_group = context.get('resource_group', 'rg-dino-dev')
            tenant_id = context.get('tenant_id', '16b3c013-d300-468d-ac64-7eda0820b6d3')
            
            # Construir Resource ID e DNS Name
            keyvault_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.KeyVault/vaults/{keyvault_name}"
            keyvault_dns_name = f"https://{keyvault_name}.vault.azure.net/"
            
            print(f"🔑 Key Vault Resource ID: {keyvault_resource_id}")
            print(f"🌐 Key Vault DNS Name: {keyvault_dns_name}")
            print(f"🏢 Tenant ID: {tenant_id}")
            
            # Criar secret scope usando API REST direta (versão simplificada)
            try:
                # Usar a abordagem que funciona para list_scopes
                import requests
                
                # Obter contexto para token e workspace URL
                context = self.dino_config.get_databricks_context(force=True)
                
                headers = {"Authorization": f"Bearer {context['admin_token']}"}
                payload = {
                    "scope": scope_name,
                    "scope_backend_type": "AZURE_KEYVAULT",
                    "backend_azure_keyvault": {
                        "resource_id": keyvault_resource_id,
                        "dns_name": keyvault_dns_name
                    },
                    "initial_manage_principal": "users"
                }
                
                url = f"{context['workspace_url']}/api/2.0/secrets/scopes/create"
                resp = requests.post(url, headers=headers, json=payload)
                
                if resp.status_code == 200:
                    print(f"✅ Secret scope criada com sucesso")
                    resp_data = resp.json() if resp.text else {"status": "created"}
                else:
                    # Verificar se é erro de scope já existente
                    if resp.status_code == 400 and "already exists" in resp.text:
                        print(f"ℹ️  Secret scope '{scope_name}' já existe")
                        resp_data = {"status": "already_exists"}
                    else:
                        raise Exception(f"Erro na API REST: {resp.status_code} - {resp.text}")
                    
            except Exception as e:
                # Se for erro de scope já existente, continuar
                if "already exists" in str(e).lower():
                    print(f"ℹ️  Secret scope '{scope_name}' já existe")
                    resp_data = {"status": "already_exists"}
                else:
                    raise Exception(f"Erro ao criar secret scope: {e}")
            
            print(f"✅ Secret Scope '{scope_name}' criado com sucesso!")
            print(f"🔗 Conectado ao Key Vault: {keyvault_name}")
            
            return {
                "scope_name": scope_name,
                "keyvault_name": keyvault_name,
                "keyvault_resource_id": keyvault_resource_id,
                "keyvault_dns_name": keyvault_dns_name,
                "response": resp_data
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao criar secret scope: {e}")
            raise
    
    def list_scopes(self) -> list:
        """
        Lista todos os secret scopes - versão simplificada
        """
        try:
            # Usar apenas requests (que estava funcionando)
            import requests
            
            context = self.dino_config.get_databricks_context(force=True)
            headers = {"Authorization": f"Bearer {context['admin_token']}"}
            url = f"{context['workspace_url']}/api/2.0/secrets/scopes/list"
            
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Scopes listados com sucesso")
                resp_data = resp.json()
            else:
                raise Exception(f"Erro na API REST: {resp.status_code} - {resp.text}")
            
            scopes = resp_data.get('scopes', [])
            
            print(f"📋 Encontrados {len(scopes)} secret scopes:")
            for scope in scopes:
                print(f"  • {scope.get('name', 'N/A')} (backend: {scope.get('backend_type', 'N/A')})")
            
            return scopes
            
        except Exception as e:
            self.logger.error(f"Erro ao listar scopes: {e}")
            raise


def dino_create_keyvault_scope(
    subscription_id: str,
    resource_group: str, 
    tenant_id: str,
    keyvault_name: str,
    scope_name: str = None,
    force_databricks: bool = True
) -> bool:
    """
    🎯 Função simplificada para criar Secret Scope com parâmetros Azure específicos
    
    Args:
        subscription_id: ID da subscription Azure
        resource_group: Nome do resource group
        tenant_id: ID do tenant Azure
        keyvault_name: Nome do Key Vault
        scope_name: Nome do scope (opcional, será gerado se não fornecido)
        force_databricks: Forçar modo Databricks
    
    Returns:
        bool: True se sucesso, False se erro
    
    Example:
        success = dino_create_keyvault_scope(
            subscription_id="bfb09176-b505-4a45-b6a9-d17bd8dc577e",
            resource_group="data-master-dev-rsg",
            tenant_id="94c7139f-16a8-4733-86c1-c5f67366ec1f",
            keyvault_name="data-master-dev-akv-1g67"
        )
    """
    try:
        print("🎯 DINO Create KeyVault Scope - Função Simplificada")
        print("=" * 55)
        print(f"🔧 Subscription ID: {subscription_id}")
        print(f"🏢 Resource Group: {resource_group}")
        print(f"🔑 Key Vault: {keyvault_name}")
        print(f"🏢 Tenant ID: {tenant_id}")
        
        # Gerar nome do scope se não fornecido
        if not scope_name:
            scope_name = f"{keyvault_name}-scope"
        
        print(f"📋 Scope Name: {scope_name}")
        
        # Criar manager personalizado
        manager = DinoSecretScopeManager(force_databricks=force_databricks)
        
        # Sobrescrever configurações Azure com os parâmetros fornecidos
        def get_custom_context(force=True):
            # Obter contexto base (workspace_url e admin_token)
            try:
                base_context = manager.dino_config._cached_context
                if not base_context:
                    # Se não há cache, tentar extrair uma vez
                    base_context = manager.dino_config.extract_context_inline()
            except:
                # Se falhar, usar valores mock para teste
                base_context = {
                    'workspace_url': 'https://mock-workspace.azuredatabricks.net',
                    'admin_token': 'mock-token'
                }
            
            # Retornar contexto com parâmetros personalizados
            return {
                'workspace_url': base_context.get('workspace_url', 'https://mock-workspace.azuredatabricks.net'),
                'admin_token': base_context.get('admin_token', 'mock-token'),
                'subscription_id': subscription_id,
                'resource_group': resource_group,
                'tenant_id': tenant_id
            }
        
        # Substituir método temporariamente
        original_method = manager.dino_config.get_databricks_context
        manager.dino_config.get_databricks_context = get_custom_context
        
        try:
            # Criar o scope com as configurações personalizadas
            result = manager.create_keyvault_scope(
                scope_name=scope_name,
                keyvault_name=keyvault_name
            )
            
            print(f"\n✅ Secret Scope criado com sucesso!")
            print(f"📝 Nome: {result['scope_name']}")
            print(f"🔗 Key Vault: {result['keyvault_name']}")
            print(f"🔑 Resource ID: {result['keyvault_resource_id']}")
            print(f"🌐 DNS Name: {result['keyvault_dns_name']}")
            
            return True
            
        finally:
            # Restaurar método original
            manager.dino_config.get_databricks_context = original_method
        
    except Exception as e:
        print(f"❌ Erro ao criar Secret Scope: {e}")
        print("🔍 Verifique:")
        print("   • Se você está executando em um notebook Databricks")
        print("   • Se tem permissões de admin no workspace")
        print("   • Se o Key Vault existe e é acessível")
        print("   • Se o Service Principal tem as permissões necessárias")
        return False


def main():
    """
    Função principal para teste
    """
    try:
        # Criar gerenciador
        manager = DinoSecretScopeManager(force_databricks=True)
        
        # Listar scopes existentes
        print("\n📋 Listando scopes existentes...")
        manager.list_scopes()
        
        # Criar novo scope
        print("\n🔧 Criando novo secret scope...")
        result = manager.create_keyvault_scope()
        
        # Listar novamente para verificar
        print("\n📋 Listando scopes após criação...")
        manager.list_scopes()
        
        print("\n✅ Teste do Secret Scope Manager concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        raise


if __name__ == "__main__":
    main()
