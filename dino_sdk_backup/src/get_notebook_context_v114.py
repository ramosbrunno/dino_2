def get_notebook_context():
    """
    Versão robusta v1.1.4: detecta dbutils NATIVO + fallback via Databricks SDK
    Prioriza dbutils nativo, mas usa SDK como fallback confiável
    
    Returns:
        dict: {'workspace_url': str, 'token': str, 'client': WorkspaceClient} ou None se falhar
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar se há contexto injetado manualmente
        global _injected_context
        if _injected_context:
            logger.info("✅ Usando contexto injetado manualmente")
            return _injected_context.copy()
        
        # FASE 1: Tentar detecção de dbutils nativo
        logger.info("🔍 FASE 1: Buscando dbutils NATIVO...")
        
        dbutils_obj = None
        all_dbutils_found = []
        
        # Método 1: Frame inspection
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
                        logger.info("✅ dbutils NATIVO encontrado no frame")
                        break
                frame = frame.f_back
        except Exception as e:
            logger.debug(f"Frame falhou: {e}")
        
        # Método 2: eval()
        if not dbutils_obj:
            try:
                candidate = eval('dbutils')
                candidate_type = str(type(candidate))
                all_dbutils_found.append(f"eval: {candidate_type}")
                
                if is_native_databricks_dbutils(candidate):
                    dbutils_obj = candidate
                    logger.info("✅ dbutils NATIVO encontrado via eval")
            except Exception as e:
                logger.debug(f"Eval falhou: {e}")
        
        # Método 3: __main__
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
                logger.debug(f"__main__ falhou: {e}")
        
        if all_dbutils_found:
            logger.info(f"🔍 dbutils encontrados: {', '.join(all_dbutils_found)}")
        
        # FASE 2: Se encontrou dbutils nativo, extrair credenciais
        if dbutils_obj:
            logger.info("🎯 FASE 2: Extraindo credenciais de dbutils nativo...")
            context = {'dbutils': dbutils_obj}
            
            try:
                # Extrair workspace URL
                databricks_instance = dbutils_obj.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
                if databricks_instance:
                    workspace_url = f"https://{databricks_instance}" if not databricks_instance.startswith('https://') else databricks_instance
                    context['workspace_url'] = workspace_url
                    logger.info(f"✅ Workspace URL: {workspace_url}")
                
                # Extrair token
                admin_token = dbutils_obj.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
                if admin_token:
                    context['token'] = admin_token
                    masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
                    logger.info(f"✅ Token: {masked_token}")
                
                # Se conseguiu URL e token, retornar
                if context.get('workspace_url') and context.get('token'):
                    logger.info("🎉 SUCESSO FASE 2: Credenciais via dbutils nativo")
                    return context
                    
            except Exception as e:
                logger.error(f"❌ Erro ao extrair credenciais: {e}")
        
        # FASE 3: Fallback via Databricks SDK
        logger.warning("⚠️ FASE 3: Usando Databricks SDK como fallback...")
        
        try:
            from .databricks_sdk_auth_v114 import get_notebook_context_via_sdk
            
            sdk_context = get_notebook_context_via_sdk()
            
            if sdk_context:
                logger.info("🎉 SUCESSO FASE 3: Autenticação via Databricks SDK")
                return sdk_context
            else:
                logger.error("❌ FASE 3 falhou: SDK não conseguiu autenticar")
                
        except ImportError as e:
            logger.error(f"❌ Erro ao importar módulo SDK: {e}")
        except Exception as e:
            logger.error(f"❌ Erro geral na FASE 3: {e}")
        
        # FASE 4: Último recurso
        logger.warning("⚠️ FASE 4: Tentativa final com WorkspaceClient básico...")
        
        try:
            WorkspaceClient = get_databricks_clients()
            client = WorkspaceClient()
            current_user = client.current_user.me()
            
            context = {
                'workspace_url': client.config.host,
                'client': client,
                'user_info': current_user,
                'auth_method': 'basic_sdk',
                'databricks_sdk': True
            }
            
            logger.info("🎉 SUCESSO FASE 4: WorkspaceClient básico")
            return context
            
        except Exception as e:
            logger.error(f"❌ FASE 4 falhou: {e}")
        
        logger.error("❌ TODAS AS FASES FALHARAM")
        return None
            
    except Exception as e:
        logger.error(f"❌ Erro geral na detecção: {e}")
        return None
