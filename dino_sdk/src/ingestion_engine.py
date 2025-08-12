#!/usr/bin/env python3
"""
Dino SDK - Ingestion Engine
Motor de ingestão batch para Databricks com Unity Catalog
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class IngestionEngine:
    """
    Motor de ingestão batch para Databricks
    
    Funcionalidades:
    - Ingestão batch de arquivos (CSV, JSON, Parquet, Delta, Avro)
    - Integração com Unity Catalog
    - Detecção automática de formato
    - Metadados de auditoria
    - Validação de pré-requisitos
    
    Pré-requisitos:
    - Schema de destino deve existir
    - Permissões adequadas no Unity Catalog
    """
    
    def __init__(
        self,
        target_schema: str,
        table_name: str,
        file_path: str,
        delimiter: str = ",",
        catalog_name: Optional[str] = None,
        output_mode: str = "append",
        file_format: Optional[str] = None,
        checkpoint_location: Optional[str] = None
    ):
        """
        Inicializa o motor de ingestão
        
        Args:
            target_schema: Schema de destino (deve existir previamente)
            table_name: Nome da tabela de destino
            file_path: Caminho do arquivo ou diretório de origem
            delimiter: Delimitador para arquivos CSV (padrão: ",")
            catalog_name: Nome do catálogo Unity Catalog
            output_mode: Modo de escrita (append, overwrite, merge)
            file_format: Formato do arquivo (detectado automaticamente se None)
            checkpoint_location: Localização do checkpoint para streaming
        """
        self.target_schema = target_schema
        self.table_name = table_name
        self.file_path = file_path
        self.delimiter = delimiter
        self.catalog_name = catalog_name or self._get_default_catalog()
        self.output_mode = output_mode
        self.file_format = file_format
        self.checkpoint_location = checkpoint_location
        
        # Detectar formato se não fornecido
        if not self.file_format:
            self.file_format = self._detect_file_format()
        
        # Gerar checkpoint location se não fornecido (para streaming)
        if not self.checkpoint_location:
            self.checkpoint_location = f"/tmp/checkpoints/{self.target_schema}/{self.table_name}"
        
        # Validações
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Valida os parâmetros de entrada"""
        if not self.target_schema or not self.table_name:
            raise ValueError("target_schema e table_name são obrigatórios")
        
        if not self.file_path:
            raise ValueError("file_path é obrigatório")
        
        # Validar formato suportado
        supported_formats = ["csv", "json", "parquet", "delta", "avro"]
        if self.file_format not in supported_formats:
            raise ValueError(f"Formato {self.file_format} não suportado. Use: {supported_formats}")
        
        # Validar modo de saída
        valid_modes = ["append", "overwrite", "merge"]
        if self.output_mode not in valid_modes:
            raise ValueError(f"output_mode deve ser um de: {valid_modes}")
    
    def _get_default_catalog(self) -> str:
        """Obtém o catálogo padrão do workspace"""
        return os.getenv("DINO_DEFAULT_CATALOG", "main")
    
    def _detect_file_format(self) -> str:
        """Detecta o formato do arquivo baseado na extensão"""
        if self.file_path.endswith('/'):
            # Diretório - assumir primeiro arquivo encontrado
            return "csv"  # Padrão para diretórios
        
        extension = Path(self.file_path).suffix.lower()
        format_map = {
            '.csv': 'csv',
            '.json': 'json', 
            '.jsonl': 'json',
            '.parquet': 'parquet',
            '.delta': 'delta',
            '.avro': 'avro'
        }
        
        detected = format_map.get(extension, 'csv')
        print(f"📋 Formato detectado: {detected}")
        return detected
    
    def get_table_full_name(self) -> str:
        """Retorna o nome completo da tabela"""
        return f"{self.catalog_name}.{self.target_schema}.{self.table_name}"
    
    def _check_schema_exists(self) -> bool:
        """Verifica se o schema existe (simulação para ambiente local)"""
        # Em ambiente Databricks real, isso seria:
        # spark.sql(f"SHOW SCHEMAS IN {self.catalog_name}").filter(col("schemaName") == self.target_schema).count() > 0
        
        print(f"🔍 Verificando se schema {self.catalog_name}.{self.target_schema} existe...")
        print(f"✅ Schema validado (simulação - em Databricks seria verificação real)")
        return True
    
    def _generate_streaming_code(self) -> str:
        """Gera código PySpark para ingestão streaming com Auto Loader"""
        table_full_name = self.get_table_full_name()
        
        code = f'''
# Dino SDK - Ingestão Streaming com Auto Loader
# Gerado automaticamente em {datetime.now().isoformat()}

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable
import time

# Configurações da ingestão
SOURCE_PATH = "{self.file_path}"
TARGET_TABLE = "{table_full_name}"
CHECKPOINT_LOCATION = "{self.checkpoint_location}"
FILE_FORMAT = "{self.file_format}"
DELIMITER = "{self.delimiter}"

print(f"🚀 Iniciando ingestão streaming com Auto Loader")
print(f"📁 Origem: {{SOURCE_PATH}}")
print(f"📊 Destino: {{TARGET_TABLE}}")
print(f"💾 Checkpoint: {{CHECKPOINT_LOCATION}}")
print(f"📋 Formato: {{FILE_FORMAT}}")

# Configurar Auto Loader
auto_loader_options = {{
    "cloudFiles.format": FILE_FORMAT,
    "cloudFiles.schemaLocation": f"{{CHECKPOINT_LOCATION}}/schema",
    "cloudFiles.useNotifications": "true",
    "cloudFiles.includeExistingFiles": "false",
    "cloudFiles.maxFilesPerTrigger": "100"
}}

# Adicionar opções específicas para CSV
if FILE_FORMAT == "csv":
    auto_loader_options.update({{
        "cloudFiles.delimiter": DELIMITER,
        "cloudFiles.header": "true",
        "cloudFiles.inferSchema": "true"
    }})

# Configurar stream de leitura
print("📖 Configurando Auto Loader...")
df_stream = (spark.readStream
    .format("cloudFiles")
    .options(**auto_loader_options)
    .load(SOURCE_PATH))

# Adicionar metadados de processamento
df_with_metadata = (df_stream
    .withColumn("_dino_ingestion_timestamp", current_timestamp())
    .withColumn("_dino_source_file", input_file_name())
    .withColumn("_dino_file_modification_time", 
               col("_metadata.file_modification_time"))
    .withColumn("_dino_batch_id", expr("uuid()"))
    .withColumn("_dino_ingestion_mode", lit("streaming"))
    .withColumn("_dino_table_name", lit("{self.table_name}"))
    .withColumn("_dino_schema_name", lit("{self.target_schema}"))
)

print("✅ Stream configurado com metadados de auditoria")

# Função para processar batch
def process_batch(batch_df, batch_id):
    print(f"📦 Processando batch {{batch_id}}")
    print(f"📊 Registros no batch: {{batch_df.count()}}")
    
    # Salvar na tabela de destino
    (batch_df.write
        .format("delta")
        .mode("{self.output_mode}")
        .option("mergeSchema", "true")
        .saveAsTable(TARGET_TABLE))
    
    print(f"✅ Batch {{batch_id}} processado com sucesso")

# Configurar streaming query
print("⚡ Iniciando streaming query...")
query = (df_with_metadata.writeStream
    .foreachBatch(process_batch)
    .option("checkpointLocation", CHECKPOINT_LOCATION)
    .trigger(availableNow=False)  # Modo contínuo
    .start())

print("🔄 Streaming em execução. Monitore os logs para acompanhar o progresso.")
print("⏹️ Para parar, execute: query.stop()")

# Aguardar (opcional - remova se quiser que rode em background)
# query.awaitTermination()
'''
        return code
    
    def _generate_batch_code(self) -> str:
        """Gera código PySpark para ingestão batch"""
        table_full_name = self.get_table_full_name()
        
        # Configurações de leitura baseadas no formato
        read_options = self._get_read_options()
        
        code = f'''
# Dino SDK - Ingestão Batch
# Gerado automaticamente em {datetime.now().isoformat()}

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable
import time

# Configurações da ingestão
SOURCE_PATH = "{self.file_path}"
TARGET_TABLE = "{table_full_name}"
FILE_FORMAT = "{self.file_format}"
OUTPUT_MODE = "{self.output_mode}"

print(f"🚀 Iniciando ingestão batch")
print(f"📁 Origem: {{SOURCE_PATH}}")
print(f"📊 Destino: {{TARGET_TABLE}}")
print(f"📋 Formato: {{FILE_FORMAT}}")
print(f"💾 Modo: {{OUTPUT_MODE}}")

# Configurar leitura baseada no formato
print("📖 Configurando leitura de dados...")

{self._generate_read_code()}

# Adicionar metadados de auditoria
print("🏷️ Adicionando metadados de auditoria...")
df_with_metadata = (df_source
    .withColumn("_dino_ingestion_timestamp", current_timestamp())
    .withColumn("_dino_source_path", lit(SOURCE_PATH))
    .withColumn("_dino_batch_id", expr("uuid()"))
    .withColumn("_dino_ingestion_mode", lit(OUTPUT_MODE))
    .withColumn("_dino_table_name", lit("{self.table_name}"))
    .withColumn("_dino_schema_name", lit("{self.target_schema}"))
)

print("✅ Metadados adicionados")
print(f"📊 Registros carregados: {{df_with_metadata.count()}}")

# Mostrar preview dos dados
print("👀 Preview dos dados:")
df_with_metadata.select("*").limit(5).show(truncate=False)

{self._generate_write_code()}

print("✅ Ingestão batch concluída com sucesso!")

# Mostrar estatísticas finais
print("📊 Estatísticas da tabela:")
spark.sql(f"SELECT COUNT(*) as total_records FROM {{TARGET_TABLE}}").show()

# Mostrar últimas ingestões
print("📈 Últimas ingestões (últimas 24h):")
spark.sql(f"""
    SELECT 
        _dino_batch_id,
        _dino_ingestion_timestamp,
        COUNT(*) as records_count,
        _dino_source_path
    FROM {{TARGET_TABLE}}
    WHERE _dino_ingestion_timestamp >= current_timestamp() - INTERVAL 1 DAY
    GROUP BY _dino_batch_id, _dino_ingestion_timestamp, _dino_source_path
    ORDER BY _dino_ingestion_timestamp DESC
    LIMIT 10
""").show(truncate=False)
'''
        return code
    
    def _get_read_options(self) -> Dict[str, str]:
        """Retorna opções de leitura baseadas no formato"""
        if self.file_format == "csv":
            return {
                "header": "true",
                "inferSchema": "true", 
                "delimiter": self.delimiter
            }
        elif self.file_format == "json":
            return {
                "multiline": "true"
            }
        else:
            return {}
    
    def _generate_read_code(self) -> str:
        """Gera código de leitura baseado no formato"""
        if self.file_format == "csv":
            return f'''df_source = (spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("delimiter", "{self.delimiter}")
    .load(SOURCE_PATH))'''
        
        elif self.file_format == "json":
            return '''df_source = (spark.read
    .format("json")
    .option("multiline", "true")
    .load(SOURCE_PATH))'''
        
        elif self.file_format == "parquet":
            return '''df_source = (spark.read
    .format("parquet")
    .load(SOURCE_PATH))'''
        
        elif self.file_format == "delta":
            return '''df_source = (spark.read
    .format("delta")
    .load(SOURCE_PATH))'''
        
        elif self.file_format == "avro":
            return '''df_source = (spark.read
    .format("avro")
    .load(SOURCE_PATH))'''
        
        else:
            return f'''df_source = (spark.read
    .format("{self.file_format}")
    .load(SOURCE_PATH))'''
    
    def _generate_write_code(self) -> str:
        """Gera código de escrita baseado no modo e particionamento"""
        partition_code = ""
        if self.partition_columns:
            partition_cols = '", "'.join(self.partition_columns)
            partition_code = f'.partitionBy("{partition_cols}")'
        
        if self.output_mode == "overwrite":
            return f'''# Salvar com overwrite
print("💾 Salvando dados (overwrite)...")
(df_with_metadata.write
    .format("delta")
    .mode("overwrite")
    .option("mergeSchema", "true"){partition_code}
    .saveAsTable(TARGET_TABLE))'''
        
        elif self.output_mode == "merge":
            return '''# Implementar merge (upsert) - requer chave primária
print("🔄 Implementando merge/upsert...")
# Nota: Para merge, você precisa definir as colunas de merge
# Exemplo de implementação:
# if DeltaTable.isDeltaTable(spark, TARGET_TABLE):
#     delta_table = DeltaTable.forName(spark, TARGET_TABLE)
#     delta_table.alias("target").merge(
#         df_with_metadata.alias("source"),
#         "target.id = source.id"  # Ajustar conforme sua chave
#     ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
# else:
#     df_with_metadata.write.format("delta").saveAsTable(TARGET_TABLE)

# Por enquanto, usar append
(df_with_metadata.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(TARGET_TABLE))
print("⚠️ Merge não implementado - usando append")'''
        
        else:  # append
            return f'''# Salvar com append
print("💾 Salvando dados (append)...")
(df_with_metadata.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true"){partition_code}
    .saveAsTable(TARGET_TABLE))'''
    
    def execute_ingestion(self, is_automated: bool = False) -> Dict[str, Any]:
        """
        Executa a ingestão (batch ou streaming)
        
        Args:
            is_automated: Se True, gera código para streaming com file arrival
                         Se False, gera código para ingestão batch
        
        Returns:
            Dict com resultado da operação
        """
        try:
            mode = "streaming" if is_automated else "batch"
            print(f"🦕 Dino SDK - Iniciando ingestão {mode}")
            print(f"📊 Tabela destino: {self.get_table_full_name()}")
            print(f"📋 Formato: {self.file_format}")
            
            # Verificar pré-requisitos
            if not self._check_schema_exists():
                raise ValueError(f"Schema {self.target_schema} não existe. Crie o schema antes da ingestão.")
            
            # Gerar código de ingestão baseado no modo
            if is_automated:
                ingestion_code = self._generate_streaming_code()
                filename = f"ingestion_streaming_{self.target_schema}_{self.table_name}.py"
            else:
                ingestion_code = self._generate_batch_code()
                filename = f"ingestion_batch_{self.target_schema}_{self.table_name}.py"
            
            # Salvar código em arquivo para execução manual
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(ingestion_code)
            
            print(f"📝 Código de ingestão salvo em: {filename}")
            print(f"💡 Execute este código em um notebook Databricks para realizar a ingestão")
            
            result = {
                'success': True,
                'table_full_name': self.get_table_full_name(),
                'detected_format': self.file_format,
                'output_mode': self.output_mode,
                'catalog_name': self.catalog_name,
                'schema_name': self.target_schema,
                'table_name': self.table_name,
                'source_path': self.file_path,
                'ingestion_file': filename,
                'is_automated': is_automated,
                'timestamp': datetime.now().isoformat()
            }
            
            # Adicionar checkpoint location se for streaming
            if is_automated:
                result['checkpoint_location'] = self.checkpoint_location
            
            return result
            
        except Exception as e:
            print(f"❌ Erro na ingestão: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_ingestion_status(self) -> Dict[str, Any]:
        """Retorna status da ingestão (simulação)"""
        # Em ambiente real, consultaria métricas da tabela
        return {
            'status': 'ready_for_execution',
            'table_name': self.get_table_full_name(),
            'last_check': datetime.now().isoformat(),
            'message': 'Código de ingestão gerado. Execute no Databricks.'
        }
