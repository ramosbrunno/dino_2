"""
🎯 DINO SDK v1.1.6 - Função Simplificada STANDALONE
Versão independente para criar Secret Scope sem dependências complexas
"""

def dino_create_keyvault_scope_standalone(
    subscription_id: str,
    resource_group: str, 
    tenant_id: str,
    keyvault_name: str,
    scope_name: str = None
) -> bool:
    """
    🎯 Função STANDALONE para criar Secret Scope - SEM DEPENDÊNCIAS
    
    Args:
        subscription_id: ID da subscription Azure
        resource_group: Nome do resource group
        tenant_id: ID do tenant Azure
        keyvault_name: Nome do Key Vault
        scope_name: Nome do scope (opcional)
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        print("🎯 DINO Create KeyVault Scope - STANDALONE")
        print("=" * 45)
        print(f"🔧 Subscription ID: {subscription_id}")
        print(f"🏢 Resource Group: {resource_group}")
        print(f"🏢 Tenant ID: {tenant_id}")
        print(f"🔑 Key Vault: {keyvault_name}")
        
        # Gerar nome do scope se não fornecido
        if not scope_name:
            scope_name = f"{keyvault_name}-scope"
        
        print(f"📋 Scope Name: {scope_name}")
        
        # Obter contexto do Databricks (método simples)
        try:
            # Tentar extrair token e workspace URL
            workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
            admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            
            print(f"✅ Workspace URL: {workspace_url}")
            print(f"✅ Token obtido: {'*' * 20}")
            
        except Exception as e:
            print(f"❌ Erro ao obter contexto Databricks: {e}")
            return False
        
        # Construir Resource ID e DNS Name
        keyvault_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.KeyVault/vaults/{keyvault_name}"
        keyvault_dns_name = f"https://{keyvault_name}.vault.azure.net/"
        
        print(f"🔑 Key Vault Resource ID: {keyvault_resource_id}")
        print(f"🌐 Key Vault DNS Name: {keyvault_dns_name}")
        
        # Criar secret scope usando requests
        import requests
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "scope": scope_name,
            "scope_backend_type": "AZURE_KEYVAULT",
            "backend_azure_keyvault": {
                "resource_id": keyvault_resource_id,
                "dns_name": keyvault_dns_name
            },
            "initial_manage_principal": "users"
        }
        
        url = f"{workspace_url}/api/2.0/secrets/scopes/create"
        
        print(f"📡 Fazendo chamada para API...")
        resp = requests.post(url, headers=headers, json=payload)
        
        if resp.status_code == 200:
            print(f"✅ Secret scope criado com sucesso!")
        elif resp.status_code == 400 and "already exists" in resp.text:
            print(f"ℹ️  Secret scope '{scope_name}' já existe")
        else:
            print(f"❌ Erro na API: {resp.status_code} - {resp.text}")
            return False
        
        print(f"🎉 Processo concluído!")
        print(f"📝 Scope Name: {scope_name}")
        print(f"🔗 Key Vault: {keyvault_name}")
        print(f"💡 Para usar: dbutils.secrets.get('{scope_name}', 'secret-name')")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False


def dino_list_scopes_standalone() -> list:
    """
    Lista Secret Scopes - versão STANDALONE
    """
    try:
        print("📋 Listando Secret Scopes...")
        
        # Obter contexto
        workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
        admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
        
        # Fazer chamada
        import requests
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        url = f"{workspace_url}/api/2.0/secrets/scopes/list"
        
        resp = requests.get(url, headers=headers)
        
        if resp.status_code == 200:
            scopes = resp.json().get('scopes', [])
            print(f"✅ Encontrados {len(scopes)} scopes:")
            for scope in scopes:
                print(f"  • {scope.get('name', 'N/A')} (backend: {scope.get('backend_type', 'N/A')})")
            return scopes
        else:
            print(f"❌ Erro: {resp.status_code} - {resp.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []


# Funções compatíveis com versão anterior
def dino_create_keyvault_scope(
    subscription_id: str,
    resource_group: str, 
    tenant_id: str,
    keyvault_name: str = None,
    scope_name: str = None
) -> bool:
    """
    Função compatível com chamada anterior
    """
    if not keyvault_name:
        keyvault_name = "dino-keyvault-dev"  # valor padrão
    
    return dino_create_keyvault_scope_standalone(
        subscription_id=subscription_id,
        resource_group=resource_group,
        tenant_id=tenant_id,
        keyvault_name=keyvault_name,
        scope_name=scope_name
    )


if __name__ == "__main__":
    print("🧪 Teste STANDALONE - Execute no Databricks")
    print("Para usar, copie as funções para seu notebook Databricks")
