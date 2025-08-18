"""
Dino SDK - Data Ingestion SDK for Databricks
SDK simplificado para automação de ingestão de dados no Databricks com Unity Catalog
"""

__version__ = "1.0.0"
__author__ = "Data Master Team"
__email__ = "support@datamaster.com"

# Imports principais
from ingestion_engine import IngestionEngine
from workflow_manager import WorkflowManager  
from genie_assistant import GenieAssistant

__all__ = [
    'IngestionEngine',
    'WorkflowManager', 
    'GenieAssistant'
]
