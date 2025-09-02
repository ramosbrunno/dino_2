#!/usr/bin/env python3
"""
Dino SDK - Configuration Manager
Gerenciador de configurações e credenciais para Databricks
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Gerenciador de configurações do Dino SDK
    
    Prioridade de configuração:
    1. Variáveis de ambiente do cluster Databricks
    2. Arquivo de configuração local
    3. Valores padrão
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa o gerenciador de configuração
        
        Args:
            config_file: Caminho para arquivo de configuração (opcional)
        """
        self.config_file = config_file or os.path.join(Path.home(), '.dino_config.json')
        self.logger = logging.getLogger(__name__)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações de múltiplas fontes"""
        config = self._get_default_config()
        
        # 1. Carregar do arquivo de configuração se existir
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                self.logger.info(f"Configuração carregada de {self.config_file}")
            except Exception as e:
                self.logger.warning(f"Erro ao carregar {self.config_file}: {e}")
        
        # 2. Sobrescrever com variáveis de ambiente do Databricks
        env_config = self._get_env_config()
        config.update(env_config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configurações padrão do SDK"""
        return {
            'catalog_name': 'main',
            'checkpoint_base_path': '/tmp/checkpoints/dino_sdk',
            'volume_base_path': '/Volumes',
            'job_cluster_config': {
                'spark_version': '13.3.x-scala2.12',
                'node_type_id': 'i3.xlarge',
                'num_workers': 2,
                'spark_conf': {
                    'spark.databricks.delta.autoCompact.enabled': 'true',
                    'spark.databricks.delta.optimizeWrite.enabled': 'true'
                }
            },
            'autoloader_options': {
                'cloudFiles.format': 'csv',
                'cloudFiles.schemaLocation': '/tmp/schemas/dino_sdk',
                'cloudFiles.inferColumnTypes': 'true',
                'cloudFiles.schemaEvolutionMode': 'addNewColumns'
            },
            'genie_config': {
                'description_template': 'Tabela gerada pelo Dino SDK para {table_name} no schema {schema}',
                'tags': ['dino-sdk', 'auto-generated']
            }
        }
    
    def _get_env_config(self) -> Dict[str, Any]:
        """Carrega configurações das variáveis de ambiente do Databricks"""
        env_config = {}
        
        # Mapeamento de variáveis de ambiente para configurações
        env_mapping = {
            'DINO_CATALOG_NAME': 'catalog_name',
            'DINO_CHECKPOINT_BASE_PATH': 'checkpoint_base_path',
            'DINO_VOLUME_BASE_PATH': 'volume_base_path',
            'DATABRICKS_WORKSPACE_URL': 'workspace_url',
            'DATABRICKS_TOKEN': 'access_token',
            'DINO_DEFAULT_CLUSTER_ID': 'default_cluster_id',
            'DINO_JOB_CLUSTER_POLICY_ID': 'job_cluster_policy_id'
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                env_config[config_key] = value
                self.logger.debug(f"Configuração {config_key} carregada da variável {env_var}")
        
        # Configurações específicas do Spark
        spark_conf = {}
        for key, value in os.environ.items():
            if key.startswith('DINO_SPARK_'):
                spark_key = key.replace('DINO_SPARK_', 'spark.').lower()
                spark_conf[spark_key] = value
        
        if spark_conf:
            env_config.setdefault('job_cluster_config', {})['spark_conf'] = spark_conf
        
        return env_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self._config.get(key, default)
    
    def get_catalog_name(self) -> str:
        """Obtém nome do catálogo configurado"""
        return self.get('catalog_name', 'main')
    
    def get_checkpoint_location(self, schema: str, table: str) -> str:
        """Gera localização do checkpoint para uma tabela"""
        base_path = self.get('checkpoint_base_path')
        return f"{base_path}/{schema}/{table}"
    
    def get_schema_location(self, schema: str, table: str) -> str:
        """Gera localização do schema para Auto Loader"""
        base_path = self.get('autoloader_options', {}).get('cloudFiles.schemaLocation', '/tmp/schemas/dino_sdk')
        return f"{base_path}/{schema}/{table}"
    
    def get_job_cluster_config(self) -> Dict[str, Any]:
        """Obtém configuração do cluster para jobs"""
        return self.get('job_cluster_config', {})
    
    def get_autoloader_options(self, file_format: str = 'csv') -> Dict[str, str]:
        """Obtém opções do Auto Loader"""
        options = self.get('autoloader_options', {}).copy()
        options['cloudFiles.format'] = file_format
        return options
    
    def get_genie_config(self) -> Dict[str, Any]:
        """Obtém configuração do Genie"""
        return self.get('genie_config', {})
    
    def save_config(self, config_updates: Dict[str, Any]):
        """Salva atualizações no arquivo de configuração"""
        self._config.update(config_updates)
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.logger.info(f"Configuração salva em {self.config_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
            raise
    
    def validate_databricks_config(self) -> bool:
        """Valida se as configurações do Databricks estão presentes"""
        required_configs = ['workspace_url']
        
        for config in required_configs:
            if not self.get(config):
                self.logger.error(f"Configuração obrigatória ausente: {config}")
                return False
        
        return True
    
    def show_config(self) -> Dict[str, Any]:
        """Retorna configuração atual (mascarando tokens)"""
        config = self._config.copy()
        
        # Mascarar tokens e senhas
        sensitive_keys = ['access_token', 'password', 'secret', 'azure_sql_password']
        for key in sensitive_keys:
            if key in config and config[key]:
                config[key] = '*' * 8
        
        return config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Atualiza configuração com novos valores
        
        Args:
            updates: Dicionário com atualizações de configuração
            
        Returns:
            True se atualizou com sucesso
        """
        try:
            # Atualizar configuração em memória
            self._config.update(updates)
            
            # Salvar no arquivo
            self._save_config()
            
            self.logger.info(f"Configuração atualizada com {len(updates)} mudanças")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configuração: {e}")
            return False
    
    def _save_config(self):
        """Salva configuração atual no arquivo"""
        try:
            # Criar diretório se não existir
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Salvar configuração (sem valores padrão para não poluir o arquivo)
            config_to_save = {}
            defaults = self._get_default_config()
            
            for key, value in self._config.items():
                # Só salvar se for diferente do padrão
                if key not in defaults or defaults[key] != value:
                    config_to_save[key] = value
            
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
                
            self.logger.debug(f"Configuração salva em {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
    
    def set_config(self, key: str, value: Any):
        """
        Define um valor específico de configuração
        
        Args:
            key: Chave da configuração
            value: Valor a ser definido
        """
        self._config[key] = value
        self._save_config()
    
    def get_config_file_path(self) -> str:
        """Retorna o caminho do arquivo de configuração"""
        return self.config_file


# Singleton instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Obtém instância singleton do gerenciador de configuração"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
