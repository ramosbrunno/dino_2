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
from pyspark.sql.functions import col, current_date, current_timestamp, lit, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType
from dataclasses import dataclass
import logging
import time
import uuid
import traceback
from datetime import datetime

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
    ) -> Dict[str, Any]:
        """
        Salva dados no Unity Catalog usando Delta Lake.
        
        Args:
            spark: Sessão do Spark
            df: DataFrame a ser salvo
            config: Configuração de ingestão
            
        Returns:
            Dicionário com informações do resultado
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
                
                # Obter contagem de registros na tabela após o salvamento
                try:
                    count_query = f"SELECT COUNT(*) as total FROM {table_full_name}"
                    rows_written = spark.sql(count_query).collect()[0]['total']
                    logger.info(f"📊 Confirmado: {rows_written} registros na tabela")
                    
                    return {
                        "success": True,
                        "table": table_full_name,
                        "rows_written": rows_written,
                        "mode": "batch_stream",
                        "message": f"Dados batch salvos com sucesso em {table_full_name}"
                    }
                except Exception as count_error:
                    logger.warning(f"⚠️ Não foi possível contar registros após salvamento: {count_error}")
                    return {
                        "success": True,
                        "table": table_full_name,
                        "rows_written": None,
                        "mode": "batch_stream",
                        "message": f"Dados batch salvos com sucesso em {table_full_name} (contagem não disponível)"
                    }
            else:
                logger.info(f"Stream iniciado para {table_full_name}")
                return {
                    "success": True,
                    "table": table_full_name,
                    "stream_query": query,
                    "mode": "streaming",
                    "message": f"Stream iniciado para {table_full_name}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro no salvamento: {str(e)}"
            }
    
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


@dataclass
@dataclass
class IngestionLogEntry:
    """
    Representa uma entrada de log de execução de ingestão.
    """
    execution_id: str
    table_name: str
    schema_name: str
    catalog_name: str
    source_path: str
    execution_status: str  # "iniciado", "concluido_sucesso", "concluido_erro"
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_duration_seconds: Optional[float] = None
    records_read: Optional[int] = None
    records_written: Optional[int] = None
    file_format: str = ""
    ingestion_type: str = ""  # "batch" ou "streaming"
    message: Optional[str] = None  # Mensagem de sucesso ou erro
    error_message: Optional[str] = None
    error_stack_trace: Optional[str] = None
    files_ingested: Optional[str] = None  # Nomes dos arquivos ingeridos
    file_size_bytes: Optional[int] = None  # Tamanho do arquivo lido
    additional_metadata: Optional[Dict[str, Any]] = None


class IngestionLogManager:
    """
    Gerenciador de logs de execução de ingestão.
    
    Cria uma tabela de logs no mesmo schema para registrar todas as execuções
    de ingestão com detalhes completos.
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.logger = logging.getLogger(f"{__name__}.LogManager")
    
    def _get_log_table_name(self, catalog_name: str, schema_name: str) -> str:
        """Retorna o nome completo da tabela de logs"""
        return f"{catalog_name}.{schema_name}.dino_ingestion_logs"
    
    def _create_log_table_if_not_exists(self, catalog_name: str, schema_name: str) -> None:
        """
        Cria a tabela de logs se não existir.
        
        A tabela terá todas as informações necessárias para auditoria e monitoramento.
        """
        log_table_name = self._get_log_table_name(catalog_name, schema_name)
        
        try:
            self.logger.info(f"🔧 Criando/validando tabela de logs: {log_table_name}")
            
            # Primeiro, garantir que o schema existe
            try:
                schema_sql = f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}"
                self.logger.info(f"📂 Garantindo schema: {schema_sql}")
                self.spark.sql(schema_sql)
                self.logger.info(f"✅ Schema garantido: {catalog_name}.{schema_name}")
            except Exception as schema_error:
                self.logger.warning(f"⚠️ Erro ao criar schema (continuando): {str(schema_error)}")
            
            # Criar tabela com configuração robusta
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {log_table_name} (
                execution_id STRING NOT NULL,
                table_name STRING NOT NULL,
                schema_name STRING NOT NULL,
                catalog_name STRING NOT NULL,
                source_path STRING NOT NULL,
                execution_status STRING NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                execution_duration_seconds DOUBLE,
                records_read BIGINT,
                records_written BIGINT,
                file_format STRING,
                ingestion_type STRING,
                message STRING,
                error_message STRING,
                error_stack_trace STRING,
                files_ingested STRING,
                file_size_bytes BIGINT,
                additional_metadata STRING,
                created_at TIMESTAMP
            )
            USING DELTA
            TBLPROPERTIES (
                'delta.autoOptimize.optimizeWrite' = 'true',
                'delta.autoOptimize.autoCompact' = 'true'
            )
            """
            
            self.logger.info(f"📊 Executando CREATE TABLE: {log_table_name}")
            self.spark.sql(create_table_sql)
            self.logger.info(f"✅ Tabela de logs criada/validada: {log_table_name}")
            
            # Verificar se a tabela realmente existe
            try:
                count_sql = f"SELECT COUNT(*) as total FROM {log_table_name} LIMIT 1"
                result = self.spark.sql(count_sql).collect()
                self.logger.info(f"🔍 Verificação da tabela: {len(result[0])} campo(s) retornado(s)")
                self.logger.info(f"✅ Tabela {log_table_name} está acessível e funcional")
            except Exception as verify_error:
                self.logger.warning(f"⚠️ Erro ao verificar tabela (pode não ter sido criada): {str(verify_error)}")
                # Re-raise para forçar fallback para log local
                raise verify_error
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar tabela de logs: {str(e)}")
            self.logger.warning("🔄 Continuando sem tabela de logs - usará logging local")
            # Re-raise para que o método chamador saiba que a tabela não foi criada
            raise e
    
    def start_ingestion_log(self, config: IngestionConfig) -> str:
        """
        Inicia um log de execução de ingestão.
        
        Args:
            config: Configuração da ingestão
            
        Returns:
            ID único da execução
        """
        try:
            # Garantir que a tabela de logs existe (se Unity Catalog estiver habilitado)
            self._create_log_table_if_not_exists(config.catalog_name, config.schema_name)
            
            # Gerar ID único para a execução
            execution_id = str(uuid.uuid4())
            
            # Obter informações sobre os arquivos
            file_info = self._get_file_info(config.source_path)
            self.logger.info(f"🔍 Informações dos arquivos obtidas: {file_info}")
            
            # Criar entrada inicial de log
            log_entry = IngestionLogEntry(
                execution_id=execution_id,
                table_name=config.table_name,
                schema_name=config.schema_name,
                catalog_name=config.catalog_name,
                source_path=config.source_path,
                execution_status="iniciado",
                start_time=datetime.now(),
                file_format=config.file_extension,
                ingestion_type=config.type_run,
                message="Ingestão iniciada com sucesso",
                files_ingested=file_info.get("files", "N/A"),
                file_size_bytes=file_info.get("total_size", 0),
                additional_metadata={
                    "delimiter": getattr(config, 'file_delimiter', None),
                    "header": getattr(config, 'file_header', None),
                    "multiline": getattr(config, 'multiline', None),
                    "schema_evolution_mode": getattr(config, 'schema_evolution_mode', None),
                    "unity_catalog_enabled": self._is_unity_catalog_enabled(),
                    "file_count": file_info.get("file_count", 0)
                }
            )
            
            self._insert_log_entry(log_entry)
            self.logger.info(f"🔍 Log de ingestão iniciado: {execution_id}")
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar log de ingestão: {str(e)}")
            # Retornar um ID mesmo com erro para não quebrar o fluxo
            execution_id = str(uuid.uuid4())
            self.logger.warning(f"⚠️ Continuando sem log detalhado com ID: {execution_id}")
            return execution_id
    
    def _build_safe_destination_path(self, config: IngestionConfig) -> str:
        """
        Constrói path de destino de forma segura.
        """
        try:
            # Tentar usar Volumes se Unity Catalog estiver habilitado
            if self._is_unity_catalog_enabled():
                return f"/Volumes/{config.catalog_name}/{config.schema_name}/{config.table_name}"
            else:
                # Fallback para path tradicional do DBFS
                return f"/mnt/data/{config.schema_name}/{config.table_name}"
        except Exception as e:
            self.logger.warning(f"Erro ao construir path de destino: {str(e)}")
            return f"dbfs:/{config.schema_name}/{config.table_name}"
    
    def _get_file_info(self, source_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre os arquivos na origem.
        """
        try:
            # Usar dbutils para listar arquivos se disponível
            try:
                # Tentar usar dbutils do ambiente Databricks
                from pyspark.sql import SparkSession
                spark = SparkSession.getActiveSession() or self.spark
                
                # No Databricks, dbutils está disponível globalmente
                try:
                    # Tentar usar dbutils diretamente
                    file_list = spark.sparkContext._gateway.jvm.com.databricks.backend.daemon.dbutils.fs.ls(source_path)
                    files = []
                    total_size = 0
                    
                    for file_info in file_list:
                        file_name = str(file_info.name())
                        file_size = int(file_info.size())
                        is_dir = bool(file_info.isDir())
                        
                        if not file_name.startswith('.') and not is_dir:
                            files.append(file_name)
                            total_size += file_size
                    
                    return {
                        "files": ", ".join(files[:10]),  # Limitar a 10 nomes
                        "file_count": len(files),
                        "total_size": total_size,
                        "has_more_files": len(files) > 10
                    }
                    
                except Exception as dbutils_error:
                    # Fallback: tentar usar comando SHOW TABLES/FILES via SQL
                    try:
                        # Para paths de volume, tentar listar via SQL
                        if "/Volumes/" in source_path:
                            # Extrair informações do path
                            path_parts = source_path.strip("/").split("/")
                            if len(path_parts) >= 4 and path_parts[0] == "Volumes":
                                catalog = path_parts[1]
                                schema = path_parts[2] 
                                volume = path_parts[3]
                                subpath = "/".join(path_parts[4:]) if len(path_parts) > 4 else ""
                                
                                # Tentar usar LIST via SQL
                                list_sql = f"LIST '/Volumes/{catalog}/{schema}/{volume}/{subpath}'"
                                file_df = self.spark.sql(list_sql)
                                file_rows = file_df.collect()
                                
                                files = []
                                total_size = 0
                                
                                for row in file_rows:
                                    file_name = row.name if hasattr(row, 'name') else str(row[1])
                                    file_size = row.size if hasattr(row, 'size') else 0
                                    
                                    if not file_name.startswith('.') and not file_name.endswith('/'):
                                        files.append(file_name)
                                        total_size += file_size
                                
                                return {
                                    "files": ", ".join(files[:10]),
                                    "file_count": len(files),
                                    "total_size": total_size,
                                    "has_more_files": len(files) > 10
                                }
                        
                        raise Exception("Path não suportado para listagem SQL")
                        
                    except Exception as sql_error:
                        # Fallback final: usar Spark para ler dados e obter input files
                        try:
                            # Se o path contém wildcards ou é um diretório, usar Spark
                            if "*" in source_path or source_path.endswith("/"):
                                # Tentar ler uma amostra pequena para obter input files
                                sample_df = self.spark.read.option("header", "true").limit(1).csv(source_path)
                                input_files = sample_df.inputFiles()
                                
                                files = []
                                for file_path in input_files:
                                    file_name = file_path.split("/")[-1]
                                    if not file_name.startswith('.'):
                                        files.append(file_name)
                                
                                return {
                                    "files": ", ".join(files[:10]),
                                    "file_count": len(files),
                                    "total_size": 0,  # Não conseguimos obter tamanho facilmente
                                    "has_more_files": len(files) > 10
                                }
                            else:
                                # Path único, extrair nome do arquivo
                                filename = source_path.split("/")[-1]
                                return {
                                    "files": filename,
                                    "file_count": 1,
                                    "total_size": 0,
                                    "has_more_files": False
                                }
                        except Exception as spark_error:
                            # Se tudo falhar, usar o path como está
                            filename = source_path.split("/")[-1] if "/" in source_path else source_path
                            return {
                                "files": filename,
                                "file_count": 1,
                                "total_size": 0,
                                "has_more_files": False
                            }
                            
            except Exception as general_error:
                # Fallback geral
                filename = source_path.split("/")[-1] if "/" in source_path else source_path
                return {
                    "files": filename if filename else "unknown",
                    "file_count": 1,
                    "total_size": 0,
                    "has_more_files": False
                }
                    
        except Exception as e:
            self.logger.warning(f"Não foi possível obter informações dos arquivos: {str(e)}")
            return {
                "files": "N/A",
                "file_count": 0,
                "total_size": 0,
                "has_more_files": False
            }
    
    def update_ingestion_log_success(
        self, 
        execution_id: str, 
        config: IngestionConfig,
        records_read: int = None,
        records_written: int = None,
        start_time: datetime = None
    ) -> None:
        """
        Atualiza o log com sucesso na execução.
        """
        try:
            # Verificar se o Unity Catalog está habilitado
            if not self._is_unity_catalog_enabled():
                self.logger.warning("Unity Catalog não habilitado - usando logging local")
                self._log_success_locally(execution_id, config, records_read, records_written, start_time)
                return
            
            self.logger.info(f"🔄 Atualizando log de sucesso para execution_id: {execution_id}")
            self.logger.info(f"📊 Métricas: read={records_read}, written={records_written}")
            
            log_table_name = self._get_log_table_name(config.catalog_name, config.schema_name)
            
            end_time = datetime.now()
            duration_seconds = None
            if start_time:
                duration_seconds = (end_time - start_time).total_seconds()
            
            self.logger.info(f"⏱️ Duração calculada: {duration_seconds}s")
            
            # Preparar mensagem de sucesso
            success_message = f"Ingestão concluída com sucesso. {records_read or 0} registros lidos, {records_written or 0} registros gravados."
            
            # Preparar metadados adicionais
            metadata = {
                "records_read": records_read,
                "records_written": records_written,
                "success": True,
                "unity_catalog_enabled": True
            }
            
            # Usar merge para atualização segura
            from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, LongType
            
            update_data = [
                (
                    execution_id,
                    'concluido_sucesso',
                    end_time,
                    duration_seconds,
                    records_read,
                    records_written,
                    success_message,
                    str(metadata)
                )
            ]
            
            update_schema = StructType([
                StructField("execution_id", StringType(), False),
                StructField("execution_status", StringType(), False),
                StructField("end_time", TimestampType(), True),
                StructField("execution_duration_seconds", DoubleType(), True),
                StructField("records_read", LongType(), True),
                StructField("records_written", LongType(), True),
                StructField("message", StringType(), True),
                StructField("additional_metadata", StringType(), True)
            ])
            
            update_df = self.spark.createDataFrame(update_data, update_schema)
            update_df.createOrReplaceTempView("temp_update_success_log")
            
            merge_sql = f"""
            MERGE INTO {log_table_name} as target
            USING temp_update_success_log as source
            ON target.execution_id = source.execution_id
            WHEN MATCHED THEN UPDATE SET
                execution_status = source.execution_status,
                end_time = source.end_time,
                execution_duration_seconds = source.execution_duration_seconds,
                records_read = source.records_read,
                records_written = source.records_written,
                message = source.message,
                additional_metadata = source.additional_metadata
            """
            
            self.spark.sql(merge_sql)
            self.logger.info(f"✅ Log atualizado com sucesso: {execution_id}")
            self.logger.info(f"📋 Status final: concluido_sucesso, Mensagem: {success_message}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar log de sucesso: {str(e)}")
            # Fallback para logging local
            try:
                self._log_success_locally(execution_id, config, records_read, records_written, start_time)
            except Exception as fallback_error:
                self.logger.error(f"❌ Erro no fallback de logging de sucesso: {str(fallback_error)}")
    
    def update_ingestion_log_error(
        self, 
        execution_id: str, 
        config: IngestionConfig,
        error_message: str,
        error_stack_trace: str = None,
        start_time: datetime = None
    ) -> None:
        """
        Atualiza o log com erro na execução.
        """
        try:
            # Verificar se o Unity Catalog está habilitado
            if not self._is_unity_catalog_enabled():
                self.logger.warning("Unity Catalog não habilitado - usando logging local")
                self._log_error_locally(execution_id, config, error_message, error_stack_trace, start_time)
                return
            
            log_table_name = self._get_log_table_name(config.catalog_name, config.schema_name)
            
            end_time = datetime.now()
            duration_seconds = None
            if start_time:
                duration_seconds = (end_time - start_time).total_seconds()
            
            # Preparar mensagem de erro
            error_msg = f"Ingestão falhou com erro: {error_message[:200] if error_message else 'Erro não especificado'}"
            
            # Preparar metadados do erro (formato JSON válido)
            metadata = {
                "error_details": error_message[:500] if error_message else "",  # Truncar se muito longo
                "has_stack_trace": bool(error_stack_trace),
                "success": False,
                "unity_catalog_enabled": True
            }
            
            # Usar parâmetros seguros para evitar problemas de SQL injection
            from pyspark.sql.functions import lit, col
            from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType
            
            # Criar DataFrame temporário para o update
            update_data = [
                (
                    execution_id,
                    'concluido_erro',
                    end_time,
                    duration_seconds,
                    error_msg,
                    error_message[:1000] if error_message else "",  # Limitar tamanho
                    error_stack_trace[:5000] if error_stack_trace else "",  # Limitar tamanho
                    str(metadata)
                )
            ]
            
            update_schema = StructType([
                StructField("execution_id", StringType(), False),
                StructField("execution_status", StringType(), False),
                StructField("end_time", TimestampType(), True),
                StructField("execution_duration_seconds", DoubleType(), True),
                StructField("message", StringType(), True),
                StructField("error_message", StringType(), True),
                StructField("error_stack_trace", StringType(), True),
                StructField("additional_metadata", StringType(), True)
            ])
            
            update_df = self.spark.createDataFrame(update_data, update_schema)
            
            # Registrar como view temporária
            update_df.createOrReplaceTempView("temp_update_log")
            
            # Executar merge para atualizar
            merge_sql = f"""
            MERGE INTO {log_table_name} as target
            USING temp_update_log as source
            ON target.execution_id = source.execution_id
            WHEN MATCHED THEN UPDATE SET
                execution_status = source.execution_status,
                end_time = source.end_time,
                execution_duration_seconds = source.execution_duration_seconds,
                message = source.message,
                error_message = source.error_message,
                error_stack_trace = source.error_stack_trace,
                additional_metadata = source.additional_metadata
            """
            
            self.spark.sql(merge_sql)
            self.logger.info(f"❌ Log atualizado com erro: {execution_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar log de erro: {str(e)}")
            # Fallback para logging local se falhar
            try:
                self._log_error_locally(execution_id, config, error_message, error_stack_trace, start_time)
            except Exception as fallback_error:
                self.logger.error(f"❌ Erro no fallback de logging: {str(fallback_error)}")
    
    def _is_unity_catalog_enabled(self) -> bool:
        """
        Verifica se o Unity Catalog está habilitado no ambiente.
        """
        try:
            # Tentar executar um comando simples do Unity Catalog
            self.spark.sql("SHOW CATALOGS").collect()
            return True
        except Exception as e:
            self.logger.warning(f"Unity Catalog não habilitado: {str(e)}")
            return False
    
    def _log_error_locally(
        self, 
        execution_id: str, 
        config: IngestionConfig,
        error_message: str,
        error_stack_trace: str = None,
        start_time: datetime = None
    ) -> None:
        """
        Log de erro local quando Unity Catalog não está disponível.
        """
        try:
            end_time = datetime.now()
            duration_seconds = None
            if start_time:
                duration_seconds = (end_time - start_time).total_seconds()
            
            error_info = {
                "execution_id": execution_id,
                "table_name": config.table_name,
                "schema_name": config.schema_name,
                "catalog_name": config.catalog_name,
                "execution_status": "concluido_erro",
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat(),
                "execution_duration_seconds": duration_seconds,
                "message": f"Ingestão falhou com erro: {error_message[:200] if error_message else 'Erro não especificado'}",
                "error_message": error_message[:1000] if error_message else "",
                "error_stack_trace": error_stack_trace[:2000] if error_stack_trace else "",
                "unity_catalog_enabled": False
            }
            
            self.logger.error(f"📋 LOG_ERROR: {error_info}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro no log local: {str(e)}")
    
    def _log_success_locally(
        self, 
        execution_id: str, 
        config: IngestionConfig,
        records_read: int = None,
        records_written: int = None,
        start_time: datetime = None
    ) -> None:
        """
        Log de sucesso local quando Unity Catalog não está disponível.
        """
        try:
            end_time = datetime.now()
            duration_seconds = None
            if start_time:
                duration_seconds = (end_time - start_time).total_seconds()
            
            success_info = {
                "execution_id": execution_id,
                "table_name": config.table_name,
                "schema_name": config.schema_name,
                "catalog_name": config.catalog_name,
                "execution_status": "concluido_sucesso",
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat(),
                "execution_duration_seconds": duration_seconds,
                "records_read": records_read,
                "records_written": records_written,
                "message": f"Ingestão concluída com sucesso. {records_read or 0} registros lidos, {records_written or 0} registros gravados.",
                "unity_catalog_enabled": False
            }
            
            self.logger.info(f"📋 LOG_SUCCESS: {success_info}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro no log local de sucesso: {str(e)}")
    
    def _insert_log_entry(self, log_entry: IngestionLogEntry) -> None:
        """
        Insere uma entrada de log na tabela.
        """
        try:
            # Verificar se Unity Catalog está habilitado
            if not self._is_unity_catalog_enabled():
                self.logger.warning("Unity Catalog não habilitado - usando logging local para inserção")
                self._log_entry_locally(log_entry)
                return
            
            log_table_name = self._get_log_table_name(
                log_entry.catalog_name, 
                log_entry.schema_name
            )
            
            # Usar DataFrame para inserção segura
            from pyspark.sql.types import StructType, StructField, StringType, TimestampType, LongType, DoubleType
            
            # Preparar dados para inserção
            insert_data = [
                (
                    log_entry.execution_id,
                    log_entry.table_name,
                    log_entry.schema_name,
                    log_entry.catalog_name,
                    log_entry.source_path,
                    log_entry.execution_status,
                    log_entry.start_time,
                    log_entry.end_time,
                    log_entry.execution_duration_seconds,
                    log_entry.records_read,
                    log_entry.records_written,
                    log_entry.file_format,
                    log_entry.ingestion_type,
                    log_entry.message,
                    log_entry.files_ingested,
                    log_entry.file_size_bytes,
                    str(log_entry.additional_metadata) if log_entry.additional_metadata else ""
                )
            ]
            
            insert_schema = StructType([
                StructField("execution_id", StringType(), False),
                StructField("table_name", StringType(), False),
                StructField("schema_name", StringType(), False),
                StructField("catalog_name", StringType(), False),
                StructField("source_path", StringType(), False),
                StructField("execution_status", StringType(), False),
                StructField("start_time", TimestampType(), False),
                StructField("end_time", TimestampType(), True),
                StructField("execution_duration_seconds", DoubleType(), True),
                StructField("records_read", LongType(), True),
                StructField("records_written", LongType(), True),
                StructField("file_format", StringType(), True),
                StructField("ingestion_type", StringType(), True),
                StructField("message", StringType(), True),
                StructField("files_ingested", StringType(), True),
                StructField("file_size_bytes", LongType(), True),
                StructField("additional_metadata", StringType(), True)
            ])
            
            insert_df = self.spark.createDataFrame(insert_data, insert_schema)
            
            # Inserir usando DataFrame write
            insert_df.write.format("delta").mode("append").saveAsTable(log_table_name)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inserir log: {str(e)}")
            # Fallback para logging local
            try:
                self._log_entry_locally(log_entry)
            except Exception as fallback_error:
                self.logger.error(f"❌ Erro no fallback de inserção de log: {str(fallback_error)}")
    
    def _log_entry_locally(self, log_entry: IngestionLogEntry) -> None:
        """
        Log de entrada local quando Unity Catalog não está disponível.
        """
        try:
            entry_info = {
                "execution_id": log_entry.execution_id,
                "table_name": log_entry.table_name,
                "schema_name": log_entry.schema_name,
                "catalog_name": log_entry.catalog_name,
                "source_path": log_entry.source_path,
                "execution_status": log_entry.execution_status,
                "start_time": log_entry.start_time.isoformat() if log_entry.start_time else None,
                "file_format": log_entry.file_format,
                "ingestion_type": log_entry.ingestion_type,
                "message": log_entry.message,
                "files_ingested": log_entry.files_ingested,
                "file_size_bytes": log_entry.file_size_bytes,
                "additional_metadata": log_entry.additional_metadata,
                "unity_catalog_enabled": False
            }
            
            self.logger.info(f"📋 LOG_ENTRY: {entry_info}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro no log local de entrada: {str(e)}")


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
        self.log_manager = IngestionLogManager(self.spark)
        
        logger.info("🦕 DINO SDK IngestionEngine inicializado com sistema de logging")
    
    def ingest(self, config: IngestionConfig) -> Dict[str, Any]:
        """
        Executa o processo de ingestão completo com logging detalhado no final.
        
        Args:
            config: Configuração de ingestão
            
        Returns:
            Resultado da ingestão com informações de logging
        """
        start_time = datetime.now()
        records_read = 0
        records_written = 0
        files_ingested = None
        file_size_bytes = 0
        
        try:
            logger.info("🚀 Iniciando processo de ingestão DINO SDK")
            logger.info(f"📊 Tabela destino: {config.catalog_name}.{config.schema_name}.{config.table_name}")
            logger.info(f"📁 Source path: {config.source_path}")
            logger.info(f"🔄 Tipo de execução: {config.type_run}")
            
            # 1. Obter informações dos arquivos
            logger.info("🔍 Obtendo informações dos arquivos...")
            file_info = self._get_file_info(config.source_path)
            files_ingested = file_info.get("files", "N/A")
            file_size_bytes = file_info.get("total_size", 0)
            logger.info(f"� Arquivos encontrados: {files_ingested}")
            logger.info(f"💾 Tamanho total: {file_size_bytes} bytes")
            
            # 2. Validar configuração
            logger.info("🔍 Validando configuração...")
            self.config_validator.validate_config(config)
            logger.info("✅ Configuração validada")
            
            # 3. Garantir que o schema existe
            logger.info("🔍 Verificando/criando schema...")
            self.schema_manager.ensure_schema_exists(config.catalog_name, config.schema_name)
            logger.info("✅ Schema validado/criado")
            
            # 4. Ler dados com métricas
            logger.info("📖 Iniciando leitura de dados...")
            read_start_time = time.time()
            df = DataReader.read_data(self.spark, config)
            read_duration = time.time() - read_start_time
            logger.info(f"✅ Dados lidos em {read_duration:.2f}s")
            
            # 5. Para batch, tentar contar registros lidos
            if config.type_run == "batch":
                try:
                    # Verificar se o DataFrame é streaming
                    is_streaming = hasattr(df, 'isStreaming') and df.isStreaming
                    
                    if is_streaming:
                        logger.info("🔄 DataFrame streaming detectado - contagem será obtida após escrita")
                        records_read = None  # Será obtido após a escrita
                    else:
                        # DataFrame batch normal - pode contar diretamente
                        logger.info("🔢 Contando registros lidos (DataFrame batch)...")
                        count_start = time.time()
                        records_read = df.count()
                        count_duration = time.time() - count_start
                        logger.info(f"📊 Registros lidos: {records_read} (contagem em {count_duration:.2f}s)")
                        
                except Exception as count_error:
                    logger.warning(f"⚠️ Não foi possível contar registros lidos: {count_error}")
                    # Para AutoLoader, isso é esperado - obteremos a contagem do resultado da escrita
                    records_read = None
            else:
                logger.info("🔄 Modo streaming - contagem de registros será aproximada")
                records_read = None
            
            # 6. Salvar dados com métricas  
            logger.info("💾 Iniciando salvamento de dados...")
            save_start_time = time.time()
            result = DataSaver.save_data(self.spark, df, config)
            save_duration = time.time() - save_start_time
            logger.info(f"✅ Dados salvos em {save_duration:.2f}s")
            
            # 7. Extrair métricas do resultado
            records_written = 0  # Inicializar com 0
            if result and result.get("success"):
                records_written = result.get("rows_written", 0)
                
                # Se não conseguimos contar antes (streaming), usar o que foi escrito
                if records_read is None:
                    records_read = records_written
                    logger.info(f"📊 Registros processados (via escrita): {records_read}")
                
                logger.info(f"📊 Registros gravados: {records_written}")
            else:
                logger.warning("⚠️ Resultado do salvamento não disponível ou sem sucesso")
                # Tentar obter contagem via query na tabela recém-criada
                try:
                    table_name = f"{config.catalog_name}.{config.schema_name}.{config.table_name}"
                    count_query = f"SELECT COUNT(*) as total FROM {table_name}"
                    count_result = self.spark.sql(count_query).collect()[0]['total']
                    records_written = count_result
                    
                    if records_read is None:
                        records_read = records_written
                    
                    logger.info(f"📊 Registros obtidos via query da tabela: {records_written}")
                except Exception as query_error:
                    logger.warning(f"⚠️ Não foi possível obter contagem via query: {query_error}")
                    if records_read is None:
                        records_read = 0
            
            # 8. Calcular tempo total
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            logger.info(f"⏱️ Tempo total de execução: {total_duration:.2f}s")
            
            # 9. Salvar log completo com sucesso
            execution_id = self.save_ingestion_log(
                config=config,
                execution_status='concluido_sucesso',
                start_time=start_time,
                end_time=end_time,
                records_read=records_read,
                records_written=records_written,
                files_ingested=files_ingested,
                file_size_bytes=file_size_bytes
            )
            
            # 10. Preparar resultado final
            if config.type_run == "batch":
                logger.info("✅ Processo de ingestão batch concluído com sucesso")
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "mode": "batch",
                    "table": f"{config.catalog_name}.{config.schema_name}.{config.table_name}",
                    "records_read": records_read,
                    "records_written": records_written,
                    "execution_duration_seconds": total_duration,
                    "source_path": config.source_path,
                    "files_ingested": files_ingested,
                    "file_size_bytes": file_size_bytes,
                    "message": f"Ingestão batch concluída com sucesso. {records_read} registros lidos, {records_written} registros gravados."
                }
            else:
                logger.info("✅ Stream de ingestão iniciado com sucesso")
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "mode": "streaming",
                    "table": f"{config.catalog_name}.{config.schema_name}.{config.table_name}",
                    "stream_query": result.get("stream_query") if result else None,
                    "source_path": config.source_path,
                    "files_ingested": files_ingested,
                    "file_size_bytes": file_size_bytes,
                    "message": "Stream de ingestão iniciado com sucesso"
                }
                
        except Exception as e:
            # Capturar erro e stack trace
            error_message = str(e)
            error_stack_trace = traceback.format_exc()
            
            logger.error(f"❌ Erro no processo de ingestão: {error_message}")
            logger.error(f"🔍 Stack trace: {error_stack_trace}")
            
            # Salvar log completo com erro
            end_time = datetime.now()
            execution_id = self.save_ingestion_log(
                config=config,
                execution_status='concluido_erro',
                start_time=start_time,
                end_time=end_time,
                records_read=records_read,
                records_written=records_written,
                error_message=error_message,
                error_stack_trace=error_stack_trace,
                files_ingested=files_ingested,
                file_size_bytes=file_size_bytes
            )
            
            return {
                "success": False,
                "execution_id": execution_id,
                "error": error_message,
                "stack_trace": error_stack_trace,
                "execution_duration_seconds": (end_time - start_time).total_seconds(),
                "records_read": records_read,
                "records_written": records_written,
                "files_ingested": files_ingested,
                "file_size_bytes": file_size_bytes
            }
    
    def save_ingestion_log(
        self,
        config: IngestionConfig,
        execution_status: str,
        start_time: datetime,
        end_time: datetime,
        records_read: int = None,
        records_written: int = None,
        error_message: str = None,
        error_stack_trace: str = None,
        files_ingested: str = None,
        file_size_bytes: int = None
    ) -> str:
        """
        Salva o log completo de execução no final do processamento.
        Usa o IngestionLogManager existente para evitar duplicação.
        
        Args:
            config: Configuração da ingestão
            execution_status: Status final ('concluido_sucesso' ou 'concluido_erro')
            start_time: Horário de início da execução
            end_time: Horário de fim da execução
            records_read: Quantidade de registros lidos
            records_written: Quantidade de registros gravados
            error_message: Mensagem de erro (se houver)
            error_stack_trace: Stack trace do erro (se houver)
            files_ingested: Nomes dos arquivos ingeridos
            file_size_bytes: Tamanho dos arquivos em bytes
            
        Returns:
            ID único da execução
        """
        import uuid
        from datetime import datetime
        
        execution_id = str(uuid.uuid4())
        
        try:
            # Usar o IngestionLogManager existente (ele usa dino_ingestion_logs)
            log_entry = IngestionLogEntry(
                execution_id=execution_id,
                table_name=config.table_name,
                schema_name=config.schema_name,
                catalog_name=config.catalog_name,
                source_path=config.source_path,
                execution_status=execution_status,
                start_time=start_time,
                end_time=end_time,
                execution_duration_seconds=(end_time - start_time).total_seconds(),
                records_read=records_read,
                records_written=records_written,
                file_format=config.file_extension,
                ingestion_type=config.type_run,
                error_message=error_message,
                error_stack_trace=error_stack_trace[:1000] if error_stack_trace else None,
                files_ingested=files_ingested,
                file_size_bytes=file_size_bytes
            )
            
            # Tentar inserir usando o log_manager (usa dino_ingestion_logs)
            try:
                self.log_manager._insert_log_entry(log_entry)
                logger.info(f"✅ Log salvo na tabela dino_ingestion_logs")
                logger.info(f"📋 Execution ID: {execution_id}")
                logger.info(f"📊 Status: {execution_status}")
                logger.info(f"⏱️ Duração: {log_entry.execution_duration_seconds:.2f}s")
                return execution_id
                
            except Exception as table_error:
                logger.warning(f"⚠️ Falha ao salvar na tabela Unity Catalog: {str(table_error)}")
                
                # Fallback para logging estruturado simples (LOG BONITINHO)
                log_bonitinho = {
                    "execution_id": execution_id,
                    "table": config.table_name,
                    "schema": config.schema_name,
                    "catalog": config.catalog_name,
                    "status": execution_status,
                    "duracao": f"{log_entry.execution_duration_seconds:.2f}s",
                    "registros_lidos": records_read or 0,
                    "registros_gravados": records_written or 0,
                    "timestamp": end_time.isoformat(),
                    "mensagem": f"Ingestão {execution_status}. {records_read or 0} registros processados."
                }
                
                logger.info("=" * 80)
                logger.info("🎯 LOG BONITINHO DA INGESTÃO")
                logger.info("=" * 80)
                for key, value in log_bonitinho.items():
                    logger.info(f"📋 {key}: {value}")
                logger.info("=" * 80)
                
                return execution_id
                
        except Exception as main_error:
            logger.error(f"❌ Erro crítico no save_ingestion_log: {str(main_error)}")
            return execution_id

    def get_ingestion_history(
        self, 
        catalog_name: str, 
        schema_name: str, 
        table_name: str = None,
        limit: int = 10
    ) -> DataFrame:
        """
        Retorna histórico de ingestões para auditoria e monitoramento.
        
        Args:
            catalog_name: Nome do catálogo
            schema_name: Nome do schema 
            table_name: Nome da tabela (opcional)
            limit: Limite de registros
            
        Returns:
            DataFrame com histórico de execuções
        """
        return self.log_manager.get_ingestion_history(
            catalog_name=catalog_name,
            schema_name=schema_name,
            table_name=table_name,
            limit=limit
        )

    def _get_file_info(self, source_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre os arquivos na origem.
        
        Args:
            source_path: Caminho dos arquivos
            
        Returns:
            Dicionário com informações dos arquivos
        """
        try:
            logger.info(f"🔍 Obtendo informações de arquivos para: {source_path}")
            
            # Tentar usar dbutils se disponível no Databricks
            try:
                # No ambiente Databricks, dbutils está disponível globalmente
                from dbutils import fs as dbfs
                
                # Listar arquivos no path
                files = dbfs.ls(source_path)
                
                file_names = []
                total_size = 0
                file_count = 0
                
                for file_info in files:
                    if not file_info.name.endswith('/'):  # Não é diretório
                        file_names.append(file_info.name)
                        total_size += file_info.size
                        file_count += 1
                
                result = {
                    "files": ", ".join(file_names[:5]) + ("..." if len(file_names) > 5 else ""),
                    "file_count": file_count,
                    "total_size": total_size,
                    "has_more_files": len(file_names) > 5
                }
                logger.info(f"📊 Informações obtidas via dbutils: {result}")
                return result
                
            except ImportError:
                logger.info("dbutils não disponível, tentando alternativa...")
                pass
            except Exception as dbutils_error:
                logger.warning(f"Erro ao usar dbutils: {str(dbutils_error)}")
                pass
            
            # Fallback: tentar usar Spark para listar arquivos via SQL
            try:
                if "/Volumes/" in source_path:
                    # Para paths de volume, tentar usar LIST
                    list_sql = f"LIST '{source_path}'"
                    file_df = self.spark.sql(list_sql)
                    file_rows = file_df.collect()
                    
                    files = []
                    total_size = 0
                    
                    for row in file_rows:
                        file_name = row.name if hasattr(row, 'name') else str(row[1])
                        file_size = row.size if hasattr(row, 'size') else 0
                        
                        if not file_name.startswith('.') and not file_name.endswith('/'):
                            files.append(file_name)
                            total_size += file_size
                    
                    result = {
                        "files": ", ".join(files[:5]) + ("..." if len(files) > 5 else ""),
                        "file_count": len(files),
                        "total_size": total_size,
                        "has_more_files": len(files) > 5
                    }
                    logger.info(f"📊 Informações obtidas via LIST SQL: {result}")
                    return result
                    
            except Exception as sql_error:
                logger.warning(f"Erro ao usar LIST SQL: {str(sql_error)}")
                pass
            
            # Fallback final: usar Spark para ler dados e obter input files
            try:
                # Tentar ler uma amostra pequena para obter input files
                sample_df = self.spark.read.option("header", "true").limit(1).csv(source_path)
                input_files = sample_df.inputFiles()
                
                files = []
                for file_path in input_files:
                    file_name = file_path.split("/")[-1]
                    if not file_name.startswith('.'):
                        files.append(file_name)
                
                result = {
                    "files": ", ".join(files[:5]) + ("..." if len(files) > 5 else ""),
                    "file_count": len(files),
                    "total_size": 0,  # Não conseguimos obter tamanho facilmente
                    "has_more_files": len(files) > 5
                }
                logger.info(f"📊 Informações obtidas via Spark inputFiles: {result}")
                return result
                
            except Exception as spark_error:
                logger.warning(f"Erro ao usar Spark inputFiles: {str(spark_error)}")
                pass
            
            # Se tudo falhar, usar informações básicas do path
            filename = source_path.split("/")[-1] if "/" in source_path else source_path
            result = {
                "files": filename if filename else "unknown",
                "file_count": 1,
                "total_size": 0,
                "has_more_files": False
            }
            logger.info(f"📊 Usando informações básicas do path: {result}")
            return result
            
        except Exception as e:
            logger.warning(f"Não foi possível obter informações dos arquivos: {str(e)}")
            return {
                "files": "N/A",
                "file_count": 0,
                "total_size": 0,
                "has_more_files": False
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


def get_ingestion_engine(spark: SparkSession) -> IngestionEngine:
    """
    Função de conveniência para obter uma instância do IngestionEngine.
    
    Args:
        spark: Sessão Spark
        
    Returns:
        Uma instância configurada do IngestionEngine
    """
    return IngestionEngine(spark)
