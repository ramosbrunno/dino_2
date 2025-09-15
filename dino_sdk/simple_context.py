# Versão Simplificada da função get_notebook_context()
# Usando exatamente as linhas sugeridas pelo usuário

def get_notebook_context_simple():
    """
    Versão simplificada e direta para extrair contexto do notebook
    Usa exatamente as linhas sugeridas pelo usuário
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar se dbutils está disponível
        if 'dbutils' not in globals():
            logger.error("❌ dbutils não encontrado em globals")
            return None
            
        logger.info("✅ dbutils encontrado em globals")
        
        context = {
            'dbutils': globals()['dbutils']
        }
        
        # Extrair workspace URL - linha exata do usuário
        try:
            databricks_instance = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
            
            if databricks_instance:
                # Garantir formato HTTPS
                if not databricks_instance.startswith('https://'):
                    workspace_url = f"https://{databricks_instance}"
                else:
                    workspace_url = databricks_instance
                    
                context['workspace_url'] = workspace_url
                logger.info(f"✅ Workspace URL extraída: {workspace_url}")
            else:
                logger.warning("⚠️ Workspace URL está vazia")
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair workspace URL: {e}")
        
        # Extrair token - linha exata do usuário
        try:
            admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            
            if admin_token:
                context['token'] = admin_token
                masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
                logger.info(f"✅ Token extraído: {masked_token}")
            else:
                logger.warning("⚠️ Token está vazio")
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair token: {e}")
        
        # Log do resultado final
        has_url = bool(context.get('workspace_url'))
        has_token = bool(context.get('token'))
        
        logger.info(f"📊 Contexto extraído: workspace_url={'✅' if has_url else '❌'}, token={'✅' if has_token else '❌'}")
        
        return context if (has_url or has_token) else None
        
    except Exception as e:
        logger.error(f"❌ Erro geral ao extrair contexto: {e}")
        return None

def test_simple_context():
    """
    Testa a função simplificada
    """
    print("🧪 Testando get_notebook_context_simple()")
    print("=" * 45)
    
    context = get_notebook_context_simple()
    
    if context:
        print("✅ Contexto extraído com sucesso!")
        print(f"   dbutils: {'✅' if context.get('dbutils') else '❌'}")
        print(f"   workspace_url: {'✅' if context.get('workspace_url') else '❌'}")
        print(f"   token: {'✅' if context.get('token') else '❌'}")
        
        if context.get('workspace_url'):
            print(f"   URL: {context['workspace_url']}")
        if context.get('token'):
            print(f"   Token: {context['token'][:15]}...")
            
        return context
    else:
        print("❌ Falha na extração de contexto")
        return None

if __name__ == "__main__":
    test_simple_context()
