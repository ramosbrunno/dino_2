"""
🎯 DINO SECRET SCOPE - FUNÇÃO ULTRASIMPLIFICADA 
Versão final para Databricks - SEM DEPENDÊNCIAS
"""

def create_dino_keyvault_scope(subscription_id, resource_group, tenant_id, keyvault_name, scope_name=None):
    """
    Função ultrasimplificada para criar Secret Scope - COLOCAR DIRETO NO NOTEBOOK
    
    Para usar: Copie essa função inteira para sua célula do notebook Databricks
    """
    try:
        print("🎯 DINO Create KeyVault Scope - ULTRA SIMPLIFICADO")
        print("=" * 50)
        
        if not scope_name:
            scope_name = f"{keyvault_name}-scope"
        
        print(f"🔧 Subscription: {subscription_id}")
        print(f"🏢 Resource Group: {resource_group}")  
        print(f"🔑 Key Vault: {keyvault_name}")
        print(f"📋 Scope: {scope_name}")
        
        # Obter contexto Databricks
        workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
        token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
        
        # Montar Resource ID e DNS
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.KeyVault/vaults/{keyvault_name}"
        dns_name = f"https://{keyvault_name}.vault.azure.net/"
        
        # Fazer chamada da API
        import requests
        
        url = f"{workspace_url}/api/2.0/secrets/scopes/create"
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "scope": scope_name,
            "scope_backend_type": "AZURE_KEYVAULT",
            "backend_azure_keyvault": {
                "resource_id": resource_id,
                "dns_name": dns_name
            },
            "initial_manage_principal": "users"
        }
        
        print("📡 Criando Secret Scope...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print("✅ SUCESSO! Secret Scope criado!")
        elif "already exists" in response.text:
            print("ℹ️  Secret Scope já existe")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
            
        print(f"🎉 Concluído! Use: dbutils.secrets.get('{scope_name}', 'secret-name')")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


# EXEMPLO DE USO (copie tudo para o notebook):

# create_dino_keyvault_scope(
#     subscription_id="your-subscription-id",
#     resource_group="your-resource-group", 
#     tenant_id="your-tenant-id",
#     keyvault_name="your-keyvault-name"
# )
