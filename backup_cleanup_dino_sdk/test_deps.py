#!/usr/bin/env python3
"""
Teste de importação das dependências críticas
Para usar no Databricks antes de executar dino-config setup
"""

def test_dependencies():
    """Testa todas as importações necessárias"""
    print("🔍 TESTE DE DEPENDÊNCIAS - DINO SDK v1.0.3")
    print("=" * 50)
    
    # Teste 1: databricks-sdk (versões específicas)
    print("\n1. Testando databricks-sdk (detalhado)...")
    try:
        import databricks
        print(f"   ✅ databricks package: {databricks.__file__}")
    except ImportError as e:
        print(f"   ❌ databricks package: ERRO - {e}")
        
    try:
        import databricks.sdk
        print(f"   ✅ databricks.sdk: {databricks.sdk.__file__}")
        print(f"   📦 Version: {getattr(databricks.sdk, '__version__', 'unknown')}")
    except ImportError as e:
        print(f"   ❌ databricks.sdk: ERRO - {e}")
        
    try:
        from databricks.sdk import WorkspaceClient
        print(f"   ✅ WorkspaceClient: OK")
    except ImportError as e:
        print(f"   ❌ WorkspaceClient: ERRO - {e}")
        
    # Teste 2: Azure libraries (versões específicas)
    print("\n2. Testando azure libraries (detalhado)...")
    try:
        import azure
        print(f"   ✅ azure package: {azure.__file__}")
    except ImportError as e:
        print(f"   ❌ azure package: ERRO - {e}")
        
    try:
        import azure.keyvault
        print(f"   ✅ azure.keyvault: OK")
    except ImportError as e:
        print(f"   ❌ azure.keyvault: ERRO - {e}")
        
    try:
        from azure.keyvault.secrets import SecretClient
        print(f"   ✅ SecretClient: OK")
    except ImportError as e:
        print(f"   ❌ SecretClient: ERRO - {e}")
        
    try:
        from azure.identity import DefaultAzureCredential
        print(f"   ✅ DefaultAzureCredential: OK")
    except ImportError as e:
        print(f"   ❌ DefaultAzureCredential: ERRO - {e}")
    
    # Teste 3: Lista de todos os pacotes instalados
    print("\n3. Pacotes instalados relacionados...")
    try:
        import pkg_resources
        installed_packages = [pkg.project_name for pkg in pkg_resources.working_set]
        
        relevant_packages = [pkg for pkg in installed_packages if any(term in pkg.lower() for term in ['databricks', 'azure', 'dino'])]
        print(f"   Pacotes relevantes: {relevant_packages}")
        
        # Versões específicas
        for pkg_name in ['databricks-sdk', 'databricks-cli', 'azure-keyvault-secrets', 'azure-identity', 'dino-sdk']:
            try:
                pkg = pkg_resources.get_distribution(pkg_name)
                print(f"   📦 {pkg_name}: {pkg.version}")
            except pkg_resources.DistributionNotFound:
                print(f"   ❌ {pkg_name}: não instalado")
                
    except Exception as e:
        print(f"   ❌ Erro listando pacotes: {e}")
    
    # Teste 4: Python path e ambiente
    print("\n4. Ambiente Python...")
    import sys
    print(f"   🐍 Python: {sys.version}")
    print(f"   📂 Executable: {sys.executable}")
    print(f"   📚 Python Path (primeiros 3):")
    for i, path in enumerate(sys.path[:3]):
        print(f"     {i+1}. {path}")
    
    # Teste 5: dino-sdk imports usando lazy loading
    print("\n5. Testando dino-sdk lazy imports...")
    try:
        from src.keyvault_config import get_databricks_clients
        print("   ✅ get_databricks_clients importado")
        
        # Tentar fazer lazy load
        try:
            workspace_client_class = get_databricks_clients()
            print("   ✅ WorkspaceClient lazy load: OK")
        except Exception as e:
            print(f"   ❌ WorkspaceClient lazy load: {e}")
            
    except ImportError as e:
        print(f"   ❌ get_databricks_clients: ERRO - {e}")
        
    try:
        from src.keyvault_config import get_azure_clients
        print("   ✅ get_azure_clients importado")
        
        # Tentar fazer lazy load
        try:
            secret_client_class, credential_class = get_azure_clients()
            print("   ✅ Azure clients lazy load: OK")
        except Exception as e:
            print(f"   ❌ Azure clients lazy load: {e}")
            
    except ImportError as e:
        print(f"   ❌ get_azure_clients: ERRO - {e}")
    
    print("\n" + "=" * 50)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("=" * 50)

if __name__ == "__main__":
    test_dependencies()
