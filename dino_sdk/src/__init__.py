"""
Dino SDK - Data Ingestion SDK for Databricks
SDK simplificado para automação de ingestão de dados no Databricks com Unity Catalog
"""

__version__ = "1.0.0"
__author__ = "Data Master Team"
__email__ = "support@datamaster.com"

# Funções de configuração programática para uso direto em notebooks
from .programmatic_config import (
    configure_dino_sdk,
    validate_dino_config, 
    show_dino_config,
    quick_setup,
    setup_with_azure_sql
)

# Funções principais para importação direta
def get_ingestion_engine():
    """Importa IngestionEngine evitando dependências circulares"""
    from .ingestion_engine import IngestionEngine
    return IngestionEngine

def get_genie_assistant():
    """Importa GenieAssistant evitando dependências circulares"""
    from .genie_assistant import GenieAssistant
    return GenieAssistant

def get_job_manager():
    """Importa JobManager evitando dependências circulares"""
    from .job_manager import JobManager
    return JobManager

def get_workflow_manager():
    """Importa WorkflowManager evitando dependências circulares"""
    from .workflow_manager import WorkflowManager
    return WorkflowManager
