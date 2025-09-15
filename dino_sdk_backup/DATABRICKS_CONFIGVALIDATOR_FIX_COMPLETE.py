# 🔧 CORREÇÃO COMPLETA PARA DATABRICKS - ConfigValidator
# Substitua TODA a célula do ConfigValidator test por este código:

# Test do ConfigValidator - VERSÃO TOTALMENTE CORRIGIDA
validator = ConfigValidator()

# Configuração de exemplo
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

print("Configuration:")
for key, value in config_dict.items():
    print(f"  {key}: {value}")
print()

# Test validação usando IngestionConfig
try:
    from dino_sdk import IngestionConfig
    
    # Criar objeto IngestionConfig
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
    print()
    
    # ÚNICA validação disponível
    validation_result = validator.validate_ingestion_config(ingestion_config)
    print("✅ IngestionConfig validation completed:", validation_result)
    print()
    
    # Mostrar métodos disponíveis
    available_methods = [m for m in dir(validator) if not m.startswith('_')]
    print("✅ ConfigValidator methods available:", available_methods)
    print()
    
    print("🎉 ConfigValidator funcionando perfeitamente!")
    print("📝 Nota: ConfigValidator tem apenas 2 métodos:")
    print("   - validate_ingestion_config(config: IngestionConfig)")  
    print("   - validate_args(required_args: List[str], config: Dict[str, Any])")
    print()
    print("❌ Métodos que NÃO existem (remover se estiverem no notebook):")
    print("   - validate_basic_config() ❌")
    print("   - validate_autoloader_config() ❌") 
    print("   - validate_clustering_config() ❌")
    
except Exception as e:
    print("❌ ConfigValidator test failed:", e)
    import traceback
    traceback.print_exc()
