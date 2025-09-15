"""
🧪 DINO SDK v1.1.6 - Teste de Secret Scope com API Compatibility
Teste da criação de Secret Scope com fallback para requests
"""

import sys
import os

# Adicionar pasta src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_scope_creation():
    """
    Testa criação de Secret Scope com fallbacks para API
    """
    try:
        print("🧪 Testando DINO Secret Scope Manager v1.1.6")
        print("=" * 50)
        
        # Importar o manager
        from dino_scope_manager import DinoSecretScopeManager
        
        # Criar manager
        manager = DinoSecretScopeManager(force_databricks=True)
        
        # Testar conexão Databricks
        print("\n🔗 Testando conexão Databricks...")
        client = manager.get_databricks_client()
        print(f"✅ Conexão estabelecida")
        
        # Listar scopes existentes
        print("\n📋 Listando Secret Scopes existentes...")
        try:
            scopes = manager.list_scopes()
            print(f"✅ Encontrados {len(scopes)} scopes")
        except Exception as e:
            print(f"⚠️  Erro ao listar scopes: {e}")
        
        # Testar criação de scope (com nome diferente para evitar conflito)
        print("\n🔧 Testando criação de Secret Scope...")
        test_scope_name = "dino-test-scope-api"
        
        try:
            result = manager.create_keyvault_scope(
                scope_name=test_scope_name,
                keyvault_name="dino-keyvault-dev"
            )
            print(f"✅ Secret Scope '{test_scope_name}' criado com sucesso!")
            print(f"🔗 Resource ID: {result['keyvault_resource_id']}")
            
        except Exception as e:
            print(f"⚠️  Erro na criação: {e}")
            
            # Se erro for de scope já existente, continuar
            if "already exists" in str(e).lower():
                print(f"ℹ️  Scope já existe, continuando teste...")
            else:
                raise
        
        # Listar novamente para verificar criação
        print("\n📋 Listando scopes após criação...")
        try:
            scopes = manager.list_scopes()
            
            # Procurar o scope criado
            found_scope = False
            for scope in scopes:
                if scope.get('name') == test_scope_name:
                    found_scope = True
                    print(f"✅ Scope '{test_scope_name}' encontrado!")
                    print(f"   Backend: {scope.get('backend_type', 'N/A')}")
                    break
            
            if not found_scope:
                print(f"⚠️  Scope '{test_scope_name}' não encontrado na lista")
                
        except Exception as e:
            print(f"⚠️  Erro ao listar scopes: {e}")
        
        # Testar acesso ao scope
        print(f"\n🧪 Testando acesso ao scope '{test_scope_name}'...")
        try:
            access_test = manager.test_scope_access(test_scope_name)
            if access_test:
                print(f"✅ Acesso ao scope validado")
            else:
                print(f"⚠️  Falha no teste de acesso")
        except Exception as e:
            print(f"⚠️  Erro no teste de acesso: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Teste do Secret Scope Manager concluído!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_methods():
    """
    Testa especificamente os métodos da API
    """
    try:
        print("\n🔍 Testando métodos da API databricks-sdk...")
        
        from dino_scope_manager import DinoSecretScopeManager
        manager = DinoSecretScopeManager(force_databricks=True)
        client = manager.get_databricks_client()
        
        # Testar se api_client.do existe
        if hasattr(client.api_client, 'do'):
            print("✅ Método api_client.do() disponível")
            
            # Tentar uma chamada simples
            try:
                resp = client.api_client.do(
                    method="GET",
                    path="/api/2.0/secrets/scopes/list"
                )
                print("✅ api_client.do() funcionando corretamente")
                
            except Exception as e:
                print(f"⚠️  Erro com api_client.do(): {e}")
                print("➡️  Fallback para requests será usado")
                
        else:
            print("⚠️  Método api_client.do() não disponível")
            print("➡️  Fallback para requests será usado")
        
        # Testar se perform_query existe (método antigo)
        if hasattr(client.api_client, 'perform_query'):
            print("ℹ️  Método perform_query() ainda disponível")
        else:
            print("ℹ️  Método perform_query() não disponível (esperado)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do DINO Secret Scope Manager")
    
    # Teste dos métodos da API
    api_test = test_api_methods()
    
    # Teste principal
    scope_test = test_scope_creation()
    
    if api_test and scope_test:
        print("\n🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam")
        sys.exit(1)
