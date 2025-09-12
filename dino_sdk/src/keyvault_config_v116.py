"""
🔑 KeyVault Config v1.1.6 - Detecção Melhorada de Databricks
Versão com detecção mais robusta e fallback para execução forçada
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Variáveis globais para cache de contexto
_extracted_context = None
_context_timestamp = None
_context_cache_ttl = 300  # 5 minutos

class KeyVaultConfigWithNotebook:
    """
    Configuração do Key Vault que usa notebook interno para extração de tokens
    Versão com detecção melhorada de ambiente Databricks
    """
    
    def __init__(self, force_databricks: bool = False):
        """
        Inicializa configuração
        
        Args:
            force_databricks: Força execução mesmo se detecção falhar
        """
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.force_databricks = force_databricks
        
        # Configurações do Key Vault
        self.KEYVAULT_URI = "https://dino-keyvault-dev.vault.azure.net/"
        self.SECRET_SCOPE_NAME = "dino-keyvault-scope"
        
        # Cache de contexto
        self.cached_context = None
        
        print("🦕 DINO SDK v1.1.6 - KeyVault com Detecção Melhorada")
        print("=" * 65)
        
    def _setup_logging(self):
        """Configura logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def is_databricks_environment(self) -> bool:
        """
        Verifica se está rodando em ambiente Databricks
        Múltiplos métodos de detecção para maior confiabilidade
        """
        if self.force_databricks:
            self.logger.info("✅ Databricks forçado via parâmetro force_databricks=True")
            return True
        
        detection_results = []
        
        # Método 1: Verificar variáveis de ambiente Databricks
        databricks_env_vars = [
            'DATABRICKS_RUNTIME_VERSION',
            'SPARK_HOME', 
            'DATABRICKS_ROOT_VIRTUALIZATION_TYPE',
            'DATABRICKS_HOST',
            'DB_HOME'
        ]
        
        for var in databricks_env_vars:
            if os.getenv(var):
                detection_results.append(f"env_var_{var}")
                self.logger.info(f"✅ Databricks detectado via {var}")
                return True
        
        # Método 2: Tentar acessar dbutils via eval
        try:
            dbutils_obj = eval('dbutils')
            if dbutils_obj is not None and hasattr(dbutils_obj, 'notebook'):
                detection_results.append("dbutils_eval")
                self.logger.info("✅ Databricks detectado via eval('dbutils')")
                return True
        except:
            detection_results.append("dbutils_eval_failed")
        
        # Método 3: Verificar se PySpark está disponível
        try:
            import pyspark
            from pyspark.sql import SparkSession
            # Se conseguir obter SparkSession, provavelmente é Databricks
            spark = SparkSession.getActiveSession()
            if spark:
                detection_results.append("pyspark_active_session")
                self.logger.info("✅ Databricks detectado via PySpark ativa")
                return True
        except:
            detection_results.append("pyspark_failed")
        
        # Método 4: Verificar se dbutils está no namespace global
        if 'dbutils' in globals():
            detection_results.append("dbutils_globals")
            self.logger.info("✅ Databricks detectado via dbutils global")
            return True
        
        # Método 5: Verificar módulos do sistema relacionados ao Databricks
        import sys
        databricks_modules = []
        for module_name in sys.modules:
            if any(keyword in module_name.lower() for keyword in ['databricks', 'dbutils', 'pyspark']):
                databricks_modules.append(module_name)
        
        if databricks_modules:
            detection_results.append(f"sys_modules_{len(databricks_modules)}")
            self.logger.info(f"✅ Databricks detectado via módulos: {databricks_modules[:3]}")
            return True
        
        # Método 6: Verificar IPython com contexto Databricks
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython:
                ipython_type = str(type(ipython))
                if 'databricks' in ipython_type.lower() or 'spark' in ipython_type.lower():
                    detection_results.append("ipython_databricks")
                    self.logger.info("✅ Databricks detectado via IPython")
                    return True
        except:
            detection_results.append("ipython_failed")
        
        # Método 7: Verificar diretórios típicos do Databricks
        databricks_paths = [
            '/databricks',
            '/dbfs',
            '/local_disk0'
        ]
        
        for path in databricks_paths:
            if os.path.exists(path):
                detection_results.append(f"path_{path.replace('/', '_')}")
                self.logger.info(f"✅ Databricks detectado via diretório {path}")
                return True
        
        # Log de debug com todos os resultados
        self.logger.warning(f"❌ Databricks não detectado. Tentativas: {', '.join(detection_results)}")
        return False
    
    def force_databricks_mode(self):
        """
        Força modo Databricks independente da detecção
        """
        self.force_databricks = True
        self.logger.info("⚡ Modo Databricks forçado")
    
    def try_extract_dbutils(self):
        """
        Tenta extrair dbutils usando diferentes métodos
        
        Returns:
            Objeto dbutils ou None se falhar
        """
        methods_tried = []
        
        # Método 1: eval('dbutils')
        try:
            dbutils_obj = eval('dbutils')
            if dbutils_obj and hasattr(dbutils_obj, 'notebook'):
                methods_tried.append("eval_success")
                self.logger.info("✅ dbutils obtido via eval()")
                return dbutils_obj
        except Exception as e:
            methods_tried.append(f"eval_failed_{str(e)[:20]}")
        
        # Método 2: globals()
        try:
            if 'dbutils' in globals():
                dbutils_obj = globals()['dbutils']
                if dbutils_obj and hasattr(dbutils_obj, 'notebook'):
                    methods_tried.append("globals_success")
                    self.logger.info("✅ dbutils obtido via globals()")
                    return dbutils_obj
        except Exception as e:
            methods_tried.append(f"globals_failed_{str(e)[:20]}")
        
        # Método 3: Tentar via __main__
        try:
            import __main__
            if hasattr(__main__, 'dbutils'):
                dbutils_obj = __main__.dbutils
                if dbutils_obj and hasattr(dbutils_obj, 'notebook'):
                    methods_tried.append("main_success")
                    self.logger.info("✅ dbutils obtido via __main__")
                    return dbutils_obj
        except Exception as e:
            methods_tried.append(f"main_failed_{str(e)[:20]}")
        
        # Método 4: Buscar em frames
        try:
            import inspect
            frame = inspect.currentframe()
            while frame:
                if 'dbutils' in frame.f_globals:
                    dbutils_obj = frame.f_globals['dbutils']
                    if dbutils_obj and hasattr(dbutils_obj, 'notebook'):
                        methods_tried.append("frame_success")
                        self.logger.info("✅ dbutils obtido via frame inspection")
                        return dbutils_obj
                frame = frame.f_back
        except Exception as e:
            methods_tried.append(f"frame_failed_{str(e)[:20]}")
        
        self.logger.error(f"❌ dbutils não encontrado. Métodos tentados: {', '.join(methods_tried)}")
        return None
    
    def extract_context_inline(self) -> Dict[str, Any]:
        """
        Extrai contexto diretamente usando dbutils (fallback)
        """
        try:
            self.logger.info("🔧 Executando extração inline...")
            
            # Tentar obter dbutils
            dbutils = self.try_extract_dbutils()
            
            if not dbutils:
                raise RuntimeError("❌ dbutils não encontrado")
            
            # Extrair dados do contexto
            admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            databricks_instance = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
            
            if not admin_token:
                raise ValueError("❌ Token de administração não encontrado")
            
            if not databricks_instance:
                raise ValueError("❌ URL do workspace não encontrada")
            
            # Garantir formato HTTPS
            if not databricks_instance.startswith('https://'):
                workspace_url = f"https://{databricks_instance}"
            else:
                workspace_url = databricks_instance
            
            # Criar contexto
            context = {
                'admin_token': admin_token,
                'workspace_url': workspace_url,
                'databricks_instance': databricks_instance,
                'headers': {"Authorization": f"Bearer {admin_token}"},
                'extraction_method': 'inline_dbutils',
                'timestamp': datetime.now().isoformat(),
                'dbutils': dbutils
            }
            
            # Log sucesso
            masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
            self.logger.info(f"✅ Token extraído inline: {masked_token}")
            self.logger.info(f"🌐 Workspace: {workspace_url}")
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração inline: {e}")
            raise
    
    def get_databricks_context(self, use_cache: bool = True, force: bool = False) -> Dict[str, Any]:
        """
        Método principal para obter contexto Databricks
        
        Args:
            use_cache: Se deve usar cache (padrão: True)
            force: Força execução mesmo se ambiente não for detectado
        
        Returns:
            Contexto Databricks extraído
        """
        global _extracted_context, _context_timestamp
        
        # Verificar cache se solicitado
        if use_cache and _extracted_context and _context_timestamp:
            cache_age = (datetime.now() - datetime.fromisoformat(_context_timestamp)).total_seconds()
            if cache_age < _context_cache_ttl:
                self.logger.info(f"✅ Usando contexto em cache (idade: {cache_age:.1f}s)")
                return _extracted_context
        
        self.logger.info("🎯 Iniciando extração de contexto Databricks...")
        
        # Verificar ambiente ou forçar
        if force:
            self.force_databricks_mode()
        
        if not self.is_databricks_environment():
            if not force:
                error_msg = (
                    "❌ Ambiente Databricks não detectado. "
                    "Use force=True para forçar execução ou verifique se está executando no Databricks."
                )
                raise RuntimeError(error_msg)
        
        # Executar extração inline (método principal)
        try:
            self.logger.info("🔧 Usando extração inline...")
            context = self.extract_context_inline()
            
            if context:
                self.logger.info("✅ Sucesso na extração inline")
                
                # Cache do resultado
                _extracted_context = context
                _context_timestamp = datetime.now().isoformat()
                self.cached_context = context
                
                self.logger.info("📦 Contexto extraído e armazenado em cache")
                return context
            else:
                raise RuntimeError("❌ Contexto extraído está vazio")
                
        except Exception as e:
            self.logger.error(f"❌ Extração inline falhou: {e}")
            raise RuntimeError(f"❌ Não foi possível extrair contexto: {e}")
    
    def create_databricks_client(self, context: Dict[str, Any] = None):
        """
        Cria cliente Databricks usando contexto extraído
        """
        if context is None:
            context = self.get_databricks_context()
        
        try:
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.core import Config
            
            # Configurar cliente com token extraído
            config = Config(
                host=context['workspace_url'],
                token=context['admin_token']
            )
            
            client = WorkspaceClient(config=config)
            
            # Testar cliente
            current_user = client.current_user.me()
            self.logger.info(f"✅ Cliente Databricks criado - Usuário: {current_user.user_name}")
            
            return client
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar cliente Databricks: {e}")
            raise
    
    def load_secrets_from_scope(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Carrega secrets da Secret Scope usando contexto extraído
        """
        if context is None:
            context = self.get_databricks_context()
        
        try:
            # Usar dbutils do contexto se disponível
            if 'dbutils' in context:
                dbutils = context['dbutils']
                self.logger.info(f"🔐 Carregando secrets via dbutils da scope '{self.SECRET_SCOPE_NAME}'...")
            else:
                # Criar cliente Databricks como fallback
                client = self.create_databricks_client(context)
                self.logger.info(f"🔐 Carregando secrets via client da scope '{self.SECRET_SCOPE_NAME}'...")
            
            # Mapeamento de secrets
            secret_mapping = {
                'azure-subscription-id': 'azure_subscription_id',
                'azure-tenant-id': 'azure_tenant_id',
                'azure-client-id': 'azure_client_id',
                'azure-client-secret': 'azure_client_secret',
                'sql-server-name': 'sql_server_name',
                'sql-database-name': 'sql_database_name',
                'sql-username': 'sql_username',
                'sql-password': 'sql_password'
            }
            
            loaded_secrets = {}
            missing_secrets = []
            
            for kv_secret, config_key in secret_mapping.items():
                try:
                    if 'dbutils' in context:
                        # Usar dbutils diretamente
                        secret_value = dbutils.secrets.get(self.SECRET_SCOPE_NAME, kv_secret)
                    else:
                        # Usar client
                        secret_result = client.secrets.get_secret(
                            scope=self.SECRET_SCOPE_NAME,
                            key=kv_secret
                        )
                        secret_value = secret_result.value if secret_result else None
                    
                    if secret_value:
                        loaded_secrets[config_key] = secret_value
                        self.logger.info(f"   ✅ {kv_secret}")
                    else:
                        missing_secrets.append(kv_secret)
                        self.logger.warning(f"   ⚠️ {kv_secret} (vazio)")
                        
                except Exception as e:
                    missing_secrets.append(kv_secret)
                    self.logger.warning(f"   ❌ {kv_secret} (erro: {e})")
            
            if missing_secrets:
                self.logger.warning(f"⚠️ Secrets não encontrados: {', '.join(missing_secrets)}")
            
            self.logger.info(f"✅ {len(loaded_secrets)} secrets carregados da scope")
            return loaded_secrets
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar secrets: {e}")
            raise
    
    def test_connection(self, force: bool = False) -> bool:
        """
        Testa conexão completa (extração + cliente + secrets)
        """
        try:
            print("\n🧪 TESTE DE CONEXÃO DINO SDK v1.1.6")
            print("=" * 50)
            
            # Teste 1: Verificar ambiente (ou forçar)
            print("1️⃣ Verificando ambiente Databricks...")
            if force:
                print("⚡ Modo forçado ativado")
                self.force_databricks_mode()
            
            if not self.is_databricks_environment():
                if not force:
                    print("❌ Não está em ambiente Databricks")
                    print("💡 Use force=True para forçar execução")
                    return False
            print("✅ Ambiente Databricks detectado")
            
            # Teste 2: Extrair contexto
            print("\n2️⃣ Extraindo contexto...")
            context = self.get_databricks_context(use_cache=False, force=force)
            if not context:
                print("❌ Falha na extração de contexto")
                return False
            print(f"✅ Contexto extraído via {context.get('extraction_method', 'unknown')}")
            
            # Teste 3: Carregar secrets
            print("\n3️⃣ Carregando secrets...")
            secrets = self.load_secrets_from_scope(context)
            print(f"✅ {len(secrets)} secrets carregados")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ DINO SDK v1.1.6 está funcionando corretamente")
            
            return True
            
        except Exception as e:
            print(f"\n❌ TESTE FALHOU: {e}")
            return False

# Função de conveniência para uso rápido
def quick_setup(force: bool = False) -> KeyVaultConfigWithNotebook:
    """
    Configuração rápida do KeyVault
    
    Args:
        force: Força execução mesmo se ambiente não for detectado
    
    Returns:
        Instância configurada do KeyVaultConfig
    """
    config = KeyVaultConfigWithNotebook(force_databricks=force)
    
    # Testar conexão
    if config.test_connection(force=force):
        print("🎯 Configuração concluída com sucesso!")
        return config
    else:
        if not force:
            print("💡 Tente: quick_setup(force=True) se estiver no Databricks")
        raise RuntimeError("❌ Falha na configuração inicial")

# Função para extrair apenas o contexto
def extract_databricks_context(use_cache: bool = True, force: bool = False) -> Dict[str, Any]:
    """
    Função standalone para extrair contexto Databricks
    
    Args:
        use_cache: Se deve usar cache
        force: Força execução mesmo se ambiente não for detectado
    
    Returns:
        Contexto Databricks extraído
    """
    config = KeyVaultConfigWithNotebook(force_databricks=force)
    return config.get_databricks_context(use_cache=use_cache, force=force)
