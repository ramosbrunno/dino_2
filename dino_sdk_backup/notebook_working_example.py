# 🦕 DINO SDK v1.2.0 - Notebook Working Example
# Cole este código diretamente no seu notebook Databricks

print("🦕 DINO SDK v1.2.0 - IngestionEngine Demo")
print("=" * 50)

# Configurações do seu ambiente
SOURCE_PATH = "/Volumes/data_master_dev_dbw/dino_v120_test/raw/fake_sales_100k.csv"
CATALOG_NAME = "data_master_dev_dbw"
SCHEMA_NAME = "dino_v120_test"
TABLE_NAME = "fake_sales_100k"

print(f"📁 Origem: {SOURCE_PATH}")
print(f"🎯 Destino: {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}")

# Método direto usando SQL e AutoLoader
print("\n🚀 Ingestão usando AutoLoader direto...")

try:
    # 1. Criar schema se não existir
    print("📂 Verificando schema...")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}")
    print(f"✅ Schema {CATALOG_NAME}.{SCHEMA_NAME} pronto")
    
    # 2. Ler dados usando AutoLoader
    print("📥 Lendo dados com AutoLoader...")
    
    df = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .option("cloudFiles.rescuedDataColumn", "_rescued")
        .option("header", "true")
        .option("delimiter", ",")
        .option("inferSchema", "false")
        .option("cloudFiles.inferColumnTypes", "false")
        .load(SOURCE_PATH)
        .select(
            "*",
            current_date().alias("dino_ingestion_date"),
            current_timestamp().alias("dino_ingestion_timestamp"),
            col("_metadata").alias("dino_metadata")
        )
    )
    
    print("✅ DataFrame criado com AutoLoader")
    
    # 3. Criar tabela Delta com Liquid Clustering
    table_full_name = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}"
    
    # Primeiro, obter schema das colunas (sample)
    sample_df = spark.read.format("csv").option("header", "true").load(SOURCE_PATH).limit(1)
    columns_list = [f"{col.lower()} STRING" for col in sample_df.columns]
    columns_definition = ", ".join(columns_list)
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_full_name} (
        {columns_definition},
        _rescued STRING,
        dino_ingestion_date DATE,
        dino_ingestion_timestamp TIMESTAMP,
        dino_metadata STRUCT<
            file_path: STRING,
            file_name: STRING,
            file_size: BIGINT,
            file_block_start: BIGINT,
            file_block_length: BIGINT,
            file_modification_time: TIMESTAMP
        >
    )
    USING DELTA
    CLUSTER BY AUTO
    """
    
    print("🏗️ Criando tabela Delta com Liquid Clustering...")
    spark.sql(create_table_sql)
    print(f"✅ Tabela {table_full_name} criada com CLUSTER BY AUTO")
    
    # 4. Ingestão batch
    print("📊 Iniciando ingestão batch...")
    
    query = (
        df.writeStream
        .outputMode("append")
        .format("delta")
        .trigger(availableNow=True)
        .option("checkpointLocation", f"/tmp/checkpoints/{TABLE_NAME}")
        .table(table_full_name)
    )
    
    # Aguardar conclusão
    query.awaitTermination()
    
    print("✅ Ingestão concluída com sucesso!")
    
    # 5. Verificar resultados
    print("\n📊 Verificando resultados...")
    
    result_df = spark.sql(f"SELECT COUNT(*) as total_rows FROM {table_full_name}")
    total_rows = result_df.collect()[0]["total_rows"]
    
    print(f"📈 Total de linhas ingeridas: {total_rows:,}")
    
    # Mostrar amostra dos dados
    print("\n🔍 Amostra dos dados ingeridos:")
    spark.sql(f"""
        SELECT *, dino_ingestion_date, dino_ingestion_timestamp 
        FROM {table_full_name} 
        LIMIT 5
    """).show(truncate=False)
    
    # Verificar metadados da tabela
    print("\n🏷️ Detalhes da tabela criada:")
    spark.sql(f"DESCRIBE DETAIL {table_full_name}").select("format", "location", "properties").show(truncate=False)
    
    print("\n🎉 Ingestão DINO SDK completada com sucesso!")
    print("✅ Tabela criada com Liquid Clustering (CLUSTER BY AUTO)")
    print("✅ Metadados de ingestão adicionados automaticamente")
    print("✅ Dados disponíveis para consulta no Unity Catalog")

except Exception as e:
    print(f"❌ Erro durante a ingestão: {str(e)}")
    print("💡 Verifique:")
    print("   - Se o arquivo existe no caminho especificado")
    print("   - Se você tem permissões no catálogo e schema")
    print("   - Se o formato do arquivo está correto")
    
    # Debug: Listar arquivos no volume
    try:
        files_df = spark.sql("LIST '/Volumes/data_master_dev_dbw/dino_v120_test/raw/'")
        print("\n📁 Arquivos encontrados no volume:")
        files_df.show()
    except:
        print("⚠️ Não foi possível listar arquivos no volume")

# Comandos úteis para debug
print(f"\n🔧 Comandos úteis para debug:")
print(f"# Verificar se tabela foi criada:")
print(f"spark.sql('SHOW TABLES IN {CATALOG_NAME}.{SCHEMA_NAME}').show()")
print(f"")
print(f"# Ver dados da tabela:")
print(f"spark.sql('SELECT * FROM {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME} LIMIT 10').show()")
print(f"")
print(f"# Verificar detalhes da tabela:")
print(f"spark.sql('DESCRIBE DETAIL {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}').show()")
