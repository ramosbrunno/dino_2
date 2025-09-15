#!/usr/bin/env python3
"""
🧪 Script de Teste - DINO SDK v1.1.4
Testa a nova funcionalidade de fallback com Databricks SDK
"""

def test_v114_functionality():
    """Testa as funcionalidades da v1.1.4"""
    
    print("🧪 TESTE DINO SDK v1.1.4")
    print("=" * 50)
    
    # Teste 1: Importação dos módulos
    print("\n1️⃣ Testando importações...")
    try:
        from src.keyvault_config import get_notebook_context, KeyVaultConfigManager
        from src.databricks_sdk_auth_v114 import get_notebook_context_via_sdk, get_databricks_auth_via_sdk
        print("   ✅ Todos os módulos importados com sucesso")
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
        return False
    
    # Teste 2: Detecção de contexto
    print("\n2️⃣ Testando detecção de contexto...")
    try:
        context = get_notebook_context()
        if context:
            print("   ✅ Contexto detectado:")
            print(f"      - Tipo: {type(context)}")
            print(f"      - Chaves: {list(context.keys())}")
            
            if 'dbutils' in context:
                print(f"      - dbutils: {type(context['dbutils'])}")
            if 'workspace_url' in context:
                print(f"      - workspace_url: {context['workspace_url'][:50]}...")
            if 'token' in context:
                token = context['token']
                masked = f"{token[:10]}...{token[-5:]}" if len(token) > 15 else "***"
                print(f"      - token: {masked}")
            if 'auth_method' in context:
                print(f"      - método: {context['auth_method']}")
                
        else:
            print("   ⚠️ Nenhum contexto detectado (normal em ambiente não-Databricks)")
            
    except Exception as e:
        print(f"   ❌ Erro na detecção: {e}")
    
    # Teste 3: Fallback SDK (apenas teste de importação)
    print("\n3️⃣ Testando módulo SDK fallback...")
    try:
        # Não executar real porque pode falhar em ambiente não-Databricks
        print("   ✅ Módulo SDK fallback disponível")
        print("   ℹ️ Teste real será feito em ambiente Databricks")
    except Exception as e:
        print(f"   ❌ Erro no módulo SDK: {e}")
    
    # Teste 4: Inicialização da classe principal
    print("\n4️⃣ Testando inicialização da classe principal...")
    try:
        config = KeyVaultConfigManager()
        print("   ✅ KeyVaultConfigManager inicializada")
        print(f"      - SECRET_SCOPE_NAME: {config.SECRET_SCOPE_NAME}")
        print(f"      - KEYVAULT_URI: {config.KEYVAULT_URI}")
    except Exception as e:
        print(f"   ❌ Erro na inicialização: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE CONCLUÍDO")
    print("📝 Para teste completo, execute em ambiente Databricks:")
    print("   pip install dist/dino_sdk-1.1.4-py3-none-any.whl --force-reinstall")
    print("   python test_v114.py")
    
    return True

if __name__ == "__main__":
    test_v114_functionality()
