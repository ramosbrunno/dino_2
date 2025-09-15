#!/usr/bin/env python3
"""
Teste específico para verificar o secret 'databricks-workspace-url' no Key Vault
"""

def test_keyvault_secret():
    """Testa especificamente o secret databricks-workspace-url"""
    
    print("🔍 TESTE ESPECÍFICO - KEY VAULT SECRET")
    print("=" * 50)
    
    keyvault_name = "data-master-dev-akv-1g67"
    secret_name = "databricks-workspace-url"
    
    print(f"Key Vault: {keyvault_name}")
    print(f"Secret: {secret_name}")
    
    try:
        # Importar dependências
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        print("✅ Bibliotecas Azure importadas com sucesso")
        
        # Construir URL do Key Vault
        vault_url = f"https://{keyvault_name}.vault.azure.net/"
        print(f"🔗 Vault URL: {vault_url}")
        
        # Criar credential
        print("🔐 Criando DefaultAzureCredential...")
        credential = DefaultAzureCredential()
        print("✅ Credential criado")
        
        # Criar client
        print("📱 Criando SecretClient...")
        secret_client = SecretClient(vault_url=vault_url, credential=credential)
        print("✅ SecretClient criado")
        
        # Obter secret
        print(f"🔍 Obtendo secret '{secret_name}'...")
        secret = secret_client.get_secret(secret_name)
        
        if secret and secret.value:
            raw_value = secret.value
            clean_value = raw_value.strip()
            
            print(f"✅ Secret obtido com sucesso!")
            print(f"   Valor bruto: '{raw_value}'")
            print(f"   Valor limpo: '{clean_value}'")
            print(f"   Tamanho: {len(clean_value)} caracteres")
            
            # Verificar formato
            if clean_value.startswith(('http://', 'https://')):
                print(f"✅ URL já tem protocolo: {clean_value}")
                final_url = clean_value
            else:
                final_url = f"https://{clean_value}"
                print(f"🔧 Protocolo adicionado: {final_url}")
            
            # Verificar se parece uma URL do Databricks
            if 'azuredatabricks.net' in final_url:
                print("✅ URL parece ser válida do Databricks")
            else:
                print("⚠️ URL não parece ser do Databricks")
            
            print(f"\n🎯 URL FINAL: {final_url}")
            
        else:
            print("❌ Secret está vazio ou None")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_keyvault_secret()
