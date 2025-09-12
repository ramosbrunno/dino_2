"""
🎯 DINO SDK v1.1.6 - Exemplo Completo de Secret Scope
Exemplo de como usar o DinoSecretScopeManager em ambiente Databricks
"""

# ========================================
# 📋 INSTRUÇÕES DE USO
# ========================================
"""
1. Instale o wheel no seu cluster Databricks:
   %pip install /path/to/dino_sdk-1.1.6-py3-none-any.whl

2. Execute este código em um notebook Databricks

3. Certifique-se de ter:
   - Permissões de admin no workspace Databricks
   - Acesso ao Azure Key Vault configurado
   - Service Principal com permissões adequadas
"""

# ========================================
# 📦 EXEMPLO DE USO BÁSICO
# ========================================

def exemplo_basico():
    """
    Exemplo básico de criação de Secret Scope
    """
    print("🔐 Exemplo Básico - Secret Scope Manager")
    print("=" * 45)
    
    try:
        # Importar o manager
        from dino_scope_manager import DinoSecretScopeManager
        
        # Criar manager (force_databricks=True garante uso em ambiente Databricks)
        manager = DinoSecretScopeManager(force_databricks=True)
        
        # Listar scopes existentes
        print("\n📋 Scopes existentes:")
        scopes = manager.list_scopes()
        
        # Criar novo scope
        print("\n🔧 Criando novo scope...")
        result = manager.create_keyvault_scope(
            scope_name="meu-projeto-scope",
            keyvault_name="dino-keyvault-dev"
        )
        
        print("\n✅ Scope criado com sucesso!")
        print(f"📝 Nome: {result['scope_name']}")
        print(f"🔗 Key Vault: {result['keyvault_name']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

# ========================================
# 🔧 EXEMPLO AVANÇADO
# ========================================

def exemplo_avancado():
    """
    Exemplo avançado com configurações personalizadas
    """
    print("🔐 Exemplo Avançado - Secret Scope Manager")
    print("=" * 45)
    
    try:
        from dino_scope_manager import DinoSecretScopeManager
        
        # Criar manager
        manager = DinoSecretScopeManager(force_databricks=True)
        
        # Configurar scope personalizado
        scope_config = {
            "scope_name": "analytics-keyvault-scope",
            "keyvault_name": "analytics-kv-prod"
        }
        
        print(f"🎯 Configuração do scope:")
        for key, value in scope_config.items():
            print(f"   {key}: {value}")
        
        # Criar scope com configurações personalizadas
        result = manager.create_keyvault_scope(**scope_config)
        
        # Verificar se o scope foi criado
        print("\n🔍 Verificando criação...")
        scopes = manager.list_scopes()
        
        scope_encontrado = any(
            scope.get('name') == scope_config['scope_name'] 
            for scope in scopes
        )
        
        if scope_encontrado:
            print(f"✅ Scope '{scope_config['scope_name']}' confirmado!")
        else:
            print(f"⚠️  Scope não encontrado na listagem")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

# ========================================
# 🧪 EXEMPLO DE TROUBLESHOOTING
# ========================================

def exemplo_troubleshooting():
    """
    Exemplo com tratamento de erros e troubleshooting
    """
    print("🔐 Exemplo Troubleshooting - Secret Scope Manager")
    print("=" * 50)
    
    try:
        from dino_scope_manager import DinoSecretScopeManager
        
        # Criar manager
        manager = DinoSecretScopeManager(force_databricks=True)
        
        # Verificar conectividade
        print("🔗 Testando conectividade Databricks...")
        client = manager.get_databricks_client()
        print("✅ Conectividade OK")
        
        # Verificar método da API
        print("\n🔍 Verificando método da API...")
        if hasattr(client.api_client, 'do'):
            print("✅ Método api_client.do() disponível")
        else:
            print("⚠️  Método api_client.do() não disponível, usando fallback")
        
        # Tentar listar scopes
        print("\n📋 Tentando listar scopes...")
        try:
            scopes = manager.list_scopes()
            print(f"✅ Listagem bem-sucedida: {len(scopes)} scopes")
        except Exception as e:
            print(f"❌ Erro na listagem: {e}")
            return False
        
        # Tentar criar scope (com nome único para evitar conflitos)
        import time
        unique_scope = f"test-scope-{int(time.time())}"
        
        print(f"\n🔧 Tentando criar scope: {unique_scope}")
        try:
            result = manager.create_keyvault_scope(
                scope_name=unique_scope,
                keyvault_name="dino-keyvault-dev"
            )
            print("✅ Criação bem-sucedida")
            
            # Cleanup - deletar scope de teste
            print(f"\n🗑️  Limpando scope de teste...")
            # manager.delete_scope(unique_scope)  # Descomente se implementado
            
        except Exception as e:
            print(f"❌ Erro na criação: {e}")
            print("🔍 Possíveis causas:")
            print("   • Permissões insuficientes no workspace")
            print("   • Key Vault não acessível")
            print("   • Service Principal mal configurado")
            print("   • Scope já existente")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

# ========================================
# 📊 EXEMPLO DE USO EM PIPELINE
# ========================================

def exemplo_pipeline():
    """
    Exemplo de uso em pipeline de dados
    """
    print("🔐 Exemplo Pipeline - Secret Scope Manager")
    print("=" * 45)
    
    try:
        from dino_scope_manager import DinoSecretScopeManager
        
        # Configuração do pipeline
        pipeline_config = {
            "projeto": "analytics-pipeline",
            "ambiente": "prod",
            "keyvault": "dino-keyvault-dev"
        }
        
        scope_name = f"{pipeline_config['projeto']}-{pipeline_config['ambiente']}-scope"
        
        # Criar manager
        manager = DinoSecretScopeManager(force_databricks=True)
        
        print(f"🚀 Configurando scope para pipeline '{pipeline_config['projeto']}'")
        print(f"📊 Ambiente: {pipeline_config['ambiente']}")
        
        # Verificar se scope já existe
        scopes = manager.list_scopes()
        scope_existe = any(scope.get('name') == scope_name for scope in scopes)
        
        if scope_existe:
            print(f"ℹ️  Scope '{scope_name}' já existe, reutilizando...")
        else:
            print(f"🔧 Criando novo scope '{scope_name}'...")
            result = manager.create_keyvault_scope(
                scope_name=scope_name,
                keyvault_name=pipeline_config['keyvault']
            )
            print(f"✅ Scope criado: {result['scope_name']}")
        
        # Simular uso do scope (em um pipeline real)
        print(f"\n📝 Scope '{scope_name}' está pronto para uso:")
        print(f"   • Para acessar secrets: dbutils.secrets.get('{scope_name}', 'secret-name')")
        print(f"   • Key Vault conectado: {pipeline_config['keyvault']}")
        print(f"   • Ambiente: {pipeline_config['ambiente']}")
        
        return scope_name
        
    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")
        raise

# ========================================
# 🎯 FUNÇÃO PRINCIPAL
# ========================================

def main():
    """
    Função principal - executa todos os exemplos
    """
    print("🎉 DINO SDK v1.1.6 - Exemplos de Secret Scope")
    print("=" * 60)
    
    exemplos = [
        ("Básico", exemplo_basico),
        ("Avançado", exemplo_avancado),
        ("Troubleshooting", exemplo_troubleshooting),
        ("Pipeline", exemplo_pipeline)
    ]
    
    for nome, funcao in exemplos:
        try:
            print(f"\n{'='*20} {nome} {'='*20}")
            resultado = funcao()
            print(f"✅ Exemplo '{nome}' concluído com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro no exemplo '{nome}': {e}")
            
        print("\n" + "."*60)
    
    print("\n🎉 Todos os exemplos foram executados!")
    print("📚 Para mais informações, consulte a documentação do DINO SDK")

# ========================================
# 🚀 EXECUÇÃO
# ========================================

if __name__ == "__main__":
    # Para executar em notebook Databricks:
    main()
    
    # Para executar exemplo específico:
    # exemplo_basico()
    # exemplo_avancado()
    # exemplo_troubleshooting()
    # exemplo_pipeline()

# ========================================
# 📋 NOTAS IMPORTANTES
# ========================================
"""
🔴 REQUISITOS:
   • Ambiente Databricks (notebook ou job)
   • Permissões de admin no workspace
   • Azure Key Vault configurado e acessível
   • databricks-sdk instalado

⚠️  TROUBLESHOOTING:
   • Se api_client.do() falhar, o código usa fallback para requests
   • Verifique permissões se receber erro 403
   • Certifique-se de que o Key Vault existe e é acessível
   • Service Principal deve ter permissões adequadas

✅ COMPATIBILIDADE:
   • databricks-sdk v0.49.0+
   • Python 3.8+
   • Databricks Runtime 13.0+
"""
