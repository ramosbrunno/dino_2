# 🔧 CORREÇÃO COMPLETA PARA O NOTEBOOK - test_ingestion_engine.ipynb
# Substitua as células problemáticas pelos códigos corretos abaixo:

# ========================================
# CÉLULA 14 - Test SchemaManager (CORRIGIDA)
# ========================================
# Test da classe SchemaManager
print("=== Test SchemaManager ===")
try:
    # SchemaManager requer catalog e schema no construtor
    catalog_name = TEST_CONFIG["target_catalog"]
    schema_name = TEST_CONFIG["target_schema"]
    
    schema_manager = SchemaManager(catalog_name, schema_name)
    print("✅ SchemaManager instantiated successfully")
    
    print(f"\nCriando estrutura Unity Catalog:")
    print(f"  Catalog: {catalog_name}")
    print(f"  Schema: {catalog_name}.{schema_name}")
    
    # Verificar se existem (métodos recebem spark como parâmetro)
    catalog_exists = schema_manager.catalog_exists(spark)
    schema_exists = schema_manager.schema_exists(spark)
    
    print(f"\n✅ Catalog '{catalog_name}' exists: {catalog_exists}")
    print(f"✅ Schema '{catalog_name}.{schema_name}' exists: {schema_exists}")
    
    # Se não existirem, criar
    if not catalog_exists:
        schema_manager.create_catalog_if_not_exists(spark)
        print(f"✅ Catalog '{catalog_name}' created")
    
    if not schema_exists:
        schema_manager.create_schema_if_not_exists(spark)
        print(f"✅ Schema '{catalog_name}.{schema_name}' created")
    
except Exception as e:
    print(f"❌ Erro no SchemaManager: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# CÉLULA 16 - Test DataReader (CORRIGIDA)
# ========================================
# Test da classe DataReader
print("=== Test DataReader ===")
try:
    # DataReader é uma classe com métodos estáticos
    print("✅ DataReader class available (static methods)")
    
    # Criar IngestionConfig para usar com DataReader
    ingestion_config = IngestionConfig(
        source_path=TEST_CONFIG["source_path"],
        catalog_name=TEST_CONFIG["target_catalog"],
        schema_name=TEST_CONFIG["target_schema"],
        table_name=TEST_CONFIG["target_table"],
        file_extension="csv",
        type_run="batch"
    )
    
    print(f"\nLendo dados de: {TEST_CONFIG['source_path']}")
    
    # Usar método estático read_data
    print("1. Reading data with DataReader.read_data():")
    df = DataReader.read_data(spark, ingestion_config)
    
    print(f"   ✅ Data read successful with AutoLoader")
    print(f"   Is Streaming: {df.isStreaming}")
    
    # Mostrar schema
    print("   Schema:")
    df.printSchema()
    
    # Para batch, podemos fazer count (para streaming seria diferente)
    if not df.isStreaming:
        row_count = df.count()
        print(f"   Row count: {row_count}")
        
        # Sample data
        print("   Sample data (5 rows):")
        df.show(5)
    else:
        print("   (Streaming DataFrame - use writeStream para processar)")
    
except Exception as e:
    print(f"❌ Erro no DataReader: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# CÉLULA 18 - Test DataSaver (CORRIGIDA)  
# ========================================
# Test da classe DataSaver
print("=== Test DataSaver ===")
try:
    # DataSaver é uma classe com métodos estáticos
    print("✅ DataSaver class available (static methods)")
    
    # Preparar target location
    target_location = f"{TEST_CONFIG['target_catalog']}.{TEST_CONFIG['target_schema']}.{TEST_CONFIG['target_table']}"
    
    print(f"\nSalvando dados em: {target_location}")
    print(f"Liquid Clustering: {TEST_CONFIG['enable_liquid_clustering']}")
    print(f"Clustering Columns: {TEST_CONFIG['clustering_columns']}")
    
    # Para demo, vamos usar um DataFrame batch simples
    if 'df' not in locals() or df.isStreaming:
        # Criar um DataFrame batch para salvar
        batch_config = IngestionConfig(
            source_path=TEST_CONFIG["source_path"],
            catalog_name=TEST_CONFIG["target_catalog"],
            schema_name=TEST_CONFIG["target_schema"],
            table_name=TEST_CONFIG["target_table"],
            file_extension="csv",
            type_run="batch"
        )
        df = DataReader.read_data(spark, batch_config)
        
        # Se ainda for streaming, converter para batch
        if df.isStreaming:
            print("   Converting streaming to batch for demo...")
            # Para demo, vamos ler diretamente sem AutoLoader
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(TEST_CONFIG["source_path"])
    
    # Usar método estático save_data
    print("   Saving with DataSaver.save_data():")
    
    # Atualizar config com tabela de destino
    save_config = IngestionConfig(
        source_path=TEST_CONFIG["source_path"],
        catalog_name=TEST_CONFIG["target_catalog"],
        schema_name=TEST_CONFIG["target_schema"],
        table_name=TEST_CONFIG["target_table"],
        file_extension="csv",
        type_run="batch"
    )
    
    result = DataSaver.save_data(spark, df, save_config)
    
    print(f"✅ Data saved successfully to {target_location}")
    print(f"✅ Save result: {result}")
    
    # Verificar dados salvos
    verification_df = spark.table(target_location)
    saved_count = verification_df.count()
    
    print(f"✅ Verification: Table has {saved_count} rows")
    
    # Mostrar sample dos dados salvos
    print("\nSample from saved table:")
    verification_df.show(5)
    
except Exception as e:
    print(f"❌ Erro no DataSaver: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# CÉLULA 20 - Test IngestionEngine (CORRIGIDA)
# ========================================
# Test completo da IngestionEngine
print("=== Test Completo IngestionEngine ===")
try:
    # Instantiar IngestionEngine
    engine = IngestionEngine(spark)
    print("✅ IngestionEngine instantiated successfully")
    
    # Nova tabela para test end-to-end
    complete_table_name = "sales_complete_ingestion"
    complete_config = IngestionConfig(
        source_path=TEST_CONFIG["source_path"],
        catalog_name=TEST_CONFIG["target_catalog"],
        schema_name=TEST_CONFIG["target_schema"],
        table_name=complete_table_name,
        file_extension="csv",
        type_run="batch"  # ou "streaming"
    )
    
    print(f"\n🚀 Executando ingestão completa:")
    print(f"  Source: {complete_config.source_path}")
    print(f"  Target: {complete_config.catalog_name}.{complete_config.schema_name}.{complete_config.table_name}")
    print(f"  Type: {complete_config.type_run}")
    
    # Usar método correto: ingest() (não ingest_data())
    result = engine.ingest(complete_config)
    
    print(f"\n✅ IngestionEngine.ingest() result: {result}")
    
    # Verificar resultado final
    complete_table_full = f"{complete_config.catalog_name}.{complete_config.schema_name}.{complete_config.table_name}"
    final_df = spark.table(complete_table_full)
    final_count = final_df.count()
    
    print(f"✅ Final verification: {complete_table_full} has {final_count} rows")
    
    # Sample final
    print("\nFinal table sample:")
    final_df.show(5)
    
    print("\n🎉 IngestionEngine test completo executado com sucesso!")
    
    # Mostrar métodos disponíveis
    engine_methods = [m for m in dir(engine) if not m.startswith('_')]
    print(f"\n📋 IngestionEngine methods available: {engine_methods}")
    
except Exception as e:
    print(f"❌ Erro no IngestionEngine: {e}")
    import traceback
    traceback.print_exc()
