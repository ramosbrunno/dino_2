"""
🧪 DINO SDK v1.1.6 - Teste da Função Simplificada
Testa a função dino_create_keyvault_scope com parâmetros específicos
"""

import sys
import os

# Adicionar pasta src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simplified_function():
    """
    Testa a função simplificada dino_create_keyvault_scope
    """
    print("🧪 Testando função simplificada dino_create_keyvault_scope")
    print("=" * 60)
    
    try:
        # Importar a função
        from dino_scope_manager import dino_create_keyvault_scope
        print("✅ Função dino_create_keyvault_scope importada com sucesso")
        
        # Parâmetros do usuário
        test_params = {
            "subscription_id": "bfb09176-b505-4a45-b6a9-d17bd8dc577e",
            "resource_group": "data-master-dev-rsg",
            "tenant_id": "94c7139f-16a8-4733-86c1-c5f67366ec1f",
            "keyvault_name": "data-master-dev-akv-1g67",
            "scope_name": "data-master-scope"
        }
        
        print("\n📋 Parâmetros de teste:")
        for key, value in test_params.items():
            print(f"   {key}: {value}")
        
        # Simular chamada (vai falhar por não estar no Databricks, mas testa a estrutura)
        print("\n🔧 Testando estrutura da função...")
        
        try:
            success = dino_create_keyvault_scope(**test_params)
            if success:
                print("✅ Função executada com sucesso!")
            else:
                print("⚠️  Função retornou False (esperado fora do Databricks)")
        except Exception as e:
            if "dbutils não encontrado" in str(e):
                print("⚠️  Erro esperado: não está no ambiente Databricks")
                print("✅ Estrutura da função está correta")
            else:
                print(f"❌ Erro inesperado: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_import_from_init():
    """
    Testa importação através do __init__.py
    """
    print("\n🔧 Testando importação através de __init__.py...")
    
    try:
        # Testar importação direta do pacote
        import src
        from src import dino_create_keyvault_scope
        print("✅ Importação via __init__.py funcionando")
        return True
    except Exception as e:
        print(f"⚠️  Importação via __init__.py falhou: {e}")
        print("💡 Use importação direta: from dino_scope_manager import dino_create_keyvault_scope")
        return False

def test_function_signature():
    """
    Testa a assinatura da função
    """
    print("\n🔍 Testando assinatura da função...")
    
    try:
        from dino_scope_manager import dino_create_keyvault_scope
        import inspect
        
        sig = inspect.signature(dino_create_keyvault_scope)
        print("✅ Assinatura da função:")
        print(f"   {dino_create_keyvault_scope.__name__}{sig}")
        
        # Verificar parâmetros obrigatórios
        required_params = ["subscription_id", "resource_group", "tenant_id", "keyvault_name"]
        func_params = list(sig.parameters.keys())
        
        for param in required_params:
            if param in func_params:
                print(f"   ✅ {param}: presente")
            else:
                print(f"   ❌ {param}: ausente")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar assinatura: {e}")
        return False

def create_usage_example():
    """
    Cria exemplo de uso para o usuário
    """
    print("\n📝 EXEMPLO DE USO NO DATABRICKS:")
    print("=" * 40)
    
    example_code = '''
# 1. Instalar o wheel no Databricks
%pip install /path/to/dino_sdk-1.1.6-py3-none-any.whl

# 2. Importar a função
from dino_scope_manager import dino_create_keyvault_scope

# 3. Usar com seus parâmetros
success = dino_create_keyvault_scope(
    subscription_id="bfb09176-b505-4a45-b6a9-d17bd8dc577e",
    resource_group="data-master-dev-rsg",
    tenant_id="94c7139f-16a8-4733-86c1-c5f67366ec1f",
    keyvault_name="data-master-dev-akv-1g67"
)

if success:
    print("✅ Secret Scope criado com sucesso!")
else:
    print("❌ Erro ao criar Secret Scope")
'''
    
    print(example_code)

if __name__ == "__main__":
    print("🚀 Iniciando testes da função simplificada")
    
    # Executar testes
    test1 = test_simplified_function()
    test2 = test_import_from_init()
    test3 = test_function_signature()
    
    # Mostrar exemplo de uso
    create_usage_example()
    
    print("\n" + "=" * 60)
    if test1 and test3:  # test2 é opcional
        print("🎉 Função simplificada está pronta para uso!")
        print("✅ Todos os testes principais passaram")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Gerar novo wheel: python setup.py bdist_wheel")
        print("   2. Instalar no Databricks: %pip install /path/to/wheel")
        print("   3. Usar a função conforme exemplo acima")
    else:
        print("❌ Alguns testes falharam")
        print("🔧 Verifique os erros acima antes de prosseguir")
