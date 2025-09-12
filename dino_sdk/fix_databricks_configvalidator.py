# 🔧 CORREÇÃO RÁPIDA PARA DATABRICKS - ConfigValidator
# Substitua a célula do ConfigValidator test por este código:

# Test do ConfigValidator - VERSÃO CORRIGIDA
validator = ConfigValidator()

# Configuração de exemplo (dict para referência)
config_dict = {
    "source_path": "/Volumes/data_master_dev_dbw/dino_v120_test/raw/fake_sales_100k.csv",
    "target_catalog": "data_master_dev_dbw",
    "target_schema": "dino_v120_test", 
    "target_table": "sales_ingested",
    "file_format": "csv",
    "auto_create_catalog": True,
    "auto_create_schema": True,
    "enable_liquid_clustering": True,
    "clustering_columns": ["product_category", "region"],
    "checkpoint_location": "/Volumes/data_master_dev_dbw/dino_v120_test/checkpoints/sales_checkpoint"
}

# Test validação usando IngestionConfig CORRETA
try:
    from dino_sdk import IngestionConfig
    
    # Criar objeto IngestionConfig com os dados corretos
    ingestion_config = IngestionConfig(
        source_path=config_dict["source_path"],
        catalog_name=config_dict["target_catalog"],
        schema_name=config_dict["target_schema"],
        table_name=config_dict["target_table"],
        file_extension="csv",
        type_run="batch"
    )
    
    print("✅ IngestionConfig criado com sucesso!")
    print(f"  Source: {ingestion_config.source_path}")
    print(f"  Target: {ingestion_config.catalog_name}.{ingestion_config.schema_name}.{ingestion_config.table_name}")
    
    # Validar configuração
    validation_result = validator.validate_ingestion_config(ingestion_config)
    print("✅ IngestionConfig validation completed:", validation_result)
    
    print("✅ ConfigValidator methods available:", [m for m in dir(validator) if not m.startswith('_')])
    print("🎉 ConfigValidator funcionando perfeitamente!")
    
except Exception as e:
    print("❌ ConfigValidator test failed:", e)
    import traceback
    traceback.print_exc()
