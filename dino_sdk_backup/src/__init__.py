"""
Dino SDK - Data Ingestion SDK for Databricks
SDK simplificado para automação de ingestão de dados no Databricks com Unity Catalog
"""

__version__ = "1.3.0"
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

# Imports diretos para WorkflowManager (função helper implementada no workflow_manager.py)
try:
    from .workflow_manager import (
        DinoWorkflowManager, 
        DinoWorkflowConfig, 
        create_dino_workflow
    )
    __all__ = [
        'configure_dino_sdk', 'validate_dino_config', 'show_dino_config',
        'quick_setup', 'setup_with_azure_sql', 'create_unity_catalog_schema',
        'get_ingestion_engine', 'get_genie_assistant', 'get_job_manager', 'get_workflow_manager',
        'DinoWorkflowManager', 'DinoWorkflowConfig', 'create_dino_workflow'
    ]
except ImportError as e:
    # WorkflowManager não implementado ainda, usar apenas o básico
    __all__ = [
        'configure_dino_sdk', 'validate_dino_config', 'show_dino_config',
        'quick_setup', 'setup_with_azure_sql', 'create_unity_catalog_schema',
        'get_ingestion_engine', 'get_genie_assistant', 'get_job_manager', 'get_workflow_manager'
    ]

# Funções de criação de Schema no Unity Catalog
def create_unity_catalog_schema(catalog_name: str, schema_name: str) -> bool:
    """
    Cria schema no Unity Catalog usando External Location
    
    Args:
        catalog_name: Nome do catálogo Unity Catalog
        schema_name: Nome do schema a ser criado
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        # No Databricks, usar a sessão Spark existente
        try:
            # Tentar usar variável global spark do Databricks
            spark_session = spark  # Esta variável deve existir no contexto Databricks
        except NameError:
            # Se não estiver no Databricks, tentar pyspark
            from pyspark.sql import SparkSession
            spark_session = SparkSession.getActiveSession()
            if not spark_session:
                print("❌ Este comando deve ser executado no ambiente Databricks")
                print("💡 No Databricks, a variável 'spark' está disponível globalmente")
                return False
        
        print(f"🦕 DINO SDK - Criação de Schema")
        print("=" * 40)
        print(f"� Catálogo: {catalog_name}")
        print(f"� Schema: {schema_name}")
        
        # Obter external location
        external_location = spark_session.sql(f"DESCRIBE EXTERNAL LOCATION {catalog_name}").select("url").collect()[0].url
        schema_location = f"{external_location}/{catalog_name}/{schema_name}/"
        
        print(f"📍 Localização: {schema_location}")
        
        # Criar schema
        spark_session.sql(f"""
            CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
            MANAGED LOCATION '{schema_location}'
        """)
        
        print(f"✅ Schema {catalog_name}.{schema_name} criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar schema: {e}")
        return False
