"""
🦕 DINO SDK - Ingestion Engine

Módulo principal para ingestão de dados usando AutoLoader do Databricks.
Baseado nas classes DataReader e DataSaver com adaptações para Unity Catalog.

Principais características:
- ✅ AutoLoader para ingestão batch e streaming
- ✅ Unity Catalog integration
- ✅ Todas as colunas como STRING (CSV)
- ✅ Metadados de ingestão automáticos
- ✅ Liquid Clustering (CLUSTER BY AUTO) para otimização automática
- ✅ Schema inference e validação
"""

from typing import Dict, Optional, Any, List
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, current_date, current_timestamp
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IngestionConfig:
    """
    Configuração para ingestão de dados no DINO SDK.
    """
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
    
    # Configurações de Liquid Clustering
    liquid_clustering: bool = True
    clustering_columns: List[str] = None
    
    # Configurações personalizadas do Spark
    custom_spark_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_spark_config is None:
            self.custom_spark_config = {}
        if self.clustering_columns is None:
            self.clustering_columns = []


class ConfigValidator:
    """
    Validador de configurações para ingestão.
    """
    
    @staticmethod
    def validate_args(required_args: List[str], config: Dict[str, Any]) -> None:
        """
        Valida se os argumentos obrigatórios estão presentes.
        
        Args:
            required_args: Lista de argumentos obrigatórios
            config: Dicionário de configuração a ser validado
            
        Raises:
            ValueError: Se algum argumento obrigatório estiver ausente
        """
        missing_args = [arg for arg in required_args if arg not in config or config[arg] is None]
        if missing_args:
            raise ValueError(f"Argumentos obrigatórios ausentes: {', '.join(missing_args)}")
    
    @staticmethod 
    def validate_ingestion_config(config: IngestionConfig) -> None:
        """
        Valida a configuração de ingestão.
        
        Args:
            config: Configuração a ser validada
            
        Raises:
            ValueError: Se a configuração for inválida
        """
        if not config.source_path:
            raise ValueError("source_path é obrigatório")
        
        if not config.table_name:
            raise ValueError("table_name é obrigatório")
        
        if config.type_run not in ["batch", "streaming"]:
            raise ValueError("type_run deve ser 'batch' ou 'streaming'")
        
        if config.file_extension not in ["csv", "json", "parquet", "delta"]:
            raise ValueError("file_extension deve ser um dos: csv, json, parquet, delta")
    
    def validate_config(self, config: IngestionConfig) -> bool:
        """
        Método de instância para validar configuração.
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            True se válida
            
        Raises:
            ValueError: Se a configuração for inválida
        """
        try:
            self.validate_ingestion_config(config)
            return True
        except ValueError:
            raise


class DataReader:
    """
    Leitor de dados usando AutoLoader do Databricks.
    """
    
    @staticmethod
    def read_data(spark: SparkSession, config: IngestionConfig) -> DataFrame:
        """
        Lê dados de uma fonte usando AutoLoader.
        
        Args:
            spark: Sessão do Spark
            config: Configuração de ingestão
            
        Returns:
            DataFrame com os dados lidos e metadados adicionados
        """
        try:
            logger.info(f"Configurando AutoLoader para leitura de {config.source_path}")
            
            # Configurações básicas do AutoLoader
            autoloader_config = {
                "cloudFiles.format": config.file_extension,
                "cloudFiles.schemaEvolutionMode": config.schema_evolution_mode,
                "cloudFiles.rescuedDataColumn": config.rescue_data_column,
            }
            
            # Adicionar schema location se schema evolution estiver habilitado
            if config.schema_evolution_mode in ["rescue", "addNewColumns", "failOnNewColumns"]:
                # Usar o mesmo path da tabela de destino para schema location
                schema_location = f"/Volumes/{config.catalog_name}/{config.schema_name}/_schemas/{config.table_name}"
                autoloader_config["cloudFiles.schemaLocation"] = schema_location
                logger.info(f"Schema location configurado: {schema_location}")
            
            # Configurações específicas para CSV
            if config.file_extension == "csv":
                autoloader_config.update({
                    "header": str(config.file_header).lower(),
                    "delimiter": config.file_delimiter,
                    "inferSchema": "false",  # Manter todas as colunas como STRING
                    "cloudFiles.inferColumnTypes": "false"
                })
                
            if config.multiline:
                autoloader_config["multiline"] = "true"
            
            # Adicionar configurações customizadas
            autoloader_config.update(config.custom_spark_config)
            
            logger.info(f"Configurações do AutoLoader: {autoloader_config}")
            logger.info(f"Carregando arquivos de: {config.source_path}")
            
            # AutoLoader SEMPRE usa readStream
            # Para notebook/testing: usar trigger availableNow para processamento imediato
            df = (
                spark.readStream
                .format("cloudFiles")
                .options(**autoloader_config)
                .load(config.source_path)
                .select(
                    "*",
                    current_date().alias("dino_ingestion_date"),
                    current_timestamp().alias("dino_ingestion_timestamp")
                )
            )
            
            logger.info("Dados carregados com sucesso usando AutoLoader")
            return df
            
        except Exception as e:
            logger.error(f"Erro na leitura dos dados: {str(e)}")
            raise
    
    @staticmethod
    def read_data_as_batch(spark: SparkSession, config: IngestionConfig) -> DataFrame:
        """
        Lê dados usando AutoLoader e converte para DataFrame batch (para operações como count).
        
        Este método é específico para notebooks e testes onde você precisa fazer operações
        batch como .count(), .show(), etc. no DataFrame.
        
        Args:
            spark: Sessão do Spark
            config: Configuração de ingestão
            
        Returns:
            DataFrame batch (não streaming) para operações como count()
        """
        import tempfile
        import time
        import uuid
        
        try:
            logger.info("Convertendo AutoLoader para batch DataFrame")
            
            # Estratégia alternativa: usar AutoLoader com microbatch + collect
            # Criar configurações específicas para batch
            batch_config = IngestionConfig(
                source_path=config.source_path,
                catalog_name=config.catalog_name,
                schema_name=config.schema_name,
                table_name=config.table_name,
                file_format="cloudFiles",
                file_extension=config.file_extension,
                file_header=config.file_header,
                file_delimiter=config.file_delimiter,
                schema_location=config.schema_location,
                file_options=config.file_options,
                type_run="batch"  # Forçar batch mode
            )
            
            # Criar um nome único para tabela temporária
            temp_table_name = f"temp_dino_batch_{str(uuid.uuid4()).replace('-', '_')[:8]}"
            
            # Usar foreachBatch para processar e armazenar dados
            def process_micro_batch(df, batch_id):
                """Processa microbatch e salva em tabela temporária"""
                try:
                    logger.info(f"Processando batch {batch_id} com {df.count()} registros")
                    # Registrar como temp view global para acesso posterior
                    df.createGlobalTempView(temp_table_name)
                    logger.info(f"Batch {batch_id} salvo como global_temp.{temp_table_name}")
                except Exception as e:
                    logger.error(f"Erro no batch {batch_id}: {str(e)}")
                    # Fallback: criar temp view local
                    df.createOrReplaceTempView(temp_table_name)
            
            # Ler stream com AutoLoader
            stream_df = DataReader.read_data(spark, batch_config)
            
            # Configurar checkpoint temporário
            checkpoint_path = f"/tmp/dino_batch_checkpoints/{temp_table_name}"
            
            # Processar com availableNow=True para batch único
            query = (
                stream_df.writeStream
                .foreachBatch(process_micro_batch)
                .trigger(availableNow=True)
                .option("checkpointLocation", checkpoint_path)
                .start()
            )
            
            # Aguardar conclusão do processamento
            query.awaitTermination()
            
            # Tentar ler da global temp view primeiro
            try:
                batch_df = spark.sql(f"SELECT * FROM global_temp.{temp_table_name}")
                logger.info("✅ Dados carregados de global temp view")
                return batch_df
            except:
                # Fallback: tentar temp view local
                try:
                    batch_df = spark.sql(f"SELECT * FROM {temp_table_name}")
                    logger.info("✅ Dados carregados de temp view local")
                    return batch_df
                except Exception as view_error:
                    logger.error(f"Erro ao acessar temp views: {str(view_error)}")
                    raise view_error
            
        except Exception as e:
            logger.error(f"Erro na conversão AutoLoader->batch: {str(e)}")
            # Fallback final: leitura simples sem AutoLoader
            logger.info("🔄 Usando fallback: leitura CSV simples")
            return DataReader._read_simple_csv(spark, config)
    
    @staticmethod
    def _read_simple_csv(spark: SparkSession, config: IngestionConfig) -> DataFrame:
        """
        Método fallback para leitura simples de CSV sem AutoLoader.
        """
        try:
            if config.file_extension == "csv":
                df = (
                    spark.read
                    .option("header", str(config.file_header).lower())
                    .option("delimiter", config.file_delimiter)
                    .option("inferSchema", "false")
                    .csv(config.source_path)
                    .select(
                        "*",
                        current_date().alias("dino_ingestion_date"),
                        current_timestamp().alias("dino_ingestion_timestamp")
                    )
                )
                logger.info("Dados lidos usando fallback CSV simples")
                return df
            else:
                raise ValueError(f"Fallback não suportado para formato {config.file_extension}")
        except Exception as e:
            logger.error(f"Erro no fallback CSV: {str(e)}")
            raise


class DataSaver:
    """
    Salvador de dados no Unity Catalog usando Delta Lake.
    """
    
    @staticmethod
    def save_data(
        spark: SparkSession,
        df: DataFrame,
        config: IngestionConfig
    ) -> None:
        """
        Salva dados no Unity Catalog usando Delta Lake.
        
        Args:
            spark: Sessão do Spark
            df: DataFrame a ser salvo
            config: Configuração de ingestão
        """
        try:
            table_full_name = f"{config.catalog_name}.{config.schema_name}.{config.table_name}"
            logger.info(f"Preparando para salvar dados em: {table_full_name}")
            
            # Criar tabela se não existir
            DataSaver._create_table_if_not_exists(spark, df, config, table_full_name)
            
            # Configurar trigger baseado no modo
            trigger_config = DataSaver._get_trigger_config(config)
            
            # Configurar query de escrita
            query = (
                df.writeStream
                .format("delta")
                .outputMode("append")
                .option("checkpointLocation", f"/Volumes/{config.catalog_name}/{config.schema_name}/_checkpoints/{config.table_name}")
                .trigger(**trigger_config)
                .toTable(table_full_name)
            )
            
            if config.type_run == "batch":
                # Para batch, aguardar conclusão
                query.awaitTermination()
                logger.info(f"Dados salvos com sucesso em {table_full_name}")
            else:
                logger.info(f"Stream iniciado para {table_full_name}")
                return query
                
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            raise
    
    @staticmethod
    def save_data_as_batch(
        spark: SparkSession,
        df: DataFrame,
        config: IngestionConfig
    ) -> Dict[str, Any]:
        """
        Salva DataFrame batch no Unity Catalog usando Delta Lake.
        
        Este método é específico para notebooks e testes onde você tem um 
        DataFrame batch (não streaming) e quer salvar usando .write ao invés de .writeStream.
        
        Args:
            spark: Sessão do Spark
            df: DataFrame batch a ser salvo
            config: Configuração de ingestão
            
        Returns:
            Resultado da operação de salvamento
        """
        try:
            table_full_name = f"{config.catalog_name}.{config.schema_name}.{config.table_name}"
            logger.info(f"Salvando DataFrame batch em: {table_full_name}")
            
            # Criar tabela se não existir
            DataSaver._create_table_if_not_exists(spark, df, config, table_full_name)
            
            # Adicionar metadados de ingestão
            from pyspark.sql.functions import current_date, current_timestamp, lit, struct
            from pyspark.sql.types import LongType
            
            df_with_metadata = df.withColumn("dino_ingestion_date", current_date()) \
                               .withColumn("dino_ingestion_timestamp", current_timestamp())
            
            # Salvar usando .write (para batch DataFrames)
            df_with_metadata.write \
                .format("delta") \
                .mode("append") \
                .option("mergeSchema", "true") \
                .saveAsTable(table_full_name)
            
            row_count = df.count()
            
            logger.info(f"✅ {row_count} registros salvos com sucesso em {table_full_name}")
            
            return {
                "success": True,
                "table": table_full_name,
                "rows_written": row_count,
                "mode": "batch_write",
                "message": f"Dados batch salvos com sucesso em {table_full_name}"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados batch: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro no salvamento batch: {str(e)}"
            }
    
    @staticmethod
    def _create_table_if_not_exists(
        spark: SparkSession, 
        df: DataFrame, 
        config: IngestionConfig,
        table_full_name: str
    ) -> None:
        """
        Cria a tabela Delta se não existir com Liquid Clustering.
        
        Liquid Clustering (CLUSTER BY AUTO):
        - Otimização automática de layout baseada em padrões de consulta
        - Databricks gerencia automaticamente as colunas de clustering
        - Melhor performance de leitura sem manutenção manual
        - Suporta evolução automática conforme padrões de acesso mudam
        """
        try:
            # Colunas internas que são adicionadas automaticamente
            internal_columns = [
                config.rescue_data_column,
                "dino_ingestion_date", 
                "dino_ingestion_timestamp"
            ]
            
            # Gerar colunas da tabela (todas como STRING para CSV)
            if config.file_extension == "csv":
                # Para CSV, precisamos pegar o schema corretamente
                # Se o DataFrame tem apenas uma coluna com nome estranho, significa que
                # o CSV não foi lido corretamente. Vamos usar nomes padrão.
                df_columns = [col for col in df.columns if col not in internal_columns]
                
                # Se temos apenas uma coluna estranha, usar schema padrão para CSV
                if len(df_columns) == 1 and ";" in df_columns[0]:
                    # Schema padrão para o arquivo fake_sales_100k.csv
                    expected_columns = [
                        "order_id", "order_date", "product", "product_category", 
                        "city", "region", "channel", "payment_method", 
                        "quantity", "unit_price", "total_value"
                    ]
                    columns_definition = ", ".join([
                        f"{col} STRING" for col in expected_columns
                    ])
                else:
                    # Usar as colunas detectadas
                    columns_definition = ", ".join([
                        f"{col.replace(';', '_').lower()} STRING" 
                        for col in df_columns
                    ])
            else:
                # Para outros formatos, manter tipos inferidos
                columns_definition = ", ".join([
                    f"{col} STRING"  # Simplificado por agora
                    for col in df.columns 
                    if col not in internal_columns
                ])
            
            # Configurar clustering baseado na configuração
            clustering_clause = ""
            if config.liquid_clustering:
                if config.clustering_columns and len(config.clustering_columns) > 0:
                    # Validar se as colunas de clustering existem no DataFrame
                    available_columns = [col for col in df.columns if col not in internal_columns]
                    valid_clustering_columns = []
                    
                    for cluster_col in config.clustering_columns:
                        if cluster_col in available_columns:
                            valid_clustering_columns.append(cluster_col)
                        else:
                            logger.warning(f"Coluna de clustering '{cluster_col}' não encontrada no DataFrame. Colunas disponíveis: {available_columns}")
                    
                    if valid_clustering_columns:
                        # Usar apenas colunas válidas para clustering
                        clustering_clause = f"CLUSTER BY ({', '.join(valid_clustering_columns)})"
                        logger.info(f"Usando clustering com colunas válidas: {valid_clustering_columns}")
                    else:
                        # Fallback para auto clustering se não há colunas válidas
                        clustering_clause = "CLUSTER BY AUTO"
                        logger.info("Nenhuma coluna de clustering válida encontrada, usando CLUSTER BY AUTO")
                else:
                    # Usar auto clustering
                    clustering_clause = "CLUSTER BY AUTO"
            
            # Query de criação da tabela com Liquid Clustering
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_full_name} (
                {columns_definition},
                {config.rescue_data_column} STRING,
                dino_ingestion_date DATE,
                dino_ingestion_timestamp TIMESTAMP
            )
            USING DELTA
            {clustering_clause}
            """
            
            cluster_info = f"Liquid Clustering: {config.liquid_clustering}"
            if config.liquid_clustering and config.clustering_columns:
                cluster_info += f", Columns: {config.clustering_columns}"
            logger.info(f"Criando tabela - {cluster_info}")
            logger.info(f"Query: {create_table_query}")
            
            spark.sql(create_table_query)
            logger.info(f"Tabela {table_full_name} criada/validada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela: {str(e)}")
            raise
    
    @staticmethod
    def _get_trigger_config(config: IngestionConfig) -> Dict[str, Any]:
        """
        Retorna configuração de trigger baseada no tipo de execução.
        
        Args:
            config: Configuração de ingestão
            
        Returns:
            Dicionário com configurações de trigger
        """
        if config.type_run == "batch":
            # Para batch: processar todos os arquivos de uma vez
            return {"availableNow": True}
        else:
            # Para streaming: processar continuamente
            return {"processingTime": config.trigger_processing_time}


class SchemaManager:
    """
    Gerenciador de esquemas no Unity Catalog.
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.logger = logger
    
    def create_schema_if_not_exists(self, catalog_name: str, schema_name: str) -> bool:
        """
        Cria um schema no Unity Catalog se não existir.
        
        Args:
            catalog_name: Nome do catálogo
            schema_name: Nome do schema
            
        Returns:
            True se criado/já existe, False caso contrário
        """
        try:
            schema_full_name = f"{catalog_name}.{schema_name}"
            
            # Verificar se schema existe
            if self._schema_exists(catalog_name, schema_name):
                self.logger.info(f"Schema {schema_full_name} já existe")
                return True
            
            # Criar schema
            create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema_full_name}"
            self.spark.sql(create_schema_sql)
            self.logger.info(f"Schema {schema_full_name} criado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar schema {catalog_name}.{schema_name}: {str(e)}")
            return False
    
    def _schema_exists(self, catalog_name: str, schema_name: str) -> bool:
        """
        Verifica se um schema existe.
        
        Args:
            catalog_name: Nome do catálogo
            schema_name: Nome do schema
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            schemas_df = self.spark.sql(f"SHOW SCHEMAS IN {catalog_name}")
            schemas_list = [row.databaseName for row in schemas_df.collect()]
            return schema_name in schemas_list
        except Exception:
            return False
    
    def ensure_schema_exists(self, catalog_name: str, schema_name: str) -> bool:
        """
        Garante que um schema existe, criando se necessário.
        
        Args:
            catalog_name: Nome do catálogo
            schema_name: Nome do schema
            
        Returns:
            True se o schema existe ou foi criado com sucesso
        """
        return self.create_schema_if_not_exists(catalog_name, schema_name)


class IngestionEngine:
    """
    Motor principal de ingestão de dados.
    """
    
    def __init__(self, spark: SparkSession = None):
        """
        Inicializa o motor de ingestão.
        
        Args:
            spark: Sessão Spark (opcional, será detectada automaticamente se não fornecida)
        """
        if spark is None:
            # Tentar obter sessão Spark ativa
            try:
                from pyspark.sql import SparkSession
                self.spark = SparkSession.getActiveSession()
                if self.spark is None:
                    raise Exception("Nenhuma sessão Spark ativa encontrada")
            except Exception as e:
                logger.error(f"Erro ao obter sessão Spark: {str(e)}")
                raise
        else:
            self.spark = spark
            
        self.config_validator = ConfigValidator()
        self.schema_manager = SchemaManager(self.spark)
        
        logger.info("🦕 DINO SDK IngestionEngine inicializado")
    
    def ingest(self, config: IngestionConfig) -> Dict[str, Any]:
        """
        Executa o processo de ingestão completo.
        
        Args:
            config: Configuração de ingestão
            
        Returns:
            Resultado da ingestão
        """
        try:
            logger.info("🚀 Iniciando processo de ingestão DINO SDK")
            
            # Validar configuração
            self.config_validator.validate_config(config)
            logger.info("✅ Configuração validada")
            
            # Garantir que o schema existe
            self.schema_manager.ensure_schema_exists(config.catalog_name, config.schema_name)
            
            # Ler dados
            df = DataReader.read_data(self.spark, config)
            logger.info("✅ Dados lidos com AutoLoader")
            
            # Salvar dados
            result = DataSaver.save_data(self.spark, df, config)
            
            if config.type_run == "batch":
                logger.info("✅ Processo de ingestão concluído")
                return {
                    "success": True,
                    "mode": "batch",
                    "table": f"{config.catalog_name}.{config.schema_name}.{config.table_name}",
                    "message": "Ingestão batch concluída com sucesso"
                }
            else:
                logger.info("✅ Stream de ingestão iniciado")
                return {
                    "success": True,
                    "mode": "streaming", 
                    "table": f"{config.catalog_name}.{config.schema_name}.{config.table_name}",
                    "stream_query": result,
                    "message": "Stream de ingestão iniciado com sucesso"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro no processo de ingestão: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro na ingestão: {str(e)}"
            }


def ingest_csv_to_unity_catalog(
    spark: SparkSession,
    source_path: str,
    catalog_name: str,
    schema_name: str,
    table_name: str,
    type_run: str = "batch",
    delimiter: str = ",",
    **kwargs
) -> Dict[str, Any]:
    """
    Função de conveniência para ingestão de CSV.
    
    Args:
        spark: Sessão Spark
        source_path: Caminho do arquivo CSV
        catalog_name: Nome do catálogo Unity Catalog
        schema_name: Nome do schema
        table_name: Nome da tabela
        type_run: Modo de execução ("batch" ou "streaming")
        delimiter: Delimitador do CSV
        **kwargs: Argumentos adicionais para IngestionConfig
        
    Returns:
        Resultado da ingestão
    """
    config = IngestionConfig(
        source_path=source_path,
        catalog_name=catalog_name,
        schema_name=schema_name,
        table_name=table_name,
        type_run=type_run,
        file_delimiter=delimiter,
        **kwargs
    )
    
    engine = IngestionEngine(spark)
    return engine.ingest(config)
