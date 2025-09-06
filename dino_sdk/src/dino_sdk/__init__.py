"""
🦕 DINO SDK v2.0.0

Databricks Integration and Orchestration SDK
Unity Catalog focused, KeyVault-free implementation
✅ v2.0.0: SINTAXE FUNCIONANDO + FILE ARRIVAL TRIGGER!
🎯 Task() + NotebookTask() + JobSettings.from_dict() com trigger DINO SDK v1.6.0

Databricks Integration and Orchestration SDK
Unity Catalog focused, KeyVault-free implementation
✅ v1.6.0: CLASSES OFICIAIS do Databricks SDK implementadas!
🎯 Baseado na sua referência da documentação oficial

Main Components:
- SchemaManager: Unity Catalog schema operations
- IngestionEngine: Carlton-based data ingestion with AutoLoader
- DataReader: Reading data with AutoLoader support
- DataSaver: Saving data with Liquid Clustering support
- ConfigValidator: Configuration validation
- WorkflowManager: Databricks Jobs/Workflows creation and management

Usage:
    from dino_sdk import (
        SchemaManager, 
        IngestionEngine,
        DataReader,
        DataSaver,
        ConfigValidator,
        WorkflowManager,
        DinoWorkflowConfig,
        ingest_csv_to_unity_catalog,
        create_dino_workflow
    )
"""

__version__ = "2.0.0"
__author__ = "DINO Team"
__description__ = "Databricks Integration and Orchestration SDK"

# Schema Management
from .schema_manager import (
    SchemaManager,
    create_schema_simple
)

# Data Ingestion  
from .ingestion_engine import (
    IngestionEngine,
    IngestionConfig,
    DataReader,
    DataSaver,
    ConfigValidator,
    ingest_csv_to_unity_catalog,
    get_ingestion_engine
)

# Workflow Management
from .workflow_manager import (
    DinoWorkflowManager,
    DinoWorkflowConfig,
    create_dino_workflow
)

# ✅ Alias para compatibilidade
WorkflowManager = DinoWorkflowManager  # ✅ Alias para facilitar importação
WorkflowConfig = DinoWorkflowConfig   # ✅ Alias para facilitar importação

def create_dino_job(catalog_name: str, schema_name: str, table_name: str, is_automated: bool = False, **kwargs):
    """
    Função simplificada para criar jobs DINO conforme especificações do usuário
    
    Args:
        catalog_name: Nome do catálogo
        schema_name: Nome do schema  
        table_name: Nome da tabela
        is_automated: Se deve usar file arrival trigger
        **kwargs: Configurações adicionais
        
    Returns:
        Dict com resultado da criação
    """
    # ✅ Montar job_name conforme especificação: dino_ingestion_{catalago}_{schema}_{tabela}
    job_name = f"dino_ingestion_{catalog_name}_{schema_name}_{table_name}"
    
    # ✅ notebook_path fixo conforme especificação
    notebook_path = "/Workspace/dino/dino_ingestion"
    
    # ✅ source_path será resolvido automaticamente
    source_path = f"temp/{table_name}"  # Será resolvido pelo SDK
    
    # Criar configuração
    config = WorkflowConfig(
        job_name=job_name,
        notebook_path=notebook_path,
        catalog_name=catalog_name,
        schema_name=schema_name,
        table_name=table_name,
        source_path=source_path,
        is_automated=is_automated,
        # ✅ Removido auto_create_cluster - agora usa job_cluster automaticamente
        **kwargs
    )
    
    # Criar workflow
    manager = WorkflowManager()
    return manager.create_workflow(config)

# Main exports
__all__ = [
    # Schema Management
    'SchemaManager',
    'create_schema_simple',
    
    # Data Ingestion
    'IngestionEngine', 
    'IngestionConfig',
    'DataReader',
    'DataSaver', 
    'ConfigValidator',
    'ingest_csv_to_unity_catalog',
    'get_ingestion_engine',
    
    # Workflow Management
    'DinoWorkflowManager',
    'WorkflowManager',  # ✅ Alias adicionado
    'DinoWorkflowConfig',
    'WorkflowConfig',   # ✅ Alias adicionado
    'create_dino_workflow',
    'create_dino_job',  # ✅ Nova função simplificada
    
    # Version info
    '__version__'
]
