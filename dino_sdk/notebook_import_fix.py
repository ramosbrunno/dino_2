# 🦕 DINO SDK v1.2.0 - Notebook Import Fix

# Código para usar diretamente no notebook Databricks quando há problemas de import

print("🔧 Configurando imports do DINO SDK...")

# Método 1: Import direto das classes
try:
    from dino_sdk.ingestion_engine import (
        IngestionEngine,
        IngestionConfig, 
        DataReader,
        DataSaver,
        ConfigValidator,
        ingest_csv_to_unity_catalog
    )
    from dino_sdk.schema_manager import SchemaManager, create_schema_simple
    print("✅ Método 1: Import via dino_sdk funcionou!")
    
except ImportError as e1:
    print(f"⚠️ Método 1 falhou: {e1}")
    
    # Método 2: Import via src path
    try:
        from src.dino_sdk.ingestion_engine import (
            IngestionEngine,
            IngestionConfig,
            DataReader, 
            DataSaver,
            ConfigValidator,
            ingest_csv_to_unity_catalog
        )
        from src.dino_sdk.schema_manager import SchemaManager, create_schema_simple
        print("✅ Método 2: Import via src.dino_sdk funcionou!")
        
    except ImportError as e2:
        print(f"⚠️ Método 2 falhou: {e2}")
        
        # Método 3: Definir classes inline (última opção)
        print("🚨 Definindo classes inline...")
        
        from typing import Dict, Optional, Any, List
        from pyspark.sql import DataFrame, SparkSession
        from pyspark.sql.functions import col, current_date, current_timestamp
        from dataclasses import dataclass
        import logging
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        @dataclass
        class IngestionConfig:
            """Configuração para ingestão de dados no DINO SDK."""
            # Configurações de origem
            source_path: str
            file_extension: str = "csv"
            file_header: bool = True
            file_delimiter: str = ","
            
            # Configurações de destino Unity Catalog
            catalog_name: str = "main"
            schema_name: str = "default" 
            table_name: str = ""
            
            # Configurações de execução
            type_run: str = "batch"  # "batch" ou "streaming"
            trigger_processing_time: str = "10 seconds"
            
            # Configurações do AutoLoader
            schema_evolution_mode: str = "rescue"
            multiline: bool = False
            rescue_data_column: str = "_rescued"
            
            # Configurações personalizadas do Spark
            custom_spark_config: Dict[str, Any] = None
            
            def __post_init__(self):
                if self.custom_spark_config is None:
                    self.custom_spark_config = {}

        
        class ConfigValidator:
            """Validador de configurações para ingestão."""
            
            @staticmethod
            def validate_args(required_args: List[str], config: Dict[str, Any]) -> None:
                missing_args = [arg for arg in required_args if arg not in config or config[arg] is None]
                if missing_args:
                    raise ValueError(f"Argumentos obrigatórios ausentes: {missing_args}")
            
            @staticmethod
            def validate_ingestion_config(config: IngestionConfig) -> None:
                if not config.source_path:
                    raise ValueError("source_path é obrigatório")
                if not config.table_name:
                    raise ValueError("table_name é obrigatório")
                if config.type_run not in ["batch", "streaming"]:
                    raise ValueError("type_run deve ser 'batch' ou 'streaming'")

        
        class DataReader:
            """Leitor de dados usando AutoLoader do Databricks."""
            
            @staticmethod
            def read_data(spark: SparkSession, config: IngestionConfig) -> DataFrame:
                try:
                    logger.info(f"Configurando AutoLoader para leitura de {config.source_path}")
                    
                    # Configurações básicas do AutoLoader
                    autoloader_config = {
                        "cloudFiles.format": config.file_extension,
                        "cloudFiles.schemaEvolutionMode": config.schema_evolution_mode,
                        "cloudFiles.rescuedDataColumn": config.rescue_data_column,
                    }
                    
                    # Configurações específicas para CSV
                    if config.file_extension == "csv":
                        autoloader_config.update({
                            "header": str(config.file_header).lower(),
                            "delimiter": config.file_delimiter,
                            "inferSchema": "false",
                            "cloudFiles.inferColumnTypes": "false"
                        })
                        
                    if config.multiline:
                        autoloader_config["multiline"] = "true"
                    
                    autoloader_config.update(config.custom_spark_config)
                    
                    # Ler dados usando AutoLoader
                    df = (
                        spark.readStream
                        .format("cloudFiles")
                        .options(**autoloader_config)
                        .load(config.source_path)
                        .select(
                            "*",
                            current_date().alias("dino_ingestion_date"),
                            current_timestamp().alias("dino_ingestion_timestamp"),
                            col("_metadata").alias("dino_metadata")
                        )
                    )
                    
                    logger.info("Dados carregados com sucesso usando AutoLoader")
                    return df
                    
                except Exception as e:
                    logger.error(f"Erro na leitura dos dados: {str(e)}")
                    raise

        
        class DataSaver:
            """Salvador de dados no Unity Catalog usando Delta Lake."""
            
            @staticmethod
            def save_data(spark: SparkSession, df: DataFrame, config: IngestionConfig) -> None:
                try:
                    ConfigValidator.validate_args(
                        ['catalog_name', 'schema_name', 'table_name'], 
                        config.__dict__
                    )
                    
                    table_full_name = f"{config.catalog_name}.{config.schema_name}.{config.table_name}"
                    logger.info(f"Preparando para salvar dados em: {table_full_name}")
                    
                    DataSaver._create_table_if_not_exists(spark, df, config, table_full_name)
                    trigger_config = DataSaver._get_trigger_config(config)
                    
                    logger.info("Iniciando escrita dos dados")
                    
                    query = (
                        df.writeStream
                        .outputMode("append")
                        .format("delta")
                        .trigger(**trigger_config)
                        .option("checkpointLocation", f"/tmp/checkpoints/{config.table_name}")
                        .table(table_full_name)
                    )
                    
                    if config.type_run == "batch":
                        query.awaitTermination()
                        logger.info(f"Dados salvos com sucesso em {table_full_name}")
                    else:
                        logger.info(f"Stream iniciado para {table_full_name}")
                        return query
                        
                except Exception as e:
                    logger.error(f"Erro ao salvar dados: {str(e)}")
                    raise
            
            @staticmethod
            def _create_table_if_not_exists(spark: SparkSession, df: DataFrame, config: IngestionConfig, table_full_name: str) -> None:
                try:
                    internal_columns = [
                        config.rescue_data_column,
                        "dino_ingestion_date", 
                        "dino_ingestion_timestamp",
                        "dino_metadata"
                    ]
                    
                    if config.file_extension == "csv":
                        columns_definition = ", ".join([
                            f"{col.lower()} STRING" 
                            for col in df.columns 
                            if col not in internal_columns
                        ])
                    else:
                        columns_definition = ", ".join([
                            f"{col} STRING"
                            for col in df.columns 
                            if col not in internal_columns
                        ])
                    
                    create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {table_full_name} (
                        {columns_definition},
                        {config.rescue_data_column} STRING,
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
                    
                    logger.info(f"Criando tabela com Liquid Clustering: {create_table_query}")
                    spark.sql(create_table_query)
                    logger.info(f"Tabela {table_full_name} criada/validada com sucesso usando Liquid Clustering")
                    
                except Exception as e:
                    logger.error(f"Erro ao criar tabela: {str(e)}")
                    raise
            
            @staticmethod
            def _get_trigger_config(config: IngestionConfig) -> Dict[str, Any]:
                if config.type_run == "batch":
                    logger.info("Configurando execução como batch (availableNow)")
                    return {"availableNow": True}
                else:
                    logger.info(f"Configurando execução como streaming ({config.trigger_processing_time})")
                    ConfigValidator.validate_args(['trigger_processing_time'], config.__dict__)
                    return {"processingTime": config.trigger_processing_time}

        
        class IngestionEngine:
            """Engine principal de ingestão do DINO SDK."""
            
            def __init__(self, spark: SparkSession):
                self.spark = spark
                logger.info("🦕 DINO SDK IngestionEngine inicializado")
            
            def ingest(self, config: IngestionConfig) -> Optional[Any]:
                try:
                    logger.info("🚀 Iniciando processo de ingestão DINO SDK")
                    ConfigValidator.validate_ingestion_config(config)
                    df = DataReader.read_data(self.spark, config)
                    result = DataSaver.save_data(self.spark, df, config)
                    logger.info("✅ Processo de ingestão concluído")
                    return result
                except Exception as e:
                    logger.error(f"❌ Erro no processo de ingestão: {str(e)}")
                    raise
            
            def create_config(self, source_path: str, catalog_name: str, schema_name: str, table_name: str, **kwargs) -> IngestionConfig:
                return IngestionConfig(
                    source_path=source_path,
                    catalog_name=catalog_name,
                    schema_name=schema_name,
                    table_name=table_name,
                    **kwargs
                )

        
        def ingest_csv_to_unity_catalog(spark: SparkSession, source_path: str, catalog_name: str, schema_name: str, table_name: str, **kwargs) -> Optional[Any]:
            """Função de conveniência para ingestão rápida de CSV para Unity Catalog."""
            engine = IngestionEngine(spark)
            config = engine.create_config(
                source_path=source_path,
                catalog_name=catalog_name,
                schema_name=schema_name,
                table_name=table_name,
                **kwargs
            )
            return engine.ingest(config)

        
        print("✅ Método 3: Classes definidas inline com sucesso!")

print("🎉 DINO SDK pronto para uso!")
print("💡 Agora você pode usar: IngestionEngine, ingest_csv_to_unity_catalog, etc.")
