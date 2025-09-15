"""
Arquivo __init__.py para o diretório de testes
Permite que o diretório seja tratado como um pacote Python
"""

# Imports para facilitar o uso dos testes
from .test_ingestion_engine import TestIngestionEngine
from .test_workflow_manager import TestWorkflowManager
from .test_genie_assistant import TestGenieAssistant
from .test_integration import TestSDKIntegration

__all__ = [
    'TestIngestionEngine',
    'TestWorkflowManager', 
    'TestGenieAssistant',
    'TestSDKIntegration'
]
