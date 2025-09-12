#!/usr/bin/env python3
"""
Dino SDK v1.1.3 - Detecção Robusta de dbutils com Fallback Inteligente
Resolve problema de dbutils do SDK vs dbutils nativo do Databricks
"""

import logging

def is_native_databricks_dbutils(dbutils_obj):
    """
    Verifica se o dbutils é o nativo do Databricks runtime ou o do SDK
    
    Args:
        dbutils_obj: Objeto dbutils a ser verificado
        
    Returns:
        bool: True se for o dbutils nativo, False se for do SDK
    """
    if not dbutils_obj:
        return False
        
    dbutils_type = str(type(dbutils_obj))
    logger = logging.getLogger(__name__)
    logger.debug(f"🔍 Verificando tipo de dbutils: {dbutils_type}")
    
    # O dbutils do SDK é um módulo: <class 'module'>
    if "module" in dbutils_type.lower():
        logger.debug("❌ dbutils é um módulo (SDK), não o nativo")
        return False
    
    # O dbutils nativo tem atributo 'notebook' diretamente
    if hasattr(dbutils_obj, 'notebook'):
        # Verificar se notebook tem entry_point (padrão Databricks)
        if hasattr(dbutils_obj.notebook, 'entry_point'):
            logger.debug("✅ dbutils nativo com entry_point encontrado")
            return True
        # Verificar se é o padrão do Databricks
        elif hasattr(dbutils_obj.notebook, 'getContext'):
            logger.debug("✅ dbutils nativo com getContext encontrado")
            return True
    
    logger.debug("❌ dbutils não tem interface nativa")        
    return False

def create_fallback_dbutils(workspace_client=None):
    """
    Cria um objeto dbutils de fallback usando WorkspaceClient
    
    Args:
        workspace_client: Cliente Databricks já autenticado
        
    Returns:
        object: Objeto com interface similar ao dbutils para extrair credenciais
    """
    class FallbackDBUtils:
        def __init__(self, client=None):
            self.client = client
            
        class EntryPoint:
            def __init__(self, client):
                self.client = client
                
            def getDbutils(self):
                return FallbackDBUtils.InnerDBUtils(self.client)
                
        class InnerDBUtils:
            def __init__(self, client):
                self.client = client
                
            def notebook(self):
                return FallbackDBUtils.NotebookUtils(self.client)
                
        class NotebookUtils:
            def __init__(self, client):
                self.client = client
                
            def getContext(self):
                return FallbackDBUtils.NotebookContext(self.client)
                
        class NotebookContext:
            def __init__(self, client):
                self.client = client
                
            def apiUrl(self):
                return FallbackDBUtils.ContextValue(
                    self.client.config.host if self.client else None
                )
                
            def apiToken(self):
                return FallbackDBUtils.ContextValue(
                    self.client.config.token if self.client else None
                )
                
        class ContextValue:
            def __init__(self, value):
                self.value = value
                
            def get(self):
                return self.value
                
        @property
        def notebook(self):
            return FallbackDBUtils.EntryPointNotebook(self.client)
            
        class EntryPointNotebook:
            def __init__(self, client):
                self.client = client
                
            @property 
            def entry_point(self):
                return FallbackDBUtils.EntryPoint(self.client)
                
    return FallbackDBUtils(workspace_client)

def get_robust_notebook_context():
    """
    Obtém contexto do notebook usando detecção robusta de dbutils NATIVO
    
    Returns:
        dict: Dicionário com workspace_url, token e dbutils ou None se não encontrado
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Cache global para contexto injetado
        from . import _injected_context
        
        # Primeiro verificar se temos contexto injetado
        if _injected_context:
            logger.info("✅ Usando contexto injetado manualmente")
            return _injected_context.copy()
        
        dbutils_obj = None
        all_dbutils_found = []  # Para debug
        
        logger.info("🔍 Iniciando busca por dbutils NATIVO...")
        
        # Método 1: Frame inspection - buscar dbutils no contexto do notebook
        try:
            import inspect
            frame = inspect.currentframe()
            while frame:
                frame_globals = frame.f_globals
                if 'dbutils' in frame_globals:
                    candidate = frame_globals['dbutils']
                    candidate_type = str(type(candidate))
                    all_dbutils_found.append(f"frame: {candidate_type}")
                    
                    if is_native_databricks_dbutils(candidate):
                        dbutils_obj = candidate
                        logger.info("✅ dbutils NATIVO encontrado no frame do caller")
                        break
                frame = frame.f_back
        except Exception as e:
            logger.debug(f"Método frame falhou: {e}")
        
        # Método 2: eval() - acessar dbutils do contexto global do notebook
        if not dbutils_obj:
            try:
                candidate = eval('dbutils')
                candidate_type = str(type(candidate))
                all_dbutils_found.append(f"eval: {candidate_type}")
                
                if is_native_databricks_dbutils(candidate):
                    dbutils_obj = candidate
                    logger.info("✅ dbutils NATIVO encontrado via eval")
            except Exception as e:
                logger.debug(f"Método eval falhou: {e}")
        
        # Método 3: __main__ - contexto principal do notebook
        if not dbutils_obj:
            try:
                import __main__
                if hasattr(__main__, 'dbutils'):
                    candidate = __main__.dbutils
                    candidate_type = str(type(candidate))
                    all_dbutils_found.append(f"__main__: {candidate_type}")
                    
                    if is_native_databricks_dbutils(candidate):
                        dbutils_obj = candidate
                        logger.info("✅ dbutils NATIVO encontrado em __main__")
            except Exception as e:
                logger.debug(f"Método __main__ falhou: {e}")
        
        # Método 4: globals() padrão
        if not dbutils_obj:
            try:
                if 'dbutils' in globals():
                    candidate = globals()['dbutils']
                    candidate_type = str(type(candidate))
                    all_dbutils_found.append(f"globals: {candidate_type}")
                    
                    if is_native_databricks_dbutils(candidate):
                        dbutils_obj = candidate
                        logger.info("✅ dbutils NATIVO encontrado em globals()")
            except Exception as e:
                logger.debug(f"Método globals falhou: {e}")
        
        # Debug: mostrar todos os dbutils encontrados
        if all_dbutils_found:
            logger.info(f"🔍 Todos os dbutils encontrados: {', '.join(all_dbutils_found)}")
        
        # Se não encontrou dbutils nativo, tentar fallback com WorkspaceClient
        if not dbutils_obj:
            logger.warning("⚠️ dbutils nativo não encontrado, tentando fallback com SDK...")
            try:
                from databricks.sdk import WorkspaceClient
                client = WorkspaceClient()
                dbutils_obj = create_fallback_dbutils(client)
                logger.info("✅ Fallback dbutils criado com WorkspaceClient")
            except Exception as e:
                logger.error(f"❌ Fallback com WorkspaceClient falhou: {e}")
                logger.error("❌ Nenhuma estratégia funcionou")
                return None
            
        logger.info(f"✅ dbutils obtido: {type(dbutils_obj)}")
        context = {'dbutils': dbutils_obj}
        
        # Extrair workspace URL
        try:
            databricks_instance = dbutils_obj.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
            
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
            # Se falhou, tentar alternativa com host do cliente
            try:
                if hasattr(dbutils_obj, 'client') and hasattr(dbutils_obj.client, 'config'):
                    workspace_url = dbutils_obj.client.config.host
                    if workspace_url:
                        context['workspace_url'] = workspace_url
                        logger.info(f"✅ Workspace URL do cliente: {workspace_url}")
            except Exception as e2:
                logger.error(f"❌ Fallback URL também falhou: {e2}")
        
        # Extrair token
        try:
            admin_token = dbutils_obj.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            
            if admin_token:
                context['token'] = admin_token
                masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
                logger.info(f"✅ Token extraído: {masked_token}")
            else:
                logger.warning("⚠️ Token está vazio")
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair token: {e}")
            # Se falhou, tentar alternativa com token do cliente
            try:
                if hasattr(dbutils_obj, 'client') and hasattr(dbutils_obj.client, 'config'):
                    admin_token = dbutils_obj.client.config.token
                    if admin_token:
                        context['token'] = admin_token
                        masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
                        logger.info(f"✅ Token do cliente: {masked_token}")
            except Exception as e2:
                logger.error(f"❌ Fallback token também falhou: {e2}")
        
        # Verificar se conseguimos pelo menos URL ou token
        if context.get('workspace_url') or context.get('token'):
            logger.info("✅ Contexto extraído com sucesso")
            return context
        else:
            logger.error("❌ Não foi possível extrair nem URL nem token")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro geral na detecção: {e}")
        return None

# Função para testar isoladamente
def test_dbutils_detection():
    """Função para testar a detecção de dbutils"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando detecção robusta de dbutils...")
    context = get_robust_notebook_context()
    
    if context:
        print("✅ SUCESSO!")
        print(f"   - dbutils: {type(context.get('dbutils'))}")
        print(f"   - workspace_url: {context.get('workspace_url', 'N/A')}")
        print(f"   - token: {'***' if context.get('token') else 'N/A'}")
    else:
        print("❌ FALHOU!")
        
    return context
