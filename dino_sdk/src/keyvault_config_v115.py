"""
🔑 KeyVault Config v1.1.5 - Com Notebook Runner
Versão que usa notebook Databricks interno para extrair tokens
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
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Configurações do Key Vault
        self.KEYVAULT_URI = "https://dino-keyvault-dev.vault.azure.net/"
        self.SECRET_SCOPE_NAME = "dino-keyvault-scope"
        
        # Cache de contexto
        self.cached_context = None
        
        print("🦕 DINO SDK v1.1.5 - KeyVault com Notebook Runner")
        print("=" * 60)
        
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
        # Método 1: Verificar variáveis de ambiente Databricks
        databricks_env_vars = [
            'DATABRICKS_RUNTIME_VERSION',
            'SPARK_HOME', 
            'DATABRICKS_ROOT_VIRTUALIZATION_TYPE'
        ]
        
        for var in databricks_env_vars:
            if os.getenv(var):
                self.logger.info(f"✅ Databricks detectado via {var}")
                return True
        
        # Método 2: Tentar importar dbutils
        try:
            import pyspark
            # Se PySpark está disponível, provavelmente é Databricks
            self.logger.info("✅ Databricks detectado via PySpark")
            return True
        except ImportError:
            pass
        
        # Método 3: Verificar se dbutils está no namespace global
        try:
            # Tentar acessar dbutils de diferentes formas
            if 'dbutils' in globals():
                self.logger.info("✅ Databricks detectado via dbutils global")
                return True
        except:
            pass
        
        # Método 4: Tentar eval('dbutils')
        try:
            dbutils_obj = eval('dbutils')
            if dbutils_obj is not None:
                self.logger.info("✅ Databricks detectado via eval('dbutils')")
                return True
        except:
            pass
        
        # Método 5: Verificar módulos do sistema
        import sys
        for module_name in sys.modules:
            if 'databricks' in module_name.lower() or 'dbutils' in module_name.lower():
                self.logger.info(f"✅ Databricks detectado via módulo {module_name}")
                return True
        
        # Método 6: Verificar se estamos em um notebook
        try:
            # No Databricks, get_ipython() geralmente está disponível
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython and 'databricks' in str(type(ipython)).lower():
                self.logger.info("✅ Databricks detectado via IPython")
                return True
        except:
            pass
        
        self.logger.warning("❌ Databricks não detectado por nenhum método")
        return False
    
    def extract_context_via_notebook(self, notebook_path: str = None) -> Dict[str, Any]:
        """
        Extrai contexto executando notebook interno
        
        Args:
            notebook_path: Caminho para o notebook (None = usar padrão)
        
        Returns:
            Dicionário com contexto extraído
        """
        try:
            if not self.is_databricks_environment():
                raise RuntimeError("❌ Não está em ambiente Databricks")
            
            # Importar notebook runner
            from .notebook_runner import NotebookRunner
            
            runner = NotebookRunner(timeout=120)  # 2 minutos timeout
            
            # Definir caminho do notebook
            if notebook_path is None:
                # Tentar caminhos padrão
                possible_paths = [
                    "/tmp/dino_sdk_token_extractor",
                    "/Workspace/Shared/dino_sdk_token_extractor",
                    "/notebooks/token_extractor"
                ]
                notebook_path = possible_paths[0]  # Usar primeiro como padrão
            
            self.logger.info(f"🚀 Executando notebook de extração: {notebook_path}")
            
            # Executar notebook
            result = runner.run_token_extraction_notebook(notebook_path)
            
            if result and isinstance(result, dict):
                self.logger.info("✅ Contexto extraído via notebook com sucesso")
                return result
            else:
                raise ValueError("Resultado do notebook inválido")
                
        except Exception as e:
            self.logger.error(f"❌ Erro na extração via notebook: {e}")
            raise
    
    def extract_context_inline(self) -> Dict[str, Any]:
        """
        Extrai contexto diretamente usando dbutils (fallback)
        """
        try:
            if not self.is_databricks_environment():
                raise RuntimeError("❌ Não está em ambiente Databricks")
            
            self.logger.info("🔧 Executando extração inline...")
            
            # Obter dbutils
            try:
                import dbutils
            except ImportError:
                dbutils = eval('dbutils')
            
            # Extrair dados do contexto
            admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            databricks_instance = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
            
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
    
    def get_databricks_context(self, use_cache: bool = True, notebook_path: str = None) -> Dict[str, Any]:
        """
        Método principal para obter contexto Databricks
        
        Args:
            use_cache: Se deve usar cache (padrão: True)
            notebook_path: Caminho customizado para notebook
        
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
        
        if not self.is_databricks_environment():
            raise RuntimeError("❌ Esta funcionalidade só funciona dentro do Databricks")
        
        context = None
        
        # Estratégia 1: Tentar notebook (se caminho especificado)
        if notebook_path:
            try:
                self.logger.info("1️⃣ Tentando extração via notebook...")
                context = self.extract_context_via_notebook(notebook_path)
                if context:
                    self.logger.info("✅ Sucesso na extração via notebook")
            except Exception as e:
                self.logger.warning(f"⚠️ Notebook falhou: {e}")
        
        # Estratégia 2: Fallback para extração inline
        if not context:
            try:
                self.logger.info("2️⃣ Usando extração inline...")
                context = self.extract_context_inline()
                if context:
                    self.logger.info("✅ Sucesso na extração inline")
            except Exception as e:
                self.logger.error(f"❌ Extração inline falhou: {e}")
                raise
        
        # Cache do resultado se bem-sucedido
        if context:
            _extracted_context = context
            _context_timestamp = datetime.now().isoformat()
            self.cached_context = context
            
            self.logger.info("📦 Contexto extraído e armazenado em cache")
            return context
        else:
            raise RuntimeError("❌ Não foi possível extrair contexto por nenhum método")
    
    def create_databricks_client(self, context: Dict[str, Any] = None):
        """
        Cria cliente Databricks usando contexto extraído
        
        Args:
            context: Contexto extraído (None = extrair automaticamente)
        
        Returns:
            Cliente Databricks configurado
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
        
        Args:
            context: Contexto extraído (None = extrair automaticamente)
        
        Returns:
            Dicionário com secrets carregados
        """
        if context is None:
            context = self.get_databricks_context()
        
        try:
            # Criar cliente Databricks
            client = self.create_databricks_client(context)
            
            self.logger.info(f"🔐 Carregando secrets da scope '{self.SECRET_SCOPE_NAME}'...")
            
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
                    secret_value = client.secrets.get_secret(
                        scope=self.SECRET_SCOPE_NAME,
                        key=kv_secret
                    )
                    if secret_value and secret_value.value:
                        loaded_secrets[config_key] = secret_value.value
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
    
    def test_connection(self, notebook_path: str = None) -> bool:
        """
        Testa conexão completa (extração + cliente + secrets)
        
        Args:
            notebook_path: Caminho opcional para notebook customizado
        
        Returns:
            True se teste passou, False caso contrário
        """
        try:
            print("\n🧪 TESTE DE CONEXÃO DINO SDK v1.1.5")
            print("=" * 50)
            
            # Teste 1: Verificar ambiente
            print("1️⃣ Verificando ambiente Databricks...")
            if not self.is_databricks_environment():
                print("❌ Não está em ambiente Databricks")
                return False
            print("✅ Ambiente Databricks detectado")
            
            # Teste 2: Extrair contexto
            print("\n2️⃣ Extraindo contexto...")
            context = self.get_databricks_context(use_cache=False, notebook_path=notebook_path)
            if not context:
                print("❌ Falha na extração de contexto")
                return False
            print(f"✅ Contexto extraído via {context.get('extraction_method', 'unknown')}")
            
            # Teste 3: Criar cliente
            print("\n3️⃣ Criando cliente Databricks...")
            client = self.create_databricks_client(context)
            if not client:
                print("❌ Falha na criação do cliente")
                return False
            print("✅ Cliente Databricks criado")
            
            # Teste 4: Carregar secrets
            print("\n4️⃣ Carregando secrets...")
            secrets = self.load_secrets_from_scope(context)
            print(f"✅ {len(secrets)} secrets carregados")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ DINO SDK v1.1.5 está funcionando corretamente")
            
            return True
            
        except Exception as e:
            print(f"\n❌ TESTE FALHOU: {e}")
            return False

# Função de conveniência para uso rápido
def quick_setup(notebook_path: str = None) -> KeyVaultConfigWithNotebook:
    """
    Configuração rápida do KeyVault com notebook
    
    Args:
        notebook_path: Caminho opcional para notebook customizado
    
    Returns:
        Instância configurada do KeyVaultConfig
    """
    config = KeyVaultConfigWithNotebook()
    
    # Testar conexão
    if config.test_connection(notebook_path):
        print("🎯 Configuração concluída com sucesso!")
        return config
    else:
        raise RuntimeError("❌ Falha na configuração inicial")

# Função para extrair apenas o contexto
def extract_databricks_context(notebook_path: str = None, use_cache: bool = True) -> Dict[str, Any]:
    """
    Função standalone para extrair contexto Databricks
    
    Args:
        notebook_path: Caminho opcional para notebook
        use_cache: Se deve usar cache
    
    Returns:
        Contexto Databricks extraído
    """
    config = KeyVaultConfigWithNotebook()
    return config.get_databricks_context(use_cache=use_cache, notebook_path=notebook_path)
