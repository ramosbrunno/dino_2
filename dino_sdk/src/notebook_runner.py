"""
🔧 Notebook Runner - DINO SDK v1.1.4
Executa notebooks Databricks internos para extrair tokens e configurações
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class NotebookRunner:
    """
    Classe para executar notebooks Databricks e extrair configurações
    """
    
    def __init__(self, timeout: int = 300):
        """
        Inicializa o runner de notebooks
        
        Args:
            timeout: Timeout em segundos para execução do notebook
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def is_databricks_environment(self) -> bool:
        """
        Verifica se está rodando em ambiente Databricks
        
        Returns:
            True se estiver em ambiente Databricks
        """
        try:
            import dbutils
            return True
        except ImportError:
            try:
                # Tentar acessar dbutils via eval
                dbutils = eval('dbutils')
                return dbutils is not None
            except:
                return False
    
    def run_notebook(self, path: str, params: Dict[str, str] = None) -> str:
        """
        Executa um notebook Databricks
        
        Args:
            path: Caminho para o notebook
            params: Parâmetros para passar ao notebook
            
        Returns:
            Resultado da execução do notebook
        """
        if params is None:
            params = {}
            
        try:
            if not self.is_databricks_environment():
                raise RuntimeError("Não está executando em ambiente Databricks")
            
            # Obter dbutils
            try:
                import dbutils
            except ImportError:
                dbutils = eval('dbutils')
            
            self.logger.info(f"🚀 Executando notebook: {path}")
            self.logger.info(f"📋 Parâmetros: {params}")
            self.logger.info(f"⏱️ Timeout: {self.timeout}s")
            
            # Executar notebook
            result = dbutils.notebook.run(path, self.timeout, params)
            
            self.logger.info(f"✅ Notebook executado com sucesso")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar notebook {path}: {e}")
            raise RuntimeError(f"Erro ao executar notebook {path}: {e}")
    
    def run_token_extraction_notebook(self, notebook_path: str = None) -> Dict[str, Any]:
        """
        Executa notebook específico para extrair token e configurações
        
        Args:
            notebook_path: Caminho para o notebook de extração (opcional)
            
        Returns:
            Dicionário com token e configurações extraídas
        """
        # Usar notebook padrão se não especificado
        if notebook_path is None:
            notebook_path = "/tmp/dino_sdk_token_extractor"
        
        try:
            self.logger.info("🔑 Executando notebook de extração de token...")
            
            # Executar notebook
            result = self.run_notebook(notebook_path)
            
            # Tentar parsear resultado como JSON
            try:
                extracted_data = json.loads(result)
                self.logger.info("✅ Dados extraídos com sucesso via notebook")
                return extracted_data
            except json.JSONDecodeError:
                # Se não for JSON, criar estrutura baseada no resultado
                self.logger.warning("⚠️ Resultado não é JSON válido, processando como texto")
                return {
                    'raw_result': result,
                    'extraction_method': 'notebook_text'
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro na extração via notebook: {e}")
            raise
    
    def create_and_run_inline_extraction(self) -> Dict[str, Any]:
        """
        Cria e executa extração inline usando dbutils diretamente
        Fallback quando notebook não estiver disponível
        
        Returns:
            Dicionário com token e configurações
        """
        try:
            self.logger.info("🔄 Executando extração inline...")
            
            if not self.is_databricks_environment():
                raise RuntimeError("Não está em ambiente Databricks")
            
            # Obter dbutils
            try:
                import dbutils
            except ImportError:
                dbutils = eval('dbutils')
            
            # Extrair configurações diretamente
            admin_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            databricks_instance = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
            
            # Garantir formato HTTPS
            if not databricks_instance.startswith('https://'):
                workspace_url = f"https://{databricks_instance}"
            else:
                workspace_url = databricks_instance
            
            # Criar estrutura de retorno
            result = {
                'admin_token': admin_token,
                'workspace_url': workspace_url,
                'databricks_instance': databricks_instance,
                'headers': {"Authorization": f"Bearer {admin_token}"},
                'extraction_method': 'inline_dbutils',
                'timestamp': str(datetime.now())
            }
            
            self.logger.info("✅ Extração inline bem-sucedida")
            masked_token = f"{admin_token[:15]}...{admin_token[-8:]}" if len(admin_token) > 23 else "***"
            self.logger.info(f"🔑 Token extraído: {masked_token}")
            self.logger.info(f"🌐 Workspace: {workspace_url}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração inline: {e}")
            raise
    
    def extract_databricks_config(self, notebook_path: str = None) -> Dict[str, Any]:
        """
        Método principal para extrair configurações Databricks
        Tenta notebook primeiro, depois fallback inline
        
        Args:
            notebook_path: Caminho opcional para notebook customizado
            
        Returns:
            Configurações extraídas
        """
        self.logger.info("🎯 Iniciando extração de configurações Databricks...")
        
        if not self.is_databricks_environment():
            raise RuntimeError("❌ Não está executando em ambiente Databricks. "
                             "Esta funcionalidade só funciona dentro do Databricks.")
        
        # Estratégia 1: Tentar executar notebook
        if notebook_path:
            try:
                self.logger.info("1️⃣ Tentando extração via notebook...")
                return self.run_token_extraction_notebook(notebook_path)
            except Exception as e:
                self.logger.warning(f"⚠️ Extração via notebook falhou: {e}")
        
        # Estratégia 2: Fallback para extração inline
        try:
            self.logger.info("2️⃣ Usando extração inline como fallback...")
            return self.create_and_run_inline_extraction()
        except Exception as e:
            self.logger.error(f"❌ Todas as estratégias falharam: {e}")
            raise RuntimeError(f"Não foi possível extrair configurações: {e}")

# Instância global para uso fácil
_notebook_runner = None

def get_notebook_runner(timeout: int = 300) -> NotebookRunner:
    """
    Obtém instância singleton do NotebookRunner
    
    Args:
        timeout: Timeout para execução de notebooks
        
    Returns:
        Instância do NotebookRunner
    """
    global _notebook_runner
    if _notebook_runner is None:
        _notebook_runner = NotebookRunner(timeout=timeout)
    return _notebook_runner

def extract_databricks_credentials(notebook_path: str = None) -> Dict[str, Any]:
    """
    Função de conveniência para extrair credenciais Databricks
    
    Args:
        notebook_path: Caminho opcional para notebook customizado
        
    Returns:
        Dicionário com credenciais extraídas
    """
    runner = get_notebook_runner()
    return runner.extract_databricks_config(notebook_path)
