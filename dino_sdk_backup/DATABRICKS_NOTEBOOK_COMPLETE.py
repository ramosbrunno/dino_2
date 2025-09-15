# 🦕 DINO SDK v1.2.0 - Solução para Notebook Databricks
# Cole este código COMPLETO no seu notebook

print("🦕 DINO SDK v1.2.0 - Ingestão com AutoLoader")
print("=" * 55)

# Imports necessários (já disponíveis no Databricks)
from pyspark.sql.functions import col, current_date, current_timestamp

# Suas configurações
SOURCE_PATH = "/Volumes/data_master_dev_dbw/dino_v120_test/raw/fake_sales_100k.csv"
CATALOG_NAME = "data_master_dev_dbw"
SCHEMA_NAME = "dino_v120_test" 
TABLE_NAME = "fake_sales_100k"

print(f"📁 Origem: {SOURCE_PATH}")
print(f"🎯 Destino: {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}")

try:
    # 1. Verificar se arquivo existe
    print("\n🔍 Verificando arquivo...")
    try:
        # Tentar listar o volume
        volume_files = spark.sql(f"LIST '{SOURCE_PATH.rsplit('/', 1)[0]}/'")
        files_list = [row.path for row in volume_files.collect()]
        
        if SOURCE_PATH in files_list or any(SOURCE_PATH.split('/')[-1] in path for path in files_list):
            print("✅ Arquivo encontrado no volume")
        else:
            print("⚠️ Arquivo não encontrado, mas continuando...")
            print("📁 Arquivos disponíveis:")
            volume_files.show(10, truncate=False)
    except Exception as e:
        print(f"⚠️ Não foi possível verificar volume: {e}")
    
    # 2. Criar schema se não existir
    print(f"\n📂 Criando schema {CATALOG_NAME}.{SCHEMA_NAME}...")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}")
    print("✅ Schema criado/verificado")
    
    # 3. Configurar AutoLoader para CSV
    print("\n⚙️ Configurando AutoLoader...")
    
    autoloader_options = {
        "cloudFiles.format": "csv",
        "cloudFiles.schemaEvolutionMode": "rescue", 
        "cloudFiles.rescuedDataColumn": "_rescued",
        "header": "true",
        "delimiter": ",",
        "inferSchema": "false",
        "cloudFiles.inferColumnTypes": "false"
    }
    
    print("📊 Configurações do AutoLoader:")
    for key, value in autoloader_options.items():
        print(f"   • {key}: {value}")
    
    # 4. Criar DataFrame com AutoLoader
    print("\n📥 Criando DataFrame com AutoLoader...")
    
    df = (
        spark.readStream
        .format("cloudFiles")
        .options(**autoloader_options)
        .load(SOURCE_PATH)
        .select(
            "*",
            current_date().alias("dino_ingestion_date"),
            current_timestamp().alias("dino_ingestion_timestamp"), 
            col("_metadata").alias("dino_metadata")
        )
    )
    
    print("✅ DataFrame streaming criado")
    print("✅ Colunas de metadados DINO adicionadas")
    
    # 5. Obter schema das colunas para criar tabela
    print("\n🏗️ Preparando estrutura da tabela...")
    
    # Ler uma amostra para descobrir as colunas
    sample_df = (
        spark.read
        .format("csv")
        .option("header", "true")
        .option("delimiter", ",")
        .load(SOURCE_PATH)
        .limit(1)
    )
    
    # Gerar definição das colunas (todas STRING)
    data_columns = [f"`{col}` STRING" for col in sample_df.columns]
    columns_definition = ",\n        ".join(data_columns)
    
    print(f"📋 Colunas detectadas: {len(sample_df.columns)}")
    for col_name in sample_df.columns[:5]:  # Mostrar apenas as primeiras 5
        print(f"   • {col_name}")
    if len(sample_df.columns) > 5:
        print(f"   ... e mais {len(sample_df.columns) - 5} colunas")
    
    # 6. Criar tabela Delta com Liquid Clustering
    table_full_name = f"`{CATALOG_NAME}`.`{SCHEMA_NAME}`.`{TABLE_NAME}`"
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_full_name} (
        {columns_definition},
        `_rescued` STRING,
        `dino_ingestion_date` DATE,
        `dino_ingestion_timestamp` TIMESTAMP,
        `dino_metadata` STRUCT<
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
    
    print(f"\n🏗️ Criando tabela Delta com Liquid Clustering...")
    print("⚡ Usando CLUSTER BY AUTO para otimização automática")
    
    spark.sql(create_table_sql)
    print(f"✅ Tabela {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME} criada")
    
    # 7. Executar ingestão batch
    print(f"\n📊 Iniciando ingestão batch...")
    
    checkpoint_location = f"/tmp/dino_checkpoints/{SCHEMA_NAME}_{TABLE_NAME}"
    print(f"💾 Checkpoint: {checkpoint_location}")
    
    query = (
        df.writeStream
        .outputMode("append")
        .format("delta")
        .trigger(availableNow=True)  # Batch processing
        .option("checkpointLocation", checkpoint_location)
        .table(f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}")
    )
    
    print("⏳ Aguardando conclusão da ingestão...")
    query.awaitTermination()
    
    print("✅ Ingestão batch concluída com sucesso!")
    
    # 8. Verificar resultados
    print(f"\n📈 Verificando resultados...")
    
    # Contar registros
    count_result = spark.sql(f"""
        SELECT COUNT(*) as total_rows 
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
    """)
    
    total_rows = count_result.collect()[0]["total_rows"]
    print(f"📊 Total de registros ingeridos: {total_rows:,}")
    
    # Verificar dados recém-ingeridos
    recent_data = spark.sql(f"""
        SELECT COUNT(*) as today_rows 
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
        WHERE dino_ingestion_date = current_date()
    """)
    
    today_rows = recent_data.collect()[0]["today_rows"] 
    print(f"📅 Registros ingeridos hoje: {today_rows:,}")
    
    # 9. Mostrar amostra dos dados
    print(f"\n🔍 Amostra dos dados ingeridos:")
    spark.sql(f"""
        SELECT *, dino_ingestion_date, dino_ingestion_timestamp
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
        ORDER BY dino_ingestion_timestamp DESC
        LIMIT 3
    """).show(truncate=False)
    
    # 10. Verificar detalhes da tabela
    print(f"\n🏷️ Detalhes da tabela criada:")
    table_details = spark.sql(f"""
        DESCRIBE DETAIL {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
    """)
    
    for row in table_details.collect():
        print(f"   📊 Formato: {row.format}")
        print(f"   📍 Localização: {row.location}")
        print(f"   🔧 Provider: {row.provider}")
        print(f"   📏 Tamanho: {row.sizeInBytes} bytes")
        break
    
    # 11. Comandos úteis
    print(f"\n💡 Comandos úteis para continuar:")
    print(f"# Ver todas as tabelas do schema:")
    print(f"spark.sql('SHOW TABLES IN {CATALOG_NAME}.{SCHEMA_NAME}').show()")
    print(f"")
    print(f"# Consultar dados:")
    print(f"spark.sql('SELECT * FROM {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME} LIMIT 10').show()")
    print(f"")
    print(f"# Ver estatísticas:")
    print(f"spark.sql('DESCRIBE EXTENDED {CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}').show()")
    
    print(f"\n🎉 DINO SDK v1.2.0 - Ingestão completada com sucesso!")
    print("✅ AutoLoader configurado corretamente")
    print("✅ Tabela Delta criada com Liquid Clustering")
    print("✅ Metadados de ingestão adicionados")
    print("✅ Dados disponíveis no Unity Catalog")

except Exception as e:
    print(f"\n❌ Erro durante a ingestão:")
    print(f"   {str(e)}")
    
    print(f"\n🔧 Troubleshooting:")
    print(f"1. Verifique se o arquivo existe:")
    print(f"   spark.sql(\"LIST '/Volumes/data_master_dev_dbw/dino_v120_test/raw/'\").show()")
    print(f"")
    print(f"2. Verifique permissões no catálogo:")
    print(f"   spark.sql('SHOW SCHEMAS IN {CATALOG_NAME}').show()")
    print(f"")
    print(f"3. Teste com arquivo menor:")
    print(f"   Tente com um arquivo CSV menor primeiro")
    
    # Tentar listar arquivos para debug
    try:
        print(f"\n📁 Tentando listar arquivos do volume:")
        debug_files = spark.sql("LIST '/Volumes/data_master_dev_dbw/dino_v120_test/raw/'")
        debug_files.show(20, truncate=False)
    except Exception as debug_e:
        print(f"⚠️ Não foi possível listar arquivos: {debug_e}")
        
    import traceback
    print(f"\n🔍 Stack trace completo:")
    traceback.print_exc()
