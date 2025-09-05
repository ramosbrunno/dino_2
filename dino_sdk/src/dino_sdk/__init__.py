"""
🦕 DINO SDK v1.2.0

Databricks Integration and Orchestration SDK
Unity Catalog focused, KeyVault-free implementation

Main Components:
- SchemaManager: Unity Catalog schema operations
- IngestionEngine: Carlton-based data ingestion with AutoLoader
- DataReader: Reading data with AutoLoader support
- DataSaver: Saving data with Liquid Clustering support
- ConfigValidator: Configuration validation

Usage:
    from dino_sdk import (
        SchemaManager, 
        IngestionEngine,
        DataReader,
        DataSaver,
        ConfigValidator,
        ingest_csv_to_unity_catalog
    )
"""

__version__ = "1.2.0"
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
    ingest_csv_to_unity_catalog
)

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
    
    # Version info
    '__version__'
]
