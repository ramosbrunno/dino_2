# Teste Direto: Extração de Contexto Databricks
# Função simplificada para testar especificamente a extração via dbutils

def test_extract_databricks_context():
    """
    Função de teste direto para extrair contexto do Databricks
    Baseada na abordagem sugerida pelo usuário
    """
    print("🔍 Teste Direto: Extração de Contexto Databricks")
    print("=" * 50)
    
    context = {}
    errors = []
    
    # 1. Verificar dbutils básico
    print("1️⃣ Verificando dbutils...")
    try:
        if 'dbutils' in globals():
            dbutils_obj = globals()['dbutils']
            print(f"   ✅ dbutils encontrado: {type(dbutils_obj)}")
            context['dbutils'] = dbutils_obj
        else:
            errors.append("dbutils não encontrado em globals")
            print("   ❌ dbutils não encontrado em globals")
            return context, errors
    except Exception as e:
        errors.append(f"Erro ao verificar dbutils: {e}")
        print(f"   ❌ Erro: {e}")
        return context, errors
    
    # 2. Extrair workspace URL - método direto
    print("\n2️⃣ Extraindo workspace URL...")
    try:
        databricks_instance = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
        
        if databricks_instance:
            # Garantir formato HTTPS
            if not databricks_instance.startswith('https://'):
                workspace_url = f"https://{databricks_instance}"
            else:
                workspace_url = databricks_instance
                
            context['workspace_url'] = workspace_url
            print(f"   ✅ Workspace URL: {workspace_url}")
        else:
            errors.append("Workspace URL retornou vazio")
            print("   ❌ Workspace URL está vazio")
            
    except Exception as e:
        errors.append(f"Erro ao extrair workspace URL: {e}")
        print(f"   ❌ Erro: {e}")
    
    # 3. Extrair token de admin - método direto  
    print("\n3️⃣ Extraindo admin token...")
    try:
        admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
        
        if admin_token:
            context['token'] = admin_token
            masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
            print(f"   ✅ Token extraído: {masked_token}")
        else:
            errors.append("Token retornou vazio")
            print("   ❌ Token está vazio")
            
    except Exception as e:
        errors.append(f"Erro ao extrair token: {e}")
        print(f"   ❌ Erro: {e}")
    
    # 4. Fallback: Spark context para URL
    if not context.get('workspace_url'):
        print("\n4️⃣ Fallback: Spark context...")
        try:
            if 'spark' in globals():
                spark_session = globals()['spark']
                spark_conf = spark_session.sparkContext.getConf()
                workspace_from_spark = spark_conf.get('spark.databricks.workspaceUrl')
                
                if workspace_from_spark:
                    workspace_url = f"https://{workspace_from_spark}" if not workspace_from_spark.startswith('https://') else workspace_from_spark
                    context['workspace_url'] = workspace_url
                    print(f"   ✅ URL via Spark: {workspace_url}")
                else:
                    errors.append("spark.databricks.workspaceUrl não encontrada")
                    print("   ❌ spark.databricks.workspaceUrl não encontrada")
            else:
                errors.append("Spark não disponível")
                print("   ❌ Spark não disponível")
                
        except Exception as e:
            errors.append(f"Erro no fallback Spark: {e}")
            print(f"   ❌ Erro: {e}")
    
    # Resultado final
    print(f"\n📊 Resultado Final:")
    print(f"   Workspace URL: {'✅' if context.get('workspace_url') else '❌'}")
    print(f"   Token: {'✅' if context.get('token') else '❌'}")
    print(f"   dbutils: {'✅' if context.get('dbutils') else '❌'}")
    
    if errors:
        print(f"\n⚠️ Erros encontrados:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    
    return context, errors

def test_create_databricks_client(context):
    """
    Teste simplificado para criar cliente Databricks com contexto extraído
    """
    print("\n🚀 Teste: Criar Cliente Databricks")
    print("=" * 35)
    
    if not context.get('workspace_url') or not context.get('token'):
        print("❌ Contexto insuficiente para criar cliente")
        return None
    
    try:
        # Importar databricks-sdk
        from databricks.sdk import WorkspaceClient
        
        # Criar cliente com credenciais extraídas
        client = WorkspaceClient(
            host=context['workspace_url'],
            token=context['token']
        )
        
        # Testar cliente
        current_user = client.current_user.me()
        print(f"✅ Cliente criado com sucesso!")
        print(f"   Usuário: {current_user.user_name}")
        print(f"   Email: {current_user.emails[0].value if current_user.emails else 'N/A'}")
        
        return client
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")
        return None

# Função principal de teste
def run_direct_test():
    """
    Executa todos os testes diretos
    """
    print("🧪 INÍCIO DOS TESTES DIRETOS")
    print("=" * 60)
    
    # Teste 1: Extrair contexto
    context, errors = test_extract_databricks_context()
    
    # Teste 2: Criar cliente se contexto OK
    client = None
    if context.get('workspace_url') and context.get('token'):
        client = test_create_databricks_client(context)
    
    # Resultado final
    print(f"\n🎯 RESULTADO FINAL:")
    context_ok = bool(context.get('workspace_url') and context.get('token'))
    client_ok = client is not None
    
    print(f"   Extração de contexto: {'✅' if context_ok else '❌'}")
    print(f"   Criação de cliente: {'✅' if client_ok else '❌'}")
    
    if context_ok and client_ok:
        print(f"\n🎉 TESTE COMPLETO PASSOU!")
        print(f"   ✅ dbutils funcionou")
        print(f"   ✅ Credenciais extraídas")
        print(f"   ✅ Cliente Databricks criado")
        print(f"   🚀 Pronto para usar com Dino SDK")
        
        # Configurar env vars para uso posterior
        import os
        os.environ['DATABRICKS_HOST'] = context['workspace_url']
        os.environ['DATABRICKS_TOKEN'] = context['token']
        print(f"   ✅ Variáveis de ambiente configuradas")
        
        return True
    else:
        print(f"\n❌ TESTE FALHOU!")
        if errors:
            print(f"   Erros: {len(errors)} encontrados")
        print(f"   🔧 Investigar problemas no ambiente")
        return False

if __name__ == "__main__":
    run_direct_test()
