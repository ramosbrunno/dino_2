"""
🧪 DINO SDK v1.1.6 - Teste de Importações
Verifica se todas as classes estão disponíveis no pacote
"""

import sys
import os

def test_package_imports():
    """
    Testa todas as importações do pacote DINO SDK
    """
    print("🧪 Testando importações do DINO SDK v1.1.6")
    print("=" * 50)
    
    # Adicionar src ao path se necessário
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"📁 Adicionado ao path: {src_path}")
    
    importacoes_testadas = []
    
    # Teste 1: DinoKeyVaultConfig
    try:
        from dino_keyvault import DinoKeyVaultConfig
        print("✅ DinoKeyVaultConfig importado com sucesso")
        importacoes_testadas.append(("DinoKeyVaultConfig", True, None))
    except Exception as e:
        print(f"❌ Erro ao importar DinoKeyVaultConfig: {e}")
        importacoes_testadas.append(("DinoKeyVaultConfig", False, str(e)))
    
    # Teste 2: DinoSecretScopeManager
    try:
        from dino_scope_manager import DinoSecretScopeManager
        print("✅ DinoSecretScopeManager importado com sucesso")
        importacoes_testadas.append(("DinoSecretScopeManager", True, None))
    except Exception as e:
        print(f"❌ Erro ao importar DinoSecretScopeManager: {e}")
        importacoes_testadas.append(("DinoSecretScopeManager", False, str(e)))
    
    # Teste 3: Dependências externas
    dependencias = [
        ("databricks.sdk", "WorkspaceClient"),
        ("databricks.sdk.core", "Config"),
        ("requests", None),
        ("logging", None),
        ("typing", "Dict")
    ]
    
    for modulo, classe in dependencias:
        try:
            if classe:
                exec(f"from {modulo} import {classe}")
                print(f"✅ {modulo}.{classe} disponível")
                importacoes_testadas.append((f"{modulo}.{classe}", True, None))
            else:
                exec(f"import {modulo}")
                print(f"✅ {modulo} disponível")
                importacoes_testadas.append((modulo, True, None))
        except Exception as e:
            print(f"❌ Erro ao importar {modulo}.{classe if classe else ''}: {e}")
            importacoes_testadas.append((f"{modulo}.{classe if classe else ''}", False, str(e)))
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 30)
    
    sucessos = sum(1 for _, sucesso, _ in importacoes_testadas if sucesso)
    total = len(importacoes_testadas)
    
    print(f"✅ Sucessos: {sucessos}/{total}")
    print(f"❌ Falhas: {total - sucessos}/{total}")
    
    if total - sucessos > 0:
        print("\n🔍 DETALHES DOS ERROS:")
        for nome, sucesso, erro in importacoes_testadas:
            if not sucesso:
                print(f"   • {nome}: {erro}")
    
    return sucessos == total

def test_create_manager():
    """
    Testa criação do manager
    """
    print("\n🔧 Testando criação do DinoSecretScopeManager...")
    
    try:
        # Adicionar src ao path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from dino_scope_manager import DinoSecretScopeManager
        
        # Tentar criar manager (pode falhar por não estar no Databricks, mas o import deve funcionar)
        try:
            manager = DinoSecretScopeManager(force_databricks=True)
            print("✅ DinoSecretScopeManager criado com sucesso")
            return True
        except Exception as e:
            if "dbutils não encontrado" in str(e):
                print("⚠️  Manager não pode ser criado (não está no Databricks), mas import funcionou")
                return True
            else:
                print(f"❌ Erro ao criar manager: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Erro ao importar DinoSecretScopeManager: {e}")
        return False

def list_files_in_src():
    """
    Lista arquivos na pasta src para debug
    """
    print("\n📁 Arquivos na pasta src:")
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    
    if os.path.exists(src_path):
        files = os.listdir(src_path)
        for file in sorted(files):
            file_path = os.path.join(src_path, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   📄 {file} ({size} bytes)")
            else:
                print(f"   📁 {file}/")
    else:
        print(f"   ❌ Pasta src não encontrada: {src_path}")

def check_python_path():
    """
    Verifica o Python path atual
    """
    print("\n🐍 Python Path atual:")
    for i, path in enumerate(sys.path):
        print(f"   {i:2d}. {path}")

if __name__ == "__main__":
    print("🚀 Iniciando testes de importação do DINO SDK")
    
    # Debug info
    list_files_in_src()
    check_python_path()
    
    # Testes principais
    import_test = test_package_imports()
    manager_test = test_create_manager()
    
    print("\n" + "=" * 50)
    if import_test and manager_test:
        print("🎉 Todos os testes de importação passaram!")
    else:
        print("❌ Alguns testes falharam")
        print("💡 Dicas para resolver:")
        print("   1. Certifique-se de que está executando no diretório correto")
        print("   2. Verifique se os arquivos .py estão na pasta src/")
        print("   3. Instale o wheel: %pip install /path/to/dino_sdk-1.1.6-py3-none-any.whl")
